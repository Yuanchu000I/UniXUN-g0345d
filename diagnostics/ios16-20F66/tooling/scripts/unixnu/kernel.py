"""XNU kernel: build from the patched Apple source, then prelink against the original kernelcache."""
import os
import hashlib
import json
import platform
import re
import shlex
import shutil
import struct
import tempfile
from pathlib import Path

from . import components, ipsw, patches
from .config import load_toml
from .util import Error, expand, log, run, sha256_file, tool


def _machine_config(ctx):
    """Return the board's XNU machine name, refusing silent BCM fallback for schema v2."""
    kernel = ctx.board.get('kernel', {})
    if getattr(ctx, 'schema_version', 1) == 2 and 'machine_config' not in kernel:
        raise Error('[kernel] machine_config is required for schema_version=2')
    machine = kernel.get('machine_config', 'BCM2837')
    if not isinstance(machine, str) or not re.fullmatch(r'[A-Z][A-Z0-9]*', machine):
        raise Error('[kernel] machine_config must be an uppercase XNU machine name')
    return machine


def xnu_env(ctx):
    """CONFIG_XNU_* of the defconfig become XNU_* variables of the legacy kernel build script."""
    env = {}
    for key, value in ctx.need_config().items():
        if not key.startswith('XNU_'):
            continue
        if isinstance(value, str):
            value = value.replace('{tree}', str(ctx.tree))
        env[key] = '1' if value is True else '0' if value is False else str(value)
    machine = _machine_config(ctx)
    env['UNIXNU_XNU_MACHINE_CONFIG'] = machine
    if getattr(ctx, 'schema_version', 1) == 2:
        env['UNIXNU_XNU_REQUIRE_MACHINE_CONFIG'] = '1'
    env['UNIXNU_XNU_OBJECT_DIR'] = str((ctx.tree / 'build/xnu/ios-obj' / f'DEVELOPMENT_ARM64_{machine}').resolve())
    return env


def xnu_object_dir(ctx):
    """Object root selected by the device's explicit XNU machine configuration."""
    machine = _machine_config(ctx)
    return ctx.tree / 'build/xnu/ios-obj' / f'DEVELOPMENT_ARM64_{machine}'


def version_env(modules, ctx=None):
    """Source versions of the Apple references, from feeds.toml, for the kernel scripts."""
    env = {}
    for name, prefix in (('xnu', 'XNU'), ('libplatform', 'LIBPLATFORM'), ('libdispatch', 'LIBDISPATCH'), ('AvailabilityVersions', 'AVAILABILITYVERSIONS'), ('libpthread', 'LIBPTHREAD'), ('IOStorageFamily', 'IOSTORAGEFAMILY')):
        module = modules.get(('refer', name))
        entry = module.source if module and module.source else {}
        if entry.get('ref'):
            env[f'UNIXNU_{prefix}_TAG'] = entry['ref']
        if entry.get('commit'):
            env[f'UNIXNU_{prefix}_COMMIT'] = entry['commit']
    xnu = (modules.get(('refer', 'xnu')) or None) and modules[('refer', 'xnu')].source or {}
    for key, variable in (('darwin', 'UNIXNU_XNU_DARWIN'), ('version', 'UNIXNU_XNU_VERSION'),
                          ('driverkit_tag', 'UNIXNU_DRIVERKIT_TAG'), ('trustcache_tag', 'UNIXNU_TRUSTCACHE_TAG')):
        if xnu.get(key):
            env[variable] = xnu[key]
    if ctx and ctx.schema_version == 2:
        profile = ctx.board.get('os', {})
        for key, variable in (('xnu_revision', 'UNIXNU_XNU_COMMIT'), ('xnu_version', 'UNIXNU_XNU_VERSION'),
                              ('darwin', 'UNIXNU_XNU_DARWIN'), ('driverkit_tag', 'UNIXNU_DRIVERKIT_TAG'),
                              ('trustcache_tag', 'UNIXNU_TRUSTCACHE_TAG')):
            if profile.get(key):
                env[variable] = profile[key]
        if profile.get('xnu_version'):
            env['UNIXNU_XNU_TAG'] = 'xnu-' + profile['xnu_version']
        if profile.get('ios_version'):
            env['UNIXNU_IOS_VERSION'] = profile['ios_version']
        # The userspace the kernel serves: ios (default) or macosx (XNU_TARGET_OS_OSX instead of XNU_TARGET_OS_IOS).
        env['UNIXNU_XNU_TARGET'] = profile.get('target', 'ios')
        # The root images of the OS: volume UUIDs and image digests the kernel and the storage builder check.
        root = ctx.board.get('root', {})
        for key, variable in (('os_volume_uuid', 'XNU_OWNER_ROOT_VOLUME_UUID'),
                              ('systemos_volume_uuid', 'XNU_OWNER_CACHE_VOLUME_UUID'),
                              ('app_volume_uuid', 'XNU_OWNER_APP_VOLUME_UUID'),
                              ('os_image_sha256', 'UNIXNU_ROOT_OS_SHA256'),
                              ('systemos_image_sha256', 'UNIXNU_ROOT_SYSTEMOS_SHA256'),
                              ('app_image_sha256', 'UNIXNU_ROOT_APP_SHA256')):
            if root.get(key):
                env[variable] = root[key]
        if root.get('os_volume_uuid'):
            env['UNIXNU_ROOT_OS_UUID'] = root['os_volume_uuid']
        if root.get('systemos_volume_uuid'):
            env['UNIXNU_ROOT_SYSTEMOS_UUID'] = root['systemos_volume_uuid']
        if root.get('app_volume_uuid'):
            env['UNIXNU_ROOT_APP_UUID'] = root['app_volume_uuid']
        env['UNIXNU_IPSW_BUILD'] = ctx.board.get('ipsw', {}).get('build', '')
        env['UNIXNU_XNU_ARCH'] = load_toml(ctx.profile_roots['arch'] / 'profile.toml').get('arch', {}).get('name', 'arm64')
    return env


def toolchain_path(path=None):
    """PATH with the Homebrew LLVM and LLD first, as the archive builders expect."""
    extra = [d for d in ('/opt/homebrew/opt/llvm/bin', '/opt/homebrew/opt/lld/bin', '/usr/local/opt/llvm/bin', '/usr/local/opt/lld/bin')
             if Path(d).is_dir()]
    return os.pathsep.join(extra + [path if path is not None else os.environ.get('PATH', '')])


def linux_target(ctx):
    """Validate explicit Linux SDK/triple metadata; retain the legacy iOS 17 default."""
    spec = ctx.board.get('kernel', {}).get('linux', {})
    if not isinstance(spec, dict):
        raise Error('[kernel.linux] must be a table')
    if not spec:
        return '17.0', 'arm64-apple-ios17.0'
    if set(spec) != {'sdk_version', 'triple'}:
        raise Error('[kernel.linux] requires exactly sdk_version and triple')

    def version(value, label):
        if not isinstance(value, str) or not re.fullmatch(r'[1-9][0-9]*\.(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*))?', value):
            raise Error(f'{label} must be a numeric major.minor[.patch] string')
        parts = tuple(int(part) for part in value.split('.'))
        return parts + (0,) * (3 - len(parts))

    sdk, triple = spec['sdk_version'], spec['triple']
    sdk_version = version(sdk, '[kernel.linux] sdk_version')
    match = re.fullmatch(r'(arm64|arm64e)-apple-ios(.+)', triple) if isinstance(triple, str) else None
    if not match:
        raise Error('[kernel.linux] triple must use arm64 or arm64e with -apple-ios<version>')
    architecture, deployment = match.groups()
    deployment_version = version(deployment, '[kernel.linux] triple deployment')
    profile = ctx.board.get('os', {})
    if architecture != profile.get('arch', 'arm64'):
        raise Error('[kernel.linux] triple architecture must match [os] arch')
    if deployment_version != version(profile.get('ios_version', '17.0'), '[os] ios_version'):
        raise Error('[kernel.linux] triple deployment must match [os] ios_version')
    if sdk_version < deployment_version:
        raise Error('[kernel.linux] sdk_version must not be older than its deployment target')
    return sdk, triple


def linux_env(ctx):
    """Environment of the kernel step on a Linux host, with the toolchain of scripts/linux/setup-toolchain.py.

    The xcrun shim answers every --sdk query with the fakeroot this build makes. Explicit [kernel.linux]
    metadata selects its SDK version and Darwin triple; absent metadata retains plain arm64 / iOS 17.
    The clang wrapper keeps C++ static destructors in __mod_term_func.
    CCC_OVERRIDE_OPTIONS (read by the clang driver itself, so also by the archive builders that replay xnu's
    compile records) turns off two warnings that upstream clang has and Apple clang does not; the builders compile
    with -Werror.
    """
    sdk_version, triple = linux_target(ctx)
    toolchain = Path(os.environ.get('UNIXNU_TOOLCHAIN', '/opt/unixnu-linux'))
    clt, xctoolchain = toolchain / 'CommandLineTools/usr', toolchain / 'XcodeDefault.xctoolchain/usr'
    # G0245D: an unprivileged install keeps the xcrun/plutil/codesign shims in
    # the prefix's bin instead of /usr/bin.
    xcrun = toolchain / 'bin/xcrun'
    if not xcrun.exists():
        xcrun = Path('/usr/bin/xcrun')
    for path in (toolchain / 'llvm/bin/clang', clt / 'bin/ld', clt / 'bin/xnu-host-cc', clt / 'libexec/migcom',
                 xctoolchain / 'bin/iig', xcrun, toolchain / 'bin/lzfse'):
        if not path.exists():
            raise Error(f'{path} missing; run "sudo scripts/linux/setup-toolchain.py {toolchain}"')
    fakeroot = ctx.tree / '.cache/fakeroot'
    return {'PATH': os.pathsep.join([str(clt / 'bin'), str(toolchain / 'bin'), os.environ.get('PATH', '')]),
            'LC_ALL': 'C', 'CLT_PREFIX': str(clt), 'XCTOOLCHAIN_PREFIX': str(xctoolchain),
            'XNU_TOOLCHAIN_BIN': f'{clt / "bin"} {xctoolchain / "bin"}',
            'UNIXNU_SDKROOT': str(fakeroot), 'UNIXNU_SDK_VERSION': sdk_version,
            'UNIXNU_PLATFORM_PATH': str(fakeroot / 'Platforms/iPhoneOS.platform'),
            'CROSS_CLANG': str(toolchain / 'llvm/bin/clang'), 'DARWIN_TRIPLE': triple,
            'CROSS_EXTRA_FLAGS': '-mllvm -disable-atexit-based-global-dtor-lowering',
            'CCC_OVERRIDE_OPTIONS': '# +-Wno-missing-designated-field-initializers +-Wno-unused-but-set-global +-Wno-unsafe-buffer-usage'}


def archive_plan(ctx):
    """Expand selected component recipes at their ordered archive positions."""
    entries = ctx.board.get('kernel', {}).get('archives', [])
    if ctx.schema_version == 1:
        return [('script', entry) for entry in entries]
    specs = {spec['id']: spec for spec in ctx.component_specs}
    required = {name for name, spec in specs.items() if spec.get('build') and spec.get('build_stage', 'kernel') == 'kernel'}
    result, visited = [], set()

    def add_component(identifier):
        if identifier in visited:
            return
        spec = specs.get(identifier)
        if spec is None:
            raise Error(f'[kernel] archives: component {identifier} is not selected')
        for dependency in spec.get('dependencies', []):
            add_component(dependency)
        visited.add(identifier)
        if identifier in required:
            result.append(('component', spec))

    explicit = any(entry.startswith('component:') for entry in entries)
    if not explicit:
        for identifier in specs:
            add_component(identifier)
    for entry in entries:
        if entry.startswith('component:'):
            add_component(entry[len('component:'):])
        else:
            result.append(('script', entry))
    missing = required - visited
    if missing:
        raise Error('[kernel] archives needs component entries for: ' + ', '.join(sorted(missing)))
    return result


def build_archives(ctx, env):
    """Build ordered component recipes and auxiliary archives from compile records."""
    if not ctx.need_config().get('XNU_BUILD_ARCHIVES'):
        return
    env = dict(env, PATH=toolchain_path(env.get('PATH')), UNIXNU_DEVICE=str(ctx.device))
    for index, (kind, entry) in enumerate(archive_plan(ctx), 1):
        if kind == 'component':
            spec = entry
            module = ctx.modules[(spec['kind'], spec['id'])]
            replacements = {'tree': str(ctx.tree), 'component': str(module.path), 'out': str(ctx.work)}
            parts = [part.format(**replacements) for part in spec['build']]
            label = f'component-{spec["id"]}'
        else:
            parts = shlex.split(entry)
            label = f'archive-{index:02d}-{Path(parts[0]).stem}'
        executable = Path(parts[0])
        if executable.suffix in ('.py', '.sh'):
            script = executable if executable.is_absolute() else ctx.tree / 'scripts' / executable
            if not script.is_file():
                raise Error(f'{label}: build script missing: {script}')
            parts = ['python3' if executable.suffix == '.py' else 'bash', str(script), *parts[1:]]
        log(f'kernel: {label}')
        run(parts, cwd=ctx.tree, env=env, log_file=ctx.logs / f'{label}.log')
        components.sync_outputs(ctx, ctx.modules)
    for key, value in sorted(xnu_env(ctx).items()):
        if key.endswith('_ARCHIVE') and value.endswith('.a') and not Path(value).is_file():
            raise Error(f'{key}: {value} not found; supply the archive or its build recipe')


BOOTSTRAP_RECIPES = ('osfmk/DEVELOPMENT/startup.o.json',
                     'iokit/DEVELOPMENT/IOPlatformExpert.cpo.json',
                     'bsd/DEVELOPMENT/vfs_conf.o.json',
                     'osfmk/DEVELOPMENT/prng_random.o.json')


def bootstrap_input_errors(ctx):
    """Check actual non-LTO XNU link inputs and the recipes replayed by archive builders."""
    root = xnu_object_dir(ctx)
    errors = []

    def nonempty(path):
        return path.is_file() and path.stat().st_size > 0

    filelist = root / 'link.filelist'
    if not nonempty(filelist):
        errors.append('missing or empty link.filelist')
    else:
        objects = [line.strip() for line in filelist.read_text().splitlines() if line.strip()]
        if not objects:
            errors.append('link.filelist has no objects')
        for entry in objects:
            path = Path(entry)
            if not path.is_absolute():
                path = root / path
            if not nonempty(path):
                errors.append(f'link.filelist object missing or empty: {entry}')

    # MakeInc.kernel's BUILD_LTO=0 link adds these outside link.filelist.
    for name in ('version.o', 'lastkerneldataconst.o', 'lastkernelconstructor.o', 'nonlto.o'):
        if not nonempty(root / name):
            errors.append(f'missing or empty {name}')

    # C/C++ driver, MockFS and pthread builders replay these actual compiler records.
    for relative in BOOTSTRAP_RECIPES:
        recipe = root / relative
        try:
            record = json.loads(recipe.read_text().strip().rstrip(','))
            arguments = record['arguments']
            directory, source, output = (record[key] for key in ('directory', 'file', 'output'))
            if (not all(isinstance(value, str) and value for value in (directory, source, output)) or
                    not isinstance(arguments, list) or not arguments or
                    not all(isinstance(value, str) for value in arguments) or
                    '-c' not in arguments or source not in arguments or
                    '-o' not in arguments or arguments[arguments.index('-o') + 1] != output):
                raise ValueError('incomplete compiler record')
            directory = Path(directory)
            source = Path(source) if Path(source).is_absolute() else directory / source
            output = Path(output) if Path(output).is_absolute() else directory / output
            if (not directory.is_absolute() or not directory.is_dir() or not source.is_file() or
                    output.resolve() != recipe.with_suffix('').resolve() or not nonempty(output)):
                raise ValueError('compiler record lacks its source or generated object')
        except (OSError, ValueError, TypeError, KeyError, IndexError) as error:
            errors.append(f'invalid or incomplete {relative}: {error}')
    return errors


def invalidate_incomplete_bootstrap_objects(ctx, errors):
    """Force a fresh compile when a prior object has no usable replay record."""
    root = xnu_object_dir(ctx)
    for relative in BOOTSTRAP_RECIPES:
        if any(error.startswith(f'invalid or incomplete {relative}:') for error in errors):
            output = root / Path(relative).with_suffix('')
            output.unlink(missing_ok=True)


def build(ctx, modules):
    log('kernel: XNU')
    script = ctx.tree / 'scripts/build-xnu-4k-baseline.sh'
    if not script.is_file():
        raise Error(f'{script} missing')
    env = dict(os.environ)
    # The external archive builders replay real XNU compiler records from both
    # bootstrap and final builds. Keep record generation enabled for every pass.
    env['BUILD_OBJECT_JSON_RECORDS'] = '1'
    # ar records each member's mtime; without this the archives change on every build and the release reference never hits its cache.
    env['ZERO_AR_DATE'] = '1'
    if platform.system() == 'Linux':
        for name in ('git', 'make', 'cmake', 'ninja', 'unifdef'):
            tool(name, 'run sudo scripts/linux/setup-toolchain.py')
        env.update(linux_env(ctx))
    else:
        for name in ('git', 'make', 'clang', 'cmake', 'ninja', 'unifdef'):
            tool(name, 'brew install ' + name)
        tool('xcodebuild', 'the kernel step builds with the Xcode iphoneos SDK')
    env.update(xnu_env(ctx))
    env.update(version_env(modules, ctx))
    if ctx.schema_version == 2:
        env['UNIXNU_PATCH_LIST'] = str(patches.prepare(ctx, modules, env=env))
        generated = ctx.tree / 'build/generated'
        generated.mkdir(parents=True, exist_ok=True)
        env['UNIXNU_GENERATED_DIR'] = str(generated)
    env['JOBS'] = str(ctx.jobs)
    initial_errors = bootstrap_input_errors(ctx)
    if initial_errors:
        # Prior objects without records are up to date to make, so force only the
        # archive seed objects whose native compiler recipes are missing or invalid.
        invalidate_incomplete_bootstrap_objects(ctx, initial_errors)
        # Compilation must reach MakeInc.kernel's non-LTO link rule. Its filelist is
        # written immediately before ld, so an expected unresolved-symbol link failure
        # may still leave all inputs needed to build the external archives. A lone
        # successful translation unit does not prove complete bootstrap readiness.
        log('kernel: bootstrap pass for complete archive inputs')
        filelist = xnu_object_dir(ctx) / 'link.filelist'
        # Prevent an earlier link attempt from masking a new source/preparation error.
        # Keep all generated objects and recipes for the incremental rebuild.
        filelist.unlink(missing_ok=True)
        subprocess_env = {**env, 'XNU_BOOT_PROGRESS': '0', 'XNU_BOOTSTRAP': '1'}
        bootstrap_error = None
        try:
            run(['bash', script], cwd=ctx.tree, env=subprocess_env, log_file=ctx.logs / 'kernel-bootstrap.log')
        except Error as error:
            bootstrap_error = error
        missing = bootstrap_input_errors(ctx)
        if missing:
            detail = '; '.join(missing[:8])
            if len(missing) > 8:
                detail += f'; and {len(missing) - 8} more missing/invalid inputs'
            raise Error(f'kernel bootstrap inputs incomplete: {detail}; see {ctx.logs / "kernel-bootstrap.log"}') from bootstrap_error
        if bootstrap_error:
            log('kernel: bootstrap link failed with complete inputs; building external archives')
    # Revalidate the selected source and regenerate headers on every archive build.
    # A pre-existing directory can belong to a different OS profile/revision.
    if (ctx.tree / 'refer/IOStorageFamily').is_dir():
        log('kernel: prepare storage headers')
        run(['python3', ctx.tree / 'scripts/prepare-storage-headers.py'], cwd=ctx.tree, env=env,
            log_file=ctx.logs / 'storage-headers.log')
    build_archives(ctx, env)
    run(['bash', script], cwd=ctx.tree, env=env, log_file=ctx.logs / 'kernel.log')


def stage_native(kernel, output):
    """Stage the native executable unchanged for bring-up without prelinked kexts."""
    data = kernel.read_bytes()
    if len(data) < 32 or struct.unpack_from('<II', data) != (0xfeedfacf, 0x100000c) or struct.unpack_from('<I', data, 12)[0] != 2:
        raise Error(f'{kernel} is not an ARM64 MH_EXECUTE native kernel')
    digest = hashlib.sha256(data).hexdigest()
    record = {'mode': 'native-only', 'format': 'MH_EXECUTE', 'native': str(kernel.resolve()),
              'native_sha256': digest, 'candidate_sha256': digest, 'candidate_bytes': len(data),
              'prelink_skipped': True, 'kernelcache_kexts_added': False, 'boot_verified': False}
    output.parent.mkdir(parents=True, exist_ok=True)
    for path, contents in ((output, data), (output.with_suffix('.json'), (json.dumps(record, indent=2) + '\n').encode())):
        name = None
        try:
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.' + path.name + '.', delete=False) as stream:
                name = stream.name
                stream.write(contents)
            os.replace(name, path)
        finally:
            if name and os.path.exists(name):
                os.unlink(name)
    log(f'kernel: native only {output} sha256 {digest}')
    return output


def check_prelink_regressions(record, policy):
    """An experimental allow-missing build may improve, but cannot add gaps."""
    slide = int(record['collection_slide'], 16)
    for kind in ('missing', 'stubbed'):
        for owner, targets in record[kind].items():
            for target, count in targets.items():
                original = hex((int(target, 16) - slide) & ((1 << 64) - 1))
                allowed = policy[kind].get(owner, {}).get(original, 0)
                if count > allowed:
                    raise Error(f'prelink regression: {kind} {owner} original {original}, {count} sites (allowed {allowed})')
    branches = {entry['symbol'] for entry in record.get('native_original_branches', [])}
    if set(policy.get('required_original_branches', [])) - branches:
        raise Error('prelink lacks required absolute adapter branch relocations')


def prelink(ctx):
    """Produce out/<device>/kernel/kernel.macho from the XNU build and the original kernelcache."""
    configuration = ctx.board.get('kernel', {})
    spec = configuration.get('prelink')
    skip = getattr(ctx.args, 'skip_prelink', False)
    if skip and 'native_kernel' in configuration:
        relative = configuration['native_kernel']
        if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or '..' in Path(relative).parts:
            raise Error('[kernel] native_kernel must be a nonempty path relative to the build tree')
        kernel = (ctx.tree / relative).resolve()
        if not kernel.is_relative_to(ctx.tree.resolve()):
            raise Error('[kernel] native_kernel must remain inside the build tree')
    else:
        if not spec:
            raise Error('board.toml has no [kernel.prelink]')
        if not isinstance(spec.get('kernel'), str) or not spec['kernel']:
            raise Error('[kernel.prelink] kernel must name the native input')
        kernel = ctx.tree / spec['kernel']
    if not kernel.is_file():
        raise Error(f'{kernel} not found; run "unixnu build kernel" first')
    output = ctx.work / 'kernel/kernel.macho'
    if skip:
        return stage_native(kernel, output)
    log('kernel: prelink')
    cache = ctx.option('kernelcache', 'UNIXNU_KERNELCACHE') or (expand(ctx.tree / spec['kernelcache']) if spec.get('kernelcache') else None)
    if not cache:
        # Not given: take it from the IPSW (--ipsw PATH_OR_URL, or the url of board.toml [ipsw]).
        cache = ipsw.kernelcache(ctx, ipsw.Ipsw(ctx))
    if not cache.is_file():
        raise Error(f'kernelcache not found: {cache}')
    wanted = spec.get('kernelcache_sha256')
    if wanted and sha256_file(cache) != wanted:
        raise Error(f'{cache} does not match the kernelcache this board was qualified against (sha256 {wanted})')
    output.parent.mkdir(parents=True, exist_ok=True)
    # A fileset stays at the native link address and has no slide; the static-prelink format needs one.
    command = ['python3', ctx.tree / spec['tool'], '--kernel', kernel, '--prelinked', cache,
               f'--slide={spec.get("slide", "0")}']
    for root in spec.get('roots', []):
        command += ['--root', root]
    if spec.get('early_security_init'):
        command += ['--early-security-init', spec['early_security_init']]
    command += spec.get('extra_args', [])
    # A failed rebuild must not remove the last candidate or its record.
    with tempfile.TemporaryDirectory(dir=output.parent, prefix='.prelink-') as directory:
        candidate = Path(directory) / output.name
        saved_map = output.with_suffix('.map.json')
        candidate_map = candidate.with_suffix('.map.json')
        if saved_map.is_file():
            shutil.copyfile(saved_map, candidate_map)
        success = False
        try:
            run(command + ['--output', candidate], cwd=ctx.tree, log_file=ctx.logs / 'prelink.log')
            if not candidate.is_file():
                raise Error('prelink completed without writing a kernel candidate')
            if spec.get('regression_policy'):
                policy = json.loads((ctx.tree / spec['regression_policy']).read_text())
                if policy['kernelcache_sha256'] != sha256_file(cache):
                    raise Error('prelink regression policy names another kernelcache')
                check_prelink_regressions(json.loads(candidate.with_suffix('.json').read_text()), policy)
            success = True
        finally:
            if candidate_map.is_file():
                os.replace(candidate_map, saved_map)
            record_path = candidate.with_suffix('.json')
            if record_path.is_file():
                record = json.loads(record_path.read_text())
                record['output'] = str(output.resolve())
                if record.get('map') == str(candidate_map.resolve()):
                    record['map'] = str(saved_map.resolve())
                record_path.write_text(json.dumps(record, indent=2) + '\n')
                destination = output.with_suffix('.json' if success else '.failed.json')
                os.replace(record_path, destination)
                if not success:
                    log(f'kernel: prelink failed; diagnostic record {destination}')
        os.replace(candidate, output)
    log(f'kernel: {output} sha256 {sha256_file(output)}')
    return output

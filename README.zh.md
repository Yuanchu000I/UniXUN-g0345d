# 格力 G0345D 的 UniXNU 移植

[English](README.md) · [结构化移植记录](porting.toml) · [当前状态](docs/status.md)

本仓是格力 G0345D（G3、MSM8996）移植实验的 M42/v185 源码整理，目标为
`ipados-17.7.11-21H461`。当前停在 `_kalloc_init` 的 fixed-zone 创建及相邻探针区间，
照片解码为 phase `0x4107`、value `1127`。尚未完成 XNU 启动或进入用户态。
UFS 数据读写、触摸、GPU、网络和音频均未实机验证，CPU1–3 关闭。

已按官方设备仓结构整理板级配置、DTS、51 个有序补丁、来源锁定、移植记录、
标准打包入口与 CI。补丁中的 `g0245d_*` 名称属于继承关系，保持原样以便比对。
原工作区和历史镜像未被改写，本次整理没有新构建或设备操作。

本仓适合上传为实验源码仓，完整官方发布仍有缺口：

- 上游组件目录尚未包含四个 MSM8996 组件；记录检查明确使用固定 fork 目录。
- fork 中部分组件标为 `LOCAL-SCAFFOLD`，但实现已经提交在固定工具版本；干净环境的完整来源解析及发布仍待验证。
- 配套 UEFI 基于旧 EDK2 分支，尚未独立整理其本地增量；普通固件构建不能直接复现冻结的 M42 容器。
- `scripts/package.sh` 是未改动的官方模板；当前 macOS 标准 release 路径未验证，手动打包工作流会明确阻止继续。

本地只需 Python 3.11+ 和 Git 即可运行源码检查：

```sh
python3 scripts/check-repository.py
```

构建环境、工具版本及命令见 [英文 README](README.md)。
发布步骤与未完成条件见 [发布说明](docs/publication.md)，
硬件参数见 [硬件记录](docs/hardware.md)，固件依赖见 [固件说明](docs/firmware-dependency.md)。
`porting.toml` 是状态的权威记录；历史日志和照片解码只描述当时的实验。

仓内不含 Apple/OEM 二进制、原始照片、个人绝对路径、设备序列号或设备种子。
本地覆盖放在忽略的 `local.toml`，示例见 `local.toml.example`。
后续实验仅允许 `fastboot boot`；保持 FD、头部 kernel_size 和 kernel/container 布局。
硬件排查继续暂停，等待明确恢复。

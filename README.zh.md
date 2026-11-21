# G0345D 的 UniXNU iPhone iOS 16.5 移植

[English](README.md) | [结构化移植记录](porting.toml) | [当前状态](docs/status.md)

目标硬件为 GREE G0345D（G3、MSM8996），目标系统为 iPhone iOS 16.5，build
20F66 / Darwin 22.5.0。当前诊断源码使用 XNU 8796.121.2 和精确的 46 个有序补丁，
仍为 native-only / skip-prelink，无 20F66 donor kext。这是实验性源码预发布，
不是可安装的 iOS 发行版，也没有完成完整 iOS 启动。

## 当前边界：2026-11-21

官方阶段 5（内核入口到平台专家）仍在进行，细分在早期 PE 初始化返回后的
WFE/时钟初始化。UEFI、菜单、payload 与 DarwinBoot 交接已有既往证据；
阶段 5 整体未完成，阶段 6 存储/根卷和阶段 7 用户态尚未到达。

v9 白色 WFE 入口带和红色分类槽结合已审计机器码，支持真实 timebase=0、
quotient=0、index=0xffffffff，并到达原 shift 前的分类像素 stores。它不证明
末尾 DSB、后续 shift/UBSAN、异常 PC、具体零时钟根因、函数返回或稳定性。
照片缺少独立整镜像传输摘要；菜单和倒计时为保留像素。

v10 精确复用 v9 内核，仅对 ADT 的 9 个 u64 字段（实际 10 字节）做隔离的
MSM8996 64 KiB SoC 窗口适配。7 个 reg 的真实物理地址及长度、真实 19.2MHz、
WFE 算法与 UBSAN 均保留。独立 FAT/ADT 审计及 Windows 核验通过，finalization
为 ready-for-temporary-device-test；**v10 尚未实机测试**。
见[脱敏的 v9/v10 摘要](docs/bringup/stage5-wfe-v10-20261121.md)。

## 源码与复现范围

- [diagnostics/ios16-20F66](diagnostics/ios16-20F66/README.md) 保存精确的 46 补丁
  源码、工具、pins、manifest 与脱敏派生摘要。
- 根 [iOS profile](docs/os-profile-proposal/ios-16.5-20F66/) 仍为独立的 XNU
  8796.101.5 提案，**不是 v9/v10 的构建输入**。board 和 profile patch_series
  保持空；空列表本身不能阻止 CLI 编译未打补丁内核。
- 旧 iPadOS 17 路线已废弃。根 patches/xnu/series 清空，51 个旧补丁经哈希
  核对后删除；[旧 main 提交保留历史](docs/ipados17-abandoned.md)。
- iPhone10,3 仅为系统 donor 身份，不改变目标硬件。20F66 kernelcache/prelink
  输入及组件 ABI 兼容性未解决；UFS、BLSP、Adreno 仍为探测脚手架。
- 完整干净构建仍缺 companion firmware delta 与合法 Apple/OEM 外部输入，
  历史封装工具不是已验证的标准 iOS 发布流水线。

## 离线检查

~~~sh
python3 scripts/check-repository.py
python3 diagnostics/ios16-20F66/check_export.py
git diff --check
~~~

检查源码完整性、哈希、记录归属与公开卫生，不证明内核编译、驱动功能、
实机稳定性或 iOS 用户态。详见[发布限制](docs/publication.md)。

本仓不发布二进制、原始 ADT、原始照片、设备序列号/种子、凭据、个人绝对路径
或私有原始报告。硬件测试需单独授权，仅允许临时 fastboot boot，禁止刷分区。

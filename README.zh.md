# G0345D 的 UniXNU iPhone iOS 16.5 移植

[English](README.md) | [结构化移植记录](porting.toml) | [当前状态](docs/status.md)

本分支的目标是 GREE G0345D（G3、MSM8996）上的 iPhone iOS 16.5，build
20F66，Darwin 22.5.0，选用 XNU 8796.101.5 及其开源 revision
aca3beaa3dfbd42498b42c5e5ce20a938e6554e5 作为基线。iPhone10,3 只表示系统
donor 身份，不改变实际目标硬件；硬件仍是 G0345D/MSM8996。

当前没有构建或启动 iOS 16.5 内核。精确 restore manifest 和 XNU 8796.101.5
源码尚未准备，现有设备补丁属于另一代 XNU。M71/v213 的 bsd_init 和 md0
MockFS 结果属于旧的 iPadOS 17.7.11 / XNU 10063.141.1 实验，不能证明 iOS
16.5、物理 UFS、APFS 或 iOS 用户态。

UnixNu 从中央仓库的 profiles/os 目录解析系统 profile；本设备仓只保留
[profile 提案](docs/os-profile-proposal/ios-16.5-20F66/)，不能把提案当作
已经被中央仓库接纳的 profile。空 patch 列表也不会阻止 CLI 构建未打补丁的
内核，因此在 profile、源码、restore 输入和补丁重基完成前不要构建或启动。

公开 main 分支的 M42/v185 快照保持原样；本分支只表达 iOS 16.5 目标和发布
记录，不把不完整的 M71 未跟踪补丁冒充为可复现源码。

本仓不含 Apple/OEM 二进制、原始照片、设备种子、私钥或个人绝对路径。任何
硬件测试仍需单独授权，并只允许临时 fastboot boot。

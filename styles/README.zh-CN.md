# EVA 表情风格包

[English guide](README.md) · [下载风格包](https://github.com/498600589-byte/Zeekr-EVA-remix/releases/download/v2.1.0/EVA_Style_Kit_v2.1.0.zip)

解压后直接打开 `EVA_六款动效对比.html`，选择机甲配色和表情，就能同屏播放 JOJO 与机甲动效。六个示例是眨眼、左右看、开心、疑问、抱心和搜索。

| 风格 | 部署名称 |
| --- | --- |
| 蓝色巡逻 | `blue-patrol` |
| 橙色工程 | `amber-duty` |
| 绿色救援 | `green-rescue` |
| 红色能量 | `red-boost` |
| 紫色侦察 | `violet-scout` |
| JOJO 动态版 | `jojo` |

## 安装与切换

适用于资源版本为 `0.0.14` 的 EVA ICR10Z1A。需要 Windows 和 Python 3.11 或更新版本。[挂载 EVA 资源盘](../README.md#2-open-the-eva-resource-drive)后，在解压目录启动 PowerShell，把下面的 `H:\` 改为实际盘符。

```powershell
python tools/select_style.py list
python tools/select_style.py apply blue-patrol --drive 'H:\' --backup '.\eva-style-backup'
```

首次会备份当前的六项表情。以后换风格时改用表中对应的部署名称，继续使用同一个备份目录。写入成功后，安全弹出再拔插 USB。

```powershell
python tools/select_style.py restore --drive 'H:\' --backup '.\eva-style-backup'
```

恢复会把这六项还原到首次部署前的状态。如果原来装过完整 JOJO 动态版，先恢复风格包，再执行完整包的复原程序。

## 历史 JOJO

- [早期坏笑版的案例与样例](../examples/jojo/) · [画面对照图](../docs/jojo-case.png)
- [JOJO 第二版完整包](https://github.com/498600589-byte/Zeekr-EVA-remix/releases/tag/v2.0.0) · [安装与复原](../docs/jojo-motion-v2.zh-CN.md)
- [纳入风格包的六个 JOJO 动效](jojo/motion-v2/)

六种风格已在浏览器中预览，并在本地资源盘副本上验证安装、切换和恢复。仍待验证 EVA 实机屏幕上的播放效果。

机甲脸来自 [EVA 表情概念图](../docs/mecha-face-study.png)，眼灯和分片面甲参考了 [《炫卡斗士》官方角色图](https://www.samg.net/en/content/5)。

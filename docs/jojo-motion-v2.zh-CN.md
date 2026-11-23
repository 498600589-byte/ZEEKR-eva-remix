# EVA JOJO 动态表情包 v2

适用于资源版本 `0.0.14` 的极氪 EVA ICR10Z1A。支持从原厂资源或已校验的上一版 JOJO 坏笑包升级。新版更新 128 个动画，含 57 个 Lottie 和 71 个 DAT。保留原有画布、播放区间和帧数。导航、安全带、充电和驾驶警示沿用原有图标，动效主要集中在屏幕周边。

[下载完整 ZIP](https://github.com/498600589-byte/Zeekr-EVA-remix/releases/download/v2.0.0/EVA_JOJO_Motion_v2.0.0.zip) · [查看动态预览](jojo-motion-v2.gif) · [查看版本说明](https://github.com/498600589-byte/Zeekr-EVA-remix/releases/tag/v2.0.0)

## 安装

1. 在 Windows 上把 ZIP 解压到电脑的独立目录。打开 `动态对照.html` 可以播放、暂停和拖动进度，比较六个表情的新版和上一版。
2. 按指南挂载 [EVA 的 USB 资源盘](../README.md#2-open-the-eva-resource-drive)，记下实际盘符。下面以 `H:\` 为例。
3. 在解压目录打开 PowerShell，使用 Python 3.11 或更高版本执行以下命令。

```powershell
python '.\部署与复原.py' verify
python '.\部署与复原.py' apply H:\
```

安装程序会核对资源版本、表情映射和文件校验值。写入前，解压目录会生成 `部署前备份`。写入后，程序会读取文件复核。安装成功后，从 Windows 安全弹出资源盘，拔插 USB 让 EVA 重新加载。请保留解压目录和备份。

## 恢复

重新挂载 EVA 资源盘，在同一解压目录运行以下命令，将本次改动恢复到安装前的版本。

```powershell
python '.\部署与复原.py' restore H:\
```

如果安装时通过 `--backup` 指定了备份目录，恢复时请使用同一个目录。

## 验证范围

全包通过本地文件校验，DAT 的所有帧均已解码检查，Lottie 已在浏览器中抽帧。安装与恢复分别在原厂和上一版 JOJO 的资源副本上通过。v2 尚未写入实机，机器人屏幕上的播放效果待确认。

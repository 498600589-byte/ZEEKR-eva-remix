# 可爱机甲全动作 v2.4

[在线同屏预览](https://498600589-byte.github.io/Zeekr-EVA-remix/cute-mecha/) · [下载四角色实机包](https://github.com/498600589-byte/Zeekr-EVA-remix/releases/tag/v2.4.0)

四个角色各有 116 项网页演示。每个实机包替换 97 个表情，涵盖日常、迎宾、听说、音乐、节日、眼神和创意动作。角色包沿用 EVA 0.0.14 的原资源编号和时序。主副驾聆听、跳舞、乐器、唱歌等有独立的开始、持续和结束段。

实机的 19 项连接、导航、行车警示、模式、充电和来电状态沿用设备已有资源。在线目录为这些场景提供标明为「情境预览」的机甲演示。

## 安装与恢复

1. 选一个角色 ZIP，解压到电脑，进入含有 `family_pack.py` 的目录。需要 Windows 和 Python 3.9 或更新版本。
2. 如果装过此前的机甲小包，用旧包和它的备份先恢复，再安装全动作版。
3. 打开 EVA 资源盘。若盘符是 H，安装时运行 `python family_pack.py install H:\`。工具会先备份，然后写入资源和校验值。
4. 操作完成后安全弹出资源盘，重新拔插 USB。
5. 要恢复，用同一目录和备份运行 `python family_pack.py restore H:\`。

[EVA 资源盘操作指南](https://github.com/498600589-byte/Zeekr-EVA-remix/blob/main/docs/eva-setup.md#2-open-the-eva-resource-drive)

# EVA 亲子表情 v2.3

[炫蓝闪电](https://github.com/498600589-byte/Zeekr-EVA-remix/releases/download/v2.3.0/eva-mecha-blue-v2.3.0.zip) · [巨力风暴](https://github.com/498600589-byte/Zeekr-EVA-remix/releases/download/v2.3.0/eva-mecha-orange-v2.3.0.zip) · [急救卫士](https://github.com/498600589-byte/Zeekr-EVA-remix/releases/download/v2.3.0/eva-mecha-medic-v2.3.0.zip) · [烈火修罗](https://github.com/498600589-byte/Zeekr-EVA-remix/releases/download/v2.3.0/eva-mecha-fire-v2.3.0.zip) · [奶龙](https://github.com/498600589-byte/Zeekr-EVA-remix/releases/download/v2.3.0/eva-nailoong-v2.3.0.zip) · [小猫咪](https://github.com/498600589-byte/Zeekr-EVA-remix/releases/download/v2.3.0/eva-kitten-v2.3.0.zip)

四款可爱机甲各替换六个表情槽位，分别为眨眼、左右看、开心、疑问、抱心和搜索。奶龙包包含 75 项表情和两张专用界面。网页可查看全部 116 项奶龙场景。小猫咪包使用下列八个已有动作槽位，实机由对应事件触发。

| 小猫咪动作 | EVA 资源名 |
| --- | --- |
| 吃鱼 | EeatFruits |
| 玩球 | PlayGames |
| 洗脸 | RubHands |
| 蹭蹭 | ActingCute |
| 求摸摸 | C00000077 |
| 害羞 | Shy |
| 打盹 | GoodNoon |
| 贴贴 | C00000103 |

## 在 Windows 上安装与恢复

1. 下载一个 ZIP 并解压到电脑，打开里面有 family_pack.py 的目录。需要 Python 3.9 或更新版本。
2. 按 [USB 操作指南](eva-setup.md#2-open-the-eva-resource-drive) 打开 EVA 资源盘，核对盘符和资源版本 0.0.14。
3. 在解压目录打开终端。例如 EVA 为 H 盘时，运行以下命令安装。程序会先在电脑创建 backup 备份，再更新选中槽位和文件校验值。
4. 安装成功后安全弹出资源盘，重新插拔 USB。要换另一套主题，先用同一目录及备份恢复当前主题。

~~~powershell
python family_pack.py install H:\
python family_pack.py restore H:\
~~~

每次操作只运行对应的一行。请保留解压目录与备份。此版本已在资源盘副本完成安装、重复安装、恢复和回读验证。新增动作的实机播放仍待验证。

## English

Choose one of four cute mecha packs (six motions each), Nailoong (75 expressions plus startup and pairing), or the minimalist kitten (eight affectionate actions). Extract your chosen ZIP on the PC and run the matching install or restore command above with your EVA drive letter. The installer checks resource version 0.0.14 and the expression map. Keep the backup and restore the current style before switching packs.

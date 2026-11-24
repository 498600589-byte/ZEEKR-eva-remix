# EVA 角色机甲整套表情

[发布页与下载](https://github.com/498600589-byte/Zeekr-EVA-remix/releases/tag/v2.2.0) · [English guide](README.md)

| 角色 | 面部识别点 | 概念稿 |
| --- | --- | --- |
| 炫蓝闪电 | 蓝色分片眉甲、斜切眼灯、黄色颊灯 | [概念图](../../docs/cardbot-concepts/blue-cop.png) |
| 巨力风暴 | 加宽的护栏眉框、橙色顶甲、双格栅下颌 | [概念图](../../docs/cardbot-concepts/mega-trucker.png) |
| 急救卫士 | 白绿面甲、红色侧灯和单侧琥珀诊断镜 | [概念图](../../docs/cardbot-concepts/mega-ambler.png) |
| 烈火修罗 | 黑色 V 形护目框、红色外翼、三角银颌 | [概念图](../../docs/cardbot-concepts/phoenix-fire.png) |

每个角色独立成包。每包有 131 个素材，覆盖 116 个登记表情和 15 个补充素材。每个角色重绘 109 个动画资源。其余用于驾驶警示、部分车况提示和静态状态的素材沿用资源原样。发布页另有可离线播放的六款对比页，包含眨眼、左右看、开心、疑问、抱心和搜索。逐帧动作复用 EVA 已登记的屏幕尺寸、帧数和时长。

## 选择角色并安装

1. 下载选中的角色 ZIP。在电脑上解压，使用 Windows 和 Python 3.11 或更新版本。
2. [挂载 EVA USB 资源盘](../../README.md#2-open-the-eva-resource-drive)。下面以 `H:\` 为例。
3. 在解压目录打开 PowerShell，校验并安装。

```powershell
python '.\部署与复原.py' verify
python '.\部署与复原.py' apply 'H:\'
```

支持资源版本 `0.0.14` 的已核验原厂包、早期 JOJO 坏笑版和 JOJO 动态整套版。装过六表情选包时，先用当时的备份恢复。安装时会生成 `部署前备份`。切换另一个整套角色前，先用当前包恢复，然后再选择新包。

```powershell
python '.\部署与复原.py' restore 'H:\'
```

每次安装或恢复后，安全弹出资源盘再重新接入 EVA。已在本地资源盘副本上完成安装与恢复测试，实机播放待验证。

## 历史风格

- [JOJO 动态整套包](https://github.com/498600589-byte/Zeekr-EVA-remix/releases/tag/v2.0.0)
- [较早的六表情配色选包](https://github.com/498600589-byte/Zeekr-EVA-remix/releases/tag/v2.1.0)

角色脸为 EVA 同人改编参考。蓝、橙、绿三位的造型参考了 [SAMG 官方角色图](https://www.samg.net/en/content/5)，烈火修罗参考了 [同款机甲图片](https://www.toysruschina.com/zh-cn/phoenix-fire-flame-shura-10014580.html)。

# EVA Character Mecha packs

[Release and downloads](https://github.com/498600589-byte/Zeekr-EVA-remix/releases/tag/v2.2.0) · [中文说明](README.zh-CN.md)

| Character | Facial design | Concept study |
| --- | --- | --- |
| Blue Cop | Angled blue brow plates and yellow cheek lights | [Blue Cop sheet](../../docs/cardbot-concepts/blue-cop.png) |
| Mega Trucker | Broad roll-cage brow and twin jaw grilles | [Mega Trucker sheet](../../docs/cardbot-concepts/mega-trucker.png) |
| Mega Ambler | White and green armor and one amber diagnostic lens | [Mega Ambler sheet](../../docs/cardbot-concepts/mega-ambler.png) |
| Phoenix Fire | Black V visor, red fins, and triangular silver jaw | [Phoenix Fire sheet](../../docs/cardbot-concepts/phoenix-fire.png) |

Each ZIP contains 131 assets across 116 mapped expressions and 15 supplementary resources. Each character reworks 109 animation resources and carries over the remaining warnings, functional cues, and static status assets. The separate offline comparison plays six representative clips.

## Install a character

Use Windows, Python 3.11 or newer, and EVA resource version `0.0.14`. Extract the ZIP for your chosen character. [Open the EVA USB resource drive](../../README.md#2-open-the-eva-resource-drive) and use its assigned letter in place of `H:\`.

```powershell
python '.\部署与复原.py' verify
python '.\部署与复原.py' apply 'H:\'
```

Supported starting points are the verified stock, original JoJo, and full JoJo Motion v2 resource sets. If you used the six-expression style kit, restore its backed-up state first. A successful install creates a local backup. Restore that backup before applying a different full character.

```powershell
python '.\部署与复原.py' restore 'H:\'
```

Safely eject and reconnect EVA after installation or restore. Installation and restore were tested on local resource copies. Playback on the physical EVA remains to be verified.

[Full historical JoJo Motion v2 pack](https://github.com/498600589-byte/Zeekr-EVA-remix/releases/tag/v2.0.0) · [Earlier colorway sample kit](https://github.com/498600589-byte/Zeekr-EVA-remix/releases/tag/v2.1.0)

These fan designs reference [SAMG's Metal Cardbot character gallery](https://www.samg.net/en/content/5) and the [Phoenix Fire product imagery](https://www.toysruschina.com/zh-cn/phoenix-fire-flame-shura-10014580.html).

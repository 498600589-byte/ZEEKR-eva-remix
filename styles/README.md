# EVA Style Kit

[中文说明](README.zh-CN.md) · [Download the Style Kit](https://github.com/498600589-byte/Zeekr-EVA-remix/releases/download/v2.1.0/EVA_Style_Kit_v2.1.0.zip)

Open `EVA_六款动效对比.html` in the ZIP to play the mecha and JoJo faces side by side. Both sides use the same canvas, frame count, and playback speed for each expression. The six examples are Blink, Look, Happy, Curiosity, Comfort, and Search.

| Style | Command name |
| --- | --- |
| Blue Patrol | `blue-patrol` |
| Amber Duty | `amber-duty` |
| Green Rescue | `green-rescue` |
| Red Boost | `red-boost` |
| Violet Scout | `violet-scout` |
| JoJo Motion v2 | `jojo` |

## Install or switch a style

Use Windows, Python 3.11 or newer, and an EVA ICR10Z1A with resources version `0.0.14`. [Open the EVA USB resource drive](../README.md#2-open-the-eva-resource-drive), extract the kit to the computer, and replace `H:\` in the commands with the letter Windows assigned to EVA.

```powershell
python tools/select_style.py list
python tools/select_style.py apply blue-patrol --drive 'H:\' --backup '.\eva-style-backup'
```

The first apply saves six expressions to the backup directory. Keep the same backup directory across subsequent switches. Repeat the apply command with a different style name to switch. Safely eject and reconnect EVA after each successful write.

```powershell
python tools/select_style.py restore --drive 'H:\' --backup '.\eva-style-backup'
```

Restore returns the six expressions to the state they were in before the first apply. If the starting state was the full JoJo pack, restore the style kit first before using the full pack's undo tool.

## JoJo history

- [Original JoJo artwork and samples](../examples/jojo/) · [Original case study](../docs/jojo-case.png)
- [JoJo Motion v2 complete pack](https://github.com/498600589-byte/Zeekr-EVA-remix/releases/tag/v2.0.0) · [Motion v2 installation guide](../docs/jojo-motion-v2.zh-CN.md)
- [Six JoJo Motion v2 expressions in this style kit](jojo/motion-v2/)

The style kit passed browser playback and switch/restore tests on local EVA resource copies. Playback on the physical EVA remains to be verified.

The mecha faces were developed from an [EVA expression concept study](../docs/mecha-face-study.png), with reference to broad visor and armor shapes in [SAMG's Metal Cardbot character gallery](https://www.samg.net/en/content/5).

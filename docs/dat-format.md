# EVA Packed JPEG Resources

In the `0.0.14` resource set, mapped `type 1` assets live under `local/emoji/jpg_merge/`. Each `.dat` contains a frame index followed by individual JPEG files.

| Field | Representation |
| --- | --- |
| Data offset | One little-endian `uint32`. In the files we checked it equals `8 + 8 × frame_count`. |
| Frame count | One little-endian `uint32`. |
| Frame index | `frame_count` pairs of `uint32` values. Each pair contains the byte offset from the start of the file and the JPEG length. |
| Frame data | Complete JPEG images in playback order. |

For a style swap, decode the source frames, keep the source dimensions, and repack the replacements with the same index layout and frame count. Calculate CRC16-CCITT-FALSE over the complete resulting `.dat` using polynomial `0x1021` and initial value `0xFFFF`. Update the matching file entry in `local/emoji/EmojiList.json`.

The DAT header carries no frame rate field. We played the offline previews at 25 fps and kept each source DAT's frame count when building the case-study pack.

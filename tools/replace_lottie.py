"""Apply or revert one existing EVA Lottie expression using a full backup."""

import argparse
from binascii import crc_hqx
import json
import os
from pathlib import Path
import re
from tempfile import NamedTemporaryFile


RESOURCE_MAP = Path('local/EmojiMapList.json')
ASSET_DIRECTORY = Path('local/emoji')
FILE_LIST = ASSET_DIRECTORY / 'EmojiList.json'
PROFILE = ('w', 'h', 'fr', 'ip', 'op')


def crc(data):
    return crc_hqx(data, 0xFFFF)


def version(root):
    for line in (root / 'version.txt').read_text(encoding='utf-8-sig').splitlines():
        if line.startswith('VERSION='):
            return line.split('=', 1)[1].strip()
    raise ValueError(f'No resource version found at {root}')


def lookup(rows, key, value):
    matches = [row for row in rows if row.get(key) == value]
    if len(matches) != 1:
        raise ValueError(f'Expected one entry for {key}={value!r}')
    return matches[0]


def atomic_write(path, content):
    with NamedTemporaryFile(dir=path.parent, prefix='.eva-swap-', suffix='.tmp', delete=False) as handle:
        temporary = Path(handle.name)
        try:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        except BaseException:
            handle.close()
            temporary.unlink(missing_ok=True)
            raise
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def load_lottie(raw):
    animation = json.loads(raw)
    if not animation.get('v') or not animation.get('layers'):
        raise ValueError('The candidate must contain a valid Lottie document with layers.')
    if any(asset.get('p') and not asset['p'].startswith('data:') for asset in animation.get('assets', [])):
        raise ValueError('Embed external image assets before copying this Lottie to EVA.')
    return animation


def replace(drive, backup, expression_id, candidate=None):
    drive, backup = drive.resolve(), backup.resolve()
    if drive == backup or backup.is_relative_to(drive) or drive.is_relative_to(backup):
        raise ValueError('Use a separate local backup directory.')
    if version(drive) != version(backup):
        raise ValueError('The EVA drive and backup have different resource versions.')
    device_map = (drive / RESOURCE_MAP).read_bytes()
    if device_map != (backup / RESOURCE_MAP).read_bytes():
        raise ValueError('The backup was made from a different expression map.')
    mapped = lookup(json.loads(device_map)['data'], 'id', expression_id)
    if mapped['type'] != 0 or not re.fullmatch(r'[A-Za-z0-9_]+', mapped['name']):
        raise ValueError('Select an existing mapped Lottie expression (type 0).')
    filename = mapped['name'] + '.json'
    relative = ASSET_DIRECTORY / filename
    asset_path, manifest_path = drive / relative, drive / FILE_LIST
    lock = drive / ASSET_DIRECTORY / '.eva-swap.lock'

    with lock.open('x', encoding='utf-8'):
        pass
    try:
        original_asset = asset_path.read_bytes()
        original_manifest = manifest_path.read_bytes()
        manifest = json.loads(original_manifest)
        row = lookup(manifest['files'], 'file', filename)
        baseline = (backup / relative).read_bytes()
        baseline_list = json.loads((backup / FILE_LIST).read_bytes())
        baseline_row = lookup(baseline_list['files'], 'file', filename)
        if row['type'] != 0 or baseline_row['type'] != 0:
            raise ValueError('The file manifest does not match the mapped Lottie type.')
        if crc(original_asset) != row['crc'] or crc(baseline) != baseline_row['crc']:
            raise ValueError('The current asset or its backup failed the CRC check.')
        if candidate is not None and original_asset != baseline:
            raise ValueError('This expression already differs from the backup. Restore it before another swap.')
        replacement = candidate.read_bytes() if candidate is not None else baseline
        animation = load_lottie(replacement)
        original_profile = load_lottie(baseline)
        if any(animation.get(key) != original_profile.get(key) for key in PROFILE):
            raise ValueError(f'The candidate must use the original canvas and timing: { {key: original_profile[key] for key in PROFILE} }')
        row['crc'] = crc(replacement)
        revised = json.dumps(manifest, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        if asset_path.read_bytes() != original_asset or manifest_path.read_bytes() != original_manifest:
            raise ValueError('EVA resources changed during validation.')

        atomic_write(asset_path, replacement)
        try:
            atomic_write(manifest_path, revised)
            if asset_path.read_bytes() != replacement or manifest_path.read_bytes() != revised:
                raise OSError('The write did not match the intended resource bytes.')
        except BaseException:
            atomic_write(asset_path, original_asset)
            atomic_write(manifest_path, original_manifest)
            raise
        print(f'ID {expression_id}: {filename} verified, CRC16 0x{row["crc"]:04X}.')
    finally:
        lock.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('apply', 'restore'))
    parser.add_argument('--drive', type=Path, required=True)
    parser.add_argument('--backup', type=Path, required=True)
    parser.add_argument('--id', dest='expression_id', type=int, required=True)
    parser.add_argument('--input', type=Path)
    args = parser.parse_args()
    if (args.action == 'apply') != (args.input is not None):
        parser.error('Use --input with apply only.')
    try:
        replace(args.drive, args.backup, args.expression_id, args.input)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f'EVA swap stopped: {error}\n')


if __name__ == '__main__':
    main()

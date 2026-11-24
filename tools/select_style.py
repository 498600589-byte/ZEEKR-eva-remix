"""Apply or restore the six mapped expressions in the EVA style kit."""

import argparse
from ctypes import windll
from hashlib import sha256
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

from replace_lottie import (
    ASSET_DIRECTORY, FILE_LIST, PROFILE, RESOURCE_MAP, atomic_write, crc, load_lottie, lookup, version,
)

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'styles' / 'catalog.json'
SNAPSHOT = 'snapshot.json'


def digest(raw):
    return sha256(raw).hexdigest()


def capture(backup, paths, contents, mapping, manifest):
    backup.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix='eva-style-backup-', dir=backup.parent) as temporary:
        source = Path(temporary)
        for path in paths:
            atomic_write(source / path.name, contents[path])
        atomic_write(source / FILE_LIST.name, manifest)
        metadata = {
            'map': digest(mapping), 'manifest': digest(manifest),
            'assets': {path.name: digest(contents[path]) for path in paths},
        }
        atomic_write(source / SNAPSHOT, json.dumps(metadata, indent=2).encode('utf-8'))
        if backup.exists():
            raise FileExistsError(backup)
        source.rename(backup)


def read_backup(backup, paths, mapping):
    metadata = json.loads((backup / SNAPSHOT).read_bytes())
    if metadata['map'] != digest(mapping) or set(metadata['assets']) != {path.name for path in paths}:
        raise ValueError('Backup expression map or file list does not match this EVA.')
    original = {path: (backup / path.name).read_bytes() for path in paths}
    for path, data in original.items():
        if metadata['assets'][path.name] != digest(data):
            raise ValueError(f'Backup failed verification for {path.name}.')
    manifest = (backup / FILE_LIST.name).read_bytes()
    if metadata['manifest'] != digest(manifest):
        raise ValueError('The backup resource manifest failed verification.')
    return original, manifest


def apply(volume, backup, style=None, *, check_device=True):
    volume, backup = volume.resolve(), backup.resolve()
    if check_device and (volume != Path(volume.anchor) or windll.kernel32.GetDriveTypeW(str(volume)) != 2):
        raise ValueError('Select the root of the EVA removable drive.')
    if backup.is_relative_to(volume) or volume.is_relative_to(backup):
        raise ValueError('Place the backup in a separate directory on the computer.')
    catalog = json.loads(CATALOG.read_bytes())
    if version(volume) != catalog['resource_version']:
        raise ValueError('This kit requires EVA resource version 0.0.14.')
    mapping = (volume / RESOURCE_MAP).read_bytes()
    rows = json.loads(mapping)['data']
    names = []
    for expression_id, spec in catalog['expressions'].items():
        entry = lookup(rows, 'id', int(expression_id))
        if entry['type'] != 0 or entry['name'] != spec['name']:
            raise ValueError(f'Expression ID {expression_id} has an unexpected name or type.')
        names.append(spec['name'])
    paths = [ASSET_DIRECTORY / f'{name}.json' for name in names]
    known = {
        key: {path: (CATALOG.parent / spec['path'] / path.name).read_bytes() for path in paths}
        for key, spec in catalog['styles'].items()
    }
    lock = volume / ASSET_DIRECTORY / '.eva-swap.lock'
    with lock.open('x', encoding='utf-8'):
        pass
    try:
        current = {path: (volume / path).read_bytes() for path in paths}
        manifest_before = (volume / FILE_LIST).read_bytes()
        manifest = json.loads(manifest_before)
        if backup.exists():
            original, manifest_original = read_backup(backup, paths, mapping)
        else:
            if style is None:
                raise ValueError('The backup is required to restore the original expressions.')
            original = current
            manifest_original = manifest_before
        target = known[style] if style else original
        for path in paths:
            row = lookup(manifest['files'], 'file', path.name)
            permitted = [original[path], *(bundle[path] for bundle in known.values())]
            if row['type'] != 0 or current[path] not in permitted:
                raise ValueError(f'{path.name} is outside the backed-up or kit styles.')
            if row['crc'] != crc(current[path]) and (style or row['crc'] not in {crc(data) for data in permitted}):
                raise ValueError(f'{path.name} failed its resource checksum.')
            old, new = load_lottie(current[path]), load_lottie(target[path])
            if any(old[prop] != new[prop] for prop in PROFILE):
                raise ValueError(f'{path.name} has a different canvas or playback profile.')
            row['crc'] = crc(target[path])

        if not backup.exists():
            capture(backup, paths, current, mapping, manifest_before)
        if style is None and manifest == json.loads(manifest_original):
            updated = manifest_original
        else:
            updated = json.dumps(manifest, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        batch = {**target, FILE_LIST: updated}
        baseline = {**current, FILE_LIST: manifest_before}
        needed = sum(len(data) for data in batch.values()) * 2
        if shutil.disk_usage(volume).free < needed:
            raise ValueError('The EVA drive has insufficient space to replace these files.')
        applied = []
        try:
            for path, data in batch.items():
                if (volume / path).read_bytes() != baseline[path]:
                    raise OSError(f'An asset changed during deployment: {path.name}')
                if data != baseline[path]:
                    atomic_write(volume / path, data)
                    applied.append(path)
            if (volume / RESOURCE_MAP).read_bytes() != mapping:
                raise OSError('The expression mapping changed during deployment.')
            for path, data in batch.items():
                if (volume / path).read_bytes() != data:
                    raise OSError(f'Write verification failed for {path.name}.')
        except BaseException:
            for path in reversed(applied):
                atomic_write(volume / path, baseline[path])
            raise
    finally:
        lock.unlink()
    print(f'{"Restored" if style is None else f"Applied {style}"}: {len(paths)} expressions verified.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    styles = json.loads(CATALOG.read_bytes())['styles']
    actions = parser.add_subparsers(dest='action', required=True)
    actions.add_parser('list')
    install = actions.add_parser('apply')
    install.add_argument('style', choices=styles)
    restore = actions.add_parser('restore')
    for action in (install, restore):
        action.add_argument('--drive', type=Path, required=True)
        action.add_argument('--backup', type=Path, required=True)
    args = parser.parse_args()
    if args.action == 'list':
        for key, style in styles.items():
            print(f"{key}\t{style['label']}")
        return
    try:
        apply(args.drive, args.backup, getattr(args, 'style', None))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f'Style operation stopped: {error}\n')


if __name__ == '__main__':
    main()

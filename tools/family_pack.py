"""Install or restore one EVA family expression pack (Windows, Python 3.9+)."""
import argparse
from binascii import crc_hqx
from contextlib import contextmanager
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

HERE = Path(__file__).resolve().parent
BASE = Path("local/emoji")
LIST = Path("EmojiList.json")
MAP = Path("local/EmojiMapList.json")
SAFE = re.compile(r"(?:[A-Za-z0-9_]+\.json|jpg_merge/([A-Za-z0-9_]+)/\1_merged\.dat)")

def digest(data):
    return sha256(data).hexdigest() if data is not None else None

def read(path):
    return path.read_bytes() if path.is_file() else None

def encode(value):
    return json.dumps(value,ensure_ascii=False,separators=(",",":")).encode("utf-8")

def replace(data,path):
    if data is None:
        path.unlink(missing_ok=True)
        return
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,temp=tempfile.mkstemp(prefix=".eva-",dir=path.parent)
    try:
        with os.fdopen(fd,"wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp,path)
    finally:
        Path(temp).unlink(missing_ok=True)

@contextmanager
def lock(base):
    guard=base/".eva-swap.lock"
    with guard.open("x"):
        pass
    try:
        yield
    finally:
        guard.unlink(missing_ok=True)

def deploy(package,volume,backup,restore=False):
    package,volume,backup=(Path(p).resolve() for p in (package,volume,backup))
    if backup.is_relative_to(volume) or volume.is_relative_to(backup):
        raise ValueError("Choose a separate PC folder for the backup.")
    spec=json.loads((package/"pack.json").read_bytes())
    mapping=(volume/MAP).read_bytes()
    if digest(mapping)!=spec["map_sha256"] or "VERSION=0.0.14" not in (volume/"version.txt").read_text(encoding="utf-8-sig").splitlines():
        raise ValueError("EVA version or expression map differs.")
    rows=json.loads(mapping)["data"]
    allowed={row["name"].lower()+(".json" if row["type"]==0 else "_merged.dat") for row in rows}
    base=volume/BASE
    with lock(base):
        original={LIST:(base/LIST).read_bytes()}
        registry=json.loads(original[LIST])
        index={row["file"].lower():row for row in registry["files"]}
        files={}
        for key,expected in spec["files"].items():
            p=Path(key)
            if not SAFE.fullmatch(key) or p.name.lower() not in allowed or p==LIST:
                raise ValueError(f"Invalid pack entry {key}")
            data=(package/BASE/p).read_bytes()
            if digest(data)!=expected:
                raise ValueError(f"Pack checksum mismatch: {key}")
            files[p]=data
            original[p]=read(base/p)
            row=index.get(p.name.lower())
            if (row is None)!=(original[p] is None) or (row and row["crc"]!=crc_hqx(original[p],0xffff)):
                raise ValueError(f"Current resource CRC failed: {p}")
        identity=digest((package/"pack.json").read_bytes())
        if not backup.exists():
            if restore:
                raise ValueError("Select the backup created for this pack.")
            backup.parent.mkdir(parents=True,exist_ok=True)
            with tempfile.TemporaryDirectory(dir=backup.parent) as temp:
                stage=Path(temp)/"snapshot"
                stage.mkdir()
                hashes={}
                for p,data in original.items():
                    hashes[p.as_posix()]=digest(data)
                    if data is not None:
                        replace(data,stage/p)
                (stage/"snapshot.json").write_bytes(encode({"pack":identity,"hashes":hashes}))
                os.rename(stage,backup)
        snap=json.loads((backup/"snapshot.json").read_bytes())
        if snap["pack"]!=identity:
            raise ValueError("Select the matching backup folder.")
        saved={p:read(backup/p) for p in original}
        if any(digest(data)!=snap["hashes"][p.as_posix()] for p,data in saved.items()):
            raise ValueError("Backup checksum failed.")
        prior={r["file"].lower():r for r in json.loads(saved[LIST])["files"]}
        desired={}
        for p,data in files.items():
            if original[p] not in (data,saved[p]):
                raise ValueError(f"Another pack changed {p.name}. Restore it first.")
            desired[p]=saved[p] if restore else data
            name=p.name.lower()
            if restore:
                if name in prior:
                    index[name]=prior[name]
                else:
                    index.pop(name,None)
            else:
                index[name]={**index.get(name,{"file":p.name,"type":int(p.suffix==".dat")}),
                             "crc":crc_hqx(data,0xffff)}
        registry["files"]=list(index.values())
        desired[LIST]=saved[LIST] if registry==json.loads(saved[LIST]) else encode(registry)
        if shutil.disk_usage(base).free<sum(len(v or b"") for v in desired.values())+1024*1024:
            raise ValueError("Insufficient free space for the update.")
        changed=[]
        try:
            for p,data in desired.items():
                if original[p]==data:
                    continue
                if read(base/p)!=original[p]:
                    raise ValueError(f"Resource changed during install: {p}")
                replace(data,base/p)
                changed.append(p)
                if read(base/p)!=data:
                    raise IOError(f"Readback failed: {p}")
        except BaseException:
            for p in reversed(changed):
                replace(original[p],base/p)
            raise
    print(f"Verified {len(files)} resources. Backup: {backup}")

if __name__=="__main__":
    from ctypes import windll
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=["install","restore"])
    parser.add_argument("volume",type=Path)
    parser.add_argument("--backup",type=Path,default=HERE/"backup")
    args=parser.parse_args()
    root=args.volume.resolve()
    if root!=Path(root.anchor) or windll.kernel32.GetDriveTypeW(str(root))!=2:
        parser.error("Select the EVA removable drive root, e.g. H:\\")
    deploy(HERE,root,args.backup,args.action=="restore")

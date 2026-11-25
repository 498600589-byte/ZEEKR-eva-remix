"""Render the expanded cute Cardbot gallery and EVA 0.0.14 resource packs."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from hashlib import sha256
from io import BytesIO
import json
from math import cos, sin, tau
from pathlib import Path
from struct import Struct
import shutil
import subprocess
import zipfile

import cv2
from PIL import Image, ImageDraw, ImageFont

from build_native import MAX_BYTES, encoded_frames, importance_order, sequence
from face_motion import ROLES, frame, prepare, _hold

REPO = Path(__file__).resolve().parents[2]
CATALOG = REPO / "docs/nailoong/library-data.js"
MEDIA = REPO / "docs/nailoong/cute-mecha/motions"
SHEET = Path(__file__).with_name("characters.png")
SYMBOL_FONT = Path("C:/Windows/Fonts/seguisym.ttf")
EMOJIFONT = Path("C:/Windows/Fonts/seguiemj.ttf")
BASE = Path("local/emoji")
PAIR = Struct("<II")
PREVIEW_FPS = 30
# Preserve the factory visuals for essential driving, charging and binding states.
PROTECTED = {1,3,27,33,34,35,36,37,38,40,41,55,56,57,67,68,69,74,75}
SIX = {4:"blink",22:"look",50:"happy",102:"question",104:"heart",108:"search"}
COLOR = dict(zip(ROLES,("#74e8ff","#ffc46e","#90fad3","#ffa77a")))
CUES = {
    "off":"⚭","scan":"◉","wave":"👋","hand":"👋","hands":"🤲","note":"♫","sax":"🎷",
    "game":"🎮","zzz":"Zz","power":"⏻","wind":"≋","route":"➜","window":"▣","seat":"🪑",
    "vent":"✣","drop":"💧","battery":"▰","charged":"✓","belt":"╱","speed":"◴","alert":"!",
    "kite":"🪁","apple":"🍎","book":"📖","sunrise":"🌅","sun":"☀","moon":"☾","hearts":"♥",
    "scent":"✿","heat":"♨","bolt":"ϟ","leaf":"🍃","cloud":"☁","headphones":"🎧","drum":"🥁",
    "microphone":"🎤","shield":"◈","phone":"☎","cake":"🎂","tools":"🔧","redpacket":"🧧",
    "cruise":"ACC","wood":"♫","orb":"●","spark":"✦","rainbow":"🌈","point":"☛","pointSpark":"☛",
    "question":"?","starOrbit":"✦","heart":"♥","search":"⌕","smirk":"✧","lens":"◉","horn":"📣"
}


def timing(row,t):
    if row["phase"]=="enter":
        return _hold(t,0,.86,1,1.1),1
    if row["phase"]=="exit":
        return 1-_hold(t,0,.92,1,1.1),1
    if row["phase"]=="loop":
        return 1,2
    return _hold(t,.03,.24,.72,.98),1


def pose_for(row,t):
    action=row["pose"]
    power,beats=timing(row,t)
    beat=sin(t*tau*beats)
    brief=_hold(t,.68,.735,.76,.86) if row["phase"]=="full" else max(0,cos(t*tau*beats-.65))**30*.5
    gaze=up=lift=asym=tilt=mouth=nod=wink=0
    blink=brief*.84
    laughter=False
    right=action.endswith("Right")
    if action in {"listen","listenRight","talk","talkRight","greet","greetRight"}:
        gaze=(20 if right else -20)*power
        up=-5*power
        mouth=(.2+.60*abs(beat))*power if action.startswith(("talk","greet")) else -.27*power
        lift=power*(5+max(0,beat)*7)
        nod=-power*(3+4*beat)
        tilt=(2.8 if right else -2.8)*power
    elif action in {"dance","laugh"}:
        laughter=True
        bounce=power*(.68+.32*cos(t*tau*beats*2))
        blink=bounce*.98
        tilt=beat*power*(7 if action=="dance" else 3)
        mouth=.95*bounce
        lift=11*bounce
        nod=-20*bounce
    elif action in {"sleep","wake","yawn"}:
        if action=="sleep":
            blink=power*.98
            mouth=-.68*power
            nod=power*(10+4*beat)
        elif action=="wake":
            wake=_hold(t,.12,.32,.42,.76)
            blink=.97*_hold(t,-.1,-.05,.18,.33)+brief*.63
            mouth=.85*wake
            lift=20*wake
            nod=-19*wake
        else:
            blink=max(blink,.91*power)
            mouth=1.33*power
            nod=-8*power
            lift=9*power
    elif action in {"up","down","glance","scan","focused"}:
        up=(-24 if action=="up" else 21 if action=="down" else 0)*power
        gaze=power*(34*beat if action in {"glance","scan"} else 7*beat)
        lift=(10 if action=="up" else -9 if action=="down" else -5)*power
        asym=gaze*.22
        tilt=gaze*.12
        nod=power*(6 if action=="down" else -5)
    elif action in {"chew","pucker","blow"}:
        mouth=power*(.81*abs(sin(t*tau*beats*3)) if action=="chew" else -.82+.33*beat)
        blink=max(blink,.29*power*(1+beat))
        nod=mouth*6
    elif action in {"shock","worry","bored","shy","cute","wink"}:
        lift=power*{"shock":20,"worry":9,"bored":-13,"shy":-7,"cute":12,"wink":7}[action]
        if action=="shock":
            mouth=1.17*power
            nod=-10*power
        else:
            blink=max(blink,power*{"worry":.45,"bored":.62,"shy":.57,"cute":.34,"wink":0}[action])
            tilt=power*{"worry":-4,"bored":2,"shy":7,"cute":-7,"wink":-3}[action]
            up=-(lift/3) if action=="cute" else 8*power
            gaze=(-15 if action in {"shy","bored"} else 6)*power
            asym=13*power*(1 if action in {"cute","wink"} else -1)
            mouth=power*(.45 if action in {"cute","wink"} else -.58)
            if action=="wink":
                wink=.97*power
    else:
        blink=max(blink,.97*_hold(t,.26,.36,.40,.54))
    return gaze,up,lift,asym,tilt,mouth,min(1,blink),nod,wink,laughter


@lru_cache(maxsize=16)
def font(size,emoji=False):
    return ImageFont.truetype(str(EMOJIFONT if emoji else SYMBOL_FONT),size)


def cue(image,row,role,t):
    symbol=row["symbol"]
    if not symbol:
        return image
    power,beats=timing(row,t)
    if row["phase"]=="full":
        power=.38+.62*power
    image=image.resize((385,330),Image.Resampling.LANCZOS)
    canvas=Image.new("RGB",(448,384))
    canvas.paste(image,(31,-9))
    if power<.007:
        return canvas
    draw=ImageDraw.Draw(canvas)
    accent=COLOR[role]
    y=314-7*sin(t*tau*beats)*power
    draw.rounded_rectangle((121,267,327,361),radius=27,fill="#101723",outline="#233344",width=2)
    draw.rounded_rectangle((139,304,146,324),radius=3,fill=accent)
    draw.rounded_rectangle((302,304,309,324),radius=3,fill=accent)
    if symbol=="voice":
        for n in range(7):
            height=10+30*(.5+.5*sin(t*tau*beats*2+n))*power
            x=180+n*13
            draw.rounded_rectangle((x,314-height/2,x+7,314+height/2),radius=3,fill=accent)
    elif symbol in {"goldBeads","orangeBeads"}:
        fill="#ffda75" if symbol=="goldBeads" else "#ffa365"
        for n in range(6):
            angle=t*tau*beats+n*tau/6
            x=224+46*cos(angle)
            by=314+16*sin(angle)
            draw.ellipse((x-8,by-8,x+8,by+8),fill=fill)
    elif symbol in {"search","lens"}:
        x=220+10*sin(t*tau*beats)
        draw.ellipse((x-22,y-22,x+22,y+22),width=6,outline=accent,fill="#1e3541")
        draw.line((x+16,y+16,x+35,y+35),width=8,fill="#ffd783")
    else:
        glyph=CUES[symbol]
        emoji=any(ord(ch)>0xffff for ch in glyph)
        size=64 if emoji else 60 if len(glyph)==1 else 41
        draw.text((224,y),glyph,font=font(size,emoji),anchor="mm",
                  fill="#ff86a7" if symbol in {"hearts","heart"} else accent,
                  embedded_color=emoji)
    return canvas


def render(model,row,t):
    if row["id"] in SIX:
        return frame(model,SIX[row["id"]],t)
    image=frame(model,row["pose"],t,scene=lambda _, u:pose_for(row,u))
    return cue(image,row,model.role,t)


def path_for(row,type_):
    name=row["name"]
    return Path(name+".json") if type_==0 else Path("jpg_merge")/name/(name+"_merged.dat")


def stock_meta(path):
    raw=path.read_bytes()
    if path.suffix==".json":
        doc=json.loads(raw)
        profile={k:doc[k] for k in ("v","w","h","fr","ip","op","ddd")}
        return profile, max(1,doc["op"]-doc["ip"]), doc["fr"]
    offset,count=PAIR.unpack_from(raw)
    start,size=PAIR.unpack_from(raw,8)
    assert offset==start==8*(count+1)
    with Image.open(BytesIO(raw[start:start+size])) as im:
        return im.size,count,25


def encode_dat(images,size):
    offset=8*(len(images)+1)
    index=bytearray(PAIR.pack(offset,len(images)))
    frames=[]
    for image in images:
        image=image.transpose(Image.Transpose.ROTATE_270).resize(size,Image.Resampling.BILINEAR)
        for quality in (84,77,68,58,48):
            buf=BytesIO()
            image.save(buf,"JPEG",quality=quality,optimize=True)
            data=buf.getvalue()
            if len(data)<=27138:
                break
        else:
            raise ValueError("Oversize JPEG")
        index.extend(PAIR.pack(offset,len(data)))
        offset+=len(data)
        frames.append(data)
    return bytes(index)+b"".join(frames)


def encode_lottie(doc,images):
    # Render a palette-indexed image sequence with the original playback interval.
    thumbs=[im.resize((48,41),Image.Resampling.BILINEAR) for im in images]
    order=importance_order(thumbs)
    dims=(152,130)
    snaps=encoded_frames(images,dims,64)
    count=len(images)
    lo,hi=min(2,count),len(order)
    while lo<hi:
        mid=(lo+hi+1)//2
        if len(sequence(doc,snaps,sorted(order[:mid]),dims))<=MAX_BYTES:
            lo=mid
        else:
            hi=mid-1
    data=sequence(doc,snaps,sorted(order[:lo]),dims)
    assert len(data)<=MAX_BYTES
    return data


def encode_preview(model,row,path,seconds):
    count=max(32,round(seconds*PREVIEW_FPS))
    with subprocess.Popen(["ffmpeg","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24",
      "-s","320x274","-framerate",str(PREVIEW_FPS),"-i","pipe:0","-c:v","libx264","-threads","1",
      "-preset","ultrafast","-crf","24","-pix_fmt","yuv420p","-movflags","+faststart",str(path)],
      stdin=subprocess.PIPE) as command:
        for i in range(count):
            still=render(model,row,i/count).resize((320,274),Image.Resampling.BILINEAR)
            command.stdin.write(still.tobytes())
        command.stdin.close()
        if command.wait():
            raise RuntimeError(f"Could not write {path}")


def build_role(args):
    role,rows,roots,output,preview = args
    cv2.setNumThreads(1)
    model=prepare(SHEET,role)
    out=output/role
    out.mkdir(parents=True,exist_ok=True)
    assets={}
    for row in rows:
        path=path_for(row,row["type"])
        stock=next((root/BASE/path for root in roots if (root/BASE/path).is_file()),None)
        if stock is None:
            raise ValueError(f"Missing baseline resource: {path}")
        profile,count,fps=stock_meta(stock)
        if not row["oem"]:
            images=[render(model,row,i/count) for i in range(count)]
            asset=encode_lottie(profile,images) if row["type"]==0 else encode_dat(images,profile)
            new=out/BASE/path
            new.parent.mkdir(parents=True,exist_ok=True)
            new.write_bytes(asset)
            assets[path.as_posix()]=sha256(asset).hexdigest()
        if preview:
            encode_preview(model,row,MEDIA/f"{role}-{row['id']}.mp4",min(5.6,max(2.8,count/fps)))
        if row["id"]%20==0:
            print(role,row["id"],flush=True)
    info={"style":f"mecha-{role}-full","map_sha256":sha256((roots[0]/"local/EmojiMapList.json").read_bytes()).hexdigest(),"files":assets}
    (out/"pack.json").write_text(json.dumps(info,indent=2),encoding="utf-8")
    shutil.copy(REPO/"tools/family_pack.py",out/"family_pack.py")
    shutil.copy(REPO/"docs/cardbot-full.md",out/"使用说明.md")
    archive=output/f"eva-cute-{role}-v2.4.0.zip"
    with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=4) as z:
        for file in sorted(out.rglob("*")):
            if file.is_file():
                z.write(file,file.relative_to(out.parent))
    return role,len(assets),archive.stat().st_size


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for option in ("stock","fallback","output"):
        ap.add_argument("--"+option,type=Path,required=True)
    ap.add_argument("--jobs",type=int,default=4)
    ap.add_argument("--no-preview",action="store_true")
    a=ap.parse_args()
    a.output.mkdir(parents=True,exist_ok=True)
    for name in ROLES:
        if (a.output/name).exists():
            raise ValueError("Use a fresh output directory to avoid mixing different pack versions.")
    catalog=json.loads(CATALOG.read_text("utf-8").split("=",1)[1].strip().rstrip(";"))
    mapping=json.loads((a.stock/"local/EmojiMapList.json").read_bytes())["data"]
    for row,original in zip(catalog["entries"],mapping,strict=True):
        assert (row["id"],row["name"])==(original["id"],original["name"])
        row["type"]=original["type"]
        row["oem"]=row["id"] in PROTECTED
    entries=[{k:row[k] for k in ("id","label","category","phase","oem")} for row in catalog["entries"]]
    if not a.no_preview:
        MEDIA.mkdir(parents=True,exist_ok=True)
        (MEDIA.parent/"catalog.js").write_text("window.mechaCatalog = "+json.dumps(
            {"categories":catalog["categories"],"entries":entries},ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    tasks=[(role,catalog["entries"],(a.stock,a.fallback),a.output,not a.no_preview) for role in ROLES]
    with ProcessPoolExecutor(max_workers=a.jobs) as pool:
        for result in pool.map(build_role,tasks):
            print("FINISHED",*result,flush=True)

if __name__=="__main__":
    main()

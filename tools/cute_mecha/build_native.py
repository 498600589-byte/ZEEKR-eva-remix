"""Build and desk-test six EVA Lottie assets for each approved face."""
import argparse
import base64
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO
import json
import math
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps, ImageStat, ImageChops
from playwright.sync_api import sync_playwright

from face_motion import prepare, frame

HERE = Path(__file__).resolve().parent.parent
SHEET = Path(__file__).with_name("characters.png")
OUTPUT = Path("output/cute-mecha")
REFERENCE = Path("stock")
ROLES = ("blue", "orange", "medic", "fire")
ACTIONS = {
    "blink": (4, "Blink"), "look": (22, "Look"), "happy": (50, "Happy"),
    "question": (102, "L00000102"), "heart": (104, "L00000104"),
    "search": (108, "L00000108"),
}
# Observed upper range of embedded-image Lotties on the reference unit.
MAX_BYTES = 245000


def reference_docs(root):
    mapping = json.loads((root/"local/EmojiMapList.json").read_bytes())["data"]
    names = {row["id"]:row["name"] for row in mapping if row["type"] == 0}
    result = {}
    for action, (number, name) in ACTIONS.items():
        if names[number] != name:
            raise ValueError(f"Resource map mismatch for {name}")
        raw = json.loads((root/"local/emoji"/(name + ".json")).read_bytes())
        result[action] = {key:raw[key] for key in ("v","w","h","fr","ip","op","ddd")}
    return result


def transform(position, anchor, scale, rotation=0):
    return {key:{"a":0, "k":value} for key, value in (
        ("p",position),("a",anchor),("s",scale),("r",rotation),("o",100)
    )}


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def sequence(doc, snapshots, indices, dimensions):
    width, height = dimensions
    duration = doc["op"] - doc["ip"]
    images, layers, known = [], [], {}
    for i, start in enumerate(indices):
        end = indices[i+1] if i+1 < len(indices) else duration
        blob = snapshots[start]
        if blob not in known:
            ref = f"imgSeq_{len(images)}"
            known[blob] = ref
            images.append({
                "id":ref,"t":"seq","w":width,"h":height,"u":"","e":1,
                "p":"data:image/png;base64," + base64.b64encode(blob).decode("ascii"),
            })
        ref = known[blob]
        if layers and layers[-1]["refId"] == ref:
            layers[-1]["op"] = end
        else:
            layers.append({"ty":2, "ddd":0, "ind":i+1, "refId":ref, "ip":start,
                           "op":end, "st":0, "sr":1, "bm":0,
                           "ks":transform([0,0], [0,0], [100,100])})
    # The display is mounted sideways. Apply the stock native rotation only once.
    scale = min(doc["h"]/width, doc["w"]/height)*100
    comp_layer = {
        "ddd":0, "ind":1, "ty":0, "refId":"seq", "w":width, "h":height,
        "ip":doc["ip"], "op":doc["op"], "st":doc["ip"], "sr":1, "bm":0,
        "ks":transform([doc["w"]/2,doc["h"]/2,0],
                       [width/2,height/2,0], [scale,scale,100], 90),
    }
    return compact({**doc, "assets":images+[{"id":"seq","layers":layers}],
                    "layers":[comp_layer], "markers":[]})


def importance_order(thumbnails):
    # Choose hold boundaries where a new image removes the most visible error.
    # The loop's last frame is always sampled to avoid a frozen final gesture.
    count = len(thumbnails)
    values = np.array(thumbnails, dtype=np.float32)
    flat = values.reshape(count,-1)
    dot = flat @ flat.T
    diag = np.diag(dot)
    error = np.maximum(diag[:,None] + diag[None,:] - 2*dot, 0)
    indexes = [0,count-1]
    order = indexes.copy()
    while len(order) < count:
        best_benefit, best_frame = -math.inf, None
        for start,end in zip(indexes,indexes[1:]):
            for candidate in range(start+1,end):
                benefit = float(error[start,candidate:end].sum() -
                                error[candidate,candidate:end].sum())
                if benefit > best_benefit:
                    best_benefit, best_frame = benefit,candidate
        if best_frame is None:
            break
        order.append(best_frame)
        indexes.append(best_frame)
        indexes.sort()
    return order


def encoded_frames(images, dimensions, colors):
    width, height = dimensions
    palette_strip = Image.new("RGB",(width,height*8))
    for tile in range(8):
        sample = images[round(tile*(len(images)-1)/7)]
        palette_strip.paste(sample.resize(dimensions,Image.Resampling.LANCZOS),(0,tile*height))
    palette = palette_strip.quantize(colors=colors,method=Image.Quantize.MEDIANCUT)
    result = []
    for image in images:
        small = image.resize(dimensions,Image.Resampling.LANCZOS)
        indexed = small.quantize(palette=palette,dither=Image.Dither.NONE)
        # Pillow pads palettes to 256 entries by default. Compact the table.
        indexed.putpalette(palette.getpalette()[:colors*3])
        target = BytesIO()
        indexed.save(target,format="PNG",optimize=False,compress_level=7)
        result.append(target.getvalue())
    return result


def native_asset(model, action, doc):
    count = doc["op"] - doc["ip"]
    source = [frame(model,action,i/count).convert("RGB") for i in range(count)]
    if source[0].size != (448,384):
        raise ValueError("Unexpected renderer canvas")
    thumbs = [im.resize((64,55),Image.Resampling.BILINEAR) for im in source]
    order = importance_order(thumbs)
    for width, colors in [(176,80),(160,64),(144,56),(128,48)]:
        dims = width, round(width*384/448)
        snaps = encoded_frames(source,dims,colors)
        chosen = []
        for index in order:
            candidate = sorted(chosen + [index])
            if len(sequence(doc,snaps,candidate,dims)) <= MAX_BYTES:
                chosen = candidate
        data = sequence(doc,snaps,chosen,dims)
        # Keep the library's real movement timings, preferring at least a third
        # of all possible samples. Entirely identical rendered frames coalesce.
        if len(chosen) >= math.ceil(count/3):
            return data
    raise ValueError(f"No checked size profile fits {action}")


def build_role(args):
    role, sheet, root, destination = args
    model = prepare(sheet,role)
    dest = destination / role / "local/emoji"
    dest.mkdir(parents=True,exist_ok=True)
    for action,doc in reference_docs(root).items():
        output = native_asset(model,action,doc)
        name = ACTIONS[action][1]+".json"
        temp = dest / (name + ".part")
        temp.write_bytes(output)
        os.replace(temp,dest/name)
        print(f"{role}/{name} {len(output)} bytes",flush=True)


BROWSER_RENDER = """doc => new Promise((resolve,reject) => {
    const box=document.createElement('div');
    box.style.width=doc.w+'px';
    box.style.height=doc.h+'px';
    document.body.append(box);
    const timer=setTimeout(()=>reject(Error('Lottie decode timeout')),8000);
    const anim=lottie.loadAnimation({
        container:box,renderer:'canvas',autoplay:false,loop:false,animationData:doc,
        rendererSettings:{dpr:1,clearCanvas:true}
    });
    anim.addEventListener('DOMLoaded',()=>{
        try {
            const canvas=box.querySelector('canvas');
            const indices=[0,.12,.27,.42,.56,.72,.87,.99].map(p=>Math.floor(p*(doc.op-doc.ip)));
            const data=indices.map(i=>{
                anim.goToAndStop(i,true);
                return [i,canvas.toDataURL('image/png').split(',')[1]];
            });
            resolve(data);
        } catch (error) { reject(error); }
        finally { clearTimeout(timer); anim.destroy(); box.remove(); }
    });
})"""


def check_all(args):
    docs = reference_docs(args.stock)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=str(args.chrome),args=["--disable-gpu"])
        page = browser.new_page()
        page.goto("about:blank")
        page.add_script_tag(path=str(args.library))
        for role in ROLES:
            for action,header in docs.items():
                name = ACTIONS[action][1]+".json"
                target = args.output/role/"local/emoji"/name
                raw = target.read_bytes()
                doc = json.loads(raw)
                assert len(raw)<=MAX_BYTES
                assert all(doc[k]==v for k,v in header.items())
                image_assets = {}
                for asset in doc["assets"][:-1]:
                    png = base64.b64decode(asset["p"].split(",",1)[1],validate=True)
                    im = Image.open(BytesIO(png)).convert("RGB")
                    assert im.size==(asset["w"],asset["h"])
                    image_assets[asset["id"]]=im
                layers = doc["assets"][-1]["layers"]
                assert len(image_assets)>=5
                assert layers[0]["ip"]==0 and layers[-1]["op"]==doc["op"]-doc["ip"]
                assert all(a["op"]==b["ip"] for a,b in zip(layers,layers[1:]))
                for index,png in page.evaluate(BROWSER_RENDER,doc):
                    canvas=Image.open(BytesIO(base64.b64decode(png))).convert("RGB")
                    upright=canvas.transpose(Image.Transpose.ROTATE_90)
                    layer=next(row for row in layers if row["ip"]<=index<row["op"])
                    src=image_assets[layer["refId"]]
                    expected=ImageOps.pad(src,upright.size,method=Image.Resampling.BILINEAR,color="black")
                    delta=ImageStat.Stat(ImageChops.difference(expected,upright)).mean
                    assert max(delta)<5, (role,action,index,delta)
                print(f"Verified {role}/{name}: {len(image_assets)} images, {len(layers)} timed holds",flush=True)
        browser.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sheet",type=Path,default=SHEET)
    parser.add_argument("--stock",type=Path,default=REFERENCE)
    parser.add_argument("--output",type=Path,default=OUTPUT)
    parser.add_argument("--library",type=Path,default=Path(os.environ["TEMP"])/"eva-lottie-web-5.13.0/lottie.min.js")
    parser.add_argument("--chrome",type=Path,default=Path("C:/Program Files/Google/Chrome/Application/chrome.exe"))
    parser.add_argument("--verify-only",action="store_true")
    parser.add_argument("--jobs",type=int,default=2)
    args=parser.parse_args()
    if not args.verify_only:
        with ProcessPoolExecutor(max_workers=args.jobs) as pool:
            list(pool.map(build_role,[(role,args.sheet,args.stock,args.output) for role in ROLES]))
    check_all(args)


if __name__=="__main__":
    main()

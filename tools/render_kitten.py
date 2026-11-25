"""Render the kitten motion artwork to stock-sized EVA JPEG sequences and web previews."""
import argparse
import base64
from io import BytesIO
from pathlib import Path
from struct import Struct
import subprocess
from PIL import Image
from playwright.sync_api import sync_playwright

PAIR=Struct("<II")
SITE=Path(__file__).resolve().parents[1]/"docs/nailoong/kitten"
PREVIEW_FPS = 60
REFERENCE_PREVIEW_FPS = 25

def sample_frames(page, move, count, width, height):
    """Sample the continuous artwork directly at the requested frame count."""
    for start in range(0,count,48):
        end=min(start+48,count)
        result=page.evaluate("""([action,count,w,h,start,end])=>{
          const upright=document.createElement('canvas'),raw=document.createElement('canvas');
          upright.width=448; upright.height=384; raw.width=w;raw.height=h;
          const ctx=upright.getContext('2d'),out=raw.getContext('2d');out.translate(w,0);out.rotate(Math.PI/2);
          return Array.from({length:end-start},(_,i)=>{renderCat(ctx,action,(i+start)/count);out.drawImage(upright,0,0,h,w);
            return raw.toDataURL('image/jpeg',.88).split(',')[1]});
        }""",[move,count,width,height,start,end])
        yield from (base64.b64decode(item) for item in result)

def render(page, stock, output):
    source=(SITE/"cat.mjs").read_text(encoding="utf-8-sig").replace("export ","")
    page.add_script_tag(content=source+"\nwindow.catMoves=moves;window.renderCat=drawCat;")
    for move,_,__,slot in page.evaluate("window.catMoves"):
        path=Path("local/emoji/jpg_merge")/slot/(slot+"_merged.dat")
        raw=(stock/path).read_bytes()
        first,count=PAIR.unpack_from(raw)
        pos,length=PAIR.unpack_from(raw,8)
        assert first==pos==8*(count+1)
        width,height=Image.open(BytesIO(raw[pos:pos+length])).size
        frames=list(sample_frames(page,move,count,width,height))
        offsets=bytearray(PAIR.pack(first,count))
        for data in frames:
            assert len(data)<=27138
            offsets.extend(PAIR.pack(first,len(data)))
            first+=len(data)
        dest=output/path
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(offsets+b"".join(frames))
        movie=SITE/(move+".mp4")
        p=subprocess.Popen(["ffmpeg","-loglevel","error","-y","-f","image2pipe","-framerate",str(PREVIEW_FPS),"-vcodec","mjpeg","-i","pipe:0","-vf","transpose=2","-c:v","libx264","-crf","18","-pix_fmt","yuv420p","-movflags","+faststart",str(movie)],stdin=subprocess.PIPE)
        preview_count=round(count*PREVIEW_FPS/REFERENCE_PREVIEW_FPS)
        try:
            for data in sample_frames(page,move,preview_count,width,height):
                p.stdin.write(data)
        finally:
            p.stdin.close()
            status=p.wait()
        if status:
            raise RuntimeError(f"Video encoding failed for {move}")
        Image.open(BytesIO(frames[int(count*.46)])).transpose(Image.Transpose.ROTATE_90).save(SITE/(move+".png"),optimize=True)
        print(slot,count,len(frames[int(count*.46)]),flush=True)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    for name in ("stock","output","chrome"):
        parser.add_argument("--"+name,type=Path,required=True)
    a=parser.parse_args()
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=str(a.chrome))
        render(browser.new_page(),a.stock,a.output)
        browser.close()

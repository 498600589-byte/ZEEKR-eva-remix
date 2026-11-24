"""Build complete Cardbot-inspired EVA resource trees from verified local EVA assets.

Requires Pillow, NumPy, OpenCV, Playwright, Chromium, and local lottie-web for analysis.
The output has no dependency on those tools at playback.
"""

import argparse
from base64 import b64decode
from binascii import crc_hqx
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from functools import lru_cache
from hashlib import sha256
from io import BytesIO
import json
import math
from pathlib import Path
from struct import Struct

import cv2
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

from build_mecha_styles import PROFILES, REST, group, paint, plain, shape
from cardbot_faces import CHARACTERS, build_native, chassis, layer


PAIR = Struct('<II')
CRITICAL = {'Disconnect','Connect','ljz','ACC','SafetyBelt','DistractionAlert','FatigueAlert',
            'Overspeed','RCTADOW','NavigationMap','SentinelMode','CallReminder','StartChargeIn',
            'StartChargeLoop','StartChargeEnd','ChargeFinish','DriveEconomic','DriveComfort','DrivePerformanc'}
BUSY = {'Driving','AirConditioner','Aromatherapy','CarWindow','Seat','SeatVentilation','HeatStrWhl',
        'ActingCute','WakingUp','Calling','LabourDay','NewYear','Kite','Book'}


def encode(document):
    return json.dumps(document, ensure_ascii=False, separators=(',',':')).encode('utf-8')


def white_pairs(frame):
    """Locate the original EVA eyes while rejecting text, thin lines and props."""
    height,width=frame.shape[:2]
    luminous=(frame.min(axis=2)>=198).astype(np.uint8)
    luminous[:int(height*.19),:]=0
    luminous[int(height*.69):,:]=0
    luminous[:,:int(width*.10)]=0
    luminous[:,int(width*.90):]=0
    _,_,stats,centroids=cv2.connectedComponentsWithStats(luminous,connectivity=8)
    candidates=[]
    for index,(x,y,w,h,area) in enumerate(stats[1:],1):
        if width*.064 <= w <= width*.30 and 2 <= h <= height*.37 and area >= w*max(1,h)*.42:
            candidates.append((x,y,w,h,area,*centroids[index]))
    best=None
    score=0
    for left in candidates:
        for right in candidates:
            x1,y1,w1,h1,a1,cx1,cy1=left
            x2,y2,w2,h2,a2,cx2,cy2=right
            if not (width*.20 < cx2-cx1 < width*.56 and abs(cy2-cy1)<height*.135
                    and .52<w1/w2<1.92 and .26<a1/a2<3.8):
                continue
            cx,cy=(cx1+cx2)/2,(cy1+cy2)/2
            balance=min(w1,w2)/max(w1,w2)
            rating=(w1+w2)*balance - abs(cx-width/2)*.20 - abs(cy1-cy2)*.45
            if rating>score:
                scale=min(1.12,max(.62,(cx2-cx1)/132))
                best=(round(cx,2),round(cy,2),round(scale,3),
                      round(min(113,130*h1/w1)),round(min(113,130*h2/w2)),
                      tuple(map(int,(x1,y1,w1,h1))),tuple(map(int,(x2,y2,w2,h2))))
                score=rating
    return best


def track_documents(documents, runtime, chrome):
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(executable_path=str(chrome),headless=True,args=['--disable-gpu'])
        page=browser.new_page()
        page.set_content('<div id="canvas"></div>')
        page.add_script_tag(path=runtime)
        results={}
        for name,document in documents.items():
            if name in PROFILES or name in CRITICAL or document['op']-document['ip']<=1:
                continue
            grab = page.evaluate('''async data => {
              const host=document.querySelector('#canvas');
              host.style.width=data.w+'px';host.style.height=data.h+'px';
              const player=lottie.loadAnimation({container:host,renderer:'canvas',loop:false,autoplay:false,animationData:data});
              if (!player.isLoaded) await new Promise(resolve=> {
                player.addEventListener('DOMLoaded',resolve);setTimeout(resolve,800);
              });
              const canvas=host.querySelector('canvas');
              if (!canvas || !player.isLoaded) {player.destroy();return [];}
              const frames=[];
              const count=Math.ceil(data.op-data.ip);
              for(let frame=0;frame<count;frame+=3) {
                player.goToAndStop(frame,true);
                frames.push([frame,canvas.toDataURL('image/png').split(',')[1]]);
              }
              player.destroy();
              return frames;
            }''',document)
            results[name]=[(frame,white_pairs(np.array(Image.open(BytesIO(b64decode(data)))
                                .convert('RGB').transpose(Image.Transpose.ROTATE_90)))) for frame,data in grab]
        browser.close()
    return results


def animated(values):
    """Encode absolute frames for the native Lottie layer."""
    items = [{'t': frame, 's': value if isinstance(value,list) else [value]} for frame,value in values]
    for item,following in zip(items,items[1:]):
        item.update(e=following['s'],o={'x':[.28],'y':[0]},i={'x':[.54],'y':[1]})
    return {'a':1,'k':items}


def eye_pose(left,right,wave):
    return replace(REST,left=max(6,left),right=max(6,right),pupil=round(wave*13),
                   brow=round(wave*6),tilt=round(wave*2))


def face_free(role,document):
    """Quiet edge animation for resources whose on-screen message occupies the center."""
    start,end=document['ip'],document['op']
    count=end-start
    geometry=[([29,48],[57,28],[49,45],[23,56]),([391,365],[425,344],[421,355],[386,374])]
    marks=group('Character running lights',[
        paint('Plate',[shape(polygon)],CHARACTERS[role].armor) for polygon in geometry],
        opacity=animated([(start,0),(start+round(count*.30),75),(start+round(count*.54),20),(end-1,0)]))
    return [marks]


def overlay_vector(role,name,document,track):
    if name in PROFILES:
        return build_native(role,name)
    if name in CRITICAL or document['op']-document['ip']<=1:
        return document
    start,end,width,height=(document[key] for key in ('ip','op','w','h'))
    valid=[pair for _,pair in track if pair]
    index=max(plane.get('ind',0) for plane in document['layers'])+1
    parts=[]
    if len(valid)>max(1,len(track)//8):
        keys_full=[]
        for frame,pair in track:
            x,y,zoom,left,right,*_=pair or valid[0]
            keys_full.append((start+frame,
                [x*450/height,y*390/width],zoom,eye_pose(left,right,math.sin(frame/11)),100 if pair else 0))
        if keys_full[-1][0]<end-1:
            keys_full.append((end-1,*keys_full[-1][1:]))
        char=chassis(role,lambda transform:animated([(frame,transform(pose)) for frame,_,_,pose,_ in keys_full]),include_jaw=False)
        # Size the narrow cover on the eyes only; original symbols and props render below.
        cover=paint('Eye field',[shape([[-111,-36],[111,-36],[111,37],[-111,37]])],'#03050B')
        parts.append(group('Tracked expression',[*char,cover],
            position=animated([(f,xy) for f,xy,_,_,_ in keys_full]),
            scale=animated([(f,[round(zoom*100)]*2) for f,_,zoom,_,_ in keys_full]),
            opacity=animated([(f,active) for f,_,_,_,active in keys_full])))
    else:
        parts=face_free(role,document)
    return {**document,'layers':[layer('Character treatment',parts,width,height,start,end,index),*document['layers']]}


def sample_path(data):
    points=[]
    vertices=data['v']
    count=len(vertices) if data['c'] else len(vertices)-1
    for index in range(count):
        next_index=(index+1)%len(vertices)
        a=np.array(vertices[index],dtype=float)
        b=a+data['o'][index]
        d=np.array(vertices[next_index],dtype=float)
        c=d+data['i'][next_index]
        for t in (0,.2,.4,.6,.8):
            points.append((1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d)
    return np.array([*points,vertices[0 if data['c'] else -1]])


def draw_vector_groups(items, canvas, transform, opacity):
    from math import radians, cos, sin
    items = list(items)
    for item in reversed(items):
        if item['ty']!='gr':
            continue
        sub=item['it']
        tr=sub[-1]
        alpha=opacity*tr['o']['k']*.01
        if alpha<=0:
            continue
        px,py=tr['p']['k']
        sx,sy=(value*.01 for value in tr['s']['k'])
        theta=radians(tr['r']['k'])
        transform2 = transform @ np.array([[sx*cos(theta),-sy*sin(theta),px],[sx*sin(theta),sy*cos(theta),py],[0,0,1]])
        draw_vector_groups(sub[:-1],canvas,transform2,alpha)
        style=next((entry for entry in sub if entry['ty'] in ('fl','st')),None)
        if not style:
            continue
        hue=tuple(round(value*255) for value in style['c']['k'][:3])+(round(alpha*255),)
        for geometry in sub:
            closed=True
            if geometry['ty']=='sh':
                points=sample_path(geometry['ks']['k'])
                closed=geometry['ks']['k']['c']
            elif geometry['ty']=='el':
                x,y=geometry['p']['k'];width,height=geometry['s']['k']
                points=np.array([(x+width*.5*cos(index/32*math.tau),y+height*.5*sin(index/32*math.tau)) for index in range(32)])
            else:
                continue
            pixels=(np.c_[points,np.ones(len(points))]@transform2.T)[:,:2].round().astype(np.int32)
            if style['ty']=='fl':
                cv2.fillPoly(canvas,[pixels],hue,lineType=cv2.LINE_AA)
            else:
                cv2.polylines(canvas,[pixels],closed,hue,round(style['w']['k']*1.25),lineType=cv2.LINE_AA)


@lru_cache(maxsize=2600)
def character_raster(role,left,right,gaze):
    pose=eye_pose(left,right,gaze*.5)
    canvas=np.zeros((196,320,4),dtype=np.uint8)
    transform=np.array([[1,0,160],[0,1,110],[0,0,1]],dtype=float)
    draw_vector_groups(chassis(role,lambda callback:plain(callback(pose)),include_jaw=False),canvas,transform,1)
    return Image.fromarray(canvas,'RGBA')


def jpeg_frame(image):
    for quality in (84,77,68,58,48,40):
        target=BytesIO()
        image.save(target,format='JPEG',quality=quality,subsampling=2,optimize=True)
        if target.tell()<=27138:
            return target.getvalue()
    raise ValueError('Frame is larger than the previously installed resource range.')


def frame_index(data):
    offset,count=PAIR.unpack_from(data)
    if offset!=PAIR.size*(count+1) or count<=0:
        raise ValueError('Invalid DAT header')
    for number in range(count):
        start,length=PAIR.unpack_from(data,PAIR.size*(number+1))
        end=start+length
        if start!=offset or data[start:start+2]!=b'\xff\xd8' or data[end-2:end]!=b'\xff\xd9':
            raise ValueError('Invalid DAT JPEG frame')
        yield data[start:end]
        offset=end
    if offset!=len(data):
        raise ValueError('Invalid DAT end')


def rebuild_dat(frames):
    offset=(1+len(frames))*PAIR.size
    index=bytearray(PAIR.pack(offset,len(frames)))
    for frame in frames:
        index.extend(PAIR.pack(offset,len(frame)))
        offset+=len(frame)
    return b''.join([index,*frames])


def build_dat(job):
    name,source,outputs=job
    cv2.setNumThreads(1)
    raw=source.read_bytes()
    if name in CRITICAL:
        for target in outputs.values():
            target.write_bytes(raw)
        return name,0
    frames=list(frame_index(raw))
    by_role={role:[] for role in outputs}
    changed=0
    for index,original in enumerate(frames):
        with Image.open(BytesIO(original)) as source_image:
            frame=source_image.convert('RGB').transpose(Image.Transpose.ROTATE_90)
        sample=np.array(frame)
        pair=white_pairs(sample)
        if pair:
            x,y,zoom,left,right,rect1,rect2=pair
            # Erase just the old white eye regions before drawing the tracked eyes.
            for x0,y0,w,h in (rect1,rect2):
                inner=sample[max(0,y0-2):y0+h+2,max(0,x0-2):x0+w+2]
                background=sample[max(0,y0-7):max(1,y0-3),x0:x0+w]
                dark=tuple(np.median(background.reshape(-1,3),axis=0).astype(np.uint8)) if background.size else (0,0,0)
                mask=cv2.dilate((inner.min(axis=2)>145).astype(np.uint8),np.ones((3,3),np.uint8))
                inner[mask>0]=dark
            changed+=1
        phase=index/max(1,len(frames)-1)
        for role in by_role:
            if pair:
                quant=lambda value:max(8,round(value/12)*12)
                art=character_raster(role,quant(left),quant(right),round(math.sin(phase*math.tau)*1.7))
                scale=zoom*(.88 if name in BUSY else 1)
                decal=art.resize((max(1,round(art.width*scale)),max(1,round(art.height*scale))),Image.Resampling.BILINEAR)
                view=Image.fromarray(sample)
                view.paste(decal,(round(x-160*scale),round(y-110*scale)),decal)
                by_role[role].append(jpeg_frame(view.transpose(Image.Transpose.ROTATE_270)))
            else:
                by_role[role].append(original)
    for role,path in outputs.items():
        content=rebuild_dat(by_role[role])
        assert len(list(frame_index(content)))==len(frames)
        path.write_bytes(content)
    return name,changed


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for option in ('stock','jojo','previous','output','lottie-web','chrome'):
        parser.add_argument('--'+option,type=Path,required=True)
    parser.add_argument('--jobs',type=int,default=6)
    args=parser.parse_args()
    source_plan=json.loads((args.jojo/'写入校验清单.json').read_bytes())
    base=Path('local/emoji')
    prior_manifest=json.loads((args.jojo/base/'EmojiList.json').read_bytes())
    sources={}
    documents={}
    for record in source_plan['assets']:
        path=Path(record['path'])
        location=args.stock if record['sha256']['stock'] else args.previous
        source=location/base/path
        sources[path]=source
        if path.suffix=='.json':
            documents[path.stem]=json.loads(source.read_bytes())
    tracks=track_documents(documents,args.lottie_web,args.chrome)
    print(f'Tracked {len(tracks)} original vector timelines.',flush=True)
    jobs=[]
    for path,source in sources.items():
        targets={role:args.output/role/base/path for role in CHARACTERS}
        for target in targets.values():
            target.parent.mkdir(parents=True,exist_ok=True)
        if path.suffix=='.dat':
            jobs.append((path.parent.name,source,targets))
        else:
            original=source.read_bytes()
            for role,target in targets.items():
                doc=documents.get(path.stem)
                if doc is None or path.stem in CRITICAL:
                    target.write_bytes(original)
                else:
                    target.write_bytes(encode(overlay_vector(role,path.stem,doc,tracks.get(path.stem,[]))))
    with ProcessPoolExecutor(max_workers=args.jobs) as workers:
        updates=list(workers.map(build_dat,jobs))
    print(f'Rendered {len(updates)} DAT clips; tracked faces in {sum(count>0 for _,count in updates)}.',flush=True)
    for role in CHARACTERS:
        root=args.output/role
        manifest=json.loads(json.dumps(prior_manifest))
        entries={row['file']:row for row in manifest['files']}
        hashes=[]
        for record in source_plan['assets']:
            path=Path(record['path'])
            data=(root/base/path).read_bytes()
            entries[path.name]['crc']=crc_hqx(data,0xffff)
            old=record['sha256']
            hashes.append({'path':record['path'],'sha256':{
                'stock':old['stock'],'previous_jojo':old['previous_jojo'],
                'jojo_v2':old['motion'],'motion':sha256(data).hexdigest()}})
        result=encode(manifest)
        (root/base/'EmojiList.json').write_bytes(result)
        states={name:source_plan['states'][name] for name in ('stock','previous_jojo')}
        states.update(jojo_v2=source_plan['states']['motion'],motion={'manifest_sha256':sha256(result).hexdigest()})
        (root/'写入校验清单.json').write_bytes(encode(dict(source_version=source_plan['source_version'],
          map_sha256=source_plan['map_sha256'],states=states,assets=hashes)))
        print(f'{role}: {len(hashes)} resources',flush=True)


if __name__=='__main__':
    main()

"""Render interpolated Nailoong poses and 30 fps gallery clips.

Run from the repository with Pillow, NumPy, OpenCV and FFmpeg installed.
"""

from argparse import ArgumentParser
from functools import lru_cache
from pathlib import Path
import json
import re
import subprocess
from tempfile import TemporaryDirectory
from math import exp, pi, sin, tau

import cv2
import numpy as np
from PIL import Image


SITE = Path(__file__).resolve().parents[1] / 'docs' / 'nailoong'
MEDIA = SITE / 'media'
ATLASES = (
    ('keyframes.png', 'stifle neutral nervous calm laugh left cry shock smirk recover pout closed'.split()),
    ('extended-keyframes.png', 'blink bored sleep yawn wink shy pucker up down talk focused right'.split()),
)
CLIPS = {
    'laugh': (('stifle','laugh','smirk','stifle'), (.66,.94,1.64,2.04,2.78,3.26)),
    'side-eye': (('neutral','left','recover','neutral'), (.56,.81,1.53,1.88,2.61,2.91)),
    'pout': (('nervous','cry','pout','nervous'), (.47,.87,1.63,2.10,2.76,3.26)),
    'surprise': (('calm','shock','closed','calm'), (.66,.87,1.75,1.94,2.11,2.39)),
}
FPS = 30
DURATION = 3.7


def load_poses(size):
    poses = {}
    for filename, names in ATLASES:
        with Image.open(MEDIA / filename) as image:
            for index, name in enumerate(names):
                x, y = index % 4 * 384 + 13, [44, 370, 698][index // 4]
                crop = image.crop((x, y, x + 358, y + 282)).convert('RGB')
                poses[name] = np.asarray(crop.resize(size, Image.Resampling.LANCZOS))
    return poses


class Morph:
    def __init__(self, poses, size):
        self.poses = poses
        self.y, self.x = np.indices((size[1], size[0]), dtype=np.float32)

    @lru_cache(maxsize=95)
    def pair(self, first, last):
        def gray(name):
            return cv2.cvtColor(self.poses[name], cv2.COLOR_RGB2GRAY)

        a, b = gray(first), gray(last)
        return (
            cv2.calcOpticalFlowFarneback(a, b, None, .5, 5, 19, 5, 7, 1.5, 0),
            cv2.calcOpticalFlowFarneback(b, a, None, .5, 5, 19, 5, 7, 1.5, 0),
        )

    def frame(self, first, last, amount):
        if first == last or amount <= 0:
            return self.poses[first]
        if amount >= 1:
            return self.poses[last]
        flow_a, flow_b = self.pair(first, last)

        def move(name, field, direction):
            return cv2.remap(self.poses[name], self.x - direction * field[:, :, 0],
                             self.y - direction * field[:, :, 1], cv2.INTER_LINEAR)

        return cv2.addWeighted(move(first, flow_a, amount), 1 - amount,
                               move(last, flow_b, 1 - amount), amount, 0)


def smooth(value):
    return value * value * (3 - 2 * value)


def generate_atlas():
    library = (SITE / 'library.js').read_text(encoding='utf-8')
    sequences = re.findall(r": \[((?:'\w+',?)+)\],", library.split('const sequence = {')[1].split('};')[0])
    pairs = set()
    for sequence in sequences:
        names = re.findall("'(\\w+)'", sequence)
        pairs.update(tuple(sorted((a, b))) for a, b in zip(names, names[1:]) if a != b)
    assert len(pairs) >= 25
    width, height, per_row, steps = 192, 152, 16, 8
    count = len(pairs) * (steps - 1)
    atlas = Image.new('RGB', (width * per_row, height * ((count + per_row - 1) // per_row)))
    morph = Morph(load_poses((width, height)), (width, height))
    lookup = {}
    for number, (first, last) in enumerate(sorted(pairs)):
        index = number * (steps - 1)
        lookup[f'{first}/{last}'] = index
        for step in range(1, steps):
            x, y = index % per_row * width, index // per_row * height
            atlas.paste(Image.fromarray(morph.frame(first, last, step / steps)), (x, y))
            index += 1
    atlas.save(MEDIA / 'face-transitions.webp', quality=89, method=4)
    data = dict(width=width, height=height, columns=per_row, steps=steps, pairs=lookup)
    (SITE / 'transitions-data.js').write_bytes(
        ('window.evaNailoongTransitions = ' + json.dumps(data, separators=(',', ':')) + ';\n').encode('utf-8'))
    print(f'{len(pairs)} pose transitions, {count} intermediate frames.')


def pose_at(t, names, beats, morph):
    for index, (start, end) in enumerate(zip(beats[::2], beats[1::2])):
        if t < start:
            return morph.poses[names[index]]
        if t < end:
            return morph.frame(names[index], names[index + 1], smooth((t - start) / (end - start)))
    return morph.poses[names[-1]]


def render_clips():
    screen = (408, 354)
    width, height = 336, 262
    morph = Morph(load_poses((width, height)), (width, height))
    for name, (poses, beats) in CLIPS.items():
        output = MEDIA / (name + '.mp4')
        with TemporaryDirectory(prefix='eva-nailoong-motion-') as temporary:
            frames = Path(temporary) / 'frames.rgb'
            with frames.open('wb') as handle:
                for index in range(round(DURATION * FPS)):
                    t = index / FPS
                    face = pose_at(t, poses, beats, morph)
                    onset = max(0, t - beats[1])
                    pulse = exp(-onset * 4.2) if t >= beats[1] else 0
                    if name == 'laugh':
                        anticipate = sin(pi * t / beats[0]) ** 2 if t < beats[0] else 0
                        bounce = pulse * sin(onset * tau * 4.3)
                        dx, dy, tilt, stretch = 0, -9 * bounce + 5 * anticipate, -1.4 * bounce, -.07 * bounce
                    elif name == 'side-eye':
                        dx, dy, tilt, stretch = -6 * pulse, 0, -1.8 * pulse, 0
                    elif name == 'pout':
                        shake = pulse * sin(onset * tau * 4.6)
                        dx, dy, tilt, stretch = 4 * shake, 2 * shake, 0, .035 * pulse
                    else:
                        dx, dy, tilt, stretch = 0, -7 * pulse, 0, .085 * pulse
                    zoom = 1 + .009 * sin(t / DURATION * tau * 2)
                    matrix = cv2.getRotationMatrix2D((width / 2, height / 2), tilt, zoom)
                    matrix[1, :2] *= 1 + stretch
                    matrix[0, 2] += (screen[0] - width) / 2 + dx
                    matrix[1, 2] += (screen[1] - height) / 2 + dy - stretch * height / 2
                    handle.write(cv2.warpAffine(face, matrix, screen, flags=cv2.INTER_LINEAR).tobytes())
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pixel_format', 'rgb24',
                            '-video_size', '408x354', '-framerate', str(FPS), '-i', str(frames),
                            '-an', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p',
                            '-movflags', '+faststart', str(output)], check=True)
        print(output.name, f'{FPS} fps')


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--atlas-only', action='store_true')
    args = parser.parse_args()
    cv2.setNumThreads(2)
    generate_atlas()
    if not args.atlas_only:
        render_clips()

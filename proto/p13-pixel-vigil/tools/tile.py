"""Dev helper: tile rendered frames into a labelled sheet. python3 tile.py out.jpg frames_dir f1,f2,... [cols] [width_per_tile]"""
import sys, os
from PIL import Image, ImageDraw
out, d, fl = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(',')]
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 3; tw = int(sys.argv[5]) if len(sys.argv) > 5 else 640
ims = []
for f in fl:
    im = Image.open(os.path.join(d, f'{f:05d}.png')).convert('RGB'); th = round(tw * im.height / im.width)
    im = im.resize((tw, th), Image.NEAREST); dr = ImageDraw.Draw(im); dr.rectangle([0, 0, 46, 14], fill=(0, 0, 0)); dr.text((3, 2), f'f{f}', fill=(255, 255, 255)); ims.append(im)
rows = (len(ims) + cols - 1) // cols; th = ims[0].height
sheet = Image.new('RGB', (cols * tw + (cols - 1) * 4, rows * th + (rows - 1) * 4), (40, 40, 40))
for k, im in enumerate(ims): sheet.paste(im, ((k % cols) * (tw + 4), (k // cols) * (th + 4)))
sheet.save(out, quality=92); print('wrote', out, sheet.size)

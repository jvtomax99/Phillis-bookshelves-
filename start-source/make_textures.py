"""Draws tex/flyleaf.png (the signed first page) and tex/endpaper.png. Edit the inscription here."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
W, H = 1500, 2200
im = Image.new('RGB', (W, H), (246, 238, 222))
noise = Image.effect_noise((W, H), 18).convert('L')
im = Image.composite(im, Image.new('RGB', (W, H), (236, 226, 206)), noise.point(lambda v: 255 if v > 120 else 200))
im = im.filter(ImageFilter.GaussianBlur(.6))
v = Image.new('L', (W, H), 0); d = ImageDraw.Draw(v)
for i in range(60): d.rectangle([i*6, i*6, W-i*6, H-i*6], outline=int(i*3.6))
v = v.filter(ImageFilter.GaussianBlur(60)); im = Image.composite(im, Image.new('RGB', (W, H), (214, 196, 166)), v)
d = ImageDraw.Draw(im)
sans = ImageFont.truetype('fonts/InstrumentSans.ttf', 44); sans.set_variation_by_axes([100, 600])
scr = ImageFont.truetype('fonts/PinyonScript.ttf', 150); sig = ImageFont.truetype('fonts/PinyonScript.ttf', 170)
def ctext(y, t, f, fill, sp=0):
    if sp:
        w = sum(d.textlength(c, font=f) + sp for c in t) - sp; x = (W - w) / 2
        for c in t: d.text((x, y), c, font=f, fill=fill); x += d.textlength(c, font=f) + sp
    else:
        w = d.textlength(t, font=f); d.text(((W - w) / 2, y), t, font=f, fill=fill)
ctext(330, 'THIS COPY BELONGS TO', sans, (128, 108, 92), sp=14); ctext(400, 'A GROWN READER', sans, (128, 108, 92), sp=14)
ctext(640, 'For the ones who', scr, (40, 26, 22)); ctext(820, 'read after dark.', scr, (40, 26, 22))   # placeholder: Phillis's own words go here
ctext(1040, 'Phillis', sig, (168, 20, 44))
d.line([(W/2 - 110, 1330), (W/2 + 110, 1330)], fill=(190, 150, 80), width=4)
ctext(1400, 'ADULTS 18+', sans, (128, 108, 92), sp=14); ctext(1470, 'EXPLICIT CONTENT', sans, (128, 108, 92), sp=14)
im.save('tex/flyleaf.png')
E = Image.new('RGB', (W, H), (74, 9, 16)); d = ImageDraw.Draw(E); s = 110
for x in range(-H, W + H, s):
    d.line([(x, 0), (x + H, H)], fill=(140, 100, 52), width=3); d.line([(x, 0), (x - H, H)], fill=(140, 100, 52), width=3)
for yi in range(0, H + s, s):
    for xi in range(0, W + s, s):
        cx, cy = xi + (s/2 if (yi // s) % 2 else 0), yi
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(190, 150, 80))
E.filter(ImageFilter.GaussianBlur(.8)).save('tex/endpaper.png')

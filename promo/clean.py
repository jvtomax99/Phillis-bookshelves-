import os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
C = os.path.join(HERE, '..', 'covers'); B = os.path.join(HERE, 'build'); os.makedirs(B, exist_ok=True)
from PIL import Image, ImageFilter
def box(m, r):
    # box blur of a 2D float array via integral image
    p = np.pad(m, r + 1, mode='edge'); c = p.cumsum(0).cumsum(1)
    k = 2 * r + 1
    s = c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]
    return s[:m.shape[0], :m.shape[1]] / (k * k)
def clean(src, dst, y1, ell, rects):
    im = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
    H, W, _ = im.shape
    lum = im.mean(2)
    bg = np.median(im[lum > 235].reshape(-1, 3), 0)
    yy, xx = np.mgrid[0:H, 0:W]
    cx, cy, rx, ry = ell
    inside = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 < 1
    rm = ((yy < y1) & ~inside).astype(np.float32)
    red = (((im[..., 0] > 140) & (im[..., 0] - im[..., 1] > 45)) | ((im[..., 0] > 200) & (im[..., 1] > 110) & (im[..., 0] - im[..., 1] > 22))) & (yy < y1)
    rm[red] = 1
    for x0, ya, x1, yb in rects:
        rm[ya:yb, x0:x1] = 1
    rm = box(rm, 3)
    out = im * (1 - rm[..., None]) + bg * rm[..., None]
    Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(dst, quality=95)
clean(f'{C}/reign-is-mine.jpg', f'{B}/reign-clean.jpg', 560, (515, 600, 95, 150), [(30, 1285, 300, 1360), (720, 1250, 1000, 1356)])
clean(f'{C}/ebony-the-club.jpg', f'{B}/ebony-clean.jpg', 405, (515, 482, 130, 147), [(25, 1150, 360, 1245), (700, 1165, 1000, 1262)])

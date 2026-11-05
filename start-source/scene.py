"""Candlelit nightstand start screen for Phillis Brown, built and rendered in Blender (bpy).
Usage: python3 scene.py --out f.png --res 540x1170 --samples 64 --open 0 [--cam phone|desk]"""
import bpy, bmesh, math, os, sys, argparse, random
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "tex"); FONTS = os.path.join(HERE, "fonts"); MESHY = os.path.join(HERE, "meshy")
ap = argparse.ArgumentParser()
ap.add_argument("--out", default=os.path.join(HERE, "render.png"))
ap.add_argument("--res", default="540x1170")
ap.add_argument("--samples", type=int, default=64)
ap.add_argument("--open", type=float, default=0.0)   # cover angle in degrees, 0 closed, 165 open
ap.add_argument("--cam", default="phone")
ap.add_argument("--noprops", action="store_true")
ap.add_argument("--blend", default="")
ap.add_argument("--nomask", action="store_true")
ap.add_argument("--anim", default="")   # folder for an opening clip
ap.add_argument("--endstill", action="store_true")  # render only the clip's last frame
ap.add_argument("--flames", default="")  # write flame screen positions (json) here
A = ap.parse_args(sys.argv[1:])

bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene

# ---------- helpers ----------
def img(name):
    p = os.path.join(TEX, name)
    return bpy.data.images.load(p, check_existing=True) if os.path.exists(p) else None

def mat_basic(name, color, rough=0.5, metal=0.0, **kw):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    for k, v in kw.items():
        b.inputs[k].default_value = v
    return m

def mat_pbr(name, prefix, scale, tint=None, rough_mul=1.0, sheen=0.0, sheen_tint=None, bump=1.0, sat=1.0, hue=0.5, val=1.0, diff=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links
    b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (scale, scale, scale)
    L.new(tc.outputs["UV"], mp.inputs["Vector"])
    def tex(suffix, non_color=False):
        for ext in ("jpg", "png"):
            im = img(f"{prefix}_{suffix}.{ext}")
            if im:
                if non_color: im.colorspace_settings.name = "Non-Color"
                t = N.new("ShaderNodeTexImage"); t.image = im
                L.new(mp.outputs["Vector"], t.inputs["Vector"]); return t
    d = tex(diff or "diff")
    if d:
        hs = N.new("ShaderNodeHueSaturation")
        hs.inputs["Hue"].default_value = hue; hs.inputs["Saturation"].default_value = sat; hs.inputs["Value"].default_value = val
        L.new(d.outputs["Color"], hs.inputs["Color"])
        out = hs.outputs["Color"]
        if tint:
            mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"
            mx.inputs["Factor"].default_value = 1.0
            L.new(out, mx.inputs["A"]); mx.inputs["B"].default_value = (*tint, 1)
            out = mx.outputs["Result"]
        L.new(out, b.inputs["Base Color"])
    elif tint:
        b.inputs["Base Color"].default_value = (*tint, 1)
    r = tex("rough", True)
    if r:
        mt = N.new("ShaderNodeMath"); mt.operation = "MULTIPLY"; mt.inputs[1].default_value = rough_mul
        L.new(r.outputs["Color"], mt.inputs[0]); L.new(mt.outputs[0], b.inputs["Roughness"])
    n = tex("nor", True)
    if n:
        nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = bump
        L.new(n.outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs["Normal"], b.inputs["Normal"])
    if sheen:
        b.inputs["Sheen Weight"].default_value = sheen
        if sheen_tint: b.inputs["Sheen Tint"].default_value = (*sheen_tint, 1)
        b.inputs["Sheen Roughness"].default_value = 0.35
    return m

def box(name, x0, x1, y0, y1, z0, z1, mat=None, bevel=0.0, parent=None):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = x0 + (v.co.x + .5) * (x1 - x0); v.co.y = y0 + (v.co.y + .5) * (y1 - y0); v.co.z = z0 + (v.co.z + .5) * (z1 - z0)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); S.collection.objects.link(ob)
    # simple box-projected UVs
    me.uv_layers.new()
    uv = me.uv_layers.active.data
    for poly in me.polygons:
        nrm = poly.normal
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            if abs(nrm.z) > .5: uv[li].uv = (co.x * 4, co.y * 4)
            elif abs(nrm.y) > .5: uv[li].uv = (co.x * 4, co.z * 4)
            else: uv[li].uv = (co.y * 4, co.z * 4)
    if mat: me.materials.append(mat)
    if bevel:
        md = ob.modifiers.new("bev", "BEVEL"); md.width = bevel; md.segments = 3; md.limit_method = "ANGLE"
    for p in me.polygons: p.use_smooth = True
    if parent: ob.parent = parent
    return ob

def plane(name, w, h, mat, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, flip=False):
    me = bpy.data.meshes.new(name)
    vs = [(-w/2, -h/2, 0), (w/2, -h/2, 0), (w/2, h/2, 0), (-w/2, h/2, 0)]
    me.from_pydata(vs, [], [(0, 1, 2, 3) if not flip else (3, 2, 1, 0)])
    me.uv_layers.new(); uv = me.uv_layers.active.data
    order = [(0, 0), (1, 0), (1, 1), (0, 1)] if not flip else [(0, 1), (1, 1), (1, 0), (0, 0)]
    for i, li in enumerate(me.polygons[0].loop_indices): uv[li].uv = order[i]
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); S.collection.objects.link(ob)
    ob.location = loc; ob.rotation_euler = rot
    if parent: ob.parent = parent
    return ob

def mat_image(name, image_name, rough=0.8, emission=0.0, bright=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    N = m.node_tree.nodes; L = m.node_tree.links; b = N["Principled BSDF"]
    t = N.new("ShaderNodeTexImage"); t.image = img(image_name)
    bc = N.new("ShaderNodeBrightContrast"); bc.inputs["Bright"].default_value = bright - 1; bc.inputs["Contrast"].default_value = 0.25 if bright > 1 else 0.0
    L.new(t.outputs["Color"], bc.inputs["Color"]); L.new(bc.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    return m

# ---------- materials ----------
M_leather = mat_pbr("leather", "leather_red_02", 3.0, tint=(0.80, 0.035, 0.075), rough_mul=0.6, bump=0.9, sat=0.0, hue=0.5, val=1.5, diff="coll1")
M_wood = mat_pbr("wood", "black_walnut_veneer_01", 1.2, tint=(0.36, 0.22, 0.15), rough_mul=0.55, bump=0.4)
M_velvet = mat_pbr("velvet", "velour_velvet", 2.0, tint=(0.13, 0.003, 0.018), sheen=1.0, sheen_tint=(1.0, 0.35, 0.35), bump=0.6, sat=0.0)
M_gold = mat_basic("gold", (0.98, 0.72, 0.36), rough=0.22, metal=1.0)
M_gold_brush = mat_basic("goldfoil", (0.95, 0.70, 0.38), rough=0.32, metal=1.0)
M_satin = mat_basic("ribbon", (0.45, 0.01, 0.04), rough=0.28, **{"Sheen Weight": 0.6})
M_fly = mat_image("flyleaf", "flyleaf.png", rough=0.85, bright=1.12)
M_end = mat_image("endpaper", "endpaper.png", rough=0.6)

# paper edges: fine stripes
M_paper = bpy.data.materials.new("pages"); M_paper.use_nodes = True
N = M_paper.node_tree.nodes; Lk = M_paper.node_tree.links; b = N["Principled BSDF"]
w = N.new("ShaderNodeTexWave"); w.wave_type = "BANDS"; w.bands_direction = "Z"; w.inputs["Scale"].default_value = 260; w.inputs["Distortion"].default_value = 1.5
cr = N.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (0.70, 0.62, 0.50, 1); cr.color_ramp.elements[1].color = (0.93, 0.88, 0.78, 1)
tco = N.new("ShaderNodeTexCoord"); Lk.new(tco.outputs["Object"], w.inputs["Vector"])
Lk.new(w.outputs["Fac"], cr.inputs["Fac"]); Lk.new(cr.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.9

# glass and wine
M_glass = bpy.data.materials.new("glass"); M_glass.use_nodes = True
gb = M_glass.node_tree.nodes["Principled BSDF"]
gb.inputs["Transmission Weight"].default_value = 1.0; gb.inputs["Roughness"].default_value = 0.0; gb.inputs["IOR"].default_value = 1.5
gb.inputs["Base Color"].default_value = (1, 1, 1, 1)
M_wine = bpy.data.materials.new("wine"); M_wine.use_nodes = True
wb = M_wine.node_tree.nodes["Principled BSDF"]
wb.inputs["Transmission Weight"].default_value = 1.0; wb.inputs["Roughness"].default_value = 0.02; wb.inputs["IOR"].default_value = 1.34
wb.inputs["Base Color"].default_value = (0.55, 0.02, 0.05, 1)
vol = M_wine.node_tree.nodes.new("ShaderNodeVolumeAbsorption"); vol.inputs["Color"].default_value = (0.6, 0.02, 0.05, 1); vol.inputs["Density"].default_value = 60
M_wine.node_tree.links.new(vol.outputs[0], M_wine.node_tree.nodes["Material Output"].inputs["Volume"])

# flame
M_flame = bpy.data.materials.new("flame"); M_flame.use_nodes = True
fn = M_flame.node_tree.nodes; fl = M_flame.node_tree.links
for n in list(fn):
    if n.type != "OUTPUT_MATERIAL": fn.remove(n)
em = fn.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (1.0, 0.62, 0.26, 1); em.inputs["Strength"].default_value = 45
fl.new(em.outputs[0], fn["Material Output"].inputs["Surface"])

# ---------- the nightstand and the curtain ----------
box("table", -0.7, 0.7, -0.6, 0.26, -0.05, 0.0, M_wood, bevel=0.004)
# curtain: a grid with soft folds
me = bpy.data.meshes.new("curtain"); bm = bmesh.new()
nx, nz = 220, 30; X0, X1, Z0, Z1 = -1.0, 1.0, -0.06, 1.1
random.seed(7); phases = [random.uniform(0, 6.28) for _ in range(4)]
grid = []
for j in range(nz + 1):
    row = []
    for i in range(nx + 1):
        x = X0 + (X1 - X0) * i / nx; z = Z0 + (Z1 - Z0) * j / nz
        y = 0.34 + 0.022 * math.sin(x * 34 + phases[0]) + 0.012 * math.sin(x * 71 + phases[1]) + 0.006 * math.sin(x * 133 + phases[2] + z * 2)
        row.append(bm.verts.new((x, y, z)))
    grid.append(row)
uvl = bm.loops.layers.uv.new()
for j in range(nz):
    for i in range(nx):
        f = bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
        for lp, (a, c) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))):
            lp[uvl].uv = (a / nx * 4, c / nz * 2.2)
        f.smooth = True
bm.normal_update(); bm.to_mesh(me); bm.free()
cur = bpy.data.objects.new("curtain", me); S.collection.objects.link(cur); me.materials.append(M_velvet)

# ---------- the book ----------
BW, BL, BT = 0.15, 0.22, 0.028
book = bpy.data.objects.new("book", None); S.collection.objects.link(book)
book.location = (0.0, -0.005, 0.0); book.rotation_euler = (0, 0, math.radians(-11))
box("back", -BW/2, BW/2, -BL/2, BL/2, 0, 0.0032, M_leather, bevel=0.0012, parent=book)
box("pages", -BW/2 + 0.004, BW/2 - 0.0035, -BL/2 + 0.003, BL/2 - 0.003, 0.0032, BT - 0.0032, M_paper, bevel=0.0006, parent=book)
plane("flyleaf", BW - 0.0085, BL - 0.0065, M_fly, loc=(0.00025, 0, BT - 0.00315), parent=book)
# spine: rounded
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=BT / 2 + 0.0004, depth=BL, location=(-BW/2 + 0.0015, 0, BT / 2), rotation=(math.radians(90), 0, 0))
sp = bpy.context.active_object; sp.name = "spine"; sp.scale = (0.55, 1, 1); sp.data.materials.append(M_leather); sp.parent = book
bpy.ops.object.shade_smooth()
# front cover on a hinge at the top of the spine
hinge = bpy.data.objects.new("hinge", None); S.collection.objects.link(hinge); hinge.parent = book
hinge.location = (-BW/2 + 0.0015, 0, BT - 0.0016)
hinge.rotation_euler = (0, -math.radians(A.open), 0)
box("front", 0, BW - 0.0015, -BL/2, BL/2, -0.0016, 0.0016, M_leather, bevel=0.0012, parent=hinge)
plane("endpaper", BW - 0.012, BL - 0.012, M_end, loc=((BW - 0.0015) / 2 + 0.002, 0, -0.00165), parent=hinge, flip=True)
plane("endpaper_l", 0.01, BL - 0.004, M_end, loc=(0.004, 0, -0.00166), parent=hinge, flip=True).hide_render = True

def gold_text(body, font, size, x, y, extrude=0.00028, spacing=1.0, mat=M_gold):
    cu = bpy.data.curves.new(body[:10], "FONT"); cu.body = body
    cu.font = bpy.data.fonts.load(os.path.join(FONTS, font), check_existing=True)
    cu.size = size; cu.align_x = "CENTER"; cu.align_y = "CENTER"; cu.extrude = extrude
    cu.bevel_depth = 0.00008; cu.space_character = spacing; cu.resolution_u = 6
    ob = bpy.data.objects.new("t_" + body[:8], cu); S.collection.objects.link(ob)
    ob.parent = hinge; ob.location = (x, y, 0.0016 + extrude * 0.2)
    cu.materials.append(mat)
    return ob

cx = (BW - 0.0015) / 2 + 0.006
gold_text("PB", "BodoniModa.ttf", 0.046, cx, 0.042, extrude=0.0004, spacing=0.92)
gold_text("Phillis Brown", "PinyonScript.ttf", 0.0235, cx, -0.008)
gold_text("S H O R T   S T O R I E S", "InstrumentSans.ttf", 0.0052, cx, -0.032)
gold_text("F O R   G R O W N   R E A D E R S", "InstrumentSans.ttf", 0.0042, cx, -0.088)
# gold frames: two thin rules
def frame(inset_l, inset, wdt):
    x0, x1 = inset_l, BW - 0.0015 - inset; y0, y1 = -BL/2 + inset, BL/2 - inset
    z0, z1 = 0.0016, 0.0016 + 0.00012
    box("fr", x0, x1, y1 - wdt, y1, z0, z1, M_gold_brush, parent=hinge); box("fr", x0, x1, y0, y0 + wdt, z0, z1, M_gold_brush, parent=hinge)
    box("fr", x0, x0 + wdt, y0, y1, z0, z1, M_gold_brush, parent=hinge); box("fr", x1 - wdt, x1, y0, y1, z0, z1, M_gold_brush, parent=hinge)
frame(0.019, 0.010, 0.0009); frame(0.0225, 0.0135, 0.0005)
# blind-tooled line near the hinge
box("tool", 0.011, 0.0118, -BL/2 + 0.004, BL/2 - 0.004, 0.0016, 0.00168, M_gold_brush, parent=hinge)
# metal corners at the fore-edge
def corner(top):
    me = bpy.data.meshes.new("corner"); s = 0.019; x1 = BW - 0.0015 + 0.0006; y1 = (BL/2 + 0.0006) * (1 if top else -1); sy = -1 if top else 1
    vs = [(x1, y1, -0.0021), (x1 - s, y1, -0.0021), (x1, y1 + sy * s, -0.0021), (x1, y1, 0.0021), (x1 - s, y1, 0.0021), (x1, y1 + sy * s, 0.0021)]
    fs = [(0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (0, 3, 5, 2), (1, 2, 5, 4)] if top else [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (0, 2, 5, 3), (1, 4, 5, 2)]
    me.from_pydata(vs, [], fs); me.materials.append(M_gold)
    ob = bpy.data.objects.new("corner", me); S.collection.objects.link(ob); ob.parent = hinge
    md = ob.modifiers.new("bev", "BEVEL"); md.width = 0.0007; md.segments = 3
    return ob
corner(True); corner(False)
# ribbon bookmark running out of the bottom edge onto the table
me = bpy.data.meshes.new("ribbon"); bm = bmesh.new(); rw = 0.0075; pts = []
for k in range(25):
    t = k / 24; y = -BL/2 + 0.02 - t * 0.085
    z = (BT - 0.0048) * (1 - min(1, t * 3.2)) ** 2 + 0.0005
    x = 0.035 + 0.012 * math.sin(t * 3.1) + t * 0.01
    pts.append((bm.verts.new((x - rw / 2, y, z)), bm.verts.new((x + rw / 2, y, z))))
for k in range(24):
    bm.faces.new((pts[k][0], pts[k][1], pts[k + 1][1], pts[k + 1][0]))
# notched end
tip = bm.verts.new((pts[-1][0].co.x + rw / 2, pts[-1][0].co.y + 0.006, 0.0005))
bm.to_mesh(me); bm.free(); me.materials.append(M_satin)
rib = bpy.data.objects.new("ribbon", me); S.collection.objects.link(rib); rib.parent = book
rib.modifiers.new("sol", "SOLIDIFY").thickness = 0.0004
for p in me.polygons: p.use_smooth = True

# ---------- the wine glass (lathe) ----------
def lathe(name, prof, mat, loc, steps=64):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); rings = []
    for (r, z) in prof:
        ring = [bm.verts.new((r * math.cos(2 * math.pi * s / steps), r * math.sin(2 * math.pi * s / steps), z)) for s in range(steps)]
        rings.append(ring)
    for a in range(len(rings) - 1):
        for s in range(steps):
            bm.faces.new((rings[a][s], rings[a][(s + 1) % steps], rings[a + 1][(s + 1) % steps], rings[a + 1][s]))
    bm.to_mesh(me); bm.free(); me.materials.append(mat)
    for p in me.polygons: p.use_smooth = True
    ob = bpy.data.objects.new(name, me); S.collection.objects.link(ob); ob.location = loc
    return ob
gl = (0.098, 0.15, 0.0)
outer = [(0.0001, 0.0), (0.036, 0.0), (0.037, 0.002), (0.034, 0.003), (0.006, 0.006), (0.0035, 0.012), (0.0032, 0.085), (0.006, 0.095), (0.022, 0.108),
         (0.038, 0.13), (0.044, 0.16), (0.042, 0.19), (0.037, 0.215), (0.0375, 0.216)]
inner = [(0.0365, 0.2155), (0.0412, 0.19), (0.043, 0.16), (0.037, 0.131), (0.021, 0.110), (0.004, 0.0985), (0.0001, 0.098)]
lathe("glass", outer + inner, M_glass, gl)
wine = [(0.0001, 0.0992), (0.0038, 0.0995), (0.0205, 0.1105), (0.0363, 0.1315), (0.0418, 0.155), (0.0001, 0.155)]
lathe("wine", wine, M_wine, gl)
# wine surface cap
me = bpy.data.meshes.new("cap"); bm = bmesh.new(); ring = [bm.verts.new((0.0418 * math.cos(2 * math.pi * s / 64), 0.0418 * math.sin(2 * math.pi * s / 64), 0.155)) for s in range(64)]
bm.faces.new(ring); bm.to_mesh(me); bm.free(); me.materials.append(M_wine)
cap = bpy.data.objects.new("cap", me); S.collection.objects.link(cap); cap.location = gl

# ---------- Meshy props ----------
def import_glb(name, target, loc, rot_z=0.0, lay_flat=False, size_axis="max"):
    p = os.path.join(MESHY, name + ".glb")
    if A.noprops or not os.path.exists(p): return None
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=p)
    new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new(name + "_root", None); S.collection.objects.link(root)
    for o in new:
        if o.parent is None: o.parent = root
    bpy.context.view_layer.update()
    meshes = [o for o in new if o.type == "MESH"]
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    dims = mx - mn
    print(name, "dims", tuple(round(d, 3) for d in dims))
    if lay_flat and dims.z > dims.y:
        root.rotation_euler = (math.radians(90), 0, 0)
        bpy.context.view_layer.update()
        pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
        mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        dims = mx - mn
    ref = {"max": max(dims), "z": dims.z}[size_axis]
    s = target / ref
    holder = bpy.data.objects.new(name + "_place", None); S.collection.objects.link(holder)
    root.parent = holder
    center = (mn + mx) / 2
    root.location = root.location - Vector((center.x, center.y, mn.z))
    holder.scale = (s, s, s); holder.location = loc; holder.rotation_euler = (0, 0, rot_z)
    bpy.context.view_layer.update()
    return holder, meshes

cand = import_glb("candles", 0.18, (-0.075, 0.21, 0.0), rot_z=math.radians(28), size_axis="max")
flames = []
if cand:
    holder, meshes = cand
    vs = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
    zt = max(v.z for v in vs)
    top = [v for v in vs if v.z > zt - 0.10]
    # find up to three candle tops: greedy local maxima in xy
    tops = []
    for v in sorted(top, key=lambda v: -v.z):
        if all((Vector((v.x, v.y)) - Vector((t.x, t.y))).length > 0.025 for t in tops):
            tops.append(v)
        if len(tops) == 3: break
    for t in tops:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1, location=(t.x, t.y, t.z + 0.012))
        f = bpy.context.active_object; f.scale = (0.0042, 0.0042, 0.0115); f.data.materials.append(M_flame)
        f.visible_shadow = False
        L = bpy.data.lights.new("candle", "POINT"); L.energy = 1.4; L.color = (1.0, 0.62, 0.34); L.shadow_soft_size = 0.004
        lo = bpy.data.objects.new("candle_light", L); S.collection.objects.link(lo); lo.location = (t.x, t.y, t.z + 0.014)
        flames.append(lo)
    print("flames", [tuple(round(c, 3) for c in t) for t in tops])
if not flames:
    for (x, y, z) in [(-0.13, 0.17, 0.17), (-0.10, 0.18, 0.13)]:
        L = bpy.data.lights.new("candle", "POINT"); L.energy = 2.6; L.color = (1.0, 0.56, 0.24); L.shadow_soft_size = 0.004
        lo = bpy.data.objects.new("candle_light", L); S.collection.objects.link(lo); lo.location = (x, y, z)
import_glb("rose", 0.105, (0.078, -0.15, 0.0), rot_z=math.radians(-35))
None if A.nomask else import_glb("mask", 0.12, (-0.072, -0.168, 0.0), rot_z=math.radians(18), lay_flat=True)

# ---------- light ----------
# warm glow wash from the candles onto the curtain, and a faint cool moon from upper right
Lw = bpy.data.lights.new("wash", "AREA"); Lw.energy = 0.12; Lw.size = 0.25; Lw.color = (1.0, 0.5, 0.25)
lw = bpy.data.objects.new("wash", Lw); S.collection.objects.link(lw); lw.location = (-0.2, 0.05, 0.35); lw.rotation_euler = (math.radians(-70), math.radians(-25), 0)
Lm = bpy.data.lights.new("moon", "AREA"); Lm.energy = 0.9; Lm.size = 0.8; Lm.color = (0.55, 0.62, 1.0)
lm = bpy.data.objects.new("moon", Lm); S.collection.objects.link(lm); lm.location = (0.5, -0.4, 0.9); lm.rotation_euler = (math.radians(35), math.radians(28), 0)
Lr = bpy.data.lights.new("rim", "AREA"); Lr.energy = 0.5; Lr.size = 0.3; Lr.color = (1.0, 0.6, 0.35)
lr = bpy.data.objects.new("rim", Lr); S.collection.objects.link(lr); lr.location = (0.25, 0.25, 0.22); lr.rotation_euler = (math.radians(-110), math.radians(30), 0)
Lk = bpy.data.lights.new("key", "AREA"); Lk.energy = 0.55; Lk.size = 0.35; Lk.color = (1.0, 0.62, 0.32)
lk = bpy.data.objects.new("key", Lk); S.collection.objects.link(lk); lk.location = (-0.12, 0.10, 0.30)
lk.rotation_euler = (Vector((0.0, -0.01, 0.0)) - Vector((-0.12, 0.10, 0.30))).to_track_quat("-Z", "Y").to_euler()
lk.visible_camera = False
for o in (lw, lm, lr): o.visible_camera = False
for o in (lw, lm): o.visible_glossy = False
for o in (lw, lm, lr, lk): o.visible_transmission = False
lr.visible_glossy = False
Lr.energy = 0.8
S.world = bpy.data.worlds.new("w"); S.world.use_nodes = True
S.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.006, 0.003, 0.003, 1)

# ---------- camera ----------
cam = bpy.data.cameras.new("cam"); co = bpy.data.objects.new("cam", cam); S.collection.objects.link(co); S.camera = co
if A.cam == "phone":
    cam.lens = 30; cam.sensor_fit = "VERTICAL"; cam.sensor_height = 36
    co.location = (0.0, -0.43, 0.34); target = Vector((0.0, 0.05, 0.035))
else:
    cam.lens = 31; cam.sensor_fit = "HORIZONTAL"; cam.sensor_width = 36; cam.shift_x = 0.17
    co.location = (0.0, -0.56, 0.39); target = Vector((0.0, 0.05, 0.05))
d = target - co.location
co.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
cam.dof.use_dof = True; cam.dof.aperture_fstop = 3.2
cam.dof.focus_distance = (Vector((0, -0.005, 0.02)) - co.location).length

# ---------- render ----------
rx, ry = map(int, A.res.split("x"))
S.render.engine = "CYCLES"; S.cycles.device = "CPU"; S.cycles.samples = A.samples
S.cycles.use_denoising = True
try: S.cycles.denoiser = "OPENIMAGEDENOISE"
except Exception: pass
S.cycles.max_bounces = 8; S.cycles.transmission_bounces = 8; S.cycles.volume_bounces = 1
S.cycles.caustics_reflective = False; S.cycles.caustics_refractive = False
S.render.resolution_x = rx; S.render.resolution_y = ry; S.render.resolution_percentage = 100
S.render.film_transparent = False
try:
    S.view_settings.view_transform = "AgX"; S.view_settings.look = "AgX - Punchy"
except Exception as e: print("look", e)
S.view_settings.exposure = -0.2
S.render.image_settings.file_format = "PNG"
S.render.filepath = A.out
if A.flames:
    import json
    from bpy_extras.object_utils import world_to_camera_view
    bpy.context.view_layer.update()
    pts = [world_to_camera_view(S, co, f.location) for f in flames]
    json.dump([[round(p.x, 4), round(1 - p.y, 4)] for p in pts], open(A.flames, "w"))
    print("flames on screen", [[round(p.x, 3), round(1 - p.y, 3)] for p in pts])
if A.blend: bpy.ops.wm.save_as_mainfile(filepath=A.blend)
if A.anim or A.endstill:
    # the opening: cover swings open while the camera pushes in over the signed page
    F = 32; S.frame_start = 1; S.frame_end = F; S.render.fps = 24
    focus = bpy.data.objects.new("focus", None); S.collection.objects.link(focus)
    page_c = book.matrix_world @ Vector((0.0, 0.0, BT))
    focus.location = (0.0, -0.005, 0.02); cam.dof.focus_object = focus
    if A.cam == "phone":
        end_loc = Vector((0.006, -0.135, 0.300)); end_tgt = page_c + Vector((0.0, 0.005, 0.0)); end_shift = 0.0
    else:
        end_loc = Vector((0.004, -0.185, 0.300)); end_tgt = page_c + Vector((0.0, 0.0, 0.0)); end_shift = 0.0
    start_loc = co.location.copy(); start_rot = co.rotation_euler.copy(); start_shift = cam.shift_x
    end_rot = (end_tgt - end_loc).to_track_quat("-Z", "Y").to_euler()
    def key(fr, loc, rot, shift, cover, fpos):
        S.frame_set(fr)
        co.location = loc; co.rotation_euler = rot; cam.shift_x = shift
        co.keyframe_insert("location"); co.keyframe_insert("rotation_euler"); cam.keyframe_insert("shift_x")
        hinge.rotation_euler = (0, -math.radians(cover), 0); hinge.keyframe_insert("rotation_euler")
        focus.location = fpos; focus.keyframe_insert("location")
    key(1, start_loc, start_rot, start_shift, 0, Vector((0.0, -0.005, 0.02)))
    key(24, start_loc.lerp(end_loc, 0.82), start_rot, start_shift * 0.2, 150, page_c)
    key(F, end_loc, end_rot, end_shift, 150, page_c)
    # rotation: blend through quaternions to avoid flips
    q0 = start_rot.to_quaternion(); q1 = end_rot.to_quaternion()
    for fr in (1, 24, F):
        S.frame_set(fr); t = {1: 0.0, 24: 0.8, F: 1.0}[fr]
        co.rotation_euler = q0.slerp(q1, t).to_euler(); co.keyframe_insert("rotation_euler")
    for fc in (co.animation_data.action.fcurves if hasattr(co.animation_data.action, "fcurves") else []):
        for kp in fc.keyframe_points: kp.interpolation = "BEZIER"; kp.easing = "AUTO"
    S.render.use_persistent_data = True
    if A.endstill:
        S.frame_set(F); S.render.filepath = A.out; bpy.ops.render.render(write_still=True)
    else:
        os.makedirs(A.anim, exist_ok=True); S.render.filepath = os.path.join(A.anim, "f####")
        bpy.ops.render.render(animation=True)
    print("rendered anim", A.anim or A.out)
    sys.exit(0)
bpy.ops.render.render(write_still=True)
print("rendered", A.out)

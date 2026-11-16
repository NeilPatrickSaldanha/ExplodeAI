"""Small helpers for building stage models in headless Blender.

Blender is Z-up and the viewer looks from -Y. The glTF exporter converts to Y-up for three.js.
Every model is built with its origin at the centre of its base.
A node that moves when the part is opened up carries a custom property "explode": [dx, dy, dz] in
three.js axes (x right, y up, z towards the viewer). It reaches three.js as object.userData.explode.
"""

import math
import os

import bpy
import numpy as np

_mats = {}


def lin(c):
    """sRGB 0-255 triple to linear RGBA."""
    out = []
    for v in c:
        s = v / 255
        out.append(s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _mats.clear()


def material(name, color, rough=0.6, metal=0.0, coat=0.0, emit=0.0):
    key = (name, color, rough, metal, coat, emit)
    if key in _mats:
        return _mats[key]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = lin(color)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if coat:
        b.inputs["Coat Weight"].default_value = coat
        b.inputs["Coat Roughness"].default_value = 0.08
    if emit:
        b.inputs["Emission Color"].default_value = lin(color)
        b.inputs["Emission Strength"].default_value = emit
    _mats[key] = m
    return m


def paper(color):
    return material("paper", color, rough=0.88)


def ink(color):
    return material("ink", color, rough=0.55)


def plastic(color):
    return material("plastic", color, rough=0.28, coat=0.6)


def link(obj, parent=None):
    if obj.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(obj)
    if parent is not None:
        obj.parent = parent


def empty(name, loc=(0, 0, 0), parent=None, explode=None):
    e = bpy.data.objects.new(name, None)
    e.location = loc
    link(e, parent)
    if explode:
        e["explode"] = list(explode)
    return e


def box(name, size, loc, mat, parent=None, bevel=0.0, rot=(0, 0, 0)):
    """A box of the given full size, centred on loc, with optional rounded edges."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        m = o.modifiers.new("bevel", "BEVEL")
        m.width = bevel
        m.segments = 3
        m.limit_method = "ANGLE"
    o.data.materials.append(mat)
    o.location = loc
    o.rotation_euler = rot
    if parent is not None:
        o.parent = parent
    return o


def cylinder(name, radius, depth, loc, mat, parent=None, rot=(0, 0, 0), verts=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=verts, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    if parent is not None:
        o.parent = parent
    return o


def text(name, body, size, loc, mat, parent=None, rot=(0, 0, 0), align="CENTER", depth=0.0006):
    """Printed text as a thin mesh. Default orientation lies flat, reading from the viewer."""
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = body
    curve.size = size
    curve.align_x = align
    curve.align_y = "CENTER"
    curve.extrude = depth
    curve.resolution_u = 3
    o = bpy.data.objects.new(name, curve)
    link(o)
    o.location = loc
    o.rotation_euler = rot
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.convert(target="MESH")
    o = bpy.context.object
    o.data.materials.clear()
    o.data.materials.append(mat)
    o.select_set(False)
    if parent is not None:
        o.parent = parent
    return o


def text_lines(prefix, origin, widths, gap, height, mat, parent=None, z=0.0):
    """Grey bars standing in for lines of body text, left-aligned from origin (x, y)."""
    out = []
    for i, w in enumerate(widths):
        x = origin[0] + w / 2
        y = origin[1] - i * gap
        out.append(box(f"{prefix}{i}", (w, height, 0.0008), (x, y, z), mat, parent))
    return out


def tile_color(v):
    """Diverging colour for one number in a vector: blue positive, orange negative, pale near zero."""
    from colors import NEG, POS, ZERO

    a = round(min(1.0, abs(v)) * 4) / 4  # nine shades in all, so the tiles share a few materials
    end = POS if v >= 0 else NEG
    return tuple(int(ZERO[i] + (end[i] - ZERO[i]) * a) for i in range(3))


def vector_values(seed, n):
    rng = np.random.default_rng(seed)
    return np.clip(rng.normal(0, 0.55, n), -1, 1)


def bounds(objs):
    import mathutils

    pts = []
    for o in objs:
        if o.type != "MESH":
            continue
        for c in o.bound_box:
            pts.append(o.matrix_world @ mathutils.Vector(c))
    xs, ys, zs = zip(*[(p.x, p.y, p.z) for p in pts])
    return (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))


STAND = (98, 106, 120)  # neutral slate: reads on both the navy and the cream background


def wedge(name, w, d, angle_deg, parent=None, mat=None):
    """A sloped board: front edge on the floor, rising towards the back at angle_deg. Returns the empty
    sitting at the centre of its top face, rotated to match, so items placed on it face the viewer."""
    import bmesh

    a = math.radians(angle_deg)
    cy, sz = d / 2 * math.cos(a), d * math.sin(a)
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    pts = [(-w / 2, -cy, 0), (w / 2, -cy, 0), (w / 2, cy, 0), (-w / 2, cy, 0), (w / 2, cy, sz), (-w / 2, cy, sz)]
    v = [bm.verts.new(p) for p in pts]
    for f in ((0, 1, 2, 3), (0, 5, 4, 1), (3, 2, 4, 5), (0, 3, 5), (1, 4, 2)):
        bm.faces.new([v[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    o = bpy.data.objects.new(name, mesh)
    link(o, parent)
    o.data.materials.append(mat or material("stand", STAND, rough=0.45, coat=0.2))
    top = empty(f"{name}_top", (0, 0, sz / 2 + 0.003), parent)
    top.rotation_euler = (a, 0, 0)
    return top


def stand(margin=0.05, height=0.03):
    """A slim slate base under the whole model, so it stands out on any background."""
    bpy.context.view_layer.update()
    (x0, x1), (y0, y1), (z0, z1) = bounds(list(bpy.context.scene.objects))
    w, d = x1 - x0 + 2 * margin, y1 - y0 + 2 * margin
    box("stand", (w, d, height), ((x0 + x1) / 2, (y0 + y1) / 2, z0 - height / 2), material("stand", STAND, rough=0.45, coat=0.2), bevel=0.012)


def settle():
    """Move the model so it rests on the floor (z = 0) and is centred on the origin in x and y."""
    bpy.context.view_layer.update()
    (x0, x1), (y0, y1), (z0, z1) = bounds(list(bpy.context.scene.objects))
    for o in bpy.context.scene.objects:
        if o.parent is None:
            o.location.x -= (x0 + x1) / 2
            o.location.y -= (y0 + y1) / 2
            o.location.z -= z0 - 0.001
    bpy.context.view_layer.update()


def optimise():
    """Apply modifiers, then merge meshes that share a parent and a material, so the browser draws few objects."""
    meshes = [o for o in bpy.context.scene.objects if o.type in ("MESH", "CURVE")]
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.convert(target="MESH")
    groups = {}
    for o in bpy.context.scene.objects:
        if o.type == "MESH" and o.data.materials:
            groups.setdefault((o.parent.name if o.parent else "", o.data.materials[0].name), []).append(o)
    for objs in groups.values():
        if len(objs) < 2:
            continue
        bpy.ops.object.select_all(action="DESELECT")
        for o in objs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        bpy.ops.object.join()
    bpy.ops.object.select_all(action="DESELECT")


def export(path):
    bpy.context.view_layer.update()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        export_apply=True,
        export_extras=True,
        export_yup=True,
    )
    (x0, x1), (y0, y1), (z0, z1) = bounds(list(bpy.context.scene.objects))
    # three.js size: width (x), height (z), depth (y)
    return round(x1 - x0, 3), round(z1 - z0, 3), round(y1 - y0, 3)


def render_preview(path, background, target=(0, 0, 0.12), dist=1.9, elev=34, samples=40):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 900
    scene.render.resolution_y = 640
    scene.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("w")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    hdr = os.path.join(bpy.utils.resource_path("LOCAL"), "datafiles", "studiolights", "world", "interior.exr")
    env.image = bpy.data.images.load(hdr)
    bg_light = nt.nodes.new("ShaderNodeBackground")
    bg_light.inputs["Strength"].default_value = 1.0
    bg_cam = nt.nodes.new("ShaderNodeBackground")
    bg_cam.inputs["Color"].default_value = lin(background)
    lp = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(env.outputs["Color"], bg_light.inputs["Color"])
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    nt.links.new(bg_light.outputs[0], mix.inputs[1])
    nt.links.new(bg_cam.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    # a ground that only catches shadows
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0))
    ground = bpy.context.object
    ground.is_shadow_catcher = True
    scene.render.film_transparent = False
    cam_data = bpy.data.cameras.new("cam")
    cam_data.lens = 50
    cam = bpy.data.objects.new("cam", cam_data)
    link(cam)
    e = math.radians(elev)
    cam.location = (target[0] + 0.25, target[1] - dist * math.cos(e), target[2] + dist * math.sin(e))
    direction = np.array(target) - np.array(cam.location)
    from mathutils import Vector

    cam.rotation_euler = Vector(direction).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(ground)
    bpy.data.objects.remove(cam)

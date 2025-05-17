import bpy, csv, pathlib
from mathutils import Vector  # only import what we use

# -------- settings ---------------------------------------------------------
DECIMALS = 6  # float precision
UNIT_SCALE = 100.0  # Blender metres → Unreal centimetres (set 1.0 if units match)

# ---------------------------------------------------------------------------

csv_headers = ["RowName", "Transform"]


def round_to_ue(number):
    return round(number, DECIMALS)


def make_transform_string(source_object):
    loc, rot, scale = source_object.matrix_world.decompose()
    loc *= UNIT_SCALE
    rot = rot.normalized()

    # To convert to Left-handed UE coords: Y and W are flipped in the rot, y is flipped in the loc
    loc.y *= -1
    rot.y *= -1
    rot.w *= -1

    return (
        f"(Rotation=(X={round_to_ue(rot.x):.6f},Y={round_to_ue(rot.y):.6f},Z={round_to_ue(rot.z):.6f},W={round_to_ue(rot.w):.6f}),"
        f"Translation=(X={round_to_ue(loc.x):.6f},Y={round_to_ue(loc.y):.6f},Z={round_to_ue(loc.z):.6f}),"
        f"Scale3D=(X={round_to_ue(scale.x):.6f},Y={round_to_ue(scale.y):.6f},Z={round_to_ue(scale.z):.6f}))"
    )


def make_object_row(source_object):
    bpy.context.view_layer.objects.active = source_object
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    return [source_object.name, make_transform_string(source_object)]


def export_object_transforms():
    selected_collection = bpy.context.collection
    if selected_collection is None:
        return

    # Blend could be unsaved; default to home dir in that case
    base_dir = pathlib.Path(bpy.data.filepath).parent if bpy.data.is_saved else pathlib.Path.home()

    clean_name = selected_collection.name.replace(" ", "_")

    csv_path = base_dir / f"{clean_name}.csv"

    selected_meshes = [o for o in selected_collection.objects if o.type == 'MESH']
    if not selected_meshes:
        print("Nothing to export: select at least one mesh and try again.")
        return

    selected_meshes = sorted(selected_meshes, key=lambda x: int(x.name.split("_")[-1]))

    rows = [csv_headers] + [make_object_row(obj) for obj in selected_meshes]

    # make sure the directory exists
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="") as fp:
        csv.writer(fp).writerows(rows)

    print(f"Saved {len(rows) - 1} transforms → {csv_path}")


# ---------------------------------------------------------------------------
export_object_transforms()

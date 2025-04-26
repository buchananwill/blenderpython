import bpy, csv, pathlib

# -------- settings ---------------------------------------------------------
DECIMALS   = 6        # float precision
UNIT_SCALE = 100.0    # Blender metres → Unreal centimetres (set 1.0 if units match)
CSV_PATH   = pathlib.Path(bpy.data.filepath).with_suffix(".ue5_transforms.csv")
# ---------------------------------------------------------------------------

csv_transform_headers = ["name", "qx", "qy", "qz", "qw", "tx", "ty", "tz", "sx", "sy", "sz"]

def make_object_row(source_object):
    # 1 · origin to geometry bounds
    bpy.context.view_layer.objects.active = source_object
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')  # docs

    # 2 · world-space TRS
    loc, rot, scale = source_object.matrix_world.decompose()
    loc *= UNIT_SCALE                # convert to cm
    rot = rot.normalized()           # ensure unit-length

    return [
        source_object.name,
        round(rot.x, DECIMALS), round(rot.y, DECIMALS),
        round(rot.z, DECIMALS), round(rot.w, DECIMALS),
        round(loc.x, DECIMALS), round(loc.y, DECIMALS), round(loc.z, DECIMALS),
        round(scale.x, DECIMALS), round(scale.y, DECIMALS), round(scale.z, DECIMALS)
    ]

def export_object_transforms():
    csv_transform_rows = [csv_transform_headers]
    mesh_objects = [selected_object for selected_object in bpy.context.selected_objects if selected_object.type == 'MESH']

    for source_object in mesh_objects:
        csv_transform_rows.append(make_object_row(source_object))

    # 4 · write CSV
    with CSV_PATH.open("w", newline="") as fp:
        csv.writer(fp).writerows(csv_transform_rows)

    print(f"Saved {len(csv_transform_rows) - 1} transforms → {CSV_PATH}")

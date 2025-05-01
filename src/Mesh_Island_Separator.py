import bpy
import bmesh
from contextlib import contextmanager
from typing import List

def duplicate_object(source: bpy.types.Object) -> bpy.types.Object:
    """Return a fully independent duplicate of *source*."""
    bpy.ops.object.select_all(action="DESELECT")
    source.select_set(True)
    bpy.context.view_layer.objects.active = source
    bpy.ops.object.duplicate(linked=False)
    print(bpy.context.active_object.name)
    return bpy.context.active_object


@contextmanager
def edit_mode(obj: bpy.types.Object):
    """Switch *obj* to Edit mode for the duration of the *with* block."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    try:
        yield
    finally:
        bpy.ops.object.mode_set(mode="OBJECT")

def put_islands_in_collection(source_name: str,
                              islands_list: List[bpy.types.Object]) -> None:
    """Link *islands* exclusively to a collection called `<source>_islands`."""
    target = f"{source_name}_islands"
    col = bpy.data.collections.get(target) or bpy.data.collections.new(target)
    if col.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(col)      # scene-root link :contentReference[oaicite:1]{index=1}

    for obj in islands_list:
        # link once
        if col not in obj.users_collection:
            col.objects.link(obj)                            # link API :contentReference[oaicite:2]{index=2}
        # unlink everywhere else
        for c in tuple(obj.users_collection):
            if c is not col:
                c.objects.unlink(obj)                        # unlink API :contentReference[oaicite:3]{index=3}

def split_islands_fast(source_object: bpy.types.Object) -> List[bpy.types.Object]:
    """C-path split: apply modifiers, loose-parts separate, return island list."""
    # 1 – freeze modifiers in one go
    bpy.context.view_layer.objects.active = source_object
    working_copy = duplicate_object(source_object)
    bpy.ops.object.convert(target='MESH', keep_original=False)        # convert = apply :contentReference[oaicite:4]{index=4}

    # 2 – split once in C
    with edit_mode(working_copy):
        bpy.ops.mesh.select_all(action='SELECT')                      # select all :contentReference[oaicite:5]{index=5}
        bpy.ops.mesh.separate(type='LOOSE')                           # one-shot split :contentReference[oaicite:6]{index=6}

    # 3 – objects now selected: first is empty residue, rest are islands
    islands_list = list(bpy.context.selected_objects)                       # selection unchanged :contentReference[oaicite:7]{index=7}


    # 4 – rename islands
    for i, obj in enumerate(islands_list):
        obj.name = f"{source_object.name}_island_{i}"

    return islands_list

# ---------------------------------------------------------------------
# Drive it on the current selection
# ---------------------------------------------------------------------
selected = bpy.context.selected_objects
if not selected:
    raise RuntimeError("Select at least one mesh object.")

for ob in selected:
    islands = split_islands_fast(ob)
    put_islands_in_collection(ob.name, islands)
print("Done.")

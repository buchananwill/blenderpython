import bpy
import bmesh
from contextlib import contextmanager
from typing import List

@contextmanager
def edit_mode(obj: bpy.types.Object):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    try:
        yield
    finally:
        bpy.ops.object.mode_set(mode="OBJECT")

def duplicate_object(source: bpy.types.Object) -> bpy.types.Object:
    """Return a fully independent duplicate of *source*."""
    bpy.ops.object.select_all(action="DESELECT")
    source.select_set(True)
    bpy.context.view_layer.objects.active = source
    bpy.ops.object.duplicate(linked=False)
    print(bpy.context.active_object.name)
    return bpy.context.active_object


def first_visible_vertex_index(obj) -> int | None:
    bm = bmesh.from_edit_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    vertex_index = next((vertex for vertex in bm.verts if not vertex.hide), None)
    return vertex_index.index if vertex_index else None

def select_connected_island(obj, vert_index: int):
    temp_mesh = bmesh.from_edit_mesh(obj.data)
    temp_mesh.verts.ensure_lookup_table()
    seed = temp_mesh.verts[vert_index]
    for vertex in temp_mesh.verts:
        if vertex == seed:
            vertex.select_set(True)
        else:
            vertex.select_set(False)

    bmesh.update_edit_mesh(obj.data)
    bpy.ops.mesh.select_linked(delimit=set())

def put_islands_in_collection(source_name: str,
                              islands: list[bpy.types.Object]) -> bpy.types.Collection:
    """
    Makes sure a collection called `<source_name>_islands` exists, link every
    island into it, and unlink them from the scene-root collection.
    Return the collection for further use.
    """
    target_name = f"{source_name}_islands"


    collection = (bpy.data.collections.get(target_name) or
                  bpy.data.collections.new(target_name))
    if collection.name not in bpy.context.scene.collection.children.keys():
        bpy.context.scene.collection.children.link(collection)

    for obj in islands:

        if obj.name not in collection.objects:
            collection.objects.link(obj)                         #

        for parent_collection in tuple(obj.users_collection):
            if parent_collection is not collection:
                parent_collection.objects.unlink(obj)

    return collection



# -----------------------------------------------------------------------------
#  Main API
# -----------------------------------------------------------------------------

def split_islands(source_object: bpy.types.Object) -> List[bpy.types.Object]:
    """Split every connected vertex island of *source_object* into its own
    object.

    The original object remains intact.  A hidden duplicate is used as a work
    surface.  Returns a list with references to all newly‑created island
    objects.
    """
    working_copy = duplicate_object(source_object)
    bpy.ops.object.convert(target='MESH', keep_original=False)
    island_objects: List[bpy.types.Object] = []

    while True:
        with edit_mode(working_copy):
            seed = first_visible_vertex_index(working_copy)
            if seed is None:
                break  # no geometry left → finished
            select_connected_island(working_copy, seed)
            bpy.ops.mesh.separate(type="SELECTED")

        # after *separate* the newborn object is active & in Object mode
        residue = bpy.context.selected_objects[0]
        new_island = bpy.context.selected_objects[-1]
        new_island.name = f"{source_object.name}_island_{len(island_objects)}"
        island_objects.append(new_island)

        # remove that island from the working copy so the next loop picks the
        # next component
        with edit_mode(working_copy):
            bpy.ops.mesh.delete(type="VERT")

    # The scratch duplicate is now empty; hide it to keep the Outliner clean
    bpy.data.objects.remove(working_copy)

    print(f"Generated {len(island_objects)} islands from '{source_object.name}'.")
    return island_objects


def separate_selected_objects():
    objects = bpy.context.selected_objects

    if not objects or len(objects) == 0:
        print("No objects selected")
        return

    for obj in objects:
        islands = split_islands(obj)
        put_islands_in_collection(obj.name, islands)


separate_selected_objects()
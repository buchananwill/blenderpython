import bpy, bmesh

print("hello")

def separate_object(obj):
    print(obj.name)
    bpy.ops.object.mode_set(mode='OBJECT')

    for o in bpy.data.objects:
        o.select_set(o == obj)

    bpy.ops.object.mode_set(mode='EDIT')
    mesh = bmesh.from_edit_mesh(obj.data)
    mesh.verts.ensure_lookup_table()

    if mesh.verts is None:
        return

    for v in mesh.verts:
        v.select_set(False)

    first_vert = mesh.verts[0]
    first_vert.select_set(True)
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.mesh.select_linked()





def separate_selected_objects():
    objects = bpy.context.selected_objects

    if not objects or len(objects) == 0:
        print("No objects selected")
        return

    for obj in objects:
        separate_object(obj)


separate_selected_objects()
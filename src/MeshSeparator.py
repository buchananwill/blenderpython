import bpy, bmesh, contextlib



def split_islands(source_object):
    
    bpy.ops.object.select_all(action='DESELECT')
    source_object.select_set(True)
    bpy.context.view_layer.objects.active = source_object
    bpy.ops.object.duplicate(linked=False)
    work_object = bpy.context.active_object
    bpy.ops.object.convert(target='MESH', keep_original=False)

    isl_id = 0                                           
    while True:
        
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(work_object.data)         
        bm.verts.ensure_lookup_table()                   

        
        seed = next((v for v in bm.verts if not v.hide), None)
        if seed is None:                                 
            break

        
        for v in bm.verts: v.select_set(False)
        seed.select_set(True)
        bmesh.update_edit_mesh(work_object.data)            
        bpy.ops.mesh.select_linked(delimit=set())        

        
        bpy.ops.mesh.separate(type='SELECTED')           
        new_island = bpy.context.selected_objects[-1]    
        new_island.name = f"{source_object.name}_island_{isl_id}"
        isl_id += 1

        
        bpy.context.view_layer.objects.active = work_object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='VERT')                 
        bpy.ops.object.mode_set(mode='OBJECT')           

    
    work_object.hide_set(True)                              

    print(f"Generated {isl_id} islands from '{source_object.name}'")






def separate_selected_objects():
    objects = bpy.context.selected_objects

    if not objects or len(objects) == 0:
        print("No objects selected")
        return

    for obj in objects:
        split_islands(obj)


separate_selected_objects()
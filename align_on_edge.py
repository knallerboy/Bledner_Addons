bl_info = {
    "name": "Align Object to Global Axis or Edge",
    "author": "linebyline",
    "version": (1, 1, 0),
    "blender": (4, 1, 1),
    "location": "Object > Align to Axis/Edge, Sidebar > LineByLine",
    "description": "Align an object by its active edge to a global axis or another object's edge",
    "category": "Object",
}

import bpy
import mathutils

def apply_rotation(obj):
    """Apply the object's current rotation as if it were baked into the mesh."""
    if obj.type == 'MESH':
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

def align_to_global_axis(obj, axis):
    if not obj:
        return
    
    apply_rotation(obj)  # Apply rotation before alignment
    
    # Find the active edge in edit mode
    mesh = obj.data
    edges = [e for e in mesh.edges if e.select]
    if not edges:
        print(f"No active edge selected in object '{obj.name}'.")
        return
    
    active_edge = edges[0]
    vert1 = mesh.vertices[active_edge.vertices[0]].co
    vert2 = mesh.vertices[active_edge.vertices[1]].co
    edge_vector = (vert2 - vert1).normalized()
    
    # Align the edge vector to the specified axis
    target_vector = mathutils.Vector((0, 0, 0))
    target_vector[axis] = 1.0
    rotation_matrix = edge_vector.rotation_difference(target_vector).to_matrix()
    
    # Apply rotation only
    obj.matrix_world = (
        mathutils.Matrix.Translation(obj.location) @
        rotation_matrix.to_4x4() @
        mathutils.Matrix.Diagonal(obj.scale).to_4x4()
    )

def align_to_another_edge(obj, target_obj):
    if not obj or not target_obj:
        return
    
    apply_rotation(obj)  # Apply rotation to source object before alignment
    apply_rotation(target_obj)  # Apply rotation to target object before alignment
    
    # Get active edge of source and target objects
    mesh = obj.data
    target_mesh = target_obj.data
    edges_src = [e for e in mesh.edges if e.select]
    edges_tgt = [e for e in target_mesh.edges if e.select]
    
    if not edges_src or not edges_tgt:
        print("Both objects need an active edge selected.")
        return
    
    active_edge_src = edges_src[0]
    active_edge_tgt = edges_tgt[0]
    
    vert_src1 = mesh.vertices[active_edge_src.vertices[0]].co
    vert_src2 = mesh.vertices[active_edge_src.vertices[1]].co
    edge_vector_src = (vert_src2 - vert_src1).normalized()
    
    vert_tgt1 = target_mesh.vertices[active_edge_tgt.vertices[0]].co
    vert_tgt2 = target_mesh.vertices[active_edge_tgt.vertices[1]].co
    edge_vector_tgt = (vert_tgt2 - vert_tgt1).normalized()
    
    rotation_matrix = edge_vector_src.rotation_difference(edge_vector_tgt).to_matrix()
    
    # Apply rotation only
    obj.matrix_world = (
        mathutils.Matrix.Translation(obj.location) @
        rotation_matrix.to_4x4() @
        mathutils.Matrix.Diagonal(obj.scale).to_4x4()
    )

# Operators
class OBJECT_OT_AlignGlobal(bpy.types.Operator):
    bl_idname = "object.align_global"
    bl_label = "Align to Global Axis"
    bl_options = {'REGISTER', 'UNDO'}
    
    axis: bpy.props.EnumProperty(
        items=[
            ('X', "X Axis", ""),
            ('Y', "Y Axis", ""),
            ('Z', "Z Axis", "")
        ],
        name="Axis",
        default='X'
    )
    
    def execute(self, context):
        selected_objects = context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected.")
            return {'CANCELLED'}
        
        axis_index = {'X': 0, 'Y': 1, 'Z': 2}[self.axis]
        for obj in selected_objects:
            if obj.type == 'MESH':  # Only align mesh objects
                align_to_global_axis(obj, axis_index)
            else:
                print(f"Skipping non-mesh object: {obj.name}")
        
        return {'FINISHED'}

class OBJECT_OT_AlignToEdge(bpy.types.Operator):
    bl_idname = "object.align_to_edge"
    bl_label = "Align to Edge of Another Object"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        objs = context.selected_objects
        if len(objs) != 2:
            self.report({'WARNING'}, "Please select two objects.")
            return {'CANCELLED'}
        
        active_obj = context.object
        target_obj = objs[0] if objs[1] == active_obj else objs[1]
        align_to_another_edge(active_obj, target_obj)
        return {'FINISHED'}

# Submenu
class OBJECT_MT_AlignSubmenu(bpy.types.Menu):
    bl_idname = "OBJECT_MT_align_submenu"
    bl_label = "Align to Axis/Edge"
    
    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_AlignGlobal.bl_idname, text="Align to Global X Axis").axis = 'X'
        layout.operator(OBJECT_OT_AlignGlobal.bl_idname, text="Align to Global Y Axis").axis = 'Y'
        layout.operator(OBJECT_OT_AlignGlobal.bl_idname, text="Align to Global Z Axis").axis = 'Z'
        layout.operator(OBJECT_OT_AlignToEdge.bl_idname, text="Align to Edge of Another Object")

# Sidebar Panel
class VIEW3D_PT_LineByLine(bpy.types.Panel):
    bl_label = "Align to Axis/Edge"
    bl_idname = "VIEW3D_PT_Align_to_Axis_or_Edge"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'linebyline'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Align Operations")
        layout.operator(OBJECT_OT_AlignGlobal.bl_idname, text="Align to Global X Axis").axis = 'X'
        layout.operator(OBJECT_OT_AlignGlobal.bl_idname, text="Align to Global Y Axis").axis = 'Y'
        layout.operator(OBJECT_OT_AlignGlobal.bl_idname, text="Align to Global Z Axis").axis = 'Z'
        layout.operator(OBJECT_OT_AlignToEdge.bl_idname, text="Align to Edge of Another Object")

# Add to Object menu
def menu_func(self, context):
    layout = self.layout
    layout.separator()
    layout.menu(OBJECT_MT_AlignSubmenu.bl_idname)

# Register
def register():
    bpy.utils.register_class(OBJECT_OT_AlignGlobal)
    bpy.utils.register_class(OBJECT_OT_AlignToEdge)
    bpy.utils.register_class(OBJECT_MT_AlignSubmenu)
    bpy.utils.register_class(VIEW3D_PT_LineByLine)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_AlignGlobal)
    bpy.utils.unregister_class(OBJECT_OT_AlignToEdge)
    bpy.utils.unregister_class(OBJECT_MT_AlignSubmenu)
    bpy.utils.unregister_class(VIEW3D_PT_LineByLine)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()

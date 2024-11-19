bl_info = {
    "name": "Add Empty at Selected Vertices",
    "blender": (4, 1, 1),
    "category": "Object",
    "author": "linebyline",
    "version": (1, 1, 0),
    "description": "Adds a Plain Axis empty at each selected vertex of selected mesh objects.",
}

import bpy

class AddEmptyAtVertexOperator(bpy.types.Operator):
    """Add an empty object at the position of selected vertices"""
    bl_idname = "object.add_empty_at_vertex"
    bl_label = "Add Empty at Vertex"
    
    def execute(self, context):
        selected_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
        
        # Iterate over selected objects
        for obj in selected_objects:
            # Ensure the object is in Object mode and has vertex selection
            if obj.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # Go through each selected vertex and add an empty at its position
            for vertex in obj.data.vertices:
                if vertex.select:  # If the vertex is selected
                    # Get the world position of the vertex
                    world_position = obj.matrix_world @ vertex.co
                    # Create the Empty object at the selected vertex position
                    bpy.ops.object.empty_add(type='PLAIN_AXES', location=world_position)
        
        return {'FINISHED'}


def add_empty_at_vertex_menu(self, context):
    layout = self.layout
    # Add a separator before the custom operator
    layout.separator()
    # Add the custom operator to the Shift+A > Empty menu
    layout.operator(AddEmptyAtVertexOperator.bl_idname, text="Empty at Selected Vertices")


def register():
    bpy.utils.register_class(AddEmptyAtVertexOperator)
    bpy.types.VIEW3D_MT_mesh_add.append(add_empty_at_vertex_menu)


def unregister():
    bpy.utils.unregister_class(AddEmptyAtVertexOperator)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_empty_at_vertex_menu)


if __name__ == "__main__":
    register()
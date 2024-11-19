bl_info = {
    "name": "Replace with Empty Plain Axis",
    "blender": (4, 1, 1),
    "category": "Object",
    "author": "linebyline",
    "version": (1, 1, 0),
    "description": "Replaces selected objects with an empty plain axis, copying location and rotation.",
}

import bpy

# Operator to replace the selected object(s) with an empty
class OBJECT_OT_replace_with_empty(bpy.types.Operator):
    bl_idname = "object.replace_with_empty"
    bl_label = "Replace with Empty Plain Axis"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = context.selected_objects
        if selected_objects:
            for obj in selected_objects:
                # Create an empty object
                empty = bpy.data.objects.new("Empty", None)
                context.collection.objects.link(empty)

                # Set location and rotation to match the original object
                empty.location = obj.location
                empty.rotation_euler = obj.rotation_euler

                # Remove the original object
                context.collection.objects.unlink(obj)
                bpy.data.objects.remove(obj)

            return {'FINISHED'}
        return {'CANCELLED'}

# Add the operator to the "W" object context menu
def menu_func(self, context):
    self.layout.operator(OBJECT_OT_replace_with_empty.bl_idname)

# Register and unregister functions
def register():
    bpy.utils.register_class(OBJECT_OT_replace_with_empty)
    bpy.types.VIEW3D_MT_object_context_menu.append(menu_func)  # Append to the "W" menu

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_replace_with_empty)
    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_func)  # Remove from the "W" menu

if __name__ == "__main__":
    register()
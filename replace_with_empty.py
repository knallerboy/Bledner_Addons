bl_info = {
    "name": "Replace with Empty Plain Axis",
    "blender": (4, 1, 1),
    "category": "Object",
    "author": "linebyline",
    "version": (1, 2, 0),
    "description": "Replaces selected objects with empty plain axis objects, copying location and rotation.",
    "support": "COMMUNITY",
}

import bpy

# Operator to replace the selected object(s) with empties
class OBJECT_OT_replace_with_empty(bpy.types.Operator):
    bl_idname = "object.replace_with_empty"
    bl_label = "Replace with Empty Plain Axis"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = context.selected_objects
        new_empties = []  # Store new empties to select them later

        if selected_objects:
            for obj in selected_objects:
                # Create an empty object
                empty = bpy.data.objects.new("Empty", None)
                context.collection.objects.link(empty)

                # Set location and rotation to match the original object
                empty.location = obj.location
                empty.rotation_euler = obj.rotation_euler

                # Add the new empty to the selection list
                new_empties.append(empty)

                # Remove the original object
                context.collection.objects.unlink(obj)
                bpy.data.objects.remove(obj)

            # Select all newly created empties
            bpy.ops.object.select_all(action='DESELECT')  # Deselect everything
            for empty in new_empties:
                empty.select_set(True)

            # Set the active object to the first empty
            context.view_layer.objects.active = new_empties[0]

            return {'FINISHED'}
        return {'CANCELLED'}

# Panel for the Tool Shelf
class OBJECT_PT_replace_with_empty_panel(bpy.types.Panel):
    bl_label = "Replace with Empty"
    bl_idname = "OBJECT_PT_replace_with_empty"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "linebyline"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_replace_with_empty.bl_idname, text="Replace with Empty")

# Add the operator to the "W" object context menu
def menu_func(self, context):
    self.layout.operator(OBJECT_OT_replace_with_empty.bl_idname)

# Register and unregister functions
def register():
    bpy.utils.register_class(OBJECT_OT_replace_with_empty)
    bpy.utils.register_class(OBJECT_PT_replace_with_empty_panel)
    bpy.types.VIEW3D_MT_object_context_menu.append(menu_func)  # Append to the "W" menu

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_replace_with_empty)
    bpy.utils.unregister_class(OBJECT_PT_replace_with_empty_panel)
    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_func)  # Remove from the "W" menu

if __name__ == "__main__":
    register()

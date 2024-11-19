bl_info = {
    "name": "Set Origin to Selected Vertex",
    "description": "Set the origin of each object to the average position of selected vertices in Object Mode.",
    "author": "linebyline",
    "version": (1, 18, 1),
    "blender": (4, 1, 1),
    "location": "Object > Set Origin",
    "category": "Object",
}

import bpy
import bmesh
from mathutils import Vector


# Addon Preferences for custom keybinding
class SetOriginAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    custom_key: bpy.props.StringProperty(
        name="Custom Key",
        description="Key to trigger the Set Origin operation",
        default="C"
    )
    use_shift: bpy.props.BoolProperty(
        name="Use Shift",
        description="Use Shift as a modifier",
        default=True
    )
    use_ctrl: bpy.props.BoolProperty(
        name="Use Ctrl",
        description="Use Ctrl as a modifier",
        default=True
    )
    use_alt: bpy.props.BoolProperty(
        name="Use Alt",
        description="Use Alt as a modifier",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "custom_key")
        layout.prop(self, "use_shift")
        layout.prop(self, "use_ctrl")
        layout.prop(self, "use_alt")


# Operator to set the origin based on selected vertices
class OBJECT_OT_SetOriginToSelectedVertex(bpy.types.Operator):
    """Set Origin to Last Selected Vertex or Average of Selected Vertices for Each Selected Object"""
    bl_idname = "object.set_origin_to_selected_vertex"
    bl_label = "Set Origin to Selected Vertex"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Ensure objects are selected and all are meshes
        return (context.selected_objects and 
                all(obj.type == 'MESH' for obj in context.selected_objects) and 
                context.object.mode == 'OBJECT')

    def set_origin_for_object(self, obj, context):
        """Set origin for a single object based on its selected vertices."""
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        # Get the object's mesh and selected vertices
        mesh = obj.data

        bm = bmesh.new()
        bm.from_mesh(mesh)

        selected_verts = [v for v in bm.verts if v.select]

        if not selected_verts:
            self.report({'WARNING'}, f"No vertices selected in object '{obj.name}'.")
            bm.free()
            return

        # Calculate the target position
        if len(selected_verts) == 1:
            target_pos = selected_verts[0].co
        else:
            target_pos = sum((v.co for v in selected_verts), Vector()) / len(selected_verts)

        # Convert to world space
        target_world_pos = obj.matrix_world @ target_pos

        # Set the origin to the calculated position
        context.scene.cursor.location = target_world_pos
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        bm.free()

    def execute(self, context):
        # Loop through each selected object
        selected_objects = context.selected_objects.copy()

        for obj in selected_objects:
            if obj.type == 'MESH':
                self.set_origin_for_object(obj, context)

        self.report({'INFO'}, "Origins updated for all selected objects.")
        return {'FINISHED'}
# Custom Menu for the shortcut
class VIEW3D_MT_SetOriginMenu(bpy.types.Menu):
    bl_label = "Set Origin Menu"
    bl_idname = "VIEW3D_MT_set_origin_custom"

    def draw(self, context):
        layout = self.layout

        if context.mode != 'OBJECT':
            layout.label(text="Operation not available in Edit Mode", icon='INFO')
            return

        layout.operator(OBJECT_OT_SetOriginToSelectedVertex.bl_idname, text="Origin to Selected Vertex")
        layout.separator()
        layout.label(text="Default Set Origin Options:")
        layout.operator("object.origin_set", text="Origin to Geometry").type = 'GEOMETRY_ORIGIN'
        layout.operator("object.origin_set", text="Origin to 3D Cursor").type = 'ORIGIN_CURSOR'
        layout.operator("object.origin_set", text="Origin to Center of Mass (Surface)").type = 'ORIGIN_CENTER_OF_MASS'
        layout.operator("object.origin_set", text="Origin to Center of Mass (Volume)").type = 'ORIGIN_CENTER_OF_VOLUME'


# Tool Panel
class VIEW3D_PT_SetOriginMenuPanel(bpy.types.Panel):
    """Custom Set Origin Panel"""
    bl_label = "Set Origin"
    bl_idname = "VIEW3D_PT_set_origin_custom"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_SetOriginToSelectedVertex.bl_idname, text="Origin to Selected Vertex")
        layout.separator()
        layout.label(text="Default Set Origin Options:")
        layout.operator("object.origin_set", text="Origin to Geometry").type = 'GEOMETRY_ORIGIN'
        layout.operator("object.origin_set", text="Origin to 3D Cursor").type = 'ORIGIN_CURSOR'
        layout.operator("object.origin_set", text="Origin to Center of Mass (Surface)").type = 'ORIGIN_CENTER_OF_MASS'
        layout.operator("object.origin_set", text="Origin to Center of Mass (Volume)").type = 'ORIGIN_CENTER_OF_VOLUME'


# Keymap registration
def keymap_func():
    addon_prefs = bpy.context.preferences.addons[__name__].preferences
    wm = bpy.context.window_manager
    keymaps = wm.keyconfigs.active.keymaps

    # Remove existing keymaps for this operator
    if "3D View" in keymaps:
        km = keymaps["3D View"].keymap_items
        for item in km:
            if item.idname == "wm.call_menu" and item.properties.name == "VIEW3D_MT_set_origin_custom":
                km.remove(item)

    # Add new keymap with user-defined keys
    if "3D View" in keymaps:
        km = keymaps["3D View"].keymap_items
        km.new(
            idname="wm.call_menu",
            type=addon_prefs.custom_key.upper(),
            value='PRESS',
            shift=addon_prefs.use_shift,
            ctrl=addon_prefs.use_ctrl,
            alt=addon_prefs.use_alt
        ).properties.name = "VIEW3D_MT_set_origin_custom"


def register():
    bpy.utils.register_class(SetOriginAddonPreferences)
    bpy.utils.register_class(OBJECT_OT_SetOriginToSelectedVertex)
    bpy.utils.register_class(VIEW3D_MT_SetOriginMenu)
    bpy.utils.register_class(VIEW3D_PT_SetOriginMenuPanel)
    keymap_func()


def unregister():
    bpy.utils.unregister_class(SetOriginAddonPreferences)
    bpy.utils.unregister_class(OBJECT_OT_SetOriginToSelectedVertex)
    bpy.utils.unregister_class(VIEW3D_MT_SetOriginMenu)
    bpy.utils.unregister_class(VIEW3D_PT_SetOriginMenuPanel)

    # Remove keymaps
    wm = bpy.context.window_manager
    if "3D View" in wm.keyconfigs.active.keymaps:
        km = wm.keyconfigs.active.keymaps["3D View"].keymap_items
        for item in km:
            if item.idname == "wm.call_menu" and item.properties.name == "VIEW3D_MT_set_origin_custom":
                km.remove(item)


if __name__ == "__main__":
    register()
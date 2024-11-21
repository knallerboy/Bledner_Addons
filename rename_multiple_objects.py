bl_info = {
    "name": "Rename Multiple Objects with Suffixes",
    "author": "linebyline",
    "version": (1, 2, 0),
    "blender": (4, 1, 1),
    "location": "View 3D > linebyline",
    "description": "Renames selected objects with a numerical suffix, additional suffixes, and custom suffix",
    "category": "Object",
}

import bpy

# Addon class to handle renaming
class OBJECT_OT_RenameMultipleObjects(bpy.types.Operator):
    bl_idname = "object.rename_multiple_objects"
    bl_label = "Rename Multiple Objects"
    bl_options = {'REGISTER', 'UNDO'}

    # Function to execute the renaming operation
    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        base_name = context.scene.rename_base_name  # Get the base name from the scene settings
        suffixes = []  # List to store selected suffixes

        # Check which suffixes are selected
        if context.scene.rename_suffix_col:
            suffixes.append("-col")
        if context.scene.rename_suffix_colonly:
            suffixes.append("-colonly")
        if context.scene.rename_suffix_convcol:
            suffixes.append("-convcol")
        if context.scene.rename_suffix_convcolonly:
            suffixes.append("-convcolonly")
        if context.scene.rename_suffix_noimp:
            suffixes.append("-noimp")
        
        # Custom suffix
        if context.scene.rename_suffix_custom_enabled:
            custom_suffix = context.scene.rename_suffix_custom
            if custom_suffix:
                suffixes.append(custom_suffix)
            else:
                self.report({'WARNING'}, "Custom suffix is empty!")
                return {'CANCELLED'}

        if not base_name:
            self.report({'WARNING'}, "Base name is empty!")
            return {'CANCELLED'}

        # Renaming selected objects
        for idx, obj in enumerate(selected_objects, start=1):
            # Construct the new name with the base name, numerical suffix, and selected additional suffixes
            name_parts = [base_name, f".{str(idx).zfill(3)}"] + suffixes
            new_name = "".join(name_parts)
            obj.name = new_name
            
        return {'FINISHED'}

# Panel to display the button, input field, checkboxes, and custom suffix input in the UI
class VIEW3D_PT_RenameMultipleObjects(bpy.types.Panel):
    bl_label = "Rename Multiple Objects"
    bl_idname = "VIEW3D_PT_rename_multiple_objects"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'linebyline'
    
    def draw(self, context):
        layout = self.layout
        
        # Input field to define the base name
        layout.prop(context.scene, "rename_base_name")
        
        # Checkboxes for suffix types
        layout.prop(context.scene, "rename_suffix_col")
        layout.prop(context.scene, "rename_suffix_colonly")
        layout.prop(context.scene, "rename_suffix_convcol")
        layout.prop(context.scene, "rename_suffix_convcolonly")
        layout.prop(context.scene, "rename_suffix_noimp")
        
        # Checkbox for custom suffix
        layout.prop(context.scene, "rename_suffix_custom_enabled")
        
        # Custom suffix input field (only shown if checkbox is enabled)
        if context.scene.rename_suffix_custom_enabled:
            layout.prop(context.scene, "rename_suffix_custom")
        
        # Button to trigger the renaming operator
        layout.operator("object.rename_multiple_objects", text="Rename Selected Objects")

# Define the properties for base name, suffixes, and custom suffix
def add_properties():
    bpy.types.Scene.rename_base_name = bpy.props.StringProperty(
        name="Base Name",
        description="Base name for renaming objects",
        default="Object"
    )
    
    bpy.types.Scene.rename_suffix_col = bpy.props.BoolProperty(
        name="-col",
        description="Append '-col' suffix",
        default=False
    )
    
    bpy.types.Scene.rename_suffix_colonly = bpy.props.BoolProperty(
        name="-colonly",
        description="Append '-colonly' suffix",
        default=False
    )
    
    bpy.types.Scene.rename_suffix_convcol = bpy.props.BoolProperty(
        name="-convcol",
        description="Append '-convcol' suffix",
        default=False
    )
    
    bpy.types.Scene.rename_suffix_convcolonly = bpy.props.BoolProperty(
        name="-convcolonly",
        description="Append '-convcolonly' suffix",
        default=False
    )
    
    bpy.types.Scene.rename_suffix_noimp = bpy.props.BoolProperty(
        name="-noimp",
        description="Append '-noimp' suffix",
        default=False
    )
    
    # Property for enabling custom suffix
    bpy.types.Scene.rename_suffix_custom_enabled = bpy.props.BoolProperty(
        name="Enable Custom Suffix",
        description="Enable the custom suffix field",
        default=False
    )
    
    # Custom suffix input field
    bpy.types.Scene.rename_suffix_custom = bpy.props.StringProperty(
        name="Custom Suffix",
        description="Enter a custom suffix",
        default=""
    )

# Registering the addon
def register():
    bpy.utils.register_class(OBJECT_OT_RenameMultipleObjects)
    bpy.utils.register_class(VIEW3D_PT_RenameMultipleObjects)
    add_properties()

# Unregistering the addon
def unregister():
    bpy.utils.unregister_class(OBJECT_OT_RenameMultipleObjects)
    bpy.utils.unregister_class(VIEW3D_PT_RenameMultipleObjects)
    del bpy.types.Scene.rename_base_name
    del bpy.types.Scene.rename_suffix_col
    del bpy.types.Scene.rename_suffix_colonly
    del bpy.types.Scene.rename_suffix_convcol
    del bpy.types.Scene.rename_suffix_convcolonly
    del bpy.types.Scene.rename_suffix_noimp
    del bpy.types.Scene.rename_suffix_custom_enabled
    del bpy.types.Scene.rename_suffix_custom

if __name__ == "__main__":
    register()

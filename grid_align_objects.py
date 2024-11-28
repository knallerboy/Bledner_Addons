bl_info = {
    "name": "Align to 2D Grid",
    "blender": (4, 1, 1),
    "category": "Object",
    "author": "linebyline",
    "version": (1, 1, 0),
    "description": "Align selected objects to a specified 2D grid with spacing",
    "support": "COMMUNITY",
}

import bpy
import math

class OBJECT_OT_AlignToGrid(bpy.types.Operator):
    bl_idname = "object.align_to_grid"
    bl_label = "Align to Grid"
    bl_options = {'REGISTER', 'UNDO'}

    grid_x: bpy.props.IntProperty(name="Columns", default=5, min=1)
    grid_y: bpy.props.IntProperty(name="Rows", default=5, min=1)
    spacing: bpy.props.FloatProperty(name="Spacing", default=2.0, min=0.1)
    auto_grid: bpy.props.BoolProperty(name="Auto Grid", default=True)

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        if len(selected_objects) == 0:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}

        # Automatically calculate grid size if Auto Grid is enabled
        if self.auto_grid:
            total_objects = len(selected_objects)
            self.grid_x = math.ceil(total_objects ** 0.5)  # Calculate columns based on square root
            self.grid_y = math.ceil(total_objects / self.grid_x)  # Calculate rows based on columns

        # Align each object to the grid with specified spacing
        for idx, obj in enumerate(selected_objects):
            # Calculate grid positions based on columns (x) and rows (y)
            col = idx % self.grid_x
            row = idx // self.grid_x

            # Apply spacing to X and Y positions
            grid_x_pos = col * self.spacing
            grid_y_pos = row * self.spacing

            obj.location.x = grid_x_pos
            obj.location.y = grid_y_pos
            obj.location.z = 0  # Keep objects aligned to the ground level (0)

        return {'FINISHED'}

class VIEW3D_PT_AlignToGridPanel(bpy.types.Panel):
    bl_label = "Align to 2D Grid"
    bl_idname = "VIEW3D_PT_align_to_grid"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'linebyline'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        align_tool = scene.align_to_grid_tool

        layout.prop(align_tool, "auto_grid")  # Add toggle for Auto Grid calculation

        # Disable grid_x and grid_y when Auto Grid is enabled
        if not align_tool.auto_grid:
            layout.prop(align_tool, "grid_x")
            layout.prop(align_tool, "grid_y")

        layout.prop(align_tool, "spacing")

        layout.operator("object.align_to_grid", text="Align Selected Objects")

class AlignToGridProperties(bpy.types.PropertyGroup):
    grid_x: bpy.props.IntProperty(name="Columns", default=5, min=1)
    grid_y: bpy.props.IntProperty(name="Rows", default=5, min=1)
    spacing: bpy.props.FloatProperty(name="Spacing", default=2.0, min=0.1)
    auto_grid: bpy.props.BoolProperty(name="Auto Grid", default=True)

def register():
    bpy.utils.register_class(OBJECT_OT_AlignToGrid)
    bpy.utils.register_class(VIEW3D_PT_AlignToGridPanel)
    bpy.utils.register_class(AlignToGridProperties)
    bpy.types.Scene.align_to_grid_tool = bpy.props.PointerProperty(type=AlignToGridProperties)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_AlignToGrid)
    bpy.utils.unregister_class(VIEW3D_PT_AlignToGridPanel)
    bpy.utils.unregister_class(AlignToGridProperties)
    del bpy.types.Scene.align_to_grid_tool

if __name__ == "__main__":
    register()

bl_info = {
    "name": "Random Manipulator",
    "author": "linebyline",
    "version": (1, 2, 0),
    "blender": (4, 1, 0),
    "location": "View3D > Tool Shelf",
    "description": "Randomly manipulate objects with rotation and movement",
    "category": "Object",
}

import bpy
import random
from math import radians

class RandomManipulatorOperator(bpy.types.Operator):
    """Randomly Rotate and Move Selected Objects"""
    bl_idname = "object.random_manipulator_operator"
    bl_label = "Random Manipulator"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene

        # Get user settings for rotation
        random_rotation_strength = scene.random_rotation_strength
        apply_rotation_x = scene.random_rotation_apply_x
        apply_rotation_y = scene.random_rotation_apply_y
        apply_rotation_z = scene.random_rotation_apply_z

        # Get user settings for movement
        move_strength_x = scene.random_move_strength_x
        move_strength_y = scene.random_move_strength_y
        move_strength_z = scene.random_move_strength_z

        for obj in context.selected_objects:
            if obj.type == 'MESH':
                # Apply random rotation
                if apply_rotation_x:
                    obj.rotation_euler.x += radians(random.uniform(-random_rotation_strength, random_rotation_strength))
                if apply_rotation_y:
                    obj.rotation_euler.y += radians(random.uniform(-random_rotation_strength, random_rotation_strength))
                if apply_rotation_z:
                    obj.rotation_euler.z += radians(random.uniform(-random_rotation_strength, random_rotation_strength))

                # Apply random movement
                obj.location.x += random.uniform(-move_strength_x, move_strength_x)
                obj.location.y += random.uniform(-move_strength_y, move_strength_y)
                obj.location.z += random.uniform(-move_strength_z, move_strength_z)

        return {'FINISHED'}

class RandomManipulatorPanel(bpy.types.Panel):
    """Creates a Panel in the Tool Shelf"""
    bl_label = "Random Manipulator"
    bl_idname = "OBJECT_PT_random_manipulator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Rotation settings
        layout.label(text="Random Rotation Settings")
        layout.prop(scene, "random_rotation_strength", text="Strength (°)")

        row = layout.row(align=True)
        row.prop(scene, "random_rotation_apply_x", text="X")
        row.prop(scene, "random_rotation_apply_y", text="Y")
        row.prop(scene, "random_rotation_apply_z", text="Z")

        # Movement settings
        layout.separator()
        layout.label(text="Random Movement Settings")
        layout.prop(scene, "random_move_strength_x", text="Strength X")
        layout.prop(scene, "random_move_strength_y", text="Strength Y")
        layout.prop(scene, "random_move_strength_z", text="Strength Z")

        # Apply button
        layout.separator()
        layout.operator("object.random_manipulator_operator", text="Apply Random Manipulation")

def register():
    bpy.utils.register_class(RandomManipulatorOperator)
    bpy.utils.register_class(RandomManipulatorPanel)

    # Rotation properties
    bpy.types.Scene.random_rotation_strength = bpy.props.FloatProperty(
        name="Rotation Strength",
        description="Maximum random rotation in degrees",
        default=30.0,
        min=0.0,
        max=360.0,
        step=0.01,
    )
    bpy.types.Scene.random_rotation_apply_x = bpy.props.BoolProperty(
        name="Apply Rotation X",
        description="Apply random rotation to the X axis",
        default=True,
    )
    bpy.types.Scene.random_rotation_apply_y = bpy.props.BoolProperty(
        name="Apply Rotation Y",
        description="Apply random rotation to the Y axis",
        default=True,
    )
    bpy.types.Scene.random_rotation_apply_z = bpy.props.BoolProperty(
        name="Apply Rotation Z",
        description="Apply random rotation to the Z axis",
        default=True,
    )

    # Movement properties
    bpy.types.Scene.random_move_strength_x = bpy.props.FloatProperty(
        name="Move Strength X",
        description="Maximum random movement along the X axis",
        default=1.0,
        min=0.0,
        max=10.0,
        step=0.001,
    )
    bpy.types.Scene.random_move_strength_y = bpy.props.FloatProperty(
        name="Move Strength Y",
        description="Maximum random movement along the Y axis",
        default=1.0,
        min=0.0,
        max=10.0,
        step=0.001,
    )
    bpy.types.Scene.random_move_strength_z = bpy.props.FloatProperty(
        name="Move Strength Z",
        description="Maximum random movement along the Z axis",
        default=1.0,
        min=0.0,
        max=10.0,
        step=0.001,
    )

def unregister():
    bpy.utils.unregister_class(RandomManipulatorOperator)
    bpy.utils.unregister_class(RandomManipulatorPanel)

    # Remove rotation properties
    del bpy.types.Scene.random_rotation_strength
    del bpy.types.Scene.random_rotation_apply_x
    del bpy.types.Scene.random_rotation_apply_y
    del bpy.types.Scene.random_rotation_apply_z

    # Remove movement properties
    del bpy.types.Scene.random_move_strength_x
    del bpy.types.Scene.random_move_strength_y
    del bpy.types.Scene.random_move_strength_z

if __name__ == "__main__":
    register()
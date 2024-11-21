import bpy
import random
import bmesh
from mathutils import noise

bl_info = {
    "name": "Cave Wall Generator",
    "blender": (4, 1, 1),
    "category": "Mesh",
    "author": "linebyline",
    "version": (1, 1, 5),
    "description": "Generate cave walls with control over randomness, erosion, veins, subdivision, size, and parabolic shape in both X and Y axes.",
}

class CaveWallOperator(bpy.types.Operator):
    bl_idname = "mesh.create_cave_wall"
    bl_label = "Create Cave Wall"
    bl_options = {'REGISTER', 'UNDO'}

    size: bpy.props.FloatProperty(
        name="Size",
        description="Controls the overall size of the cave wall",
        default=10.0,
        min=1.0,
        max=100.0,
    )

    subdivision: bpy.props.IntProperty(
        name="Subdivision",
        description="Number of subdivisions to add for detail",
        default=2,
        min=0,
        max=100,
    )

    parabolic_curve_x: bpy.props.FloatProperty(
        name="Parabolic Curve X",
        description="Controls the parabolic curvature along the X axis",
        default=0.01,
        min=-0.1,
        max=0.1,
    )

    parabolic_curve_y: bpy.props.FloatProperty(
        name="Parabolic Curve Y",
        description="Controls the parabolic curvature along the Y axis",
        default=0.01,
        min=-0.1,
        max=0.1,
    )

    randomize_values: bpy.props.BoolProperty(
        name="Randomize All",
        description="Randomize all values for a unique cave wall",
        default=False,
    )

    randomness: bpy.props.FloatProperty(
        name="Randomness",
        description="Controls the randomness of the wall's surface",
        default=0.5,
        min=0.0,
        max=1.0,
    )

    erosion: bpy.props.FloatProperty(
        name="Erosion",
        description="Simulates smoother erosion on the cave wall",
        default=1.0,
        min=0.0,
        max=10.0,
    )

    veins: bpy.props.FloatProperty(
        name="Veins",
        description="Controls the appearance of veins on the cave wall using a cellular noise pattern",
        default=1.0,
        min=0.0,
        max=2.0,
    )

    vein_tiling_x: bpy.props.FloatProperty(
        name="Vein Tiling X",
        description="Controls the tiling of the Voronoi texture on the X axis",
        default=1.0,
        min=0.1,
        max=5.0,
    )

    vein_tiling_y: bpy.props.FloatProperty(
        name="Vein Tiling Y",
        description="Controls the tiling of the Voronoi texture on the Y axis",
        default=1.0,
        min=0.1,
        max=5.0,
    )

    vein_depth: bpy.props.FloatProperty(
        name="Vein Depth",
        description="Controls how deep the veins are displaced",
        default=1.0,
        min=0.1,
        max=10.0,
    )

    def execute(self, context):
        if self.randomize_values:
            self.randomize_parameters()
            self.randomize_values = False  # Reset button to default state after action

        # Create and manipulate cave wall
        bpy.ops.mesh.primitive_plane_add(size=self.size, location=(0, 0, 0))
        obj = context.object
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')

        self.subdivide_plane(obj)
        self.apply_parabolic_shape(obj)
        self.apply_random_displacement(obj)
        self.generate_veins(obj)
        self.apply_erosion(obj)

        return {'FINISHED'}
    
    def subdivide_plane(self, obj):
        # Subdivide the plane mesh for more detail based on the subdivision property
        if self.subdivision > 0:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.subdivide(number_cuts=self.subdivision)
            bpy.ops.object.mode_set(mode='OBJECT')

    def apply_parabolic_shape(self, obj):
        # Apply parabolic curvature along both X and Y axes
        for v in obj.data.vertices:
            # Apply parabolic formula to Z, using X and Y for the curvature
            v.co.z = (v.co.x ** 2) * self.parabolic_curve_x + (v.co.y ** 2) * self.parabolic_curve_y

    def apply_random_displacement(self, obj):
        # Displace vertices randomly to create a bumpy cave wall
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)

        for v in bm.verts:
            # Apply randomness to all vertices using absolute coordinates
            displacement = random.uniform(-self.randomness, self.randomness)
            v.co.z += displacement  # Apply randomness along Z-axis

        bmesh.update_edit_mesh(obj.data)
        bpy.ops.object.mode_set(mode='OBJECT')

    def generate_veins(self, obj):
        # Generate veins using a cellular noise pattern (e.g. Voronoi) with X and Y tiling control
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)

        for v in bm.verts:
            # Compute a cellular noise pattern based on vertex coordinates with tiling control
            cellular_value = noise.noise((v.co.x * self.vein_tiling_x, v.co.y * self.vein_tiling_y, v.co.z * 0.1)) * self.veins
            if cellular_value > 0.1:  # Ensure veins are noticeable
                depth = cellular_value * self.vein_depth  # Use vein_depth to control how deep the veins are
                v.co.z -= depth  # Displace the vertex down to create a vein

        bmesh.update_edit_mesh(obj.data)
        bpy.ops.object.mode_set(mode='OBJECT')

    def apply_erosion(self, obj):
        # Apply erosion by smoothing vertex heights
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)

        # Create a mapping of vertex heights to smooth later
        heights = {v: v.co.z for v in bm.verts}
        smoothed_heights = {}

        for v in bm.verts:
            # Collect neighboring vertices
            connected_verts = [e.other_vert(v) for e in v.link_edges]

            # Average the heights of the vertex and its neighbors
            avg_height = (heights[v] + sum(heights[n] for n in connected_verts)) / (len(connected_verts) + 1)
            erosion_effect = avg_height * self.erosion

            # Store the smoothed height
            smoothed_heights[v] = avg_height - erosion_effect

        # Apply smoothed heights
        for v, new_z in smoothed_heights.items():
            v.co.z = new_z

        bmesh.update_edit_mesh(obj.data)
        bpy.ops.object.mode_set(mode='OBJECT')

    def randomize_parameters(self):
        # Randomize all parameters except size, subdivision, and parabolic curvature
        self.randomness = random.uniform(0.0, 1.0)
        self.erosion = random.uniform(0.0, 3.0)
        self.veins = random.uniform(0.0, 2.0)
        self.vein_tiling_x = random.uniform(0.1, 5.0)
        self.vein_tiling_y = random.uniform(0.1, 5.0)
        self.vein_depth = random.uniform(0.1, 3.0)


def menu_func(self, context):
    self.layout.separator()
    self.layout.operator(CaveWallOperator.bl_idname)

def register():
    bpy.utils.register_class(CaveWallOperator)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)

def unregister():
    bpy.utils.unregister_class(CaveWallOperator)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()

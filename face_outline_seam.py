bl_info = {
    "name": "Mark Outline of Selected Faces as Seams",
    "blender": (4, 1, 1),
    "category": "Mesh",
    "version": (1, 0, 1),
    "author": "linebyline",
    "description": "Marks the outline of selected faces as UV seams",
}

import bpy
import bmesh

def mark_face_outline_as_seams(context):
    obj = context.object
    if obj is None or obj.type != 'MESH':
        return {"CANCELLED"}
    
    # Get the bmesh for the object
    bm = bmesh.from_edit_mesh(obj.data)
    
    # Ensure we are working with face selection
    bm.edges.ensure_lookup_table()
    
    # Deselect all edges to ensure only the desired edges are marked
    for edge in bm.edges:
        edge.select = False
    
    # Mark boundary edges of selected faces as seams
    for face in bm.faces:
        if face.select:
            for edge in face.edges:
                if any(other_face.select for other_face in edge.link_faces) and sum(1 for other_face in edge.link_faces if other_face.select) == 1:
                    edge.seam = True
                    edge.select = True

    # Update the mesh
    bmesh.update_edit_mesh(obj.data)
    return {"FINISHED"}

class MESH_OT_mark_face_outline_seams(bpy.types.Operator):
    """Mark Outline of Selected Faces as Seams"""
    bl_idname = "mesh.mark_face_outline_seams"
    bl_label = "Mark Face Outline as Seams"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return mark_face_outline_as_seams(context)

def edge_menu_func(self, context):
    self.layout.separator()  # Add a separator
    self.layout.operator(
        MESH_OT_mark_face_outline_seams.bl_idname, 
        text="Mark Face Outline as Seams"
    )

def register():
    bpy.utils.register_class(MESH_OT_mark_face_outline_seams)
    bpy.types.VIEW3D_MT_edit_mesh_edges.append(edge_menu_func)

def unregister():
    bpy.utils.unregister_class(MESH_OT_mark_face_outline_seams)
    bpy.types.VIEW3D_MT_edit_mesh_edges.remove(edge_menu_func)

if __name__ == "__main__":
    register()
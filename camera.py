bl_info = {
    "name": "Camera From View",
    "author": "Paolo A.",
    "version": (1, 0, 0),
    "blender": (3, 3, 0),
    "location": "View3D > Add > Camera > Camera From View",
    "description": "Create a camera aligned with the current viewport",
    "warning": "",
    "doc_url": "",
    "category": "Camera",
}

import bpy
import math
from mathutils import Matrix

class VERTEXLAB_OT_camera_from_view(bpy.types.Operator):
    """Create a camera perfectly aligned with the current viewport view"""
    bl_idname = "vertexlab.camera_from_view"
    bl_label = "Camera From View"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Capture the current viewport state
        region_3d = context.space_data.region_3d
        view_matrix = region_3d.view_matrix.copy()

        # Generate a unique camera name
        camera_name = self.get_unique_camera_name()
        
        # Create camera with the appropriate settings
        camera_data = bpy.data.cameras.new(name=camera_name)
        camera_object = bpy.data.objects.new(name=camera_name, object_data=camera_data)
        
        # Link the camera to the active collection
        context.collection.objects.link(camera_object)

        # Position and orient the camera to match current view
        camera_object.matrix_world = view_matrix.inverted()
        
        # Make this the active camera for the scene
        context.scene.camera = camera_object

        # Select and make camera the active object
        bpy.ops.object.select_all(action='DESELECT')
        camera_object.select_set(True)
        context.view_layer.objects.active = camera_object
        
        self.report({'INFO'}, f"Camera '{camera_name}' created from current view")
        return {'FINISHED'}

    def get_unique_camera_name(self):
        """Generate a unique and professional camera name"""
        existing_cameras = [obj.name for obj in bpy.data.objects if obj.type == 'CAMERA']
        
        # Format: CAM_001, CAM_002, etc.
        index = 1
        while True:
            padded_index = str(index).zfill(3)
            name = f"CAM_{padded_index}"
            if name not in existing_cameras:
                return name
            index += 1

def menu_func_camera(self, context):
    """Add the operator to the Camera menu"""
    self.layout.operator(VERTEXLAB_OT_camera_from_view.bl_idname, 
                        text="Camera From View", 
                        icon='OUTLINER_OB_CAMERA')

def register():
    bpy.utils.register_class(VERTEXLAB_OT_camera_from_view)
    bpy.types.VIEW3D_MT_camera_add.append(menu_func_camera)
    
    # Register keyboard shortcut
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(
            VERTEXLAB_OT_camera_from_view.bl_idname, 
            type='C', 
            value='PRESS', 
            ctrl=True, 
            alt=True, 
            shift=True
        )

def unregister():
    # Remove keyboard shortcut
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.get('3D View')
        if km:
            for kmi in km.keymap_items:
                if kmi.idname == VERTEXLAB_OT_camera_from_view.bl_idname:
                    km.keymap_items.remove(kmi)
                    break
    
    bpy.types.VIEW3D_MT_camera_add.remove(menu_func_camera)
    bpy.utils.unregister_class(VERTEXLAB_OT_camera_from_view)

if __name__ == "__main__":
    register()
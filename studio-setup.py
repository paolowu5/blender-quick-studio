bl_info = {
    "name": "Quick Studio Setup",
    "author": "Paolo A.",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > QuickStudio",
    "description": "Set up a studio with camera and lights",
    "warning": "",
    "doc_url": "",
    "category": "Quick Studio",
}

import bpy
import math
from mathutils import Vector

def update_camera_track_toggle(self, context):
    if "CAM1" in bpy.data.objects:
        cam = bpy.data.objects["CAM1"]
        use_track = context.scene.quickstudio_use_camera_track
        
        if use_track:
            context.scene.quickstudio_camera_target = None
        
        for constraint in cam.constraints:
            if constraint.type == 'TRACK_TO':
                cam.constraints.remove(constraint)
        
        if use_track:
            if "CAM1 TRACK" not in bpy.data.objects:
                if "STUDIO" in bpy.data.collections:
                    studio_coll = bpy.data.collections["STUDIO"]
                else:
                    studio_coll = bpy.context.scene.collection
                
                cam_track = bpy.data.objects.new("CAM1 TRACK", None)
                cam_track.empty_display_type = 'SPHERE'
                cam_track.empty_display_size = 0.5
                studio_coll.objects.link(cam_track)
                cam_track.location = (0, 0, 0)
                cam_track.color = (0, 0, 1, 1.0)
                cam_track.show_name = True
            else:
                cam_track = bpy.data.objects["CAM1 TRACK"]
                
            constraint = cam.constraints.new(type='TRACK_TO')
            constraint.target = cam_track
            constraint.track_axis = 'TRACK_NEGATIVE_Z'
            constraint.up_axis = 'UP_Y'
        else:
            if "CAM1 TRACK" in bpy.data.objects:
                track_obj = bpy.data.objects["CAM1 TRACK"]
                bpy.data.objects.remove(track_obj, do_unlink=True)
            
            target = context.scene.quickstudio_camera_target
            if target:
                constraint = cam.constraints.new(type='TRACK_TO')
                constraint.target = target
                constraint.track_axis = 'TRACK_NEGATIVE_Z'
                constraint.up_axis = 'UP_Y'

def update_camera_target(self, context):
    if "CAM1" in bpy.data.objects and not context.scene.quickstudio_use_camera_track:
        cam = bpy.data.objects["CAM1"]
        target = context.scene.quickstudio_camera_target
        
        for constraint in cam.constraints:
            if constraint.type == 'TRACK_TO':
                cam.constraints.remove(constraint)
        
        if target is not None:
            constraint = cam.constraints.new(type='TRACK_TO')
            constraint.target = target
            constraint.track_axis = 'TRACK_NEGATIVE_Z'
            constraint.up_axis = 'UP_Y'

def update_light_target(self, context):
    lights_control = bpy.data.objects.get("LIGHTS CONTROL")
    if not lights_control:
        return
        
    target = context.scene.quickstudio_light_target
    
    for light_name in ["Key Light", "Fill Light", "Rim Light", "Back Light"]:
        light = bpy.data.objects.get(light_name)
        if not light:
            continue
            
        for constraint in light.constraints:
            if constraint.type == 'CHILD_OF':
                light.constraints.remove(constraint)
                
        if target is not None:
            constraint = light.constraints.new(type='CHILD_OF')
            constraint.target = target
            constraint.influence = 0.5
        else:
            if lights_control:
                constraint = light.constraints.new(type='CHILD_OF')
                constraint.target = lights_control
                constraint.influence = 0.5

def update_dof_target(self, context):
    if "CAM1" in bpy.data.objects:
        cam = bpy.data.objects["CAM1"]
        use_target = context.scene.quickstudio_dof_use_target
        target = context.scene.quickstudio_dof_target
        
        if use_target and target:
            cam.data.dof.focus_object = target
        else:
            cam.data.dof.focus_object = None

def update_background_color(self, context):
    world = context.scene.world
    if world:
        world.use_nodes = True
        if "Background" in world.node_tree.nodes:
            bg_node = world.node_tree.nodes["Background"]
            if context.scene.quickstudio_bg_transparent:
                context.scene.render.film_transparent = True
            else:
                context.scene.render.film_transparent = False
                bg_node.inputs[0].default_value = (
                    context.scene.quickstudio_bg_color[0],
                    context.scene.quickstudio_bg_color[1],
                    context.scene.quickstudio_bg_color[2],
                    1.0
                )

def update_background_transparent(self, context):
    update_background_color(self, context)
    
class QUICKSTUDIO_PT_panel(bpy.types.Panel):
    bl_label = "Quick Studio Setup"
    bl_idname = "QUICKSTUDIO_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QuickStudio'

    def draw(self, context):
        layout = self.layout
        
        studio_exists = "STUDIO" in bpy.data.collections
        
        if not studio_exists:
            row = layout.row()
            row.scale_y = 2.0
            row.operator("quickstudio.create_studio", text="CREATE STUDIO")
        else:
            box = layout.box()
            box.label(text="Camera Controls", icon='CAMERA_DATA')
            
            if "CAM1" in bpy.data.objects:
                cam = bpy.data.objects["CAM1"]
                
                row = box.row()
                row.prop(context.space_data, "lock_camera", text="Lock to View")
                
                col = box.column(align=True)
                col.prop(cam.data, "lens", text="Focal Length")
                col.prop(cam.data, "clip_start", text="Clip Start")
                col.prop(cam.data, "clip_end", text="Clip End")
                
                row = box.row()
                row.prop(context.scene, "quickstudio_use_camera_track", text="Use Camera Track", 
                         icon='EMPTY_DATA', 
                         toggle=True)
                
                if context.scene.quickstudio_use_camera_track:
                    if "CAM1 TRACK" in bpy.data.objects:
                        cam_track = bpy.data.objects["CAM1 TRACK"]
                        sub_box = box.box()
                        col = sub_box.column(align=True)
                        col.label(text="Camera Track Position:")
                        col.prop(cam_track, "location", text="")
                else:
                    row = box.row()
                    row.label(text="Camera Target:")
                    row.prop(context.scene, "quickstudio_camera_target", text="")
                
                row = box.row()
                row.prop(cam.data.dof, "use_dof", text="Depth of Field")
                if cam.data.dof.use_dof:
                    col = box.column(align=True)
                    row = col.row(align=True)
                    row.prop(context.scene, "quickstudio_dof_use_target", text="Use Target Object")
                    
                    if context.scene.quickstudio_dof_use_target:
                        col.prop(context.scene, "quickstudio_dof_target", text="Focus Object")
                    else:
                        col.prop(cam.data.dof, "focus_distance", text="Focus Distance")
                    
                    col.prop(cam.data.dof, "aperture_fstop", text="F-Stop")
            
            box = layout.box()
            box.label(text="Lights Control", icon='LIGHT')
            box.prop(context.scene, "quickstudio_light_target", text="Lights Target")
            
            if "LIGHTS CONTROL" in bpy.data.objects:
                lights_control = bpy.data.objects["LIGHTS CONTROL"]
                
                for light_prefix in ["Key", "Fill", "Rim", "Back"]:
                    box = layout.box()
                    prop_name = f"quickstudio_show_{light_prefix.lower()}_light"
                    row = box.row()
                    row.prop(context.scene, prop_name, icon='DOWNARROW_HLT' if getattr(context.scene, prop_name) else 'RIGHTARROW', icon_only=True, emboss=False)
                    row.label(text=f"{light_prefix} Light", icon='LIGHT_AREA')
                    
                    if getattr(context.scene, prop_name):
                        energy_prop = f"{light_prefix}_Energy"
                        if energy_prop in lights_control:
                            col = box.column(align=True)
                            col.prop(lights_control, f'["{energy_prop}"]', text="Energy")
                        
                        size_prop = f"{light_prefix}_Size"
                        size_y_prop = f"{light_prefix}_SizeY"
                        if size_prop in lights_control and size_y_prop in lights_control:
                            col = box.column(align=True)
                            col.prop(lights_control, f'["{size_prop}"]', text="Size X")
                            col.prop(lights_control, f'["{size_y_prop}"]', text="Size Y")
                        
                        col = box.column(align=True)
                        col.label(text="Color:")
                        
                        light_obj = bpy.data.objects.get(f"{light_prefix} Light")
                        if light_obj and light_obj.data:
                            col.prop(light_obj.data, "color", text="")
            
            box = layout.box()
            box.label(text="Background", icon='WORLD')
            row = box.row()
            row.prop(context.scene, "quickstudio_bg_transparent", text="Transparent Background")
            if not context.scene.quickstudio_bg_transparent:
                box.prop(context.scene, "quickstudio_bg_color", text="")
            
            row = layout.row()
            row.scale_y = 1.5
            row.operator("quickstudio.reset_studio", text="Reset Studio", icon='TRASH')

class QUICKSTUDIO_OT_create_studio(bpy.types.Operator):
    bl_idname = "quickstudio.create_studio"
    bl_label = "Create Studio"
    bl_description = "Create a camera and lighting setup"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        studio_collection = bpy.data.collections.new("STUDIO")
        bpy.context.scene.collection.children.link(studio_collection)
        
        layer_collection = bpy.context.view_layer.layer_collection
        for child in layer_collection.children:
            if child.name == "STUDIO":
                bpy.context.view_layer.active_layer_collection = child
                break
        
        view = context.space_data.region_3d
        view_matrix = view.view_matrix.copy()
        
        cam_data = bpy.data.cameras.new("CAM1")
        cam = bpy.data.objects.new("CAM1", cam_data)
        bpy.context.collection.objects.link(cam)
        
        cam.matrix_world = view_matrix.inverted()
        bpy.context.scene.camera = cam
        
        if hasattr(context.scene, "quickstudio_use_camera_track"):
            context.scene.quickstudio_use_camera_track = False
        
        lights_control = self.create_empty("LIGHTS CONTROL", location=(0, 0, 0), color=(1, 1, 0))
        
        target_point = Vector((0, 0, 0))
        
        key_pos = target_point + Vector((4, -4, 4))
        key_light = self.create_light("Key Light", 'AREA', energy=250, location=key_pos, target=target_point)
        self.add_light_constraint(key_light, lights_control)
        
        fill_pos = target_point + Vector((-4, -3, 2))
        fill_light = self.create_light("Fill Light", 'AREA', energy=100, location=fill_pos, target=target_point)
        self.add_light_constraint(fill_light, lights_control)
        
        rim_pos = target_point + Vector((2, 5, 3))
        rim_light = self.create_light("Rim Light", 'AREA', energy=80, location=rim_pos, target=target_point)
        self.add_light_constraint(rim_light, lights_control)
        
        back_pos = target_point + Vector((0, 1, 5))
        back_light = self.create_light("Back Light", 'AREA', energy=100, location=back_pos, target=target_point)
        self.add_light_constraint(back_light, lights_control)
        
        self.add_light_controls(lights_control, key_light, "Key")
        self.add_light_controls(lights_control, fill_light, "Fill")
        self.add_light_controls(lights_control, rim_light, "Rim")
        self.add_light_controls(lights_control, back_light, "Back")
        
        self.setup_light_drivers(key_light, lights_control, "Key")
        self.setup_light_drivers(fill_light, lights_control, "Fill")
        self.setup_light_drivers(rim_light, lights_control, "Rim")
        self.setup_light_drivers(back_light, lights_control, "Back")
        
        if context.scene.world is None:
            world = bpy.data.worlds.new("Studio World")
            context.scene.world = world
        
        world = context.scene.world
        world.use_nodes = True
        
        if "Background" in world.node_tree.nodes:
            bg_node = world.node_tree.nodes["Background"]
            bg_node.inputs[0].default_value = (
                context.scene.quickstudio_bg_color[0],
                context.scene.quickstudio_bg_color[1],
                context.scene.quickstudio_bg_color[2],
                1.0
            )
        
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        lights_control.select_set(True)
        bpy.context.view_layer.objects.active = lights_control
        
        self.report({'INFO'}, "Studio setup created successfully!")
        return {'FINISHED'}
    
    def create_empty(self, name, location=(0, 0, 0), color=(1, 1, 1)):
        empty = bpy.data.objects.new(name, None)
        empty.empty_display_type = 'SPHERE'
        empty.empty_display_size = 0.5
        bpy.context.collection.objects.link(empty)
        empty.location = location
        empty.color = (color[0], color[1], color[2], 1.0)
        empty.show_name = True
        return empty
    
    def create_camera(self, name, location=(0, 0, 0), rotation=(0, 0, 0)):
        cam_data = bpy.data.cameras.new(name)
        cam = bpy.data.objects.new(name, cam_data)
        bpy.context.collection.objects.link(cam)
        cam.location = location
        cam.rotation_euler = rotation
        bpy.context.scene.camera = cam
        return cam
    
    def create_light(self, name, light_type, energy=1000, location=(0, 0, 0), target=Vector((0, 0, 0))):
        light_data = bpy.data.lights.new(name=name, type=light_type)
        light_data.energy = energy
        
        if light_type == 'AREA':
            light_data.shape = 'RECTANGLE'
            light_data.size = 1
            light_data.size_y = 0.5
        
        light_obj = bpy.data.objects.new(name=name, object_data=light_data)
        bpy.context.collection.objects.link(light_obj)
        light_obj.location = location
        
        direction = target - Vector(location)
        rot_quat = direction.to_track_quat('-Z', 'Y')
        light_obj.rotation_euler = rot_quat.to_euler()
        
        return light_obj
    
    def add_light_constraint(self, light, target):
        constraint = light.constraints.new(type='CHILD_OF')
        constraint.target = target
        constraint.influence = 0.5
    
    def add_light_controls(self, control_empty, light, prefix):
        light_data = light.data
        control_empty[f"{prefix}_Energy"] = light_data.energy
        
        if light_data.type == 'AREA':
            control_empty[f"{prefix}_Size"] = light_data.size
            control_empty[f"{prefix}_SizeY"] = light_data.size_y
    
    def setup_light_drivers(self, light, control, prefix):
        light_data = light.data
        
        energy_driver = light_data.driver_add("energy").driver
        energy_driver.type = 'AVERAGE'
        var = energy_driver.variables.new()
        var.name = "energy"
        var.type = 'SINGLE_PROP'
        var.targets[0].id = control
        var.targets[0].data_path = f'["{prefix}_Energy"]'
        
        if light_data.type == 'AREA':
            size_driver = light_data.driver_add("size").driver
            size_driver.type = 'AVERAGE'
            var = size_driver.variables.new()
            var.name = "size"
            var.type = 'SINGLE_PROP'
            var.targets[0].id = control
            var.targets[0].data_path = f'["{prefix}_Size"]'
            
            size_y_driver = light_data.driver_add("size_y").driver
            size_y_driver.type = 'AVERAGE'
            var = size_y_driver.variables.new()
            var.name = "size_y"
            var.type = 'SINGLE_PROP'
            var.targets[0].id = control
            var.targets[0].data_path = f'["{prefix}_SizeY"]'

class QUICKSTUDIO_OT_reset_studio(bpy.types.Operator):
    bl_idname = "quickstudio.reset_studio"
    bl_label = "Reset Studio"
    bl_description = "Delete the studio setup"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        context.scene.quickstudio_camera_target = None
        context.scene.quickstudio_light_target = None
        context.scene.quickstudio_dof_target = None
        context.scene.quickstudio_dof_use_target = False
        context.scene.quickstudio_use_camera_track = False
        context.scene.quickstudio_bg_transparent = False
        
        context.scene.render.film_transparent = False
        
        if context.scene.world and "Background" in context.scene.world.node_tree.nodes:
            bg_node = context.scene.world.node_tree.nodes["Background"]
            bg_node.inputs[0].default_value = (0.05, 0.05, 0.05, 1.0)
        
        if "STUDIO" in bpy.data.collections:
            studio_collection = bpy.data.collections["STUDIO"]
            
            for obj in list(studio_collection.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            
            bpy.data.collections.remove(studio_collection)
            
            self.report({'INFO'}, "Studio has been reset")
        else:
            self.report({'WARNING'}, "No studio to reset")
            
        return {'FINISHED'}

classes = (
    QUICKSTUDIO_PT_panel,
    QUICKSTUDIO_OT_create_studio,
    QUICKSTUDIO_OT_reset_studio,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.quickstudio_show_camera = bpy.props.BoolProperty(
        name="Show Camera Settings",
        default=True
    )
    bpy.types.Scene.quickstudio_show_key_light = bpy.props.BoolProperty(
        name="Show Key Light Settings",
        default=False
    )
    bpy.types.Scene.quickstudio_show_fill_light = bpy.props.BoolProperty(
        name="Show Fill Light Settings",
        default=False
    )
    bpy.types.Scene.quickstudio_show_rim_light = bpy.props.BoolProperty(
        name="Show Rim Light Settings",
        default=False
    )
    bpy.types.Scene.quickstudio_show_back_light = bpy.props.BoolProperty(
        name="Show Back Light Settings",
        default=False
    )
    bpy.types.Scene.quickstudio_use_camera_track = bpy.props.BoolProperty(
        name="Use Camera Track",
        description="Create a null object to control the camera",
        default=False,
        update=update_camera_track_toggle
    )
    bpy.types.Scene.quickstudio_camera_target = bpy.props.PointerProperty(
        name="Camera Target",
        type=bpy.types.Object,
        update=update_camera_target
    )
    bpy.types.Scene.quickstudio_light_target = bpy.props.PointerProperty(
        name="Lights Target",
        type=bpy.types.Object,
        update=update_light_target
    )
    bpy.types.Scene.quickstudio_dof_target = bpy.props.PointerProperty(
        name="Focus Object",
        type=bpy.types.Object,
        update=update_dof_target
    )
    bpy.types.Scene.quickstudio_dof_use_target = bpy.props.BoolProperty(
        name="Use Target for DOF",
        default=False,
        update=update_dof_target
    )
    bpy.types.Scene.quickstudio_bg_color = bpy.props.FloatVectorProperty(
        name="Background Color",
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(0.05, 0.05, 0.05),
        update=update_background_color
    )
    bpy.types.Scene.quickstudio_bg_transparent = bpy.props.BoolProperty(
        name="Transparent Background",
        default=False,
        update=update_background_transparent
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.quickstudio_show_camera
    del bpy.types.Scene.quickstudio_show_key_light
    del bpy.types.Scene.quickstudio_show_fill_light
    del bpy.types.Scene.quickstudio_show_rim_light
    del bpy.types.Scene.quickstudio_show_back_light
    del bpy.types.Scene.quickstudio_use_camera_track
    del bpy.types.Scene.quickstudio_camera_target
    del bpy.types.Scene.quickstudio_light_target
    del bpy.types.Scene.quickstudio_dof_target
    del bpy.types.Scene.quickstudio_dof_use_target
    del bpy.types.Scene.quickstudio_bg_color
    del bpy.types.Scene.quickstudio_bg_transparent

if __name__ == "__main__":
    register()
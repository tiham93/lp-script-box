import bpy
import os

def open_file_in_text_editor(context, filepath):
    bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
    area = context.window_manager.windows[-1].screen.areas[0]
    area.ui_type = 'TEXT_EDITOR'
    area.spaces.active.show_region_ui = False
    script_name = bpy.path.basename(filepath)
    if bpy.data.texts.get(script_name):
        area.spaces.active.text = bpy.data.texts[script_name]
    else:
        bpy.ops.text.open(filepath=filepath)

class LP_OpenScriptView3D(bpy.types.Operator):
    bl_label = 'Open or Switch to Script in Editor'
    bl_idname = 'text.open_unique_view3d'
    bl_options = {'UNDO', 'REGISTER', 'INTERNAL'}
    filepath: bpy.props.StringProperty()
    
    def execute(self, context):
        open_file_in_text_editor(context, self.filepath)
        return {'FINISHED'}
    
class LP_RunScriptView3D(bpy.types.Operator):
    bl_label = 'Run Script in Editor'
    bl_idname = 'text.run_unique_view3d'
    bl_options = {'UNDO', 'REGISTER', 'INTERNAL'}
    filepath:bpy.props.StringProperty()
    
    def execute(self, context):
        script_name = bpy.path.basename(self.filepath)
        if not bpy.data.texts.get(script_name):
            bpy.ops.text.open(filepath=self.filepath)
        bpy.data.texts[script_name].as_module()       
        return {'FINISHED'}

class OsOpenDir(bpy.types.Operator):
    bl_label = 'Open Path in Explorer'
    bl_idname = 'wm.os_open_dir'
    bl_options = {'REGISTER'}
    filepath: bpy.props.StringProperty()
    def execute(self, context):
        if self.filepath != '':
            os.startfile(self.filepath)
        else:
            self.report({'ERROR'}, 'Empty File Path')
        return {'FINISHED'}  

classes = [
    OsOpenDir,
    LP_OpenScriptView3D,
    LP_RunScriptView3D,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

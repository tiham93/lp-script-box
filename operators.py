if 'bpy' in locals():
    import importlib
    if 'preferences' in locals():
        importlib.reload(preferences) #pyright:ignore
import bpy
from . import preferences
import os

def open_file_in_text_editor(context, filepath):
    bpy.ops.screen.userpref_show('INVOKE_DEFAULT') #type:ignore
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
    filepath: bpy.props.StringProperty() #type:ignore
    def execute(self, context):
        open_file_in_text_editor(context, self.filepath)
        return {'FINISHED'}

def edit_external(context, filepath):
    prefs = preferences.get_prefs(context)
    editor = prefs.editor_path
    if editor:
        from subprocess import Popen, CREATE_NEW_CONSOLE
        try:
            proc = Popen([editor, filepath], creationflags=CREATE_NEW_CONSOLE)
        except:
            return

class LPY_PT_EditExternal(bpy.types.Operator):
    bl_label = 'Edit With External Editor'
    bl_idname = 'lpy.edit_external'
    bl_options = {
        # 'INTERNAL',
        'REGISTER',
        'UNDO'
    }
    filepath: bpy.props.StringProperty() #type:ignore

    @classmethod
    def poll(cls, context):
        prefs = preferences.get_prefs(context)
        return prefs.editor_path

    def execute(self, context):
        edit_external(context, self.filepath)
        return {'FINISHED'}

class LP_RunScriptView3D(bpy.types.Operator):
    bl_label = 'Run Script in Editor'
    bl_idname = 'text.run_unique_view3d'
    bl_options = {'UNDO', 'REGISTER', 'INTERNAL'}
    filepath:bpy.props.StringProperty() #type:ignore
    def execute(self, context):
        global_namespace = {'__file__': self.filepath, '__name__': '__main__'}
        with open(self.filepath, 'rb') as file:
            exec(compile(file.read(), self.filepath, 'exec'), global_namespace)
        return {'FINISHED'}

class OsOpenDir(bpy.types.Operator):
    bl_label = 'Open Path in Explorer'
    bl_idname = 'wm.os_open_dir'
    bl_options = {'REGISTER'}
    filepath: bpy.props.StringProperty() #type:ignore
    def execute(self, context):
        if self.filepath != '':
            os.startfile(self.filepath)
        else:
            self.report({'ERROR'}, 'Empty File Path')
        return {'FINISHED'}  

class LPY_OT_PinScript(bpy.types.Operator):
    bl_label = 'Pin Active Script'
    bl_idname = 'lpy.pin_script'
    bl_options = {
        # 'INTERNAL',
        'REGISTER',
        'UNDO'
    }

    @classmethod
    def poll(cls, context):
        scripts = context.scene.lpy.lpy_group
        active = context.scene.lpy.lpy_active
        return ( active > -1 ) and ( active < len(scripts) )

    def execute(self, context):
        lpy = context.scene.lpy
        scripts = lpy.lpy_group
        active = lpy.lpy_active
        pinned = lpy.pinned

        item = pinned.add()
        item.name = scripts[active].name
        return {'FINISHED'}

class LPY_OT_RemovePinned(bpy.types.Operator):
    bl_label = 'Remove Pinned Script'
    bl_idname = 'lpy.remove_pinned'
    bl_options = {
        # 'INTERNAL',
        'REGISTER',
        'UNDO'
    }
    target_id: bpy.props.IntProperty() #type:ignore

    def execute(self, context):
        pinned = context.scene.lpy.pinned
        target_id = self.target_id
        if ( target_id > -1 ) and ( target_id < len(pinned) ):
            pinned.remove(target_id)
        else:
            self.report({'ERROR'}, 'Target pinned script does not exist')
            return {'CANCELLED'}
        return {'FINISHED'}

classes = [
    OsOpenDir,
    LP_OpenScriptView3D,
    LP_RunScriptView3D,
    LPY_OT_PinScript,
    LPY_OT_RemovePinned,
    LPY_PT_EditExternal,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

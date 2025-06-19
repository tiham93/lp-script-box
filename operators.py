if 'bpy' in locals():
    import importlib
    if 'preferences' in locals():
        importlib.reload(preferences) #pyright:ignore
    if 'utils' in locals():
        importlib.reload(utils) #pyright:ignore
    if 'fuzzy_finder' in locals():
        importlib.reload(fuzzy_finder) #pyright:ignore
import bpy
from . import preferences
from . import utils
from . import fuzzy_finder
import os

def edit_internal(context, filepath):
    bpy.ops.screen.userpref_show('INVOKE_DEFAULT') #type:ignore
    area = context.window_manager.windows[-1].screen.areas[0]
    area.ui_type = 'TEXT_EDITOR'
    area.spaces.active.show_region_ui = False
    script_name = bpy.path.basename(filepath)
    if bpy.data.texts.get(script_name):
        area.spaces.active.text = bpy.data.texts[script_name]
    else:
        bpy.ops.text.open(filepath=filepath)


def edit_external(context, filepath):
    prefs = preferences.get_prefs(context)
    editor = prefs.editor_path
    if editor:
        from subprocess import Popen, CREATE_NEW_CONSOLE
        try:
            Popen([editor, filepath], creationflags=CREATE_NEW_CONSOLE, cwd=prefs.script_dir)
        except Exception as e:
            print(f'Opening external editor FAILED: {e}')
            return


class LP_OT_Fetch(bpy.types.Operator):
    bl_label = 'Refresh LPY List'
    bl_idname = 'wm.lpy_list_fetch'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        utils.update_scripts(self, context)
        return {'FINISHED'}


class LPY_OT_MovePinned(bpy.types.Operator):
    bl_label = 'Reorder Pinned Scripts'
    bl_idname = 'lpy.reorder_pinned'
    bl_options = {
        'INTERNAL',
        'REGISTER',
        'UNDO'
    }
    id: bpy.props.IntProperty(default=0) #type:ignore
    new_id: bpy.props.IntProperty(default=0) #type:ignore

    def execute(self, context):
        pinned = context.scene.lpy.pinned
        if utils.check_col_bounds(self.id, pinned) and utils.check_col_bounds(self.new_id, pinned):
            pinned.move(self.id, self.new_id)
        return {'FINISHED'}


class LPY_OT_CallPinnedPie(bpy.types.Operator):
    bl_label = 'Call Pinned Scripts Pie Menu'
    bl_idname = 'wm.lpy_call_pinned'
    bl_options = {
        # 'INTERNAL',
        'REGISTER',
        'UNDO'
    }

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name='LPY_MT_PinnedScriptPie')
        return {'FINISHED'}


class LPY_OT_QuickRun(bpy.types.Operator):
    bl_label = 'Quick Run'
    bl_idname = 'wm.lpy_quick_run'
    bl_options = {
        # 'INTERNAL',
        'REGISTER',
        'UNDO'
    }

    @classmethod
    def poll(cls, context):
        prefs = preferences.get_prefs(context)
        return os.path.exists(prefs.script_dir)

    def script_suggestion_callback(self, context, edit_text):
        prefix = edit_text[0:3]
        if prefix in (':e ', ':x '):
            candidates = [prefix + file for file in os.listdir(preferences.get_prefs(context).script_dir) if file.endswith('.py')]
        else:
            candidates = [file for file in os.listdir(preferences.get_prefs(context).script_dir) if file.endswith('.py')]
        return fuzzy_finder.fuzzy_match_result(edit_text, candidates)

    script: bpy.props.StringProperty(default='', search=script_suggestion_callback) #pyright:ignore[reportInvalidTypeForm]

    def execute(self, context):
        # Prepare script_path
        if not self.script.strip():
            return {'CANCELLED'}
        prefs = preferences.get_prefs(context)
        prefix = self.script[0:3]
        if prefix in (':e ', ':x '):
            script_path = os.path.join(prefs.script_dir, self.script[3:])
        else:
            prefix = ''
            script_path = os.path.join(prefs.script_dir, self.script)
        if not script_path.endswith('.py'):
            script_path += '.py'

        # Create script_path file if the file doesn't exist
        existed = True
        if not os.path.exists(script_path):
            with open(script_path, 'w') as file:
                file.write('import bpy\nC = bpy.context\nD = bpy.data')
            utils.update_scripts(self, context)
            existed = False

        # Highlight script in UIList, report missing if not found
        scripts = context.scene.lpy.scripts
        for i in range(len(scripts)):
            if scripts[i].name == script_path:
                context.scene.lpy.lpy_active = i
                break
        else:
            self.report({'WARNING'}, 'Script not found in list!')

        match prefix:
            case ':e ':
                edit_internal(context, script_path)
                return {'FINISHED'}
            case ':x ':
                edit_external(context, script_path)
                return {'FINISHED'}
            case '':
                if not existed:
                    edit_internal(context, script_path)
                    return {'FINISHED'}
                # else
                # Run the script
                global_namespace = {"__file__": script_path, "__name__": "__main__"}
                with open(script_path, 'rb') as file:
                    exec(compile(file.read(), script_path, 'exec'), global_namespace)
                return {'FINISHED'}

    def draw(self, context):
        self.layout.label(text='- Input script name to run (create new if not found)')
        self.layout.label(text='- Prefix script name with :e to edit')
        self.layout.label(text='- Prefix script name with :x to edit with external editor')
        row = self.layout.row()
        row.activate_init = True
        row.prop(self, 'script', text='')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_popup(self, event)


class LPY_OT_EditInternal(bpy.types.Operator):
    bl_label = 'Open or Switch to Script in Editor'
    bl_idname = 'wm.lpy_edit_internal'
    bl_options = {'UNDO', 'REGISTER', 'INTERNAL'}
    filepath: bpy.props.StringProperty() #type:ignore
    def execute(self, context):
        edit_internal(context, self.filepath)
        return {'FINISHED'}


class LPY_OT_EditExternal(bpy.types.Operator):
    bl_label = 'Edit With External Editor'
    bl_idname = 'wm.lpy_edit_external'
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


class LPY_OT_RunScriptView3D(bpy.types.Operator):
    bl_label = 'Run Script in Editor'
    bl_idname = 'wm.lpy_run_script'
    bl_options = {'UNDO', 'REGISTER'}
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
    filepath: bpy.props.StringProperty(default='') #type:ignore

    def execute(self, context):
        lpy = context.scene.lpy
        pinned = lpy.pinned

        if self.filepath and os.path.exists(self.filepath):
            item = pinned.add()
            item.name = self.filepath
            return {'FINISHED'}
        return {'CANCELLED'}


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
    LP_OT_Fetch,
    LPY_OT_EditInternal,
    LPY_OT_RunScriptView3D,
    LPY_OT_PinScript,
    LPY_OT_RemovePinned,
    LPY_OT_EditExternal,
    LPY_OT_CallPinnedPie,
    LPY_OT_MovePinned,
    LPY_OT_QuickRun,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

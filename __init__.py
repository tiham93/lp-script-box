bl_info = {
    "name": "LP Script Box",
    "author": "Long Phan",
    "version": (1, 3, 0),
    "blender": (4, 4, 0),
    "location": "Text Editor > Sidebar > LP Scripts",
    "description": "Manage python scripts. List, create, run, edit python scripts conveniently with hotkey-friendly panels in 3D Viewport.",
    "category": "Scripting",
}

if 'bpy' in locals():
    import importlib
    if 'preferences' in locals():
        importlib.reload(preferences) #pyright:ignore
    if 'operators' in locals():
        importlib.reload(operators) #pyright:ignore
    if 'fuzzy_finder' in locals():
        importlib.reload(fuzzy_finder) #pyright:ignore
    if 'utils' in locals():
        importlib.reload(utils) #pyright:ignore
import bpy
from . import preferences
from . import operators
from . import fuzzy_finder
from . import utils
import os

@bpy.app.handlers.persistent #pyright:ignore
def fetch_handler(dummy=None):
    utils.update_lpy_group(None, bpy.context)

class VIEW3D_PT_LPScriptPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "LP Script Box"
    bl_category = "LP Tools"

    def draw(self, context):
        script_dir = preferences.get_prefs(context).script_dir
        if not os.path.exists(script_dir):
            self.layout.label(text='Script Directory')
            self.layout.row().prop(preferences.get_prefs(context), 'script_dir', text='')
        if not context.scene.lpy.lpy_group:
            self.layout.operator(operators.LP_OT_Fetch.bl_idname, text='Fetch')
        else:
            lpy = context.scene.lpy
            scripts = lpy.lpy_group
            active = lpy.lpy_active
            row = self.layout.row()
            row.template_list('LPY_UL_scripts', '', lpy, 'lpy_group', lpy, 'lpy_active', rows=5)

            row = self.layout.row()
            row.operator(operators.LPY_OT_EditInternal.bl_idname, text='Edit').filepath = scripts[active].name
            row.active_default = True
            row.operator(operators.LPY_OT_RunScriptView3D.bl_idname, icon='PLAY', text='Run').filepath = scripts[active].name
            self.layout.operator(operators.LPY_OT_EditExternal.bl_idname, text='Edit with External Editor').filepath = scripts[active].name
        self.layout.operator('wm.os_open_dir', text='Open Script Folder').filepath = os.path.dirname(preferences.get_prefs(context).script_dir)   

class LPY_PT_PinnedScripts(bpy.types.Panel):
    bl_label = 'Pinned Scripts'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'LP Tools'
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = 'VIEW3D_PT_LPScriptPanel'
    bl_order = 0

    def draw(self, context):
        pinned = context.scene.lpy.pinned
        index = 0
        for script in pinned:
            if os.path.exists(script.name):
                row = self.layout.row(align=True)
                script_name = os.path.basename(script.name)
                row.operator(operators.LPY_OT_RunScriptView3D.bl_idname, text=script_name).filepath = script.name
                op = row.operator(operators.LPY_OT_MovePinned.bl_idname, text='', icon='TRIA_UP')
                op.id = index
                op.new_id = index - 1
                op = row.operator(operators.LPY_OT_MovePinned.bl_idname, text='', icon='TRIA_DOWN')
                op.id = index
                op.new_id = index + 1
                row.operator(operators.LPY_OT_RemovePinned.bl_idname, text='', icon='REMOVE').target_id = index
            index += 1

        scripts = context.scene.lpy.lpy_group
        active = context.scene.lpy.lpy_active
        if ( active > -1 ) and ( active < len(scripts) ):
            self.layout.operator(operators.LPY_OT_PinScript.bl_idname, text='Pin Script', icon='ADD').filepath = scripts[active].name

class LPY_OT_QuickRun(bpy.types.Operator):
    bl_label = 'Quick Run'
    bl_idname = 'wm.lpy_quick_run'
    bl_options = {
        # 'INTERNAL',
        'REGISTER',
        'UNDO'
    }

    def script_suggestion_callback(self, context, edit_text):
        return fuzzy_finder.fuzzy_match_result(edit_text, [file for file in os.listdir(preferences.get_prefs(context).script_dir) if file.endswith('.py')])

    script: bpy.props.StringProperty(default='', search=script_suggestion_callback) #type:ignore

    @classmethod
    def poll(cls, context):
        prefs = preferences.get_prefs(context)
        return os.path.exists(prefs.script_dir)

    def execute(self, context):
        # Prepare script_path
        if not self.script.strip():
            return
        prefs = preferences.get_prefs(context)
        script_path = os.path.join(prefs.script_dir, self.script)
        if script_path[-3:] != '.py':
            script_path += '.py'

        # Create script_path file if the file doesn't exist
        if not os.path.exists(script_path):
            with open(script_path, 'w') as file:
                file.write('')
            operators.open_file_in_text_editor(context, script_path)
            return {'FINISHED'}

        # Highlight script in UIList, report missing if not found
        utils.update_lpy_group(self, context)
        scripts = context.scene.lpy.lpy_group
        for i in range(len(scripts)):
            if scripts[i].name == script_path:
                context.scene.lpy.lpy_active = i
                break
        else:
            self.report({'ERROR'}, 'Script does not exist!')
            return {'CANCELLED'}

        # Run the script
        global_namespace = {"__file__": script_path, "__name__": "__main__"}
        with open(script_path, 'rb') as file:
            exec(compile(file.read(), script_path, 'exec'), global_namespace)
        return {'FINISHED'}

    def draw(self, context):
        self.layout.label(text='Quick Run/Create Scripts')
        row = self.layout.row()
        row.activate_init = True
        row.prop(self, 'script', text='')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_popup(self, event)

class LPY_PT_QuickAccess(bpy.types.Panel):
    bl_label = 'Quick Access'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'LP Tools'
    # bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = 'VIEW3D_PT_LPScriptPanel'
    bl_order = 1

    def draw(self, context):
        self.layout.operator(LPY_OT_QuickRun.bl_idname, text='Quick Run/Create Scripts')
        self.layout.operator(operators.LPY_OT_CallPinnedPie.bl_idname, text='Pinned Scripts Pie Menu')

class LPY_MT_PinnedScriptPie(bpy.types.Menu):
    bl_label = 'Pinned Scripts'

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.scale_x = 1.1
        pie.scale_y = 1.5
        i = 0
        for script in context.scene.lpy.pinned:
            if i >= 8:
                break
            script_name = os.path.basename(script.name)
            row = pie.row(align=True)
            if i % 2 == 0:
                row.operator(operators.LPY_OT_EditInternal.bl_idname, text='', icon='TEXT').filepath = script.name
                row.operator(operators.LPY_OT_RunScriptView3D.bl_idname, text=script_name).filepath = script.name
            else:
                row.operator(operators.LPY_OT_RunScriptView3D.bl_idname, text=script_name).filepath = script.name
                row.operator(operators.LPY_OT_EditInternal.bl_idname, text='', icon='TEXT').filepath = script.name
            i += 1

class LPY_UL_scripts(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index): #pyright:ignore
        self.use_filter_show = True
        basename = bpy.path.basename(item.name)
        row = layout.row()
        row.label(text=basename)
        row.operator(operators.LPY_OT_PinScript.bl_idname, 
                     text='', 
                     icon='PINNED' if item.name in context.scene.lpy.pinned else 'UNPINNED'
        ).filepath = item.name

class LPYProps(bpy.types.PropertyGroup):
    lpy_group: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement) #type:ignore
    lpy_active: bpy.props.IntProperty(update=utils.update_lpy_group) #type:ignore
    pinned: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement) #type:ignore

classes = [
    LPY_UL_scripts,
    VIEW3D_PT_LPScriptPanel,
    LPYProps,
    LPY_PT_PinnedScripts,
    LPY_OT_QuickRun,
    LPY_PT_QuickAccess,
    LPY_MT_PinnedScriptPie,
]

def register():
    print('\n===========================')
    print('Registering LP Addon: lp_script_box')
    print(os.path.abspath(__file__))
    preferences.register()
    for cls in classes:
        bpy.utils.register_class(cls)
    operators.register()
    bpy.types.Scene.lpy = bpy.props.PointerProperty(type=LPYProps)
    bpy.app.handlers.load_post.append(fetch_handler)
    # fetch_handler()
    print('===========================\n')
    
def unregister():
    print('\n===========================')
    print('Unregistering LP Addon: lp_script_box')
    del bpy.types.Scene.lpy
    for cls in classes:
        bpy.utils.unregister_class(cls)
    operators.unregister()
    preferences.unregister()
    print('===========================\n')
        
if __name__ == '__main__':
    register()

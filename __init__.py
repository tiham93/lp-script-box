bl_info = {
    "name": "LP Script Box",
    "author": "Long Phan",
    "version": (1, 0, 0),
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
import bpy
from . import preferences
from . import operators
from . import fuzzy_finder
import os


class LP_OT_Fetch(bpy.types.Operator):
    bl_label = 'Refresh LPY List'
    bl_idname = 'lpy.list_fetch'
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        update_lpy_group(self, context)
        return {'FINISHED'}

def update_lpy_group(self, context):
    context.scene.lpy.lpy_group.clear()
    script_dir = preferences.get_prefs(context).script_dir
    if not os.path.exists(script_dir):
        try:
            self.report({'ERROR'}, 'Invalid script directory. Check addon preferences.')
            return
        except:
            return
    for t in os.listdir(script_dir):
        if (t != '__init__.py') and t.endswith('.py'):
            filepath = os.path.join(script_dir, t)
            item = context.scene.lpy.lpy_group.add()
            item.name = filepath

@bpy.app.handlers.persistent #pyright:ignore
def fetch_handler(dummy=None):
    context = bpy.context
    context.scene.lpy.lpy_group.clear()
    script_dir = preferences.get_prefs(context).script_dir
    if not os.path.exists(script_dir):
        return
    for t in os.listdir(script_dir):
        if t != '__init__.py' and t[-3:] == '.py':
            filepath = os.path.join(script_dir, t)
            item = context.scene.lpy.lpy_group.add()
            item.name = filepath

class VIEW3D_PT_LPScriptPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "LP Script Box"
    bl_category = "LP Tools"

    def draw(self, context):
        script_dir = preferences.get_prefs(context).script_dir
        if not script_dir:
            self.layout.row().prop(preferences.get_prefs(context), 'script_dir', text='Script Directory')
            return
        if not context.scene.lpy.lpy_group:
            self.layout.operator(LP_OT_Fetch.bl_idname, text='Fetch')
        else:
            lpy = context.scene.lpy
            scripts = lpy.lpy_group
            active = lpy.lpy_active
            row = self.layout.row()
            row.template_list('LPY_UL_scripts', '', lpy, 'lpy_group', lpy, 'lpy_active', rows=5)

            row = self.layout.row()
            row.operator('text.open_unique_view3d', text='Edit').filepath = scripts[active].name
            row.active_default = True
            row.operator('text.run_unique_view3d', icon='PLAY', text='Run').filepath = scripts[active].name
            self.layout.operator(operators.LPY_PT_EditExternal.bl_idname, text='Edit with External Editor').filepath = scripts[active].name
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
        scripts = context.scene.lpy.pinned
        index = 0
        for script in scripts:
            if os.path.exists(script.name):
                row = self.layout.row(align=True)
                script_name = os.path.basename(script.name)
                row.operator(operators.LP_RunScriptView3D.bl_idname, text=script_name).filepath = script.name
                row.operator(operators.LPY_OT_RemovePinned.bl_idname, text='', icon='REMOVE').target_id = index
            index += 1
        self.layout.operator(operators.LPY_OT_PinScript.bl_idname, text='Pin Script', icon='ADD')

class LPY_PT_QuickRun(bpy.types.Panel):
    bl_label = 'Quick Run'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'LP Tools'
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = 'VIEW3D_PT_LPScriptPanel'
    bl_order = 1

    def draw(self, context):
        self.layout.label(text='Quick Run/Create Script')
        row = self.layout.row()
        row.activate_init = True
        row.prop(context.scene.lpy, 'lpy_quick', text='')

class LPY_UL_scripts(bpy.types.UIList):
    use_filter_show = True
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index): #pyright:ignore
        basename = bpy.path.basename(item.name)
        layout.label(text=basename)

def script_suggestion_callback(self, context, edit_text):
    return fuzzy_finder.fuzzy_match_result(edit_text, os.listdir(preferences.get_prefs(context).script_dir))

def quick_run_callback(self, context):
    if not context.scene.lpy.lpy_quick.strip():
        return
    script_path = os.path.join(preferences.get_prefs(context).script_dir, context.scene.lpy.lpy_quick)
    if script_path[-3:] != '.py':
        script_path += '.py'
    if not os.path.exists(script_path):
        with open(script_path, 'w') as file:
            file.write('')
        operators.open_file_in_text_editor(context, script_path)
        return

    update_lpy_group(self, context)
    for i in range(len(context.scene.lpy.lpy_group)):
        if os.path.basename(context.scene.lpy.lpy_group[i].name) == context.scene.lpy.lpy_quick:
            context.scene.lpy.lpy_active = i
            break
    global_namespace = {"__file__": script_path, "__name__": "__main__"}
    with open(script_path, 'rb') as file:
        exec(compile(file.read(), script_path, 'exec'), global_namespace)

class LPYProps(bpy.types.PropertyGroup):
    lpy_group: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement) #type:ignore
    lpy_active: bpy.props.IntProperty(update=update_lpy_group) #type:ignore
    lpy_quick: bpy.props.StringProperty(search=script_suggestion_callback, update=quick_run_callback) #type:ignore
    pinned: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement) #type:ignore

classes = [
    LPY_UL_scripts,
    VIEW3D_PT_LPScriptPanel,
    LP_OT_Fetch,
    LPYProps,
    LPY_PT_PinnedScripts,
    LPY_PT_QuickRun,
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

# ruff: noqa: E402
bl_info = {
    "name": "LP Script Panel - testing",
    "author": "Sadist",
    "version": (0, 6, 0),
    "blender": (3, 6, 0),
    "location": "Text Editor > Sidebar > LP Scripts",
    "description": "Add panel to sidebar in text editor and 3d view for quick custom script access",
    "category": "Scripting",
}
if 'bpy' in locals():
    import importlib
    if 'preferences' in locals():
        importlib.reload(preferences)
    if 'operators' in locals():
        importlib.reload(operators)
    if 'fuzzy_finder' in locals():
        importlib.reload(fuzzy_finder)
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

@bpy.app.handlers.persistent
def fetch_handler(dummy=None):
    context = bpy.context
    context.scene.lpy.lpy_group.clear()
    script_dir = preferences.get_prefs(context).script_dir
    if not os.path.exists(script_dir):
        try:
            self.report({'ERROR'}, 'Invalid script directory. Check addon preferences.')
            return
        except:
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
            self.layout.template_list('LPY_UL_scripts', '', context.scene.lpy, 'lpy_group', context.scene.lpy, 'lpy_active', rows=5)
            row = self.layout.row()
            op = row.operator('text.open_unique_view3d', text='Open')
            op.filepath = context.scene.lpy.lpy_group[context.scene.lpy.lpy_active].name
            row.active_default = True
            op = row.operator('text.run_unique_view3d', icon='PLAY', text='')
            op.filepath = context.scene.lpy.lpy_group[context.scene.lpy.lpy_active].name
        op = self.layout.operator('wm.os_open_dir', text='Open Script Folder')
        op.filepath = os.path.dirname(preferences.get_prefs(context).script_dir)   
        self.layout.row().label(text='Quick Run:')
        self.layout.row().label(text='Enter new file name to create.')
        row = self.layout.row()
        row.activate_init = True
        row.prop(context.scene.lpy, 'lpy_quick', text='')

class LPY_UL_scripts(bpy.types.UIList):
    use_filter_show = True
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        self.use_filter_show = True
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
        print('not exist')
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
    lpy_group: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement)
    lpy_active: bpy.props.IntProperty(update=update_lpy_group)
    lpy_quick: bpy.props.StringProperty(search=script_suggestion_callback, update=quick_run_callback)

classes = [
    LPY_UL_scripts,
    VIEW3D_PT_LPScriptPanel,
    LP_OT_Fetch,
    LPYProps,
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

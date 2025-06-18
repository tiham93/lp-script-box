if 'bpy' in locals():
	import importlib
	if 'preferences' in locals():
		importlib.reload(preferences) #pyright:ignore
import bpy
from . import preferences
import os

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

def check_col_bounds(index, col):
    return (index > -1) and (index < len(col))

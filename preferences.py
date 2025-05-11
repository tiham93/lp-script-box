import bpy
import os

class LP_PF_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    script_dir: bpy.props.StringProperty(subtype='DIR_PATH')

    def read_json(self):
        import json
        json_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'preferences.json')
        if not os.path.exists(json_file_path):
            return
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            self['script_dir'] = data['script_dir']

    def write_json(self):
        import json
        json_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'preferences.json')
        data = {}
        data["script_dir"] = self.script_dir
        json_data = json.dumps(data, indent=4)
        with open(json_file_path,'w') as file:
            file.write(json_data)

    def draw(self, context):
        layout = self.layout
        if (not self.script_dir):
            self.read_json()
        layout.row().prop(self, 'script_dir', text='Script Directory')

def get_prefs(context) -> LP_PF_AddonPreferences:
    return context.preferences.addons[__package__].preferences

classes = [
	LP_PF_AddonPreferences
]
def register():
    for cls in classes:
       bpy.utils.register_class(cls)
    get_prefs(bpy.context).read_json()

def unregister():
    get_prefs(bpy.context).write_json()
    for cls in classes:
        bpy.utils.unregister_class(cls)

# SPDX-FileCopyrightText: 2024 Shape Keys Widget Authors
# SPDX-License-Identifier: GPL-3.0

import logging
log = logging.getLogger(__package__)

import bpy
from bpy.types import Operator


class ANIM_OT_insert_keyframes_shapekey_category(Operator):
    bl_idname = "anim.skw_insert_keyframes_shapekey_category"
    bl_label = "Keyframe Category"
    bl_description = "Add keyframes for the Shape Keys of the category with the selected cursor"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        """Called to finish this operator's action.
        """

        for selected_object in bpy.context.selected_objects:
            if "-cursor" in selected_object.name:
                category = "Eyes"
                mesh_obj = bpy.data.objects["GEO-face"]
                for key in mesh_obj.data.shape_keys.key_blocks:
                    if key.name.startswith("Eyes - "):
                        if not key.name.endswith("- Neutral"):
                            current_frame = context.scene.frame_current
                            key.keyframe_insert(data_path="value", frame=current_frame)

        return {'FINISHED'}



# Add-on Registration #############################################################################

classes = (
    ANIM_OT_insert_keyframes_shapekey_category,
    #ANIM_OT_insert_keyframes_all_shapekeys,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

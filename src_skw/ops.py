# SPDX-FileCopyrightText: 2024 Shape Keys Widget Authors
# SPDX-License-Identifier: GPL-3.0

import logging
log = logging.getLogger(__package__)

import bpy
from bpy.types import Operator


class ANIM_OT_insert_keyframes_shapekey_category(Operator):
    bl_idname = "anim.skw_insert_keyframes_shapekey_category"
    bl_label = "Keyframe Category"
    bl_description = "Add keyframes for the Shape Keys of the (selected?) category"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        """Called to finish this operator's action.
        """

        print("Added a keyframe for all Shape Keys in a category")

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

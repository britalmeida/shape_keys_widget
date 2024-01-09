# SPDX-FileCopyrightText: 2024 Shape Keys Widget Authors
# SPDX-License-Identifier: GPL-3.0

import logging
log = logging.getLogger(__package__)

import bpy
from bpy.props import BoolProperty
from bpy.types import Operator

def keyframe_sk_influence(cursor_obj, frame):
    name_parts = cursor_obj.name.split('-')
    if name_parts[1] != "skw":
        # Object does not have the naming convention of a Shape Key Widget Cursor.
        return

    mesh_col_name = name_parts[0]+"-model"
    category_name = name_parts[2].capitalize()+" - "

    mesh_obj = bpy.data.collections[mesh_col_name].objects[0]
    mesh_data = mesh_obj.data

    for key in mesh_data.shape_keys.key_blocks:
        if key.name.startswith(category_name) and not key.name.endswith("- Neutral"):
            key.keyframe_insert(data_path="value", frame=frame)


def keyframe_skw_cursor_pos(cursor_obj, frame):
    name_parts = cursor_obj.name.split('-')
    if name_parts[1] != "skw":
        # Object does not have the naming convention of a Shape Key Widget Cursor.
        return

    cursor_obj.keyframe_insert(data_path="location", frame=frame)


class ANIM_OT_insert_keyframes_shapekey_category(Operator):
    bl_idname = "anim.skw_insert_keyframes_shapekey_category"
    bl_label = "Keyframe Category"
    bl_description = "Add keyframes for the Shape Keys of the category with the selected cursor"
    bl_options = {'UNDO', 'REGISTER'}

    keyframe_values: BoolProperty(
        name="Keyframe SK Values",
        default=True,
    )
    keyframe_cursor: BoolProperty(
        name="Keyframe Cursor",
        default=True,
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        current_frame = context.scene.frame_current

        for selected_object in context.selected_objects:
            if selected_object.name.endswith("-cursor"):
                if self.keyframe_cursor:
                    keyframe_skw_cursor_pos(selected_object, current_frame)
                if self.keyframe_values:
                    keyframe_sk_influence(selected_object, current_frame)

        return {'FINISHED'}


class ANIM_OT_insert_keyframes_all_shapekeys(Operator):
    bl_idname = "anim.skw_insert_keyframes_all_categories"
    bl_label = "Keyframe All"
    bl_description = "Add keyframes for all Shape Keys in all widget categories for all characters"
    bl_options = {'UNDO', 'REGISTER'}

    keyframe_values: BoolProperty(
        name="Keyframe SK Values",
        default=True,
    )
    keyframe_cursor: BoolProperty(
        name="Keyframe Cursor",
        default=True,
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        current_frame = context.scene.frame_current

        for collection in bpy.data.collections:
            if collection.name.endswith("-cursor"):
                if self.keyframe_cursor:
                    keyframe_skw_cursor_pos(collection, current_frame)
                if self.keyframe_values:
                    keyframe_sk_influence(collection, current_frame)

        return {'FINISHED'}



# Add-on Registration #############################################################################

classes = (
    ANIM_OT_insert_keyframes_shapekey_category,
    ANIM_OT_insert_keyframes_all_shapekeys,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

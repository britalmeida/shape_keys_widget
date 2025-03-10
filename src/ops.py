# SPDX-FileCopyrightText: 2024-2025 Shape Keys Widget Authors
# SPDX-License-Identifier: GPL-3.0

import uuid

import bpy
from bpy.props import (
    StringProperty,
)
from bpy.types import Operator

from . import utils

import logging
log = logging.getLogger(__package__)


class OperatorAddShapeKeysWidgetCategory(Operator):
    bl_idname = "shape_keys_widget.add_shape_keys_widget_category"
    bl_label = "Add Shape Keys Widget Category"
    bl_description = "Create an arrangement of shape keys to show in the 3D View"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mesh

    def execute(self, context):
        """Called to finish this operator's action."""

        cats = context.mesh.shape_key_cats

        # Create the new category with a unique ID.
        new_cat = cats.add()
        new_cat.uuid = uuid.uuid4().hex
        # Generate a 'Object', 'Object.001' name unique for this mesh.
        default_name = new_cat.skw_name
        name = utils.create_unique_name(default_name, cats)
        new_cat.name = name
        new_cat.skw_name = name

        # Generate...
        # TODO

        return {'FINISHED'}


class OperatorDelShapeKeysWidgetCategory(Operator):
    bl_idname = "shape_keys_widget.del_shape_keys_widget_category"
    bl_label = "Delete Shape Keys Widget Category"
    bl_description = "Delete the arrangement of shape keys, but not the keys themselves"
    bl_options = {'REGISTER', 'UNDO'}

    cat_uuid: StringProperty(
        name="Category UUID",
        description="Identifier of the category to be deleted",
        default="",
    )

    @classmethod
    def poll(cls, context):
        return context.mesh

    def execute(self, context):
        """Called to finish this operator's action."""

        cats = context.mesh.shape_key_cats

        # Find the index of the category to remove.
        try:
            idx_to_remove = next((i for i, cat in enumerate(cats) if cat.uuid == self.cat_uuid))
        except StopIteration:
            log.error("Tried to remove a Shape Keys Widget Category that does not exist")
            return {'CANCELLED'}

        cat = cats[idx_to_remove]
        log.debug(f"Deleting Category '{cat.skw_name}'")

        # TODO tear down widget from rig.

        # Unlink the category.
        cats.remove(idx_to_remove)

        return {'FINISHED'}


# Add-on Registration #############################################################################

classes = (
    OperatorAddShapeKeysWidgetCategory,
    OperatorDelShapeKeysWidgetCategory,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

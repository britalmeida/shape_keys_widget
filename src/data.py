# SPDX-FileCopyrightText: 2024-2025 Shape Keys Widget Authors
# SPDX-License-Identifier: GPL-3.0

import logging
log = logging.getLogger(__package__)

import bpy
from bpy.app.handlers import persistent
from bpy.props import (
    CollectionProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import (
    AddonPreferences,
    PropertyGroup,
    ShapeKey,
)

from .. import ADDON_ID


class ShapeKeysWidgetShapeKey(PropertyGroup):
    """A reference to a regular Blender Shape Key with additional SKWidget data"""

    # Note: Blender's ShapeKey is a bpy struct, not an ID.
    # Therefore, it's not possible to have a PointerProperty to a ShapeKey or
    # to add custom props directly to it or to have a native asset preview in future.
    # The SKW ShapeKey is a PropertyGroup that:
    # - can be added to a Python CollectionProperty,
    # - holds additional data for the shape key's widget,
    # - holds a reference by name to the Blender SK.
    # Blender SKs are manually ordered which affects their blending order, best leave that be.
    # Blender SKs are named ["Basis", "Key 1", "Key 2",...] and names are enforced unique within
    # their Key if needed with "Key 1.001". Key is an ID.
    shape_key_name: StringProperty(
        name="Shape Key",
        description="Name of a Blender native Shape Key",
    )
    # TODO thumbnail


class ShapeKeysWidgetCategory(PropertyGroup):
    """A category of Shape Keys"""

    uuid: StringProperty(
        name="UUID",
        description="Unique identifier for this category",
        options={'HIDDEN'},
    )
    # PropertyGroup has 'name' already. Pick different to preserve options.
    skw_name: StringProperty(
        name="Name",
        description="Name to display in the UI",
        default="Category",
    )
    # TODO is_mirrored
    # TODO basis, keys
    shape_keys: CollectionProperty(
        type=ShapeKeysWidgetShapeKey,
        name="Shape Keys",
        description="Set of shape keys in a Shape Key Widget",
    )
    active_sk_idx: IntProperty(
        name="Active Shape Key",
        description="Index of the currently active shape key in the UIList",
        default=0,
    )
    # TODO layout
    num_cols: IntProperty(
        name="Columns",
        description="Number of columns to arrange the Shape Keys in",
        default=5,
    )
    # TODO camera setup


class ShapeKeysWidgetPreferences(AddonPreferences):
    bl_idname = ADDON_ID

    character_name: StringProperty(
        name="Character Name",
        description="Existing rig where to add new bone controls for the shape keys",
        default="claudia",
    )

    categories_str: StringProperty(
        name="Shape Key Categories",
        description="Comma separated list of Shape Key categories to generate controls for",
        default="Mouth, Eyes",
    )


# Patching named references #######################################################################

# RNA msg_bus subscription owner.
owner = object()


def msgbus_on_shapekey_rename(*args):
    # On any shape key name change, try to patch the name references.
    on_shapekey_rename()


def on_shapekey_rename(*args):
    # This will replace all shape keys with a mismatched name, not only the one that was renamed.
    # TODO Check for a better way to get the data change.
    context = bpy.context
    sel_shape_key_index = context.object.active_shape_key_index
    mesh = context.object.data
    print("Name change! ", sel_shape_key_index)

    shape_keys = mesh.shape_keys.key_blocks
    sk_names_in_mesh = shape_keys.keys()
    cats = mesh.shape_key_cats
    for cat in cats:
        for sk in cat.shape_keys:
            if sk.shape_key_name not in sk_names_in_mesh:
                sk.shape_key_name = shape_keys[sel_shape_key_index].name


@persistent
def on_undo(scene):
    # TODO - not sure I want to do this.
    print("Undo")
    on_shapekey_rename()


@persistent
def on_redo(scene):
    print("Redo")
    on_shapekey_rename()


def subscribe_to_shapekey_name_changes(scene):
    subscribe_to = (bpy.types.ShapeKey, "name")
    bpy.msgbus.subscribe_rna(
        key=subscribe_to,
        owner=owner,
        args=(),
        notify=msgbus_on_shapekey_rename,
    )


# Add-on Registration #############################################################################

classes = (
    ShapeKeysWidgetPreferences,
    ShapeKeysWidgetShapeKey,
    ShapeKeysWidgetCategory,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Mesh.shape_key_cats = CollectionProperty(
        type=ShapeKeysWidgetCategory,
        name="Shape Key Categories",
        description="Arrangements of Shape Keys for rig widgets",
    )

    subscribe_to_shapekey_name_changes(None)
    bpy.app.handlers.load_post.append(subscribe_to_shapekey_name_changes)
    # The RNA subscription doesn't trigger on undo/redo.
    bpy.app.handlers.undo_post.append(on_undo)
    bpy.app.handlers.redo_post.append(on_redo)


def unregister():
    bpy.app.handlers.redo_post.remove(on_redo)
    bpy.app.handlers.undo_post.remove(on_undo)
    bpy.app.handlers.load_post.remove(subscribe_to_shapekey_name_changes)
    bpy.msgbus.clear_by_owner(owner)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Mesh.shape_key_cats

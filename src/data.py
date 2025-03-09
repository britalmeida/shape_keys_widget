# SPDX-FileCopyrightText: 2024-2025 Shape Keys Widget Authors
# SPDX-License-Identifier: GPL-3.0

import logging
log = logging.getLogger(__package__)

import bpy
from bpy.props import (
    PointerProperty,
    StringProperty,
)
from bpy.types import (
    AddonPreferences,
    PropertyGroup,
)

from .. import ADDON_ID


class ShapeKeysWidgetCategory(PropertyGroup):
    """A category of Shape Keys."""

    uuid: StringProperty(
        name="UUID",
        description="Unique identifier for this category",
    )
    # PropertyGroup has 'name' already. Pick different to preserve options.
    sk_cat_name: StringProperty(
        name="Name",
        description="Name to display in the UI",
        default="Category",
    )
    # basis, keys


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


# Add-on Registration #############################################################################

classes = (
    ShapeKeysWidgetPreferences,
    ShapeKeysWidgetCategory,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.test_cat = PointerProperty(
        name="SK Category",
        type=ShapeKeysWidgetCategory,
        description="Test Cat",
    )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


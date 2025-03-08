# SPDX-FileCopyrightText: 2024-2025 Shape Keys Widget Authors
# SPDX-License-Identifier: GPL-3.0

import logging
log = logging.getLogger(__package__)

import bpy
from bpy.props import StringProperty
from bpy.types import AddonPreferences

from .. import ADDON_ID


class VIEW3D_ShapeKeysWidget_Preferences(AddonPreferences):
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
    VIEW3D_ShapeKeysWidget_Preferences,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


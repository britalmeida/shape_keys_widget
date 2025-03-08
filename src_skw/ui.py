# SPDX-FileCopyrightText: 2024-2025 Shape Keys Widget Authors
# SPDX-License-Identifier: GPL-3.0

import logging
log = logging.getLogger(__package__)

import bpy
from bpy.props import StringProperty
from bpy.types import AddonPreferences, Panel

from .. import ADDON_ID


class VIEW3D_PT_shape_key_widgets_setup(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Shape Key Widgets"
    bl_label = "Setup"
    bl_description = """Configuration of thumbnails and categories should go here."""

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        col = layout.column()
        col.label(text="WIP :)")


class VIEW3D_PT_shape_key_widgets_conversion(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Shape Key Widgets"
    bl_label = "Migration from SKS"
    bl_description = """Controls for converting an existing Shape Key Selector V1 setup to a rig"""

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        addon_prefs = context.preferences.addons[ADDON_ID].preferences
        char_name = addon_prefs.character_name

        col = layout.column()
        col.prop(addon_prefs, "character_name")
        col.prop(addon_prefs, "categories_str")

        op = col.operator("scene.convert_sks_to_skw")
        op.rig_name = "RIG-"+char_name
        op.geo_name = f"GEO-{char_name}-head"
        op.thumbs_collection_name = f"{char_name}-rig-widgets-thumbnails"
        op.wgts_collection_name = f"{char_name}-rig-widgets"
        op.categories_str = addon_prefs.categories_str


class VIEW3D_ShapeKeyWidgets_Preferences(AddonPreferences):
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
    VIEW3D_ShapeKeyWidgets_Preferences,
    VIEW3D_PT_shape_key_widgets_setup,
    VIEW3D_PT_shape_key_widgets_conversion,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

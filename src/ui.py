# SPDX-FileCopyrightText: 2024-2025 Shape Keys Widget Authors
# SPDX-License-Identifier: GPL-3.0

import logging
log = logging.getLogger(__package__)

import bpy
from bpy.types import Panel

from .. import ADDON_ID


class VIEW3D_PT_shape_key_widgets_setup(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Shape Keys Widget"
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
    bl_category = "Shape Keys Widget"
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


class DATA_PT_ShapeKeysWidgetCategories(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_order = 1  # It doesn't seem possible to place programmatically after 'Shape Keys'.
    # Blender's mesh panels are on 0, Viewport Display: 10, Animation: 999, Custom Props: 1000.
    bl_options = {'DEFAULT_CLOSED'}

    bl_label = "Shape Keys Widget Categories"
    bl_description = """Configuration of thumbnails and categories should go here."""

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type in {'MESH'}  # TODO: 'LATTICE', 'CURVE', 'SURFACE'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        # context.mesh
        cat = context.scene.test_cat

        col = layout.column()
        col.label(text="WIP panel for SK category config")
        col.prop(cat, "uuid")
        col.prop(cat, "sk_cat_name")


# Add-on Registration #############################################################################

classes = (
    VIEW3D_PT_shape_key_widgets_setup,
    VIEW3D_PT_shape_key_widgets_conversion,
    DATA_PT_ShapeKeysWidgetCategories,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

# SPDX-FileCopyrightText: 2024-2025 Shape Keys Widget Authors
# SPDX-License-Identifier: GPL-3.0

import logging
log = logging.getLogger(__package__)

import bpy
from bpy.types import (
    Panel,
    UIList,
)

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

    bl_label = "Shape Keys Widget"
    bl_description = """Configuration of thumbnails and categories should go here."""

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type in {'MESH'}  # TODO: 'LATTICE', 'CURVE', 'SURFACE'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        col = layout.column()

        # 'Add Category' button.
        row = col.row()
        row.operator("shape_keys_widget.add_shape_keys_widget_category")

        # List of categories.
        cats = context.mesh.shape_key_cats
        for i, cat in enumerate(cats):
            col.separator()
            box = col.box()
            row = box.row()

            # Color (empty space)
            split = row.split(factor=0.1)
            row = split.row(align=True)
            row.alignment = 'LEFT'

            # Icon
            row = split.row(align=True)
            split = row.split(factor=0.75)
            row = split.row(align=False)
            row.alignment = 'LEFT'
            row.label(text="", icon='SHAPEKEY_DATA')

            # Name
            row.label(text=cat.skw_name)

            # Edit button
            row = split.row(align=True)
            row.alignment = 'RIGHT'
            edit_op = row.operator(
                "shape_keys_widget.del_shape_keys_widget_category", text="", icon="GREASEPENCIL"
            )
            edit_op.cat_idx = i
            #edit_op.skw_name = cat.skw_name

            # Delete button
            row.operator(
                "shape_keys_widget.del_shape_keys_widget_category", text="", icon="X"
            ).cat_idx = i

            # Category Details
            row = box.row()
            split = row.split(factor=0.1)
            row = split.row(align=True)
            # Leave area under color empty, for alignment
            row = split.row(align=True)
            split = row.split(factor=1.0)

            row = box.row()
            # UI list
            num_rows = 5
            # fmt: off
            row.template_list(
                "DATA_UL_CategoryShapeKeys", "",  # Type and unique id.
                cat, "shape_keys",  # Pointer to the CollectionProperty.
                cat, "active_sk_idx",  # Pointer to the active identifier.
                rows=num_rows,
            )
            # fmt: on
            # Buttons on the right
            but_col = row.column(align=True)
            add_op = but_col.operator(
                "shape_keys_widget.add_shape_key_to_category", icon='ADD', text=""
            ).cat_idx = i
            del_op = but_col.operator(
                "shape_keys_widget.del_shape_key_from_category", icon='REMOVE', text=""
            ).cat_idx = i

            but_col.separator()

            move_up_op = but_col.operator(
                "shape_keys_widget.move_shape_key_in_category", icon='TRIA_UP', text=""
            )
            move_up_op.direction = 'UP'
            move_up_op.cat_idx = i

            move_down_op = but_col.operator(
                "shape_keys_widget.move_shape_key_in_category", icon='TRIA_DOWN', text=""
            )
            move_down_op.direction = 'DOWN'
            move_down_op.cat_idx = i

            row = box.row()
            tex = bpy.data.textures["Eyes - Closed"]
            img = bpy.data.images["Eyes - Closed.png"]
            row.template_preview(tex)

            row = box.row()
            row.use_property_decorate = False
            row.prop(cat, "num_cols")
            row = box.row()
            #row.prop_search(cat, "shape_key_name", cat, "shape_keys")
            #row.prop_search(cat, "shape_key_name", key, "key_blocks")
            # fmt: off
            row.use_property_decorate = False
            row.template_list(
                "DATA_UL_CategoryShapeKeys", "",  # Type and unique id.
                cat, "shape_keys",  # Pointer to the CollectionProperty.
                cat, "active_sk_idx",  # Pointer to the active identifier.
                rows=5,
                type='GRID', columns=cat.num_cols,
            )
            # fmt: on


class DATA_UL_CategoryShapeKeys(UIList):
    """UI List for the shape keys in a SKW category."""

    def draw_item(self, context, layout, data, item, icon, active_data, active_property,
                  index: int = 0, flt_flag: int = 0):
        sk = item

        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            # split = layout.split(factor=0.12)
            # row = split.row(align=True)
            # row.alignment = 'LEFT'
            # row.prop(sk, "color", text="", emboss=True)
            #
            # row = split.row(align=True)
            # row.alignment = 'LEFT'
            # row.prop(sk, "name", text="", emboss=False)

            layout.prop(sk, "shape_key_name", text="", emboss=False, icon_value=icon)


class DATA_UL_shape_keys(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property,
                  index: int = 0, flt_flag: int = 0):
        obj = active_data
        # key = data
        key_block = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.5, align=True)
            split.prop(key_block, "name", text="", emboss=False, icon_value=icon)
            row = split.row(align=True)
            row.emboss = 'NONE_OR_STATUS'
            row.alignment = 'RIGHT'
            if key_block.mute or (obj.mode == 'EDIT' and not (obj.use_shape_key_edit_mode and obj.type == 'MESH')):
                split.active = False
            if not item.id_data.use_relative:
                row.prop(key_block, "frame", text="")
            elif index > 0:
                row.prop(key_block, "value", text="")
            else:
                row.label(text="")
            row.prop(key_block, "mute", text="", emboss=False)
            row.prop(key_block, "lock_shape", text="", emboss=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            if key_block.name == "Basis":
                layout.label(text="Basis", icon_value=icon)
            else:
                img_name = f"{key_block.name}.png"
                tex_name = key_block.name
                try:
                    tex = bpy.data.textures[tex_name]
                except KeyError:
                    try:
                        img = bpy.data.images[img_name]
                        texture = bpy.data.textures.new(name=tex_name, type="IMAGE")
                        texture.image = img
                        texture.extension = 'CLIP'
                        tex = texture
                    except KeyError:
                        tex = bpy.data.textures["Eyes - Closed"]
                layout.template_preview(tex)


# Add-on Registration #############################################################################

classes = (
    VIEW3D_PT_shape_key_widgets_setup,
    VIEW3D_PT_shape_key_widgets_conversion,
    DATA_UL_CategoryShapeKeys,
    DATA_UL_shape_keys,
    DATA_PT_ShapeKeysWidgetCategories,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

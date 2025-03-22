# SPDX-FileCopyrightText: 2024-2025 Shape Keys Widget Authors
# SPDX-License-Identifier: GPL-3.0

import logging
log = logging.getLogger(__package__)

import bpy
from bpy.types import (
    Menu,
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
        col.separator()

        # List of categories.
        cats = context.mesh.shape_key_cats
        for i, cat in enumerate(cats):

            # Create context data so that buttons and operators can look up which
            # category they operate on. This is needed for menus while ops can also uses props.
            col.context_pointer_set("skw_category", cat)
            # The ID is an arbitrary string, unique per panel instance for collapse state.
            panel_id = f"skw_cat_{cat.skw_name}"

            # Make a panel layout (collapsible header row + body col).
            header, body = col.panel(panel_id, default_closed=False)

            def draw_cat_header():
                row = header.row(align=True)

                # Name
                row.prop(cat, "skw_name", text="")

                # Edit button
                row.menu("DATA_MT_CategoryMenu", text="", icon='DOWNARROW_HLT')

                # Delete button
                row.operator(
                    "shape_keys_widget.del_shape_keys_widget_category", text="", icon="X"
                ).cat_idx = i
            draw_cat_header()

            if body:  # If it is unfolded, draw.
                box = body.column()

                # Category Details
                def draw_cat_properties():
                    row = box.row()
                    split = row.split(factor=0.1)
                    row = split.row(align=True)
                    # Leave area under color empty, for alignment
                    row = split.row(align=True)
                    split = row.split(factor=1.0)
                draw_cat_properties()

                def draw_cat_sks():
                    row = box.row()
                    # UI list
                    num_rows = 5
                    # fmt: off
                    row.template_list(
                        "DATA_UL_CategoryShapeKeys", "",  # Type and unique id.
                        cat, "shape_keys",  # Pointer to the CollectionProperty.
                        cat, "active_sk_idx",  # Pointer to the active identifier.
                        rows=num_rows,
                        type='DEFAULT'
                    )
                    # fmt: on

                    # Buttons on the right
                    def draw_sk_op_buttons():
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
                    draw_sk_op_buttons()

                    row = box.row()
                    row.use_property_decorate = False
                    row.prop(cat, "num_cols")
                    row = box.row()
                    # row.prop_search(cat, "shape_key_name", cat, "shape_keys")
                    # row.prop_search(cat, "shape_key_name", key, "key_blocks")
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
                    draw_sk_op_buttons()
                draw_cat_sks()

                def draw_sk_properties():
                    row = box.row()

                    skw_sk = cat.shape_keys[cat.active_sk_idx]
                    img_name = f"{skw_sk.shape_key_name}.png"
                    preview_idx = 182  # hardcoded 'SHAPEKEY_DATA' icon fallback
                    if img_name in bpy.data.images:
                        img = bpy.data.images[img_name]
                        preview_idx = img.preview.icon_id
                    row.template_icon(preview_idx, scale=6.0)
                draw_sk_properties()


class DATA_UL_CategoryShapeKeys(UIList):
    """UI List for the shape keys in a SKW category"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_property,
                  index: int = 0, flt_flag: int = 0):
        skw_sk = item

        img_name = f"{skw_sk.shape_key_name}.png"
        preview_idx = 182  # hardcoded 'SHAPEKEY_DATA' icon fallback
        if img_name in bpy.data.images:
            img = bpy.data.images[img_name]
            preview_idx = img.preview.icon_id

        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            split = layout.split(factor=0.12)
            row = split.row(align=True)
            row.alignment = 'LEFT'
            #     tex_name = sk.shape_key_name
            #     tex = bpy.data.textures[tex_name]
            #     # row.template_preview(tex, preview_id="skw")
            #     tex.preview_ensure()

            row = split.row(align=True)
            # row.alignment = 'LEFT'
            # row.prop(sk, "name", text="", emboss=False)

            row.prop(skw_sk, "shape_key_name", text="", emboss=False, icon_value=preview_idx)
        else:  # GRID
            col = layout.column(align=True)
            col.prop(skw_sk, "shape_key_name", text="", emboss=False)
            col.template_icon(preview_idx, scale=2.5)


class DATA_MT_CategoryMenu(Menu):
    bl_label = "Shape Key Category Specials"

    def draw(self, context):
        layout = self.layout

        # cat = context.skw_category

        layout.operator("shape_keys_widget.mute_shape_keys_in_category", icon='CHECKBOX_DEHLT', text="Mute All").action = 'MUTE'
        layout.operator("shape_keys_widget.mute_shape_keys_in_category", icon='CHECKBOX_HLT', text="Unmute All").action = 'UNMUTE'
        # TODO lock and clear values for all sks in cat
        # layout.separator()
        # layout.operator("object.shape_key_lock", icon='LOCKED', text="Lock All").action = 'LOCK'
        # layout.operator("object.shape_key_lock", icon='UNLOCKED', text="Unlock All").action = 'UNLOCK'


# Add-on Registration #############################################################################

classes = (
    VIEW3D_PT_shape_key_widgets_setup,
    VIEW3D_PT_shape_key_widgets_conversion,
    DATA_MT_CategoryMenu,
    DATA_UL_CategoryShapeKeys,
    DATA_PT_ShapeKeysWidgetCategories,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

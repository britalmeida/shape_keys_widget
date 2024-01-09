# SPDX-FileCopyrightText: 2024 Shape Keys Widget Authors
# SPDX-License-Identifier: GPL-3.0

import logging
log = logging.getLogger(__package__)

import bpy
from bpy.types import Panel


class VIEW3D_PT_anim_sel_cursor(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Shape Key Widgets"
    bl_label = "Animation (SKS)"
    bl_description = """As in SKS, key selected cursor category.
    Key Shape Key values and cursor location"""

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        col = layout.column()
        col.operator("anim.skw_insert_keyframes_shapekey_category")
        col.operator("anim.skw_insert_keyframes_all_categories")


class VIEW3D_PT_anim_listed_values(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Shape Key Widgets"
    bl_label = "Animation (SK values)"
    bl_description = """Selection doesn't matter.
    Key Shape Key values, but *not* SKWidget cursor location"""

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        # Collect all the existing SKW cursors per mesh.
        meshes = {}
        for collection in bpy.data.collections:
            if collection.name.endswith("-skw"):
                mesh_col_name = collection.name[:-4]
                meshes[mesh_col_name] = []

                for obj in collection.objects:
                    name_parts = obj.name.split('-')
                    if len(name_parts) == 3:
                        category_name = name_parts[2]
                        meshes[mesh_col_name].append(category_name)

        for mesh_col_name in sorted(meshes):
            col = layout.column(align=True)
            col.label(text=mesh_col_name.capitalize()+":")
            row = col.row(align=True)
            for category_name in sorted(meshes[mesh_col_name]):
                row.operator("anim.skw_insert_keyframes_shapekey_category",
                    text=category_name.capitalize()).keyframe_cursor = False
            col.operator("anim.skw_insert_keyframes_shapekey_category",
                    text="All").keyframe_cursor = False


class VIEW3D_PT_anim_listed_cursor(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Shape Key Widgets"
    bl_label = "Animation (cursor)"
    bl_description = """Key the SKWidget cursor location, but *not* Shape Key values"""

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        # Collect all the existing SKW cursors per mesh.
        meshes = {}
        for collection in bpy.data.collections:
            if collection.name.endswith("-skw"):
                mesh_col_name = collection.name[:-4]
                meshes[mesh_col_name] = []

                for obj in collection.objects:
                    name_parts = obj.name.split('-')
                    if len(name_parts) == 3:
                        category_name = name_parts[2]
                        meshes[mesh_col_name].append(category_name)

        for mesh_col_name in sorted(meshes):
            col = layout.column(align=True)
            col.label(text=mesh_col_name.capitalize()+":")
            row = col.row(align=True)
            for category_name in sorted(meshes[mesh_col_name]):
                row.operator("anim.skw_insert_keyframes_shapekey_category",
                    text=category_name.capitalize()).keyframe_values = False
            col.operator("anim.skw_insert_keyframes_shapekey_category",
                    text="All").keyframe_values = False



# Add-on Registration #############################################################################

classes = (
    VIEW3D_PT_anim_sel_cursor,
    VIEW3D_PT_anim_listed_values,
    VIEW3D_PT_anim_listed_cursor,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

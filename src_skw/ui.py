# SPDX-FileCopyrightText: 2024 Shape Keys Widget Authors
# SPDX-License-Identifier: GPL-3.0

import logging
log = logging.getLogger(__package__)

import bpy
from bpy.types import Panel


class VIEW3D_PT_shape_key_widgets(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Shape Key Widgets"
    bl_label = "Animation"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()
        col.label(text="Hi there!")


# Add-on Registration #############################################################################

classes = (
    VIEW3D_PT_shape_key_widgets,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

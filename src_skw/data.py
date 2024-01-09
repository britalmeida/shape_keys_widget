# SPDX-FileCopyrightText: 2024 Shape Keys Widget Authors
# SPDX-License-Identifier: GPL-3.0

import logging
log = logging.getLogger(__package__)

import bpy
from bpy.app.handlers import persistent


@persistent
def on_depsgraph_update(scene):

    # Check for Shape Key Widget Cursors that are selected.
    for selected_object in bpy.context.selected_objects:
        if selected_object.name.endswith("-cursor"):
            name_parts = selected_object.name.split('-')
            if name_parts[1] != "skw":
                # Selected object does not have the naming convention of a Shape Key Widget Cursor.
                continue

            mesh_col_name = name_parts[0]+"-model"
            category_name = name_parts[2].capitalize()+" - "

            # If a SKW cursor has moved, transfer the shape key weights that are calculated by a
            # driver in a custom prop of the mesh, to the corresponding actual shape key.
            mesh_obj = bpy.data.collections[mesh_col_name].objects[0]
            mesh_data = mesh_obj.data
            for key in mesh_data.shape_keys.key_blocks:
                if key.name.startswith(category_name):
                    key.value = mesh_data[key.name]


# Add-on Registration #############################################################################

classes = (
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)

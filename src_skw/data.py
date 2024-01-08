# SPDX-FileCopyrightText: 2024 Shape Keys Widget Authors
# SPDX-License-Identifier: GPL-3.0

import logging
log = logging.getLogger(__package__)

import bpy
from bpy.app.handlers import persistent


@persistent
def on_depsgraph_update(scene):
    print("update")
    for selected_object in bpy.context.selected_objects:
        print(selected_object.name)
        if "-cursor" in selected_object.name:

            # If a SKW cursor has moved, transfer the shape key weights that are calculated by a
            # driver in a custom prop of the mesh, to the corresponding actual shape key.
            mesh_obj = bpy.data.objects["GEO-face"]
            for key in mesh_obj.data.shape_keys.key_blocks:
                print(key.name)
                if key.name.startswith("Eyes - "):
                    key.value = mesh_obj.data[key.name]


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

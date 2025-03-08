# SPDX-FileCopyrightText: 2024-2025 Shape Keys Widget Authors
# SPDX-License-Identifier: GPL-3.0

bl_info = {
    "name": "Shape Keys Widget",
    "description": "Visual UI for Shape Key selection in the 3D View",
    "author": "Inês Almeida",
    "warning": "WIP development, not released for general usage yet",
    "version": (0, 2, 1),
    "blender": (3, 6, 0),
    "location": "View3D > Properties > Shape Keys Widget",
    "doc_url": "https://github.com/britalmeida/shape_keys_widget",
    "tracker_url": "https://github.com/britalmeida/shape_keys_widget/issues",
    "category": "Rigging",
}

import logging
log = logging.getLogger(__name__)

if "src_skw" in locals():
    import importlib
    importlib.reload(src_skw)
else:
    from . import src_skw


def register():
    log.info("------Registering Add-on---------------------------")

    src_skw.register()

    log.info("------Done Registering-----------------------------")


def unregister():

    log.info("------Unregistering Add-on-------------------------")

    src_skw.unregister()

    log.info("------Done Unregistering---------------------------")


if __name__ == "__main__":
    register()

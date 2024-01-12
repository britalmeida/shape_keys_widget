# SPDX-FileCopyrightText: 2024 Shape Keys Widget Authors
# SPDX-License-Identifier: GPL-3.0

if "convert_sks_to_skw_rig" in locals():
    import importlib
    importlib.reload(convert_sks_to_skw_rig)
    importlib.reload(data)
    importlib.reload(ops)
    importlib.reload(ui)
else:
    from . import convert_sks_to_skw_rig
    from . import data
    from . import ops
    from . import ui


def register():
    convert_sks_to_skw_rig.register()
    data.register()
    ops.register()
    ui.register()

def unregister():

    ui.unregister()
    ops.unregister()
    data.unregister()
    convert_sks_to_skw_rig.unregister()

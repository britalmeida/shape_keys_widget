# SPDX-FileCopyrightText: 2024 Shape Keys Widget Authors
# SPDX-License-Identifier: GPL-3.0

if "ops" in locals():
    import importlib
    importlib.reload(data)
    importlib.reload(ops)
    importlib.reload(ui)
else:
    from . import data
    from . import ops
    from . import ui


def register():
    data.register()
    ops.register()
    ui.register()

def unregister():

    ui.unregister()
    ops.unregister()
    data.unregister()

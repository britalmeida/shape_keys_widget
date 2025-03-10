# SPDX-FileCopyrightText: 2024-2025 Shape Keys Widget Authors
# SPDX-License-Identifier: GPL-3.0

from bpy.types import UILayout


def draw_stat_label(layout: UILayout, label: str, value: str) -> None:
    """Add a label-value pair to Blender's UI, aligned as a split property"""

    split = layout.split(factor=0.4, align=True)
    split.alignment = 'RIGHT'
    split.label(text=label)
    split.alignment = 'LEFT'
    split.label(text=value)


def create_unique_name(base_name: str, existing_objects: list) -> str:
    """Returns a name not yet present in existing_objects which starts with base_name.

    Names follow Blender convention: base_name, base_name.001, base_name.002, etc.
    e.g.: create_unique_name("Object", all_objects)
    - all_objects = [] -> "Object"
    - all_objects = ["Object"] -> "Object.001"
    - all_objects = ["Object.002"] -> "Object"
    """

    # Get the object names.
    existing_names = (ob.name for ob in existing_objects)

    # If this is the first of its name, no need to add a suffix.
    if base_name not in existing_names:
        return base_name

    # Construct a sorted list of number suffixes already in use for base_name.
    offset = len(base_name) + 1
    suffixes = (name[offset:] for name in existing_names if name.startswith(base_name + '.'))
    numbers = sorted(int(suffix) for suffix in suffixes if suffix.isdigit())
    print(numbers)

    # Find the first unused number.
    min_index = 1
    for num in numbers:
        if min_index < num:
            break
        min_index = num + 1

    return f"{base_name}.{min_index:03d}"

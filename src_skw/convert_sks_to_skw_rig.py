# SPDX-FileCopyrightText: 2024 Shape Keys Widget Authors
# SPDX-License-Identifier: GPL-3.0

from math import radians

import bpy
from mathutils import Vector, Matrix



# Name of the rig and mesh with the shape keys.
RIG_NAME = 'RIG-claudia'
GEO_NAME = 'GEO-claudia-head'
#THUMBNAILS_FILEPATH = "//widget_demo_thumbs"
THUMBS_COLLECTION_NAME = "claudia-rig-widgets-thumbnails"
WGTS_COLLECTION_NAME = "claudia-rig-widgets"
CURSOR_MESH_OBJ_NAME = "WGT-sk-cursor"
THUMB_MESH_OBJ_NAME = "WGT-thumbnail-selector"

# Shape Key categories to generate widgets for.
SHAPE_KEY_CATEGORIES = ["Mouth", "Phoneme", "Eyebrows"]
# !!
# File needs to already have: (e.g.: for category "Eyes")
# - Shape keys called 'Eyes - Neutral', 'Eyes - Bla bla'
# - Bone called 'SKS-eyes', in the desired position
# - Objects with a picture called 'Eyes - Neutral', 'Eyes - Bla bla',
#### Future: just the image files for 'Eyes - Neutral', 'Eyes - Bla bla'.
# - Collection for thumbnails e.g.: 'rig-thumbnails'
# - Collection for rig widgets e.g.: 'rig-WGT'
# - The rig widget mesh objects

# --- Naming conventions ---

def get_sk_category_base_bone_name(sk_category_name):
    return f"SKS-{slugify_name(sk_category_name)}"

def get_sk_category_cursor_bone_name(sk_category_name):
    return f"SKS-{slugify_name(sk_category_name)}-cursor"

def get_sk_bone_name(sk_name):
    return f"SKS-{slugify_name(sk_name)}"

def get_sk_thumb_obj_name(sk_name):
    return f"{sk_name}"

def slugify_name(name):
    name = name.replace(' ', '')
    name = name.lower()
    return name


# --- Stuff ---

def nuke_existing_and_make_new_bone(edit_bones, bone_name):
    # If the bone already existed in the file, delete it and create a fresh new one.
    bone = edit_bones.get(bone_name)
    if bone:
        edit_bones.remove(bone)
    return edit_bones.new(bone_name)


def lock_transform(ob, lock_also_x_and_y = False):
    ob.lock_location[0] = lock_also_x_and_y
    ob.lock_location[1] = lock_also_x_and_y
    ob.lock_location[2] = True
    ob.lock_rotation[0] = True
    ob.lock_rotation[1] = True
    ob.lock_rotation[2] = True
    ob.lock_rotation_w = True
    ob.lock_scale[0] = True
    ob.lock_scale[1] = True
    ob.lock_scale[2] = True


def move_to_collection(ob, collection):
    # Remove the object from the collections that it is already into.
    for col in ob.users_collection:
        col.objects.unlink(ob)

    # Add the object to the given collection.
    collection.objects.link(ob)


def create_bones(rig, sk_category_name, shape_key_names):

    # Get the armature datablock
    armature = rig.data

    # Switch to Edit Mode to add bones
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = armature.edit_bones

    # Find the base bone. The new bones will be parented to this one.
    base_bone_name = get_sk_category_base_bone_name(sk_category_name)
    base_bone = edit_bones.get(base_bone_name)
    if not base_bone:
        raise ValueError(f"Rig does not have an already existing bone called '{base_bone_name}'")

    # Create cursor bone.
    cursor_bone_name = get_sk_category_cursor_bone_name(sk_category_name)
    cursor_bone = nuke_existing_and_make_new_bone(edit_bones, cursor_bone_name)
    # Parent the cursor bone.
    cursor_bone.parent = base_bone

    # Create bones for each shape key thumbnail.
    for sk_name in shape_key_names:
        # Generate the bone name
        new_bone_name = get_sk_bone_name(sk_name)

        # If the bone already existed in the file, delete it and create a fresh new one.
        new_bone = nuke_existing_and_make_new_bone(edit_bones, new_bone_name)

        # Parent the bone.
        new_bone.parent = base_bone

        # Find the corresponding thumbnail object which should already exist in the file.
        thumb_obj = bpy.data.objects.get(get_sk_thumb_obj_name(sk_name))
        if not thumb_obj:
            raise ValueError(f"File does not have an already existing thumbnail object called '{sk_name}'")

        # Place the bone at the thumbnail's center coordinates in world space.
        pos = thumb_obj.matrix_world.to_translation()
        new_bone.tail = pos
        new_bone.head = pos + Vector((0, 0, -0.05))

    # Place the cursor bone on the Neutral thumbnail.
    neutral_thumb_obj = bpy.data.objects.get(get_sk_thumb_obj_name(f"{sk_category_name} - Neutral"))
    pos = neutral_thumb_obj.matrix_world.to_translation()
    cursor_bone.tail = pos
    cursor_bone.head = pos + Vector((0, 0, -0.05))

    # Update the scene
    bpy.context.view_layer.update()

    # Leave edit mode so that pose bones become available.
    bpy.ops.object.mode_set(mode='OBJECT')


def add_custom_properties(rig, sk_category_name, shape_key_names):
    # Get the armature datablock
    armature = rig.data

    # Switch to Pose Mode to configure bone properties usable in pose mode.
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='POSE')
    pose_bones = rig.pose.bones

    # Add cursor custom property 'snapping'.
    cursor_bone_name = get_sk_category_cursor_bone_name(sk_category_name)
    cursor_bone = pose_bones.get(cursor_bone_name)
    cursor_bone["snapping"] = True
    id_props = cursor_bone.id_properties_ui("snapping")
    id_props.update(description="Snap the widget cursor to shape key poses")

    # Add thumbnail bone custom property 'cursor_influence'.
    for sk_name in shape_key_names:
        bone_name = get_sk_bone_name(sk_name)
        bone = pose_bones.get(bone_name)
        bone["cursor_influence"] = 0.0
        id_props = bone.id_properties_ui("cursor_influence")
        id_props.update(subtype='FACTOR', min=0.0, max=1.0)


def setup_thumbnails(rig, shape_key_names):
    # Find the thumbnails collection.
    thumbs_col = bpy.data.collections.get(THUMBS_COLLECTION_NAME)
    if not thumbs_col:
        raise ValueError(f"File does not have an already existing collection named '{THUMBS_COLLECTION_NAME}'")

    # The thumbnails should not be selectable or end up in final renders.
    thumbs_col.hide_select = True
    thumbs_col.hide_render = True
    thumbs_col.hide_viewport = False

    # Switch to Pose Mode to access pose bone locations.
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='POSE')
    pose_bones = rig.pose.bones

    for sk_name in shape_key_names:
        thumb_obj = bpy.data.objects.get(get_sk_thumb_obj_name(sk_name))
        bone_name = get_sk_bone_name(sk_name)
        bone = pose_bones.get(bone_name)

        # At this moment, the sk thumb bone should be in the desired location.
        # So we clear everything from the thumbnail object,
        # set it to that world location and parent it to follow the bone in pose mode.

        # Remove any existing drivers, constraints, parenting and transform.
        thumb_obj.animation_data_clear()
        thumb_obj.constraints.clear()
        thumb_obj.parent = None
        thumb_obj.matrix_basis = Matrix()

        # Set the thumbnail image object to the bone location.
        thumb_obj.location = bone.tail
        thumb_obj.rotation_euler[0] = radians(90)

        # Parent the thumbnail objects to the bone.
        # Use an armature constraint to prevent unreliable transform results from reparenting.
        # This way, there is no invisble offset to the parent, and it also makes a cleaner outliner.
        con = thumb_obj.constraints.new(type='ARMATURE')
        con_target = con.targets.new()
        con_target.target = rig
        con_target.subtarget = bone_name

        # Lock the thumbnail transform from being manually changed, as it should follow the bone.
        lock_transform(thumb_obj, lock_also_x_and_y=True)

        # Place in the appropriate collection.
        move_to_collection(thumb_obj, thumbs_col)

        # TODO setup material and thumbnail texture.


def setup_bone_custom_shapes(rig, sk_category_name, shape_key_names):
    # Get the armature datablock
    armature = rig.data

    # Switch to Pose Mode to configure bone shapes.
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='POSE')
    pose_bones = rig.pose.bones

    cursor_bone_name = get_sk_category_cursor_bone_name(sk_category_name)
    cursor_bone = pose_bones.get(cursor_bone_name)

    cursor_mesh_obj = bpy.data.objects.get(CURSOR_MESH_OBJ_NAME)
    cursor_bone.custom_shape = cursor_mesh_obj
    cursor_bone.use_custom_shape_bone_size = False
    cursor_bone.custom_shape_rotation_euler[0] = radians(90)
    cursor_bone.custom_shape_translation[1] = 0.05
    cursor_bone.custom_shape_translation[2] = 0.001

    # Thumbnail bones
    thumb_mesh_obj = bpy.data.objects.get(THUMB_MESH_OBJ_NAME)
    for sk_name in shape_key_names:
        bone_name = get_sk_bone_name(sk_name)
        bone = pose_bones.get(bone_name)
        bone.custom_shape = thumb_mesh_obj



def setup_bones_movement(rig, sk_category_name, shape_key_names):
    # Get the armature datablock
    armature = rig.data

    # Switch to Pose Mode to configure transform channels that can be keyed.
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='POSE')
    pose_bones = rig.pose.bones

    # Cursor
    cursor_bone_name = get_sk_category_cursor_bone_name(sk_category_name)
    cursor_bone = pose_bones.get(cursor_bone_name)

    lock_transform(cursor_bone, lock_also_x_and_y=False)

    add_snap_location_driver(rig, cursor_bone, 'LOC_X', use_snap_user_option=True)
    add_snap_location_driver(rig, cursor_bone, 'LOC_Y', use_snap_user_option=True)

    # Thumbnail bones
    for sk_name in shape_key_names:
        bone_name = get_sk_bone_name(sk_name)
        bone = pose_bones.get(bone_name)

        lock_transform(bone, lock_also_x_and_y=False)

        add_snap_location_driver(rig, bone, 'LOC_X', use_snap_user_option=False)
        add_snap_location_driver(rig, bone, 'LOC_Y', use_snap_user_option=False)


def find_shape_keys(category_name):
    shape_keys = bpy.data.objects[GEO_NAME].data.shape_keys.key_blocks
    filtered_shape_key_names = []
    for key in shape_keys:
        if key.name.startswith(category_name + ' - '):
            filtered_shape_key_names.append(key.name)
    return filtered_shape_key_names


def add_snap_location_driver(rig, bone, tf_channel, use_snap_user_option=False):
    """
    This function takes in an object and makes it snap to the grid using location drivers

    Args:
        tf_channel: 'LOC_X' or 'LOC_Y'
    """
    property_index = 0 if tf_channel == 'LOC_X' else 1

    # Remove the existing driver if it exists
    bone.driver_remove(f'location[{property_index}]')

    # Add a driver to the given axis
    dr = bone.driver_add("location", property_index)
    # Remove automatically added polynomial modifier.
    if dr.modifiers:
        dr.modifiers.remove(dr.modifiers[0])

    dr.driver.type = 'SCRIPTED'
    # round(var*10)/10 snaps the driver to increments of 0.1
    # but the scale of the thumbnail images is 0.1 so that becomes a scale of 1
    if use_snap_user_option:
        dr.driver.expression = "round(loc*10)/10 if is_snapping_on else loc"
    else:
        dr.driver.expression = "round(loc*10)/10"

    # Add the own location variable to the driver
    loc_var = dr.driver.variables.new()
    loc_var.name = 'loc'
    loc_var.type = 'TRANSFORMS'

    loc_var_target = loc_var.targets[0]
    loc_var_target.id = rig
    loc_var_target.bone_target = bone.name

    loc_var_target.transform_type = tf_channel
    loc_var_target.transform_space = 'TRANSFORM_SPACE'

    if use_snap_user_option:
        # Add a variable for the user option to have snapping enabled.
        snap_var = dr.driver.variables.new()
        snap_var.name = 'is_snapping_on'
        snap_var.type = 'SINGLE_PROP'

        snap_var_target = snap_var.targets[0]
        snap_var_target.id_type = 'OBJECT'
        snap_var_target.id = rig
        snap_var_target.data_path = f'pose.bones["{bone.name}"]["snapping"]'


def setup_sk_value_drivers(rig, shape_key_names):

    bpy.ops.object.mode_set(mode='POSE')
    pose_bones = rig.pose.bones
    cursor_bone_name = get_sk_category_cursor_bone_name(sk_category_name)

    # Setup driver for the cursor influence on each thumbnail bone.
    for sk_name in shape_key_names:
        bone_name = get_sk_bone_name(sk_name)
        bone = pose_bones.get(bone_name)

        # Remove the existing driver if it exists
        bone.driver_remove('["cursor_influence"]')

        # Add a driver to the given axis
        dr = bone.driver_add('["cursor_influence"]')
        # Remove automatically added polynomial modifier.
        if dr.modifiers:
            dr.modifiers.remove(dr.modifiers[0])

        dr.driver.type = 'SCRIPTED'
        dr.driver.expression = "max(0, 1 - 10 * var)"

        # Create a new variable
        var = dr.driver.variables.new()
        var.name = 'var'
        var.type = 'LOC_DIFF'

        # Set the targets for the custom property
        object1 = var.targets[0]
        object2 = var.targets[1]

        # Set object1 to be the Selector Icon and Object 2 to be the image plane
        object1.id = rig
        object1.bone_target = cursor_bone_name
        object2.id = rig
        object2.bone_target = bone_name

        object1.transform_space = 'WORLD_SPACE'
        object2.transform_space = 'WORLD_SPACE'

    # Setup driver for the SK value from the cursor influence.
    shape_keys = bpy.data.objects[GEO_NAME].data.shape_keys.key_blocks
    for sk_name in shape_key_names:
        sk = shape_keys[sk_name]

        # Remove the existing driver if it exists
        sk.driver_remove(f'value')

        # Add a driver to the given axis
        dr = sk.driver_add("value")
        # Remove automatically added polynomial modifier.
        if dr.modifiers:
            dr.modifiers.remove(dr.modifiers[0])

        dr.driver.type = 'SUM'

        # Add a variable for the influence of the cursor on this shape key
        var = dr.driver.variables.new()
        var.name = 'var'
        var.type = 'SINGLE_PROP'

        var_target = var.targets[0]
        var_target.id_type = 'OBJECT'
        var_target.id = rig
        var_target.data_path = f'pose.bones["{get_sk_bone_name(sk_name)}"]["cursor_influence"]'


def move_bones_to_layer(rig):
    bpy.ops.object.mode_set(mode='OBJECT')
    for bone in rig.data.bones:
        if not bone.name.startswith('SKS-'):
            continue
        for i in range(32):
            rig.data.bones[bone.name].layers[i] = False
        rig.data.bones[bone.name].layers[21] = True


# --- Run ---

print("Generating Shape Key widget rigs...")

# Check the rig widgets collection.
wgts_col = bpy.data.collections.get(WGTS_COLLECTION_NAME)
if not wgts_col:
    raise ValueError(f"File does not have an already existing collection named '{WGTS_COLLECTION_NAME}'")
wgts_col.hide_select = True
wgts_col.hide_render = True
wgts_col.hide_viewport = True

# Setup custom mesh to be shared for the cursor(s).
cursor_mesh_obj = bpy.data.objects.get(CURSOR_MESH_OBJ_NAME)
if not cursor_mesh_obj:
    cursor_mesh_data = bpy.data.meshes.get("Selector Icon")
    if not cursor_mesh_data:
        raise ValueError(f"File does not have an already existing mesh object named 'Selector Icon'")
    cursor_mesh_obj = bpy.data.objects.new(CURSOR_MESH_OBJ_NAME, cursor_mesh_data)
move_to_collection(cursor_mesh_obj, wgts_col)
# Remove old cursors using the mesh.
objs_to_remove = [ob for ob in bpy.data.objects if ob.name.startswith("Selector Icon")]
for ob in objs_to_remove:
    bpy.data.objects.remove(ob)

# Find the rig
rig = bpy.data.objects.get(RIG_NAME)
if not rig:
    raise ValueError(f"Can not find rig with name '{RIG_NAME}' to modify")

for sk_category_name in SHAPE_KEY_CATEGORIES:

    shape_key_names = find_shape_keys(sk_category_name)
    print(f"... Creating '{sk_category_name}' widget with {len(shape_key_names)} shapes.")

    create_bones(rig, sk_category_name, shape_key_names)
    move_bones_to_layer(rig)
    add_custom_properties(rig, sk_category_name, shape_key_names)
    setup_thumbnails(rig, shape_key_names)
    setup_bone_custom_shapes(rig, sk_category_name, shape_key_names)
    setup_bones_movement(rig, sk_category_name, shape_key_names)
    setup_sk_value_drivers(rig, shape_key_names)

print("Done")

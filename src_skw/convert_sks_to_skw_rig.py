# SPDX-FileCopyrightText: 2024 Shape Keys Widget Authors
# SPDX-License-Identifier: GPL-3.0

import logging
from math import radians

import bpy
from bpy.props import StringProperty
from bpy.types import Operator
from mathutils import Vector, Matrix

log = logging.getLogger(__package__)


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
# This is what gets generated for the Blender bones and objects as seen in the outliner.
# Change as desired for the result.

def get_sk_category_base_bone_name(sk_category_name):
    return f"SKS-{slugify_name(sk_category_name)}"

def get_sk_category_cursor_bone_name(sk_category_name):
    return f"SKS-{slugify_name(sk_category_name)}-cursor"

def get_sk_bone_name(sk_name):
    return f"SKS-{slugify_name(sk_name)}"

def get_sk_thumb_obj_name(sk_name):
    return f"{sk_name}"

def get_wgt_category_obj_name(sk_category_name):
    return f"WGT-sk-text-{slugify_name(sk_category_name)}"

def get_wgt_cursor_obj_name():
    return "WGT-sk-cursor"

def get_wgt_thumb_obj_name():
    return "WGT-thumbnail-selector"

def slugify_name(name):
    name = name.replace(' ', '')
    name = name.lower()
    return name


# --- Stuff ---

def find_shape_keys(mesh_name, category_name):
    shape_keys = bpy.data.objects[mesh_name].data.shape_keys.key_blocks
    filtered_shape_key_names = []
    for key in shape_keys:
        if key.name.startswith(category_name + ' - '):
            filtered_shape_key_names.append(key.name)
    return filtered_shape_key_names


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


def create_bones(rig, sk_category_name, shape_key_base_names, has_lr_keys):
    # If the bones already exist, delete them and create fresh new ones.

    # Switch to Edit Mode to add bones.
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = rig.data.edit_bones

    # Find the base bone. The new bones will be parented to this one.
    base_bone_name = get_sk_category_base_bone_name(sk_category_name)
    base_bone = edit_bones.get(base_bone_name)

    # Find the Neutral thumbnail position.
    neutral_thumb_obj = bpy.data.objects.get(get_sk_thumb_obj_name(f"{sk_category_name} - Neutral"))
    neutral_thumb_pos = neutral_thumb_obj.matrix_world.to_translation()

    # Create cursor bones.
    # (before the thumbnails so it looks nice in the outliner)
    for cursor_type in ['.L', '.R'] if has_lr_keys else ['']:
        cursor_bone_name = get_sk_category_cursor_bone_name(sk_category_name)+cursor_type
        cursor_bone = nuke_existing_and_make_new_bone(edit_bones, cursor_bone_name)
        cursor_bone.use_deform = False
        cursor_bone.parent = base_bone

        # Place the cursor bones(s) on the Neutral thumbnail.
        cursor_bone.tail = neutral_thumb_pos
        cursor_bone.head = neutral_thumb_pos + Vector((0, 0, -0.05))

    # Create bones for each shape key thumbnail.
    for sk_name in shape_key_base_names:
        new_bone_name = get_sk_bone_name(sk_name)
        new_bone = nuke_existing_and_make_new_bone(edit_bones, new_bone_name)
        new_bone.use_deform = False
        new_bone.parent = base_bone

        # Place the bone at the corresponding thumbnail's center coordinates in world space.
        thumb_obj = bpy.data.objects.get(get_sk_thumb_obj_name(sk_name))
        pos = thumb_obj.matrix_world.to_translation()
        new_bone.tail = pos
        new_bone.head = pos + Vector((0, 0, -0.05))

    # Update the scene
    bpy.context.view_layer.update()

    # Leave edit mode so that pose bones become available.
    bpy.ops.object.mode_set(mode='OBJECT')


def add_bone_custom_properties(rig, sk_category_name, shape_key_base_names, has_lr_keys):

    # Switch to Pose Mode to configure bone properties usable in pose mode.
    bpy.ops.object.mode_set(mode='POSE')
    pose_bones = rig.pose.bones

    for cursor_type in ['.L', '.R'] if has_lr_keys else ['']:
        # Add cursor custom property 'snapping'.
        cursor_bone_name = get_sk_category_cursor_bone_name(sk_category_name)+cursor_type
        cursor_bone = pose_bones.get(cursor_bone_name)
        cursor_bone["snapping"] = True
        id_props = cursor_bone.id_properties_ui("snapping")
        id_props.update(description="Snap the widget cursor to shape key poses")

        # Add thumbnail bone custom property 'cursor_influence'.
        for sk_name in shape_key_base_names:
            bone_name = get_sk_bone_name(sk_name)
            bone = pose_bones.get(bone_name)
            bone["cursor_influence"+cursor_type] = 0.0
            id_props = bone.id_properties_ui("cursor_influence"+cursor_type)
            id_props.update(subtype='FACTOR', min=0.0, max=1.0)


def setup_thumbnails(thumbs_col_name, rig, shape_key_base_names):
    # Find the thumbnails collection.
    thumbs_col = bpy.data.collections.get(thumbs_col_name)

    # The thumbnails should not be selectable or end up in final renders.
    thumbs_col.hide_select = True
    thumbs_col.hide_render = True
    thumbs_col.hide_viewport = False

    # Switch to Pose Mode to access pose bone locations.
    bpy.ops.object.mode_set(mode='POSE')
    pose_bones = rig.pose.bones

    for sk_name in shape_key_base_names:
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


def setup_bone_custom_shapes(rig, sk_category_name, shape_key_base_names, has_lr_keys):

    # Switch to Pose Mode to configure bone shapes.
    bpy.ops.object.mode_set(mode='POSE')
    pose_bones = rig.pose.bones

    # Cursor custom shape.
    for cursor_type in ['.L', '.R'] if has_lr_keys else ['']:
        cursor_bone_name = get_sk_category_cursor_bone_name(sk_category_name)+cursor_type
        cursor_bone = pose_bones.get(cursor_bone_name)

        cursor_mesh_name = get_wgt_cursor_obj_name()+cursor_type
        cursor_mesh_obj = bpy.data.objects.get(cursor_mesh_name)
        cursor_bone.custom_shape = cursor_mesh_obj
        cursor_bone.use_custom_shape_bone_size = False
        cursor_bone.custom_shape_rotation_euler[0] = radians(90)
        cursor_bone.custom_shape_translation[1] = 0.05
        cursor_bone.custom_shape_translation[2] = 0.001

    # Thumbnail bones
    thumb_mesh_obj = bpy.data.objects.get(get_wgt_thumb_obj_name())
    for sk_name in shape_key_base_names:
        bone_name = get_sk_bone_name(sk_name)
        bone = pose_bones.get(bone_name)
        bone.custom_shape = thumb_mesh_obj


def setup_bones_movement(rig, sk_category_name, shape_key_base_names, has_lr_keys):

    # Switch to Pose Mode to configure transform channels that can be keyed.
    bpy.ops.object.mode_set(mode='POSE')
    pose_bones = rig.pose.bones

    # Cursor
    for cursor_type in ['.L', '.R'] if has_lr_keys else ['']:
        cursor_bone_name = get_sk_category_cursor_bone_name(sk_category_name)+cursor_type
        cursor_bone = pose_bones.get(cursor_bone_name)

        lock_transform(cursor_bone, lock_also_x_and_y=False)

        add_snap_location_driver(rig, cursor_bone, 'LOC_X', use_snap_user_option=True)
        add_snap_location_driver(rig, cursor_bone, 'LOC_Y', use_snap_user_option=True)

    # Thumbnail bones
    for sk_name in shape_key_base_names:
        bone_name = get_sk_bone_name(sk_name)
        bone = pose_bones.get(bone_name)

        lock_transform(bone, lock_also_x_and_y=False)

        add_snap_location_driver(rig, bone, 'LOC_X', use_snap_user_option=False)
        add_snap_location_driver(rig, bone, 'LOC_Y', use_snap_user_option=False)


def add_snap_location_driver(rig, bone, tf_channel, use_snap_user_option=False):
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


def add_cursor_influence_driver(rig, bone, cursor_influence_prop_name, cursor_bone_name):
    # Note: driver is being added to a bone, which were (re)created fresh.
    # Therefore, there is no need to look for previously existing drivers.

    # Add a driver to the given custom property name.
    dr = bone.driver_add(f'["{cursor_influence_prop_name}"]')
    # Remove automatically added polynomial modifier.
    if dr.modifiers:
        dr.modifiers.remove(dr.modifiers[0])

    dr.driver.type = 'SCRIPTED'
    dr.driver.expression = "max(0, 1 - 10 * var)"

    # Create a variable for the world space distance between a thumbnail and cursor bone.
    var = dr.driver.variables.new()
    var.name = 'var'
    var.type = 'LOC_DIFF'

    object1 = var.targets[0]
    object2 = var.targets[1]

    object1.id = rig
    object1.bone_target = cursor_bone_name
    object2.id = rig
    object2.bone_target = bone.name

    object1.transform_space = 'WORLD_SPACE'
    object2.transform_space = 'WORLD_SPACE'


def add_shape_key_value_driver(rig, shape_key, thumbnail_bone_name, cursor_influence_prop_name):
    # Remove the existing driver if it exists
    shape_key.driver_remove('value')

    # Add a driver to the given axis
    dr = shape_key.driver_add('value')
    # Remove automatically added polynomial modifier.
    if dr.modifiers:
        dr.modifiers.remove(dr.modifiers[0])

    dr.driver.type = 'SUM'  # Get value of single variable.

    # Add a variable for the influence of the cursor on this shape key
    var = dr.driver.variables.new()
    var.name = 'var'
    var.type = 'SINGLE_PROP'

    var_target = var.targets[0]
    var_target.id_type = 'OBJECT'
    var_target.id = rig
    var_target.data_path = f'pose.bones["{thumbnail_bone_name}"]["{cursor_influence_prop_name}"]'


def setup_sk_value_drivers(mesh_name, rig, sk_category_name, shape_key_base_names, has_lr_keys):

    bpy.ops.object.mode_set(mode='POSE')
    pose_bones = rig.pose.bones
    cursor_bone_name = get_sk_category_cursor_bone_name(sk_category_name)

    # Setup driver for the cursor influence on each thumbnail bone.
    for sk_name in shape_key_base_names:
        bone_name = get_sk_bone_name(sk_name)
        bone = pose_bones.get(bone_name)

        for cursor_type in ['.L', '.R'] if has_lr_keys else ['']:
            add_cursor_influence_driver(
                rig, bone,
                "cursor_influence"+cursor_type,
                cursor_bone_name+cursor_type)

    # Setup driver for the SK value from the cursor influence.
    shape_keys = bpy.data.objects[mesh_name].data.shape_keys.key_blocks
    for sk_base_name in shape_key_base_names:
        thumbnail_bone_name = get_sk_bone_name(sk_base_name)

        if sk_base_name.endswith('Neutral'):
            sk = shape_keys[sk_base_name]
            add_shape_key_value_driver(
                rig, sk,
                thumbnail_bone_name, "cursor_influence")
            continue

        for cursor_type in ['.L', '.R'] if has_lr_keys else ['']:
            sk = shape_keys[sk_base_name+cursor_type]
            add_shape_key_value_driver(
                rig, sk,
                thumbnail_bone_name, "cursor_influence"+cursor_type)


def move_bones_to_layer(rig):
    bpy.ops.object.mode_set(mode='OBJECT')
    for bone in rig.data.bones:
        if not bone.name.startswith('SKS-'):
            continue
        for i in range(32):
            rig.data.bones[bone.name].layers[i] = False
        rig.data.bones[bone.name].layers[21] = True


def setup_wgt_objects_and_collection(wgts_col_name, category_names):

    # Rig widgets collection should not be visible in the viewport when using the rig.
    wgts_col = bpy.data.collections.get(wgts_col_name)
    wgts_col.hide_select = True
    wgts_col.hide_render = True
    wgts_col.hide_viewport = True

    # Setup custom mesh to be shared for the cursor(s).
    for cursor_type in ["", ".L", ".R"]:
        cursor_mesh_data_name = "Selector Icon"+cursor_type
        cursor_mesh_obj_name = get_wgt_cursor_obj_name()+cursor_type
        cursor_mesh_data = bpy.data.meshes.get(cursor_mesh_data_name)
        cursor_mesh_obj = bpy.data.objects.get(cursor_mesh_obj_name)

        if not cursor_mesh_obj:
            cursor_mesh_obj = bpy.data.objects.new(cursor_mesh_obj_name, cursor_mesh_data)

        move_to_collection(cursor_mesh_obj, wgts_col)

    # Remove old cursors using the mesh.
    objs_to_remove = [ob for ob in bpy.data.objects if ob.name.startswith("Selector Icon")]
    for ob in objs_to_remove:
        bpy.data.objects.remove(ob)


    # Create text widgets for each SK category.

    # Save state of selection and enabled collections.
    user_preferred_exclude_value = True
    for layer_col in bpy.context.view_layer.layer_collection.children:
        if layer_col.name == wgts_col_name:
            user_preferred_exclude_value = layer_col.exclude
            layer_col.exclude = False
            break
    active_object = bpy.context.view_layer.objects.active
    selected_objects = bpy.context.selected_objects
    for obj in selected_objects:
        obj.select_set(False)

    for sk_category_name in category_names:
        text_obj = create_category_text_custom_shape_obj(wgts_col, sk_category_name)
        text_obj.select_set(True)

    bpy.context.view_layer.update()
    #bpy.ops.object.convert(target='CURVE', keep_original=False)

    # Restore selection and collections state.
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    for obj in selected_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = active_object
    for layer_col in bpy.context.view_layer.layer_collection.children:
        if layer_col.name == wgts_col_name:
            layer_col.exclude = user_preferred_exclude_value
            break


def create_category_text_custom_shape_obj(wgts_col, sk_category_name):

    display_name = sk_category_name
    wgt_obj_name = get_wgt_category_obj_name(sk_category_name)

    text_data = bpy.data.curves.new(type="FONT", name=wgt_obj_name)
    text_data.body = display_name
    text_data.dimensions = '3D'

    text_obj = bpy.data.objects.new(name=wgt_obj_name, object_data=text_data)
    move_to_collection(text_obj, wgts_col)

    return text_obj


class SCENE_OT_convert_sks_to_skw(Operator):
    bl_idname = "scene.convert_sks_to_skw"
    bl_label = "Convert SKS to SKW rig"
    bl_description = """
        Migrate data on a file that was setup with the Shape Key Selector V1 addon to a rig"""
    bl_options = {'UNDO', 'REGISTER'}


    rig_name: StringProperty(
        name="Rig Name",
        description="Existing rig where to add new bone controls for the shape keys",
        default="RIG-claudia",
    )
    geo_name: StringProperty(
        name="GEO Name",
        description="Mesh with shape keys",
        default="GEO-claudia-head",
    )
    thumbs_collection_name: StringProperty(
        name="Thumbnails Collection",
        description="Collection for thumbnail objects. Will be visible in the viewport.",
        default="claudia-rig-widgets-thumbnails",
    )
    wgts_collection_name: StringProperty(
        name="Rig Widgets Collection",
        description="Collection for rig WGT objects. Will be hidden in the viewport.",
        default="claudia-rig-widgets",
    )
    categories_str: StringProperty(
        name="Shape Key Categories",
        description="Comma separated list of Shape Key categories to generate controls for",
        default="Mouth, Eyes",
    )

    def meets_requirements_for_conversion(self, context) -> bool:

        wgts_col = bpy.data.collections.get(self.wgts_collection_name)
        if not wgts_col:
            self.report({'ERROR'},
                f"Missing collection named '{self.wgts_collection_name}'\n"
                "Needed to hold meshes for bone custom shapes.\n"
                "It will be hidden in the viewport.")
            return False

        # TODO: SKW should make the custom shape mesh data for the cursors and thumbnail moving.
        # Then it won't be a user error, but now the mesh data needs to be in the file.
        cursor_mesh_data = bpy.data.meshes.get("Selector Icon")
        cursor_l_mesh_data = bpy.data.meshes.get("Selector Icon.L")
        cursor_r_mesh_data = bpy.data.meshes.get("Selector Icon.R")
        thumb_selector_mesh_data = bpy.data.meshes.get(get_wgt_thumb_obj_name())
        if not cursor_mesh_data or not cursor_l_mesh_data or not cursor_r_mesh_data or not thumb_selector_mesh_data:
            self.report({'ERROR'},
                "Missing custom mesh objects for bone custom shapes.\n"
                f"Needs objects with a mesh called 'Selector Icon', 'Selector Icon.L', 'Selector Icon.R' and '{get_wgt_thumb_obj_name()}'")
            return False

        thumbs_col = bpy.data.collections.get(self.thumbs_collection_name)
        if not thumbs_col:
            self.report({'ERROR'},
                f"Missing collection named '{self.thumbs_collection_name}'\n"
                "Needed to hold thumbnail mesh objects that are parented to the rig.\n"
                "It will be shown in the viewport, but hidden in renders.")
            return False

        mesh_obj = bpy.data.objects[self.geo_name]
        if not mesh_obj:
            self.report({'ERROR'},
                f"Model/character mesh named '{self.geo_name}' not found")
            return False

        # Check for a match in SK and thumbnail objects for each SK in each category.
        category_names = [n.strip() for n in self.categories_str.split(',')]
        for sk_category_name in category_names:
            shape_key_names = sorted(find_shape_keys(self.geo_name, sk_category_name))

            if not shape_key_names:
                self.report({'ERROR'},
                    f"Mesh does not have any Shape Keys for category '{sk_category_name}'")
                return False

            # Check for the 'Neutral' Shape Key.
            neutral_sk_name = f"{sk_category_name} - Neutral"
            if neutral_sk_name not in shape_key_names:
                self.report({'ERROR'}, f"Mesh does not have a Shape Key called '{neutral_sk_name}'")
                return False

            # Match L and R shapes if they exist.
            left_sk_names = [sk for sk in shape_key_names if sk.endswith(".L")]
            right_sk_names = [sk for sk in shape_key_names if sk.endswith(".R")]
            global_sk_names = [sk for sk in shape_key_names if not sk.endswith(".L") and not sk.endswith(".R")]
            has_lr_keys = (len(left_sk_names) > 0 or len(right_sk_names) > 0)

            if has_lr_keys:
                if len(left_sk_names) != len(right_sk_names) or len(global_sk_names) > 1:
                    self.report({'ERROR'},
                        f"Mesh has mismatched shape keys for '{sk_category_name}'\n"
                        f"Category needs 1 'Neutral' and all others (or none) ending with '.L' and '.R'.\n"
                        f"Found: {len(global_sk_names)} global, {len(left_sk_names)} .L, {len(right_sk_names)} .R")
                    return False

                for lname, rname in zip(left_sk_names, right_sk_names):
                    if lname[:-2] != rname[:-2]:
                        self.report({'ERROR'},
                            f"Mesh has mismatched shape keys for '{sk_category_name}'\n"
                            f"Shapes ending with '.L' and '.R' need to match in name.\n"
                            f"'{lname}' ≠ '{rname}'")
                        return False

            # Look for a thumbnail object matching each shape key (1 for each L/R pair).
            sk_base_names = global_sk_names
            if has_lr_keys:
                sk_base_names += [sk[:-2] for sk in left_sk_names]

            for sk_name in sk_base_names:
                thumb_obj = bpy.data.objects.get(get_sk_thumb_obj_name(sk_name))
                if not thumb_obj:
                    self.report({'ERROR'},
                        f"File does not have an already existing thumbnail object called '{sk_name}'")
                    return False

        rig = bpy.data.objects.get(self.rig_name)
        if not rig:
            self.report({'ERROR'}, f"Can not find rig with name '{self.rig_name}' to modify")
            return False

        # Check for a base bone for each SK category.
        armature = rig.data
        category_names = [n.strip() for n in self.categories_str.split(',')]
        for sk_category_name in category_names:
            base_bone_name = get_sk_category_base_bone_name(sk_category_name)
            base_bone = armature.bones.get(base_bone_name)
            if not base_bone:
                self.report({'ERROR'}, f"Rig does not have an already existing bone called '{base_bone_name}'")
                return False

        return True


    def invoke(self, context, event):
        """Present dialog to configure the properties before running the operator"""
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


    def execute(self, context):

        # Check for the required setup to run the conversion and early out
        # before modifying data if something is missing.
        if not self.meets_requirements_for_conversion(context):
            return {'CANCELLED'}

        log.info("Generating Shape Key widget rigs...")

        category_names = [n.strip() for n in self.categories_str.split(',')]

        # Set the rig as the active object so the conversion can switch between edit/pose/object mode as needed.
        rig = bpy.data.objects.get(self.rig_name)
        bpy.context.view_layer.objects.active = rig

        setup_wgt_objects_and_collection(self.wgts_collection_name, category_names)

        # Convert the selector widget setup for each shape key category.
        for sk_category_name in category_names:

            # Gather the set of thumbnail and shape key names to configure the widget.
            shape_key_names = find_shape_keys(self.geo_name, sk_category_name)
            left_sk_names = [sk for sk in shape_key_names if sk.endswith(".L")]
            global_sk_names = [sk for sk in shape_key_names if not sk.endswith(".L") and not sk.endswith(".R")]

            # Prepare set of shape key names matching the thumbnails, by stripping '.L' endings
            # and having only one base name per pair.
            has_lr_keys = any(sk.endswith(".L") for sk in shape_key_names)
            shape_key_base_names = global_sk_names
            if has_lr_keys:
                shape_key_base_names += [sk[:-2] for sk in left_sk_names]

            log.info(f"... Creating '{sk_category_name}' widget with {shape_key_base_names} thumbnails.")

            create_bones(rig, sk_category_name, shape_key_base_names, has_lr_keys)
            move_bones_to_layer(rig)
            add_bone_custom_properties(rig, sk_category_name, shape_key_base_names, has_lr_keys)

            setup_thumbnails(self.thumbs_collection_name, rig, shape_key_base_names)
            setup_bone_custom_shapes(rig, sk_category_name, shape_key_base_names, has_lr_keys)
            setup_bones_movement(rig, sk_category_name, shape_key_base_names, has_lr_keys)
            setup_sk_value_drivers(self.geo_name, rig, sk_category_name, shape_key_base_names, has_lr_keys)

        # TODO Cleanup SKS objects.
        # find collection, if only empty text objects and no thumbnails, delete it.

        log.info("Done")
        return {'FINISHED'}



# Add-on Registration #############################################################################

classes = (
    SCENE_OT_convert_sks_to_skw,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

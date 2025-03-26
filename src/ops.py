# SPDX-FileCopyrightText: 2024-2025 Shape Keys Widget Authors
# SPDX-License-Identifier: GPL-3.0

import uuid

import bpy
from bpy.props import (
    CollectionProperty,
    EnumProperty,
    IntProperty,
    StringProperty,
)
from bpy.types import (
    Context,
    Operator,
)

from . import utils
from .data import ShapeKeysWidgetCategory

import logging
log = logging.getLogger(__package__)


class CreateShapeKeyWidgetsCategoryMixin:
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, context):
        if not context.mesh:
            cls.poll_message_set("Operator only available in the Mesh tab of the Properties Editor")
            return False
        if not context.mesh.shape_keys:
            cls.poll_message_set("Mesh has no Shape Keys")
            return False
        return True

    def invoke(self, context, event):
        """Present dialog to configure the properties before running the operator"""
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class ShapeKeyWidgetsCategoryOperator(Operator):
    bl_options = {'UNDO', 'REGISTER'}

    cat_idx: IntProperty(
        name="Category Index",
        description="Index of the category to operate on",
        default=0,
    )

    @classmethod
    def poll(cls, context):
        if not context.mesh:
            cls.poll_message_set("Operator only available in the Mesh tab of the Properties Editor")
            return False
        if not context.mesh.shape_key_cats:
            cls.poll_message_set("Mesh has no shape key widget categories")
            return False
        return True


def create_and_add_category(base_name: str, cats: CollectionProperty) -> ShapeKeysWidgetCategory:
    """Create the new category with a unique name and ID in the given collection"""

    new_cat = cats.add()
    new_cat.uuid = uuid.uuid4().hex
    # Generate a name unique for this mesh, ending in '.001' if necessary.
    name = utils.create_unique_name(base_name, cats)
    new_cat.name = name
    new_cat.widget_name = name  # TODO don't have this duplicated.
    return new_cat


def add_basis_as_neutral_shape(context: Context, new_cat: ShapeKeysWidgetCategory) -> None:
    # Set the basis as "neutral" shape.
    sks = context.mesh.shape_keys
    basis_key_name = sks.key_blocks[0].name
    new_cat.neutral_key_name = basis_key_name
    # Add neutral shape to the shape keys collection.
    new_widget_key = new_cat.shape_keys.add()
    new_widget_key.shape_key_name = basis_key_name


class OperatorAddShapeKeysWidgetCategory(Operator, CreateShapeKeyWidgetsCategoryMixin):
    bl_idname = "shape_keys_widget.add_shape_keys_widget_category"
    bl_label = "Add Shape Keys Widget Category"
    bl_description = "Create an arrangement of shape keys to show in the 3D View"

    def invoke(self, context, event):
        # Nothing to configure before running this operator.
        return self.execute(context)

    def execute(self, context):

        # Create the new category with a unique ID.
        cats = context.mesh.shape_key_cats
        new_cat = create_and_add_category("Category", cats)

        add_basis_as_neutral_shape(context, new_cat)

        # Generate...
        # TODO

        return {'FINISHED'}


class OperatorCreateCatFromNamingConvention(Operator, CreateShapeKeyWidgetsCategoryMixin):
    bl_idname = "shape_keys_widget.create_category_from_naming_convention"
    bl_label = "Create Category from Naming Convention"
    bl_description = "Create SKW Category with shape keys matching an input string"

    input_str: StringProperty(
        name="Name to Match",
        description="Partial match to the naming convention used in the Shape Keys",
        default="Mouth -",
    )

    def execute(self, context):

        # Create the new category with a unique ID based on the naming convention.
        cats = context.mesh.shape_key_cats
        new_cat = create_and_add_category(self.input_str, cats)

        add_basis_as_neutral_shape(context, new_cat)

        # Find SKs based on the input naming convention
        shape_keys = context.object.data.shape_keys.key_blocks
        matching_sk_names = [name for name in shape_keys.keys() if self.input_str in name]

        # Add new shape keys to the widget.
        for sk_name in matching_sk_names:
            new_widget_key = new_cat.shape_keys.add()
            new_widget_key.shape_key_name = sk_name

        # Generate...
        # TODO

        return {'FINISHED'}


def get_sks_used_as_relative_to(self, context, edit_text):
    shape_keys = context.object.data.shape_keys.key_blocks

    base_sk_names = set()
    for sk in shape_keys:
        base_sk_names.add(sk.relative_key.name)

    return list(base_sk_names)

class OperatorCreateCatFromRelativeShape(Operator, CreateShapeKeyWidgetsCategoryMixin):
    bl_idname = "shape_keys_widget.create_category_from_relative_shape"
    bl_label = "Create Category from Relative Shape"
    bl_description = "Create SKW Category with shape keys having the same Relative To shape"

    sk_name: StringProperty(
        name="Relative To",
        description="Name of the Shape Key that the keys to add are relative to",
        default="",
        search=get_sks_used_as_relative_to
    )

    def execute(self, context):

        # Create the new category with a unique ID based on the naming convention.
        cats = context.mesh.shape_key_cats
        new_cat = create_and_add_category(self.sk_name, cats)

        sks = context.mesh.shape_keys.key_blocks
        sk = sks[self.sk_name]

        # Set the Relative To key as "neutral" shape.
        new_cat.neutral_key_name = self.sk_name
        # Add it to the widget, unless it is relative to itself, as then it will be added anyway.
        if sk.relative_key != sk:
            new_widget_key = new_cat.shape_keys.add()
            new_widget_key.shape_key_name = self.sk_name

        # Find SKs which are relative to the input SK.
        matching_sks = [sk for sk in sks.values() if sk.relative_key.name == self.sk_name]

        # Add new shape keys to the widget.
        for sk in matching_sks:
            new_widget_key = new_cat.shape_keys.add()
            new_widget_key.shape_key_name = sk.name

        # Generate...
        # TODO

        return {'FINISHED'}


def get_vertex_groups_used_by_sks(self, context, edit_text):
    shape_keys = context.object.data.shape_keys.key_blocks

    vtx_group_names = set()
    for sk in shape_keys:
        if sk.vertex_group:
            vtx_group_names.add(sk.vertex_group)

    return list(vtx_group_names)

class OperatorCreateCatFromVertexGroup(Operator, CreateShapeKeyWidgetsCategoryMixin):
    bl_idname = "shape_keys_widget.create_category_from_vertex_group"
    bl_label = "Create Category from Vertex Group"
    bl_description = "Create SKW Category with shape keys having the same Vertex Group"

    vtx_group_name: StringProperty(
        name="Vertex Group",
        description="Name of the Shape Key that the keys to add are relative to",
        default="",
        search=get_vertex_groups_used_by_sks
    )

    @classmethod
    def poll(cls, context):
        if not CreateShapeKeyWidgetsCategoryMixin.poll(context):
            return False
        if not get_vertex_groups_used_by_sks({}, context, ""):
            cls.poll_message_set("No Shape Keys of this Mesh use a Vertex Group")
            return False
        return True

    def execute(self, context):

        # Create the new category with a unique ID based on the naming convention.
        cats = context.mesh.shape_key_cats
        new_cat = create_and_add_category(self.vtx_group_name, cats)

        add_basis_as_neutral_shape(context, new_cat)

        # Find SKs which use the given Vertex Group.
        shape_keys = context.object.data.shape_keys.key_blocks
        matching_sks = [sk for sk in shape_keys.values() if sk.vertex_group == self.vtx_group_name]

        # Add new shape keys to the widget.
        for sk in matching_sks:
            new_widget_key = new_cat.shape_keys.add()
            new_widget_key.shape_key_name = sk.name

        # Generate...
        # TODO

        return {'FINISHED'}


class OperatorDelShapeKeysWidgetCategory(ShapeKeyWidgetsCategoryOperator):
    bl_idname = "shape_keys_widget.del_shape_keys_widget_category"
    bl_label = "Delete Shape Keys Widget Category"
    bl_description = "Delete the arrangement of shape keys, but not the keys themselves"

    def execute(self, context):
        """Called to finish this operator's action"""

        cats = context.mesh.shape_key_cats
        cat = cats[self.cat_idx]
        log.debug(f"Deleting Category '{cat.widget_name}'")

        # TODO tear down widget from rig.

        # Unlink the category.
        cats.remove(self.cat_idx)

        return {'FINISHED'}


def get_all_sks(self, context, edit_text):
    sk_names = bpy.context.object.data.shape_keys.key_blocks.keys()
    return sk_names


def get_all_sks_except_basis(self, context, edit_text):
    sk_names = bpy.context.object.data.shape_keys.key_blocks.keys()
    return [sk for sk in sk_names if sk != "Basis"]


def get_sks_not_added_yet(self, context, edit_text):
    sk_names = get_all_sks_except_basis(self, context, edit_text)

    cats = context.mesh.shape_key_cats
    cat = cats[self.cat_idx]
    shape_key_names_already_in_cat = [sk.shape_key_name for sk in cat.shape_keys]

    return [sk for sk in sk_names if sk not in shape_key_names_already_in_cat]


def get_sks_as_enum_items(self, context):
    sk_names = get_sks_not_added_yet(self, context, "")
    return [(sk, sk, sk) for sk in sk_names]


class OperatorAddShapeKeyToCategory(ShapeKeyWidgetsCategoryOperator):
    bl_idname = "shape_keys_widget.add_shape_key_to_category"
    bl_label = "Add Shape Key to Widget Category"
    bl_description = "Add the shape key to the widget"

    bl_property = "sk_name_search"  # For invoke_search_popup
    sk_name: StringProperty(
        name="Shape Key Name",
        description="Name of the Shape Key to add",
        default="",
        search=get_sks_not_added_yet
    )
    sk_name_search: EnumProperty(
        name="Shape Key Name",
        description="Name of the Shape Key to add",
        default="Eyes - Neutral",
        items=[('Eyes - Neutral', 'Eyes - Neutral', 'Eyes - Neutral'),
               ('Eyes - Open', 'Eyes - Open', 'Eyes - Open'),
               ('Eyes - Closed', 'Eyes - Closed', 'Eyes - Closed'),
               ('Mouth - Happy', 'Mouth - Happy', 'Mouth - Happy'),
               ('Mouth - Surprise', 'Mouth - Surprise', 'Mouth - Surprise'),
               ('Mouth - Sad', 'Mouth - Sad', 'Mouth - Sad'),
               ('Mouth - Neutral', 'Mouth - Neutral', 'Mouth - Neutral')],
        options=set(),
    )
    # items=get_sks_not_added_yet_as_enum_items

    def draw(self, context):
        row = self.layout.row()
        row.activate_init = True
        row.prop(self, "sk_name", text='')

    def invoke(self, context, event):
        """Present dialog to configure the properties before running the operator"""
        wm = context.window_manager
        return wm.invoke_props_popup(self, event)
        # return wm.invoke_search_popup(self)
        # return wm.invoke_props_dialog(self, width=200)
        # return wm.invoke_popup(self)

    def execute(self, context):
        """Called to finish this operator's action"""

        cats = context.mesh.shape_key_cats
        cat = cats[self.cat_idx]

        log.info(f"Adding SK '{self.sk_name}' to '{cat.widget_name}' category")

        # Add a new shape key to the widget.
        new_widget_key = cat.shape_keys.add()
        new_widget_key.shape_key_name = self.sk_name

        return {'FINISHED'}


class OperatorDelShapeKeyFromCategory(ShapeKeyWidgetsCategoryOperator):
    bl_idname = "shape_keys_widget.del_shape_key_from_category"
    bl_label = "Remove Shape Key from Widget Category"
    bl_description = "Remove the shape key from the widget"

    @classmethod
    def poll(cls, context):
        if not ShapeKeyWidgetsCategoryOperator.poll(context):
            return False

        # TODO can't do it like this, either there ends up being an active cat on the context.
        # TODO Or it needs to be polled after instancing.
        # Check that the Shape Key index to operate on is valid.
        # cats = context.mesh.shape_key_cats
        # cat = cats[cls.cat_idx]
        # if not 0 <= cat.active_sk_idx < len(cat.shape_keys):
        #     cls.poll_message_set("Widget category has no shape key selected")
        #     return False

        return True

    def execute(self, context):
        """Called to finish this operator's action"""

        cats = context.mesh.shape_key_cats
        cat = cats[self.cat_idx]
        sk_idx_to_remove = cat.active_sk_idx
        sk = cat.shape_keys[sk_idx_to_remove]

        log.info(f"Removing SK '{sk.shape_key_name}' from '{cat.widget_name}' category")

        # TODO tear down data.

        # Remove the Shape Key configuration from the category.
        cat.shape_keys.remove(sk_idx_to_remove)

        # Ensure the selected shape key is within range.
        num_sks = len(cat.shape_keys)
        if cat.active_sk_idx > (num_sks - 1) and num_sks > 0:
            cat.active_sk_idx = num_sks - 1

        return {'FINISHED'}


class OperatorMoveShapeKeyInCategory(ShapeKeyWidgetsCategoryOperator):
    bl_idname = "shape_keys_widget.move_shape_key_in_category"
    bl_label = "Move Shape Key in Widget Category"
    bl_description = "Move the active Shape Key in the category arrangement"

    direction: EnumProperty(
        name="Move Direction",
        description="Direction to move the active Shape Key: UP (default) or DOWN",
        items=[
            ('UP', "Up", "", -1),
            ('DOWN', "Down", "", 1),
        ],
        default='UP',
        options={'HIDDEN'},
    )

    def execute(self, context):
        """Called to finish this operator's action"""

        cats = context.mesh.shape_key_cats
        cat = cats[self.cat_idx]

        if not 0 <= cat.active_sk_idx < len(cat.shape_keys):
            # TODO also poll if not len(cat.shape_keys) > 1
            self.report({'ERROR'}, "Widget category has no shape key selected")
            return False

        active_idx = cat.active_sk_idx
        new_idx = active_idx + (-1 if self.direction == 'UP' else 1)

        if new_idx < 0 or new_idx >= len(cat.shape_keys):
            return {'FINISHED'}

        cat.shape_keys.move(active_idx, new_idx)
        cat.active_sk_idx = new_idx

        return {'FINISHED'}


class OperatorMuteShapeKeysInCategory(ShapeKeyWidgetsCategoryOperator):
    bl_idname = "shape_keys_widget.mute_shape_keys_in_category"
    bl_label = "Mute Shape Keys in Widget Category"
    bl_description = "Mute all the Shape Keys in the category"

    action: EnumProperty(
        name="Action",
        items=[
            ('MUTE', "Mute", ""),
            ('UNMUTE', "Unmute", ""),
        ],
        default='MUTE',
        options={'HIDDEN'},
    )

    def execute(self, context):
        """Called to finish this operator's action"""

        cat = getattr(context, "skw_category", None)
        if not cat:
            self.report({'ERROR'}, "Missing widget category to operate on")
            return False

        shape_keys = context.mesh.shape_keys.key_blocks

        make_mute = self.action == 'MUTE'

        log.info(f"{'Muting' if make_mute else 'Unmuting'} all "
                 f"{len(cat.shape_keys)} SKs from '{cat.widget_name}' category")

        missing_sk_names = []

        for skw_sk in cat.shape_keys:
            try:
                sk = shape_keys[skw_sk.shape_key_name]
                sk.mute = make_mute
            except KeyError:
                missing_sk_names.append(skw_sk.shape_key_name)

        if len(missing_sk_names) == 1:
            self.report(
                {'WARNING'},
                f"Could not find shape key '{missing_sk_names[0].shape_key_name}' to "
                f"{'mute' if make_mute else 'unmute'}"
            )
        elif len(missing_sk_names) > 1:
            names_str = ', '.join(f"'{n}'" for n in missing_sk_names)
            self.report(
                {'WARNING'},
                f"Operation failed for {len(missing_sk_names)} shape keys: {names_str}"
            )

        return {'FINISHED'}


# Add-on Registration #############################################################################

classes = (
    OperatorAddShapeKeysWidgetCategory,
    OperatorCreateCatFromNamingConvention,
    OperatorCreateCatFromRelativeShape,
    OperatorCreateCatFromVertexGroup,
    OperatorDelShapeKeysWidgetCategory,
    OperatorAddShapeKeyToCategory,
    OperatorDelShapeKeyFromCategory,
    OperatorMoveShapeKeyInCategory,
    OperatorMuteShapeKeysInCategory,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

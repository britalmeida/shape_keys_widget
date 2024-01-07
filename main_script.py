# SPDX-FileCopyrightText: 2024 Shape Keys Widget Authors
# SPDX-License-Identifier: GPL-3.0-or-later

#This version snaps the selector based on the buttons

import bpy
import os
import glob  # For file searching
import json
from bpy.app.handlers import persistent
import re
from bpy.props import PointerProperty


globalScale = 0.1
img_column_count = 5


#This funciton checks for moving Selectors in the scene. It'll then update the shape key value
@persistent
def obj_init(scene):
	# Replace "Selector Icon" and "Head" with the actual names of your objects
	character_obj = bpy.data.objects.get(bpy.context.scene.selected_character)
	current_category = bpy.context.scene.category_name

	if hasattr(bpy.context, "object"):
		selected_object = bpy.context.object

	for selected_object in bpy.context.selected_objects:
		# Check if the selected object has a parent
		if selected_object.parent:
			parent_name = selected_object.parent.name

			# If this object has a Selector Icon as a child
			if any("Selector Icon" in child.name for child in selected_object.parent.children):
				if not bpy.context.scene.category_name == parent_name:
					bpy.context.scene.category_name = parent_name

			# If the before location isn't equal to the current location then the object has moved
			if selected_object.before_loc != selected_object.location:

				bpy.context.scene.selected_expression_selector = selected_object.name
				selected_object.before_loc = selected_object.location

				# Loop through shape keys and check if the keyword is in the name
				for key in character_obj.data.shape_keys.key_blocks:
					# Skip the basis shape key
					if key.name == "Basis":
						continue

					# Skip shape keys with more than two dashes in the name
					if key.name.count('-') > 2:
						continue

					# Instead of updating all of them, only update the category you're currently moving
					if key.name.startswith(bpy.context.scene.category_name + " - "):

						# Check if the associated object exists in the scene
						associated_object = bpy.data.objects.get(key.name.replace(".L", "").replace(".R",""))
						if associated_object:
							# If we've selected either a Left or Right Selector
							if ".L" in selected_object.name and ".L" in key.name:
								key.value = character_obj.data[key.name]

							elif ".R" in selected_object.name and ".R" in key.name:
								key.value = character_obj.data[key.name]

							elif ".L" not in selected_object.name and ".R" not in selected_object.name:
								key.value = character_obj.data[key.name]
						else:
							print(f"Associated object for shape key {key.name} not found. Skipping.")

		# The object doesn't have a parent, therefore it is the parent object
		else:
			if selected_object.type == 'FONT':
				# Check if the text object has a child with a name containing "Selector Icon"
				if any("Selector Icon" in child.name for child in selected_object.children):
					# Set the category name to the name of the selected object
					if     not bpy.context.scene.category_name == selected_object.name:
						bpy.context.scene.category_name = selected_object.name
				else:
					print("Selected text object does not have a child with a name containing 'Selector Icon'")
			'''else:
				print("Selected object is not a text object")'''

bpy.app.handlers.depsgraph_update_post.append(obj_init)

def update_category(self, context):

	# Get the category name from the scene
	category_name = context.scene.category_name

	# Find the text object with the category name
	text_obj = bpy.data.objects.get(category_name)

	if text_obj:
		# The text object with the specified category name exists
		print(f"Found text object for category: {category_name}")

		# Set the snapping option based on the custom property
		snapping_option = text_obj.get("snapping_increment")

		# Ensure snapping_option is an integer
		try:
			snapping_option = int(snapping_option)
		except (ValueError, TypeError):
			print("Invalid snapping option, defaulting to OPTION1")
			snapping_option = 1

		# Prepend "OPTION" to the integer value
		snapping_option_str = f"OPTION{snapping_option}"

		# Set the snapping_str
		context.scene.snapping_str = snapping_option_str

	else:
		print(f"Text object not found for category: {category_name}")


def snapping_options(self, context):
	"""
	This function allows us to snap the location of the selector icon to different increments
	"""

	text_array = []
	selector_array = []

	# Loop through all selected objects
	for obj in bpy.context.selected_objects:
		# Check if the object is a Font object and has a child with the words "Selector Icon" in the name
		if obj.type == 'FONT' and any("Selector Icon" in child.name for child in obj.children):
			text_array.append(obj)

		# Check if the object has the name "Selector Icon"
		if "Selector Icon" in obj.name:
			# Add the object to the selector array list
			selector_array.append(obj)
			text_array.append(obj.parent)

	print(text_array)

	# Loop through all text objects
	for text_obj in text_array:
		# Check for children with the name "Selector Icon"
		selector_children = [child for child in text_obj.children if "Selector Icon" in child.name]

		# Add selector children to the selector array
		selector_array.extend(selector_children)

	print(selector_array)

	for text_obj in text_array:
		# Get the current snapping increment from the text object
		current_snapping_increment = text_obj.get("snapping_increment", 0)

		# Insert keyframes for all shape keys and selectors
		if self.snapping_str == "OPTION1" and current_snapping_increment != 1:

			if text_obj:
				print("Setting snapping to Off")
				text_obj["snapping_increment"] = 1  # Set the custom property value

			for selector in selector_array:
				driver_snap_location(selector, 0, 'LOC_X', 'var')
				driver_snap_location(selector, 1, 'LOC_Y', 'var')

		elif self.snapping_str == "OPTION2" and current_snapping_increment != 2:

			for selector in selector_array:
				driver_snap_location(selector, 0, 'LOC_X', 'round(var*40)/40')
				driver_snap_location(selector, 1, 'LOC_Y', 'round(var*40)/40')

			if text_obj:
				print("Setting snapping to 1/4")
				text_obj["snapping_increment"] = 2  # Set the custom property value

		elif self.snapping_str == "OPTION3" and current_snapping_increment != 3:

			for selector in selector_array:
				driver_snap_location(selector, 0, 'LOC_X', 'round(var*30)/30')
				driver_snap_location(selector, 1, 'LOC_Y', 'round(var*30)/30')

			if text_obj:
				print("Setting snapping to 1/3")
				text_obj["snapping_increment"] = 3  # Set the custom property value

		elif self.snapping_str == "OPTION4" and current_snapping_increment != 4:

			for selector in selector_array:
				driver_snap_location(selector, 0, 'LOC_X', 'round(var*20)/20')
				driver_snap_location(selector, 1, 'LOC_Y', 'round(var*20)/20')

			if text_obj:
				print("Setting snapping to 1/2")
				text_obj["snapping_increment"] = 4  # Set the custom property value

		elif self.snapping_str == "OPTION5" and current_snapping_increment != 5:

			for selector in selector_array:
				driver_snap_location(selector, 0, 'LOC_X', 'round(var*10)/10')
				driver_snap_location(selector, 1, 'LOC_Y', 'round(var*10)/10')

			if text_obj:
				print("Setting snapping to 1")
				text_obj["snapping_increment"] = 5  # Set the custom property value

def update_selected_character(self, context):

	#If the property is empty
	if not context.scene.prop:
		print("Property is empty")
		context.scene.selected_character = ""
	else:
		# Update the selected_character property when prop changes
		context.scene.selected_character = context.scene.prop.name

		print(f"Prop name: {context.scene.prop.name}")
		print(f"Selected Character name: {context.scene.selected_character}")

def image_path_updated_callback(self, context):
	"""
	This is a callback function that allows us to update anything when we change the selected image
	In this case, we're searching through the shape keys to find a matching shape key to save the user some time
	"""
	# Access the selected image path
	image_path = context.scene.image_path
	print(f"Image path: {image_path}")

	# Convert the relative path to an absolute path
	absolute_path = os.path.realpath(bpy.path.abspath(image_path))

	# Ensure the absolute path has a trailing backslash
	if not absolute_path.endswith(os.path.sep):
		absolute_path += os.path.sep

	print(f"Absolute path: {absolute_path}")

	# Check if the new path is different from the current path
	if context.scene.image_path != absolute_path:
		# Update the scene property with the absolute path
		context.scene.image_path = absolute_path


# Add properties to store the image file path, character model, shape key, and expression selector
bpy.types.Scene.image_path = bpy.props.StringProperty(
	name="Image Path",
	subtype='DIR_PATH',
	description = "Choose the folder where you want your images to be saved",
	update=image_path_updated_callback,
)
bpy.types.Scene.selected_character = bpy.props.StringProperty(
	name="Model",
	description="Select your character object"
)
bpy.types.Scene.selected_shape_key = bpy.props.EnumProperty(
	name="Shape Key",
	items=[],  # Will be populated dynamically
)
bpy.types.Scene.selected_expression_selector = bpy.props.StringProperty(
	name="Picker Object",
)
# Define a property to store the category name
bpy.types.Scene.category_name = bpy.props.StringProperty(
	name="Category Name",
	description="Enter the category name for expressions i.e. Mouth, Eyes, Eyebrows etc",
	default="Enter the category name",  # Set a default value if needed
	update=update_category,
)
# Define a property to store error messages
bpy.types.Scene.error_message = bpy.props.StringProperty(
	name="Error Message",
	description="Error message for the user",
	default="",
)
# Define a property to store the error type
bpy.types.Scene.error_type = bpy.props.EnumProperty(
	name="Error Type",
	items=[
		("ERROR", "Error", "Error message"),
		("INFO", "Info", "Info message"),
		("DEFAULT", "Default", "Default message"),
	],
	default="ERROR",  # Set the default error type
)
# Register the update callback
bpy.types.Scene.snapping_str = bpy.props.EnumProperty(
	items= [
	("OPTION1", "Off", "Turn Selector Snapping off"),
	("OPTION2", "1/4", "Snap to 1/4 increments"),
	("OPTION3", "1/3", "Snap to 1/3 increments"),
	("OPTION4", "1/2", "Snap to 1/2 increments"),
	("OPTION5", "1", "Snap to 1 unit increments"),
	],
	name="Button Array Property",
	description="Selector Snapping",
	default="OPTION1",
	update=snapping_options,  # This will execute the function when the property changes
)

class SKS_panel:
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Shape Key Selector"
	bl_options = {"HEADER_LAYOUT_EXPAND"}

#The primary panel, no parents
class MainPanel(SKS_panel, bpy.types.Panel):
	bl_idname = "_PT_Main_Panel"
	bl_label = "Shape Key Selector"

	def draw(self, context):
		pass

#subpanel only used as a grouping of child panels
class RequiredPanel(SKS_panel, bpy.types.Panel):
	bl_parent_id = "_PT_Main_Panel"
	bl_label = "Required Fields"
	bl_options = {'HIDE_HEADER'}

	def draw(self, context):
		layout = self.layout

		# Display the file picker for the image
		layout.prop(context.scene, "image_path", text="Folder Path")

		layout.prop(context.scene, "prop")

		# Inside the box for "Manually Add Expressions"
		layout.prop(context.scene, "category_name", text="Category Name")

		# In your UI layout, use the error_type to determine the icon
		if context.scene.error_type == "ERROR":
			layout.label(text=context.scene.error_message, icon="ERROR")
		elif context.scene.error_type == "INFO":
			layout.label(text=context.scene.error_message, icon="INFO")

	# Populate the shape keys section
	def populate_shape_key_items(self, context):
		# Function to dynamically populate shape key dropdown items
		items = []
		selected_character = context.scene.selected_character
		if selected_character:
			obj = bpy.data.objects[selected_character]
			if obj.type == 'MESH' and obj.data.shape_keys:
				for shape_key in obj.data.shape_keys.key_blocks:
					items.append((shape_key.name, shape_key.name, ""))

		return items



#subpanel only used as a grouping of child panels
class ManualPanel1(SKS_panel, bpy.types.Panel):
	bl_parent_id = "_PT_Main_Panel"
	bl_label = "Setup"
	bl_idname = "_PT_Manual_Panel1"
	bl_options = {"HEADER_LAYOUT_EXPAND"}

	def draw(self, context):
		layout = self.layout

		# Add a dropdown to select a shape key from the selected character
		layout.label(text="Select a Shape Key:")
		layout.prop(context.scene, "selected_shape_key", text="")

		#subpanel only used as a grouping of child panels

class ManualPanel2(SKS_panel, bpy.types.Panel):
	bl_parent_id = "_PT_Manual_Panel1"
	bl_label = "Set Up Shape Key Images"
	bl_idname = "_PT_Manual_Panel2"
	bl_options = {"HEADER_LAYOUT_EXPAND"}
	bl_order =1

	def draw(self, context):
		layout = self.layout

		layout.label(text="Set Up a Category:")

		layout.operator("expressions.add_neutral", icon='TOOL_SETTINGS')

		layout.separator()

		layout.label(text = "Render Shape Key Images:")
		row = layout.row()

		# Button for rendering a single image
		row.operator("expressions.render_single_image", icon='SCENE')
		row.operator("expressions.render_category", icon='CAMERA_DATA')
		row.operator("expressions.render_all", icon='OUTLINER_OB_CAMERA')

		layout.label(text = "Set Up Shape Key Images:")
		row = layout.row()
		row.operator("expressions.add_expression", icon='FILE_IMAGE')
		row.operator("expressions.bulk_add_expressions", icon='IMGDISPLAY')
		row.operator("expressions.bulk_add_all_expressions", icon='SHORTDISPLAY')

#child panel, without showing title
class ExtrasPanel(SKS_panel, bpy.types.Panel):
	bl_parent_id = "_PT_Main_Panel"
	bl_label = "Extras"
	bl_options = {"HEADER_LAYOUT_EXPAND"}

	def draw(self, context):
		layout = self.layout


		layout.label(text = "Selector Snapping:")
		# Add the EnumProperty (button array) to the panel
		layout.prop(context.scene, "snapping_str", expand=True)

		layout.separator()


		layout.label(text = "Insert Keyframes:")
		row = layout.row()
		# Add a dropdown to select a shape key from the selected character
		row.operator("expressions.insert_keyframes", icon='KEYTYPE_KEYFRAME_VEC')
		row.operator("expressions.insert_all_keyframes", icon='KEYTYPE_EXTREME_VEC')

		layout.separator()

		#child panel, without showing title
class OptionalPanel(SKS_panel, bpy.types.Panel):
	bl_parent_id = "_PT_Manual_Panel1"
	bl_label = "Optional Settings"
	#bl_options = {'HIDE_HEADER'}

	def draw(self, context):
		layout = self.layout

		layout.label(text="Before Setting up a Category:")

		layout.operator("object.rename_shape_keys", icon = 'LINENUMBERS_ON')

		# Add a dropdown to select a shape key from the selected character
		layout.operator("expressions.separate_lr", icon='MOD_PHYSICS')

		layout.operator("expressions.create_example_shape_keys", icon='PLUS')

		layout.operator("object.create_cameras", icon = 'SCENE')




class RenameShapeKeysOperator(bpy.types.Operator):
	bl_idname = "object.rename_shape_keys"
	bl_label = "Rename/Validate Shape Keys (Optional)"
	bl_description = "If you insert the ---- Label ---- shape keys, you can use this button to rename all of the shape keys for you. It will use the Label name and rename any shape keys under that label with the correct name. If you have already renamed them manually, you can use this to validate the shape keys which will make sure that all of the names match and that everything is spelled correctly"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		selected_character = context.scene.selected_character
		selected_character_obj = bpy.data.objects[selected_character]

		if selected_character_obj is None or selected_character_obj.type != 'MESH' or selected_character_obj.data.shape_keys is None:
			self.report({'ERROR_INVALID_INPUT'}, "Please select a mesh object with shape keys")
			return {'CANCELLED'}

		# Check if there is an "OTHER" label, if not, add a temporary label
		has_other_label = any("OTHER" in key.name for key in selected_character_obj.data.shape_keys.key_blocks)
		if not has_other_label:
			temp_label_key = selected_character_obj.shape_key_add(name="----- TEMP -----")
			temp_label_key.value = 0  # You can set the value to 0 or any other suitable value

		# Initialize variables
		labels = []
		normalised_labels = []

		# Iterate through shape keys to collect labels
		for key in selected_character_obj.data.shape_keys.key_blocks:
			# Skip the "Basis" shape key and temporary label
			if key.name == "Basis":
				continue

			# Check if the key is a label
			if key.name.count('-') > 2:
				label = key.name.strip('-').strip()
				labels.append(label)
				normalised_labels.append(label.title())

		print(labels)
		print(normalised_labels)

		# Iterate through labels to rename shape keys
		for i in range(len(labels) - 1):
			label_start = labels[i]
			label_end = labels[i + 1]
			normalised_label_start = normalised_labels[i]
			normalised_label_end = normalised_labels[i + 1]
			print(f"Start: {label_start}, End: {label_end}")

			renaming = False

			for shape_key in selected_character_obj.data.shape_keys.key_blocks:

				# When we reach the OTHER category then skip it
				if "OTHER" in shape_key.name:
					break

				# Skip the "Basis" shape key
				if shape_key.name == "Basis":
					continue

				# Check if the key is within the specified label range
				if shape_key.name.count('-') > 2:
					if label_start in shape_key.name and label_start == shape_key.name.strip('-').strip():
						renaming = True
					elif label_end in shape_key.name:
						renaming = False

				# Check if the label prefix is already present
				if renaming and normalised_label_start + " - " in shape_key.name:
					continue

				# Error checking: Replace incorrect label
				if renaming:
					# Ignore labels
					if not shape_key.name.count('-') > 2:
						if '-' in shape_key.name:
							# Extract the incorrect label and remove spaces to the right of the dash
							incorrect_label = shape_key.name.split("-")[0].rstrip()
							print(incorrect_label)
							shape_key.name = shape_key.name.replace(incorrect_label, "").strip().replace("-", "").replace("- ", "").replace(" -", "").replace(" - ", "")
							print(f"Shape key name after removing incorrect stuff: {shape_key.name}")

				# Rename shape keys within the specified range
				if renaming:
					if not shape_key.name.count('-') > 2:
						shape_key.name = shape_key.name.replace(normalised_label_start, "").strip()  # Extract category name
						print(f"Renaming: {shape_key.name} for category {normalised_label_start}")
						shape_key.name = f"{normalised_label_start} - {shape_key.name}"

						# Set the updated name
						shape_key.name = shape_key.name

		# Clean up: Remove the temporary label
		if not has_other_label:
			selected_character_obj.shape_key_remove(temp_label_key)

		return {'FINISHED'}






class CreateCamerasOperator(bpy.types.Operator):
	bl_idname = "object.create_cameras"
	bl_label = "Create Category Cameras (Optional)"
	bl_description = "Create cameras in your scene for each category of shape keys that you have"

	def execute(self, context):

		selected_character = context.scene.selected_character

		if selected_character == "":
			set_error_text(f"No model selected, please select a model with shape keys", "INFO")
			self.report({'INFO'}, "No model selected, please select a model with shape keys")
			return {'CANCELLED'}

		selected_shape_key = context.scene.selected_shape_key
		if selected_shape_key == "":
			set_error_text("This model has no shape keys. Please select a valid model", "INFO")
			self.report({'INFO'}, "This model has no shape keys. Please select a valid model")
			return {'CANCELLED'}

		categories = FindCategoriesInShapeKeys()
		print("Categories found:", categories)

		# Iterate through the categories and create a camera for each
		for category in categories:
			create_camera(category)

		return {'FINISHED'}


class RenderSingleImageOperator(bpy.types.Operator):
	bl_idname = "expressions.render_single_image"
	bl_label = "Render Shape Key"
	bl_description = "Renders a single 512px x 512px image for the shape key that you've selected. You must have a camera in your scene with the Category name in it"

	def execute(self, context):
		# Store the category and camera names from the FindCategories function
		category_names = [context.scene.category_name]

		RenderImages(self, category_names, 'SINGLE')

		return {'FINISHED'}

class RenderCategoryOperator(bpy.types.Operator):
	bl_idname = "expressions.render_category"
	bl_label = "Render Category"
	bl_description = "Renders all images for the category you've selected at 512px resolution. You must have a camera in your scene with the Category name in it"

	def execute(self, context):

		result = user_error_check(self, bpy.context)
		if result == {'CANCELLED'}:
			return {'CANCELLED'}  # Operator is cancelled due to errors

		category_names, camera_names = FindCategoriesInScene()

		# Flag to check if a matching camera is found
		camera_found = False

		selected_category = bpy.context.scene.category_name

		# Loop through all camera names
		for camera_name in camera_names:
			# If the name of the category exists in the camera name, set the flag and break
			if selected_category in camera_name:
				camera_found = True
				break

			# If a matching camera is found, break out of the outer loop
			if camera_found:
				break

		# If no matching camera is found, print an error and return {'CANCELLED'}
		if not camera_found:
			set_error_text(f"No camera found for category: {selected_category}", "INFO")
			return {'CANCELLED'}

		#Store the category and camera names from the FindCategories function
		category_names = [context.scene.category_name]

		RenderImages(self, category_names, 'ALL')

		return {'FINISHED'}

class RenderALLOperator(bpy.types.Operator):
	bl_idname = "expressions.render_all"
	bl_label = "Render ALL"
	bl_description = "Renders ALL images for ALL categories for your model at 512px resolution. You must have cameras that match all of your Categories"

	def execute(self, context):

		#Store the category and camera names from the FindCategories function
		category_names, camera_names = FindCategoriesInScene()

		print(f"Camera names: {camera_names}")

		RenderImages(self, category_names, 'ALL')

		return {'FINISHED'}

def RenderImages(self, category_array, type):
	"""
	This function will render and save images based on the parameters you pass in.
	This will control all 3 buttons, so it can render only a single image, a category of images, or all images

	Args:
		category_names: The array of categories to be rendered, set this to a single element to render one category
		type: The type of image we want to render 'SINGLE' or 'ALL'
	"""


	# Replace with the actual output folder path
	output_folder = bpy.context.scene.image_path

	# Store the name of the currently active camera before changing it
	previous_camera = bpy.context.scene.camera

	# Store the category and camera names from the FindCategories function
	category_names, camera_names = FindCategoriesInScene()

	# Access the selected character name
	selected_character = bpy.context.scene.selected_character


	# Get the Selected character object
	selected_character_obj = bpy.data.objects[selected_character]

	#Store all of the shape keys
	shape_keys = selected_character_obj.data.shape_keys.key_blocks

	selected_category = bpy.context.scene.category_name

	selected_shape_key = bpy.context.scene.selected_shape_key

	#If we only want to render a single image
	if type == 'SINGLE':

		if selected_shape_key == "Basis":
			set_error_text("The Basis Shape Key can not be rendered", "INFO")

			SetShapeKeyValues(selected_shape_key, category_names, 1.0)

			for shape_key in shape_keys:
				if shape_key.name == selected_category:
					selected_shape_key = shape_key.name
					break

			# Find and set the camera based on the shape key name
			SetCamera(category_array, camera_names, selected_shape_key)

			# Insert keyframes for all shape keys and selectors
			InsertDeleteKeyframes(category_names, 'INSERT')

			# If the name has a .L or .R then get rid of it when saving the image
			normalized_name = selected_category + " - Neutral"

			# Render and Save the image
			RenderAndSaveImage(output_folder, normalized_name)

			# Restore the previous active camera
			bpy.context.scene.camera = previous_camera

			# Set the shape key values back to 0
			SetShapeKeyValues(selected_shape_key, category_names, 0.0)

			# Delete the keyframes
			InsertDeleteKeyframes(category_names, 'DELETE')

			return {'CANCELLED'}  # Operator is cancelled due to errors

		if selected_shape_key.count('-') > 2:

			set_error_text(f"{selected_shape_key} is a label and can not be rendered", "INFO")

			return {'CANCELLED'}  # Operator is cancelled due to errors


		shape_key_category = selected_shape_key.split(" - ")
		single_category = []

		# Loop through the categories
		for category in category_names:

			# Check if any part of the shape key category is in the category name
			if any(part in category for part in shape_key_category):
				single_category.append(category)

		SetShapeKeyValues(selected_shape_key, single_category, 1.0)

		# Find and set the camera based on the shape key name
		SetCamera(category_array, camera_names, selected_shape_key)

		# Insert keyframes for all shape keys and selectors
		InsertDeleteKeyframes(category_names, 'INSERT')

		# If the name has a .L or .R then get rid of it when saving the image
		normalized_name = selected_shape_key.replace('.L', '').replace('.R', '')

		# Render and Save the image
		RenderAndSaveImage(output_folder, normalized_name)

		# Restore the previous active camera
		bpy.context.scene.camera = previous_camera

		# Set the shape key values back to 0
		SetShapeKeyValues(selected_shape_key, single_category, 0.0)

		# Delete the keyframes
		InsertDeleteKeyframes(category_names, 'DELETE')

	#if the type of image
	elif type == 'ALL':

		SetShapeKeyValues(selected_shape_key, category_array, 0.0)

		#Loop through the categories
		for category_name in category_array:
			print({category_name})
			#For all of the cameras in the scene
			for camera_name in camera_names:
				print({camera_name})
				#IF the name of the category exists in the camera name
				if category_name in camera_name:
					for shape_key in shape_keys:
						if category_name in shape_key.name:
							#Make that the active camera
							SetCamera(category_array, camera_names, shape_key.name)

							# Insert keyframes for all shape keys and selectors
							InsertDeleteKeyframes(category_names, 'INSERT')
							break

			normalized_name = f"{category_name} - Neutral.png"

			# Render and Save the image
			RenderAndSaveImage(output_folder, f"{category_name} - Neutral")

			SetShapeKeyValues(shape_key.name, category_array, 0.0)

			for shape_key in shape_keys:

				if selected_shape_key.count('-') > 2:

					set_error_text(f"{selected_shape_key} is a label and can not be rendered", "INFO")

					return {'CANCELLED'}  # Operator is cancelled due to errors

				# Check if the category name exists in the shape keys
				if category_name == shape_key.name.split(" - ")[0]:

					SetShapeKeyValues(shape_key.name, category_array, 1.0)

					# Find and set the camera based on the shape key name
					SetCamera(category_array, camera_names, shape_key.name)

					# Insert keyframes for all shape keys and selectors
					InsertDeleteKeyframes(category_array, 'INSERT')

					# If the name has a .L or .R then get rid of it when saving the image
					normalized_name = shape_key.name.replace('.L', '').replace('.R', '')

					# Render and Save the image
					RenderAndSaveImage(output_folder, normalized_name)

					# Set the shape key values back to 0
					SetShapeKeyValues(shape_key.name, category_array, 0.0)

					# Restore the previous active camera
					bpy.context.scene.camera = previous_camera

					# Delete the keyframes

			InsertDeleteKeyframes(category_names, 'DELETE')


def SetCamera(category_names, camera_names, selected_shape_key):
	"""
	This function will find and set the camera for the scene using the shape key name
	It extract the category name from the shape key and find a camera with that name

	Args:
		folder: The folder where we want to save our image
		image_name: The name of your image as a string
	"""
	current_shape_key_category = selected_shape_key.split()[0]

	found_camera = False  # Initialize a flag variable

	for category_name in category_names:
		if found_camera:
			break  # If a camera has already been found, break out of the outer loop
			return {'FINISHED'}

		for camera_name in camera_names:
			if current_shape_key_category in camera_name:
				bpy.context.scene.camera = bpy.data.objects[camera_name]
				#set_error_text(f"Set camera to '{camera_name}' for Category '{current_shape_key_category}'", "INFO")
				found_camera = True  # Set the flag to True to indicate a camera has been found
				break  # Break out of the inner loop
				return {'FINISHED'}


		if not found_camera:
			set_error_text(f"No camera found for Category name: '{current_shape_key_category}'", "INFO")
			return {'CANCELLED'}

def InsertDeleteKeyframes(category_names, type):
	"""
	This function will delete keyframes for all of the shape keys and the selectors on the current frame
	"""

	# Access the selected character name
	selected_character = bpy.context.scene.selected_character

	if selected_character == "":
		set_error_text(f"No model selected, please select a model with shape keys", "INFO")
		return {'CANCELLED'}

	# Get the Selected character object
	selected_character_obj = bpy.data.objects[selected_character]

	# Clear keyframes on the current frame
	current_frame = bpy.context.scene.frame_current

	shape_keys = None

	if selected_character_obj.data.shape_keys:
		# Store all of the shape keys
		shape_keys = selected_character_obj.data.shape_keys.key_blocks

	print (f"Category names: {category_names}")

	# If the shape keys exist and have elements
	if shape_keys:

		# Loop through all of the shape keys
		for shape_key in shape_keys:
			print (f"Current shape key: {shape_key.name}")
			# If the category name exists in the name of the shape keys
			for category_name in category_names:

				print ("Category: {category_name}, ShapeKey: {shape_key.name.split(' - ')[0]}")
				# Ignore any shape keys that don't have the category name, Basis and Labels
				if shape_key.name.split(' - ')[0] != category_name or shape_key.name == "Basis" or shape_key.name.count('-') > 2:
					continue

				print (f"Current category {category_name}")

				# Inserting the keyframe for that shape key
				if type == 'INSERT':
					shape_key.keyframe_insert(data_path="value", frame=current_frame)
					print(f"Inserting keyframe: {shape_key.name}")

				# Deleting the keyframe for that shape key
				elif type == 'DELETE':

					shape_key.keyframe_delete(data_path="value", frame=current_frame)
					print(f"Deleting keyframe: {shape_key.name}")

	else:
		set_error_text("This model has no shape keys. Please select a valid model", "INFO")
		return {'CANCELLED'}



	# Iterate through the category names array and keyframe the location of the Selector objects
	for category_name in category_names:
		# Search for Text object with the given category name
		text_obj = bpy.data.objects.get(category_name)

		#If a text object exists
		if text_obj:

			# Iterate through children of the Text object to find Selector Icons
			for child_obj in text_obj.children:
				#If we find a Selector object
				if child_obj.name.startswith("Selector Icon"):

					#Insert the location keyframe
					if type == 'INSERT':
						child_obj.keyframe_insert(data_path="location", frame=bpy.context.scene.frame_current, group="Location")
						#print(f"Inserting location keyframes for: {child_obj.name}")

						#Set the interpolation of the Selectors to Constant
						for fcurve in child_obj.animation_data.action.fcurves:
							if fcurve.data_path == 'location':
								fcurve.keyframe_points[-1].interpolation = 'CONSTANT'

					#Delete the location keyframe
					elif type == 'DELETE':
						child_obj.keyframe_delete(data_path="location", frame=bpy.context.scene.frame_current, group="Location")
						#print(f"Deleting location keyframes for: {child_obj.name}")


def RenderAndSaveImage(folder, image_name):
	"""
	This function will Render and Save an image to the folder directory and name it

	Args:
		folder: The folder where we want to save our image
		image_name: The name of your image as a string
	"""

	# Store the current resolution and percentage
	original_resolution_x = bpy.context.scene.render.resolution_x
	original_resolution_y = bpy.context.scene.render.resolution_y
	original_percentage_scale = bpy.context.scene.render.resolution_percentage

	# Store the current output folder, file format, and color mode
	original_output_path = bpy.context.scene.render.filepath
	original_file_format = bpy.context.scene.render.image_settings.file_format
	original_color_mode = bpy.context.scene.render.image_settings.color_mode

	# Set the desired values for renderinga
	bpy.context.scene.render.filepath = "/tmp/"
	bpy.context.scene.render.image_settings.file_format = 'PNG'
	bpy.context.scene.render.image_settings.color_mode = 'RGBA'

	# Set the desired resolution and percentage for rendering
	bpy.context.scene.render.resolution_x = 500
	bpy.context.scene.render.resolution_y = 500
	bpy.context.scene.render.resolution_percentage = 100

	# Render the image
	bpy.ops.render.render(write_still=True)

	output_file = os.path.join(folder, f"{image_name}.png")

	# Save the rendered image
	bpy.data.images['Render Result'].save_render(output_file)
	print(f"Rendered image for shape key '{image_name}'")

	# Restore the original output folder, file format, and color mode
	bpy.context.scene.render.filepath = original_output_path
	bpy.context.scene.render.image_settings.file_format = original_file_format
	bpy.context.scene.render.image_settings.color_mode = original_color_mode
	bpy.context.scene.render.resolution_x = original_resolution_x
	bpy.context.scene.render.resolution_y = original_resolution_y
	bpy.context.scene.render.resolution_percentage = original_percentage_scale



def SetShapeKeyValues(selected_shape_key, category_names, value):
	"""
	This function will set the values of shape keys by name. If it is a .L or .R it will set both shapes to the value
	Otherwise it will just set the name normally

	Args:
		selected_shape_key: The name if the shape key you want to set
		value: The new value of the shape key
	"""
	# Access the selected character name
	selected_character = bpy.context.scene.selected_character

	#Get the Selected character object
	selected_character_obj = bpy.data.objects[selected_character]

	#Store all of the shape keys
	shape_keys = selected_character_obj.data.shape_keys.key_blocks

	#If the shape keys exist and has elements
	if shape_keys:
		#Loop through all of the shape keys
		for shape_key in shape_keys:
			#If the category name exists in the name of the shape keys
			for category_name in category_names:
				#Ignore any shape keys that don't have the category name, Basis and Labels
				if not category_name in shape_key.name or shape_key.name == "Basis" or shape_key.name.count('-') > 2:
					continue

				print(f"Setting {shape_key.name} to {value}")
				shape_key.value = 0.0


	# Check if the shape key ends with .L or .R
	if selected_shape_key.endswith(".L") or selected_shape_key.endswith(".R"):
		print (f"Setting {selected_shape_key} to {value}")

		# Remove the .L from the name so all we have is Eyebrows - Raised etc.
		normalized_name = selected_shape_key.replace('.L', '').replace('.R', '')

		shape_key_L_name = normalized_name + ".L"
		shape_key_R_name = normalized_name + ".R"

		#Set the L and R key to be 1
		selected_character_obj.data.shape_keys.key_blocks[shape_key_L_name].value = value
		selected_character_obj.data.shape_keys.key_blocks[shape_key_R_name].value = value

	#If the shape key doesn't have a .L or .R then just render it
	else:
		print (f"Setting {selected_shape_key} to {value}")
		# Set the shape key to 1.0
		selected_character_obj.data.shape_keys.key_blocks[selected_shape_key].value = value


def FindCategoriesInScene():
	"""
	This function will find all of the categories that exist in your scene if you have a matching camera

	Returns:
		Returns a list of all categories in the scene

	"""

	#An empty list of category names
	category_names = set()
	#Storing the first word of all shape keys on the selected character
	shape_key_first_words = set()
	#Store a list of all the cameras in the scene
	camera_names = []

	# Access the selected character name
	selected_character = bpy.context.scene.selected_character

	if selected_character == "":
		set_error_text(f"No model selected, please select a model with shape keys", "INFO")
		return category_names, camera_names
		return {'CANCELLED'}

	#Getting the selected object
	selected_character_obj = bpy.data.objects[selected_character]


	#If the character exists, is a MESH and has shape keys
	if selected_character and selected_character_obj.type == 'MESH' and selected_character_obj.data.shape_keys:
		#Store the shape keys
		shape_keys = selected_character_obj.data.shape_keys.key_blocks

		#Loop through the shape keys
		for shape_key in shape_keys:
			#Ignore the Basis and Label keys
			if shape_key.name == "Basis" or shape_key.name.count('-') > 2:
				continue

			#Store and add the first word to the array
			left_of_dash = shape_key.name.split('-')[0].strip()
			shape_key_first_words.add(left_of_dash)
			print(f"Shape Key First Words: {left_of_dash}")


	# Loop through camera objects in the scene to get names
	for obj in bpy.data.objects:
		if obj.type == 'CAMERA':
			camera_names.append(obj.name)


	#print(f"Shape Key First Words: {shape_key_first_words}")
	#print(f"Camera Names: {camera_names}")

	#For all shape key first words
	for shape_key_name in shape_key_first_words:
		#For all cameras
		for camera_name in camera_names:
			#IF the first word of the shape key exists in the camera name
			if shape_key_name in camera_name:
				#Then we have found a category
				category_names.add(shape_key_name)

	#print(f"Categories: {category_names}")
	return category_names, camera_names

def FindCategoriesInFolder(folder_path):
	# Get a list of all files in the specified folder
	files = os.listdir(folder_path)

	# Extract the first word from each file name
	categories = [os.path.splitext(file)[0].split()[0] for file in files]

	# Filter out duplicate categories
	unique_categories = list(set(categories))

	return unique_categories

def FindCategoriesInShapeKeys():
	# Get the active object (assumes only one object is selected)

	# Access the selected character name
	selected_character = bpy.context.scene.selected_character

	if selected_character == "":
		set_error_text(f"No model selected, please select a model with shape keys", "INFO")
		return category_names, camera_names
		return {'CANCELLED'}

	#Getting the selected object
	selected_character_obj = bpy.data.objects[selected_character]

	# Get the shape keys of the active object
	shape_keys = selected_character_obj.data.shape_keys

	if not shape_keys:
		print("No shape keys found.")
		return []

	# Initialize an empty array to store categories
	category_array = []
	label_array = []


	# Iterate through shape keys
	for key in shape_keys.key_blocks:
		# Skip the "Basis" shape key
		if key.name == "Basis":
			continue

		# When we come to the labels, get the normalised version of the name and add this to another array
		# When we come to the labels, get the normalised version of the name and add this to another array
		if key.name.count('-') > 2:
			normalised_key_name = key.name.replace('-', '').lower()

			# Remove the first character if it is a space
			if normalised_key_name and normalised_key_name[0] == ' ':
				normalised_key_name = normalised_key_name[1:]

			# Remove the last character if it is a space
			if normalised_key_name and normalised_key_name[-1] == ' ':
				normalised_key_name = normalised_key_name[:-1]

			label_array.append(normalised_key_name)


		# Extract anything to the left of the dash from the shape key name
		left_of_dash = key.name.split('-')[0].strip()

		# Add it to the category array if it's not already present
		if left_of_dash not in category_array:
			category_array.append(left_of_dash)

	# Initialize an empty array to store the final categories
	final_categories = []

	print(f"Category array: {category_array}")
	print(f"Label array: {label_array}")

	# Compare elements in category_array and label_array
	for category in category_array:
		for label in label_array:
			if label in category.lower():
				# If there is a match, use the original category name and break the inner loop
				final_categories.append(category)
				break

	return final_categories



class InsertKeyframesOperator(bpy.types.Operator):
	bl_idname = "expressions.insert_keyframes"
	bl_label = "Keyframe Category"
	bl_description = "Insert keyframes for all shape keys for the selected Category"


	def execute(self, context):

		selected_category = bpy.context.scene.category_name

		# Check if a category is selected
		if not selected_category:
			set_error_text(f"Please select a category", "ERROR")
			return {'CANCELLED'}

		# Get the text from the "Category Name" property
		category_names = [context.scene.category_name]

		#Insert the keyframes
		InsertDeleteKeyframes(category_names, 'INSERT')

		return {'FINISHED'}


class InsertAllKeyframesOperator(bpy.types.Operator):
	bl_idname = "expressions.insert_all_keyframes"
	bl_label = "Keyframe ALL"
	bl_description = "Insert keyframes for ALL shape keys"

	def execute(self, context):

		#Store the category and camera names from the FindCategories function
		category_names, camera_names = FindCategoriesInScene()
		#Insert the keyframes
		InsertDeleteKeyframes(category_names, 'INSERT')

		return {'FINISHED'}

class CreateExampleShapeKeysOperator(bpy.types.Operator):
	bl_idname = "expressions.create_example_shape_keys"
	bl_label = "Create Example Shape Keys (Optional)"
	bl_description = "Create example shape keys if none exist on the selected character"

	def execute(self, context):
		# Access the selected character name
		selected_character = bpy.context.scene.selected_character

		if selected_character == "":
			set_error_text(f"No model selected, please select a model with shape keys", "INFO")
			self.report({'INFO'}, "No model selected, please select a model with shape keys")
			return {'CANCELLED'}

		# Get the Selected character object
		selected_character_obj = bpy.data.objects[selected_character]

		# Check if the character object has shape keys already
		if selected_character_obj.type == 'MESH' and selected_character_obj.data.shape_keys is None:
			# Create example shape keys with names like Mouth - Angry, Eyebrows - Sad, etc.
			shape_keys = selected_character_obj.shape_key_add(name="Basis")
			shape_keys = selected_character_obj.shape_key_add(name="---------- EYEBROWS ----------")
			shape_keys = selected_character_obj.shape_key_add(name="Eyebrows - Angry")
			shape_keys = selected_character_obj.shape_key_add(name="Eyebrows - Sad")
			shape_keys = selected_character_obj.shape_key_add(name="Eyebrows - Raised")
			shape_keys = selected_character_obj.shape_key_add(name="---------- MOUTH ----------")
			shape_keys = selected_character_obj.shape_key_add(name="Mouth - Happy")
			shape_keys = selected_character_obj.shape_key_add(name="Mouth - Sad")
			shape_keys = selected_character_obj.shape_key_add(name="Mouth - Open")
			shape_keys = selected_character_obj.shape_key_add(name="---------- MOUTH POSITION ----------")
			shape_keys = selected_character_obj.shape_key_add(name="Mouth Position - Left")
			shape_keys = selected_character_obj.shape_key_add(name="Mouth Position - Right")
			shape_keys = selected_character_obj.shape_key_add(name="Mouth Position - Up")
			shape_keys = selected_character_obj.shape_key_add(name="Mouth Position - Down")
			shape_keys = selected_character_obj.shape_key_add(name="---------- OTHER ----------")

			# Add more shape keys as needed

			set_error_text("Example shape keys created." , "INFO")

		else:
			set_error_text("Shape keys already exist on the selected character." , "INFO")

		return {'FINISHED'}

class SeparateLROperator(bpy.types.Operator):
	bl_idname = "expressions.separate_lr"
	bl_label = "Separate Shape Keys into .L and .R (Optional)"
	bl_description = "Separates the shape keys for the given category into Left and Right. DO THIS BEFORE YOU SET UP THE CATEGORY. Make sure you have two vertex groups LEFT SIDE and RIGHT SIDE with the repective parts of the model selected"

	def execute(self, context):

		result = user_error_check(self, context)
		if result == {'CANCELLED'}:
			return {'CANCELLED'}  # Operator is cancelled due to errors

		# Get the selected category
		current_category = context.scene.category_name

		# Check if a category is selected
		if not current_category:
			set_error_text(f"Please select a category", "ERROR")
			return {'CANCELLED'}

		# Get the text from the "Category Name" property
		category_name = context.scene.category_name

		# Check if there's an text object by name
		text_name = category_name
		text_obj = bpy.data.objects.get(text_name)

		#if not text_obj:
			#set_error_text(f"Category: '{category_name}' does not exist. Please setup the Category first", "ERROR")
			#return {'CANCELLED'}

		# Get the selected category
		current_category = context.scene.category_name

		selected_character = context.scene.selected_character

		# Check if a character is selected
		if selected_character:
			obj = bpy.data.objects[selected_character]

			# Check if the character is a mesh and has shape keys
			if obj.type == 'MESH' and obj.data.shape_keys:
				shape_keys = obj.data.shape_keys.key_blocks

				# Iterate through shape keys to find matching ones
				for shape_key in shape_keys:

					# Loop through all shape keys and set their values to 0
					for sk in shape_keys:
						sk.value = 0.0

					print (f"Current category: {current_category}, Shape key category: {shape_key.name.split(' - ')[0]}")

					if current_category == shape_key.name.split(" - ")[0] and not shape_key.name.endswith(".L") and not shape_key.name.endswith(".R"):

						# Create new names for the left and right shape keys
						left_name = f"{shape_key.name}.L"
						right_name = f"{shape_key.name}.R"

						print (f"Left name: {left_name}, Right name: {right_name}")

						# Set the value of the current shape key to 1
						shape_key.value = 1.0



						# Create a new shape key for the right side
						right_shape = obj.shape_key_add(name=right_name, from_mix=True)

						print("Created new shape from mix")

						# Set the value of the current shape key back to 0
						shape_key.value = 0.0
						# Set the value for the right shape key (if needed)
						right_shape.value = 0.0

						# Delete the original custom property
						#del obj.data[shape_key.name]

						# Rename the original shape key to ".L"
						shape_key.name = left_name

						if 'LEFT SIDE' not in obj.vertex_groups:
						  obj.vertex_groups.new(name='LEFT SIDE')

						if 'RIGHT SIDE' not in obj.vertex_groups:
						  obj.vertex_groups.new(name='RIGHT SIDE')

						#TODO Fix these lines
						obj.data.shape_keys.key_blocks[f"{left_name}"].vertex_group = "LEFT SIDE"
						obj.data.shape_keys.key_blocks[f"{right_name}"].vertex_group = "RIGHT SIDE"

						# Find the index of the original shape key
						original_index = obj.data.shape_keys.key_blocks.find(left_name)

						# Get the total number of shape keys
						total_shape_keys = len(obj.data.shape_keys.key_blocks)

						# Calculate the number of times to move the right shape key
						num_moves = total_shape_keys - original_index - 2

						# Select the right shape key
						obj.active_shape_key_index = total_shape_keys-1

						# Move the right shape key up the calculated number of times
						for _ in range(num_moves):
							bpy.ops.object.shape_key_move(type='UP')

						print("Moved the shape key up")



				set_error_text(f"The shape keys for the category '{current_category}' have been separated" , "INFO")
				return {'FINISHED'}

		self.report({'ERROR'}, "No valid character object selected.")
		return {'CANCELLED'}



class AddNeutralOperator(bpy.types.Operator):
	"""
	This is the function that runs when we click the Add Neutral Button.
	It will first of all , check for a Neutral expression within the folder.
	It will then create an image plane with the Neutral image.
	It will also create a Text header that will act as the parent for the expressions
	"""

	bl_idname = "expressions.add_neutral"
	bl_label = "Category Setup (Once Per Category)"
	bl_description = "This will load the Neutral image for your character, as well as set up the header and selector icon for the category"

	def execute(self, context):

		#The very first thing we need to is add a driver to any value to initialise the animation data
		# Get the active scene
		scene = bpy.context.scene

		# Access the selected image path
		image_path = context.scene.image_path
		# Specify the directory containing PNG files
		image_path_without_image = os.path.dirname(image_path)
		# Access the selected image path
		neutral_image_path = find_neutral_image(image_path_without_image, context.scene.category_name)

		if neutral_image_path:
			if not neutral_image_path.lower().endswith('.png'):
				set_error_text(f"Neutral image is not a .png - '{neutral_image_path.lower()}'", "INFO")
				# Access the selected image path
				return {'CANCELLED'}


		#IF we can't find the neutral image for the category, then just use the provided image instead
		if not neutral_image_path:
			set_error_text(f"Neutral expression image not found for category '{context.scene.category_name}'", "INFO")
			# Access the selected image path
			image_path = context.scene.image_path
			return {'CANCELLED'}

		else:
			image_path = neutral_image_path
			set_error_text("Found matching neutral image for category", "DEFAULT")

		# Get the text from the "Category Name" property
		category_name = context.scene.category_name

		# Check if the category name is empty
		if not category_name:
			category_name = "Default Text"  # Set a default text

		# Check if a text object with the same name already exists
		existing_text_obj = bpy.data.objects.get(category_name)
		if existing_text_obj:
			set_error_text(f"Text object with name '{category_name}' already exists", "INFO")
			return {'CANCELLED'}

		selected_character = context.scene.selected_character
		character_obj = bpy.data.objects[selected_character]

		# TODO Delete drivers before adding anything
		# We need a blank slate or it won't work
		# Set up the data path for the custom property

		# Loop through shape keys and check if the keyword is in the name
		for key in character_obj.data.shape_keys.key_blocks:
			#Skip the basis shape key
			if key.name == "Basis":
				 continue

			 # Skip shape keys with more than two dashes in the name
			if key.name.count('-') > 2:
				continue

			# Check if the category name is in the shape key name
			if bpy.context.scene.category_name == key.name.split("-")[0].replace(" ",""):
				data_path = f'["{key.name}"]'
				character_obj.data.driver_remove(data_path)

		# Define the category name
		category_name = bpy.context.scene.category_name

		# Create a list of custom property names containing the category name to delete
		properties_to_delete = [prop for prop in character_obj.data.keys() if category_name in prop and category_name != prop.split(" - ")[0].replace(" ","")]

		# Delete the custom properties outside of the loop
		for prop in properties_to_delete:
			del character_obj.data[prop]


		create_camera(category_name)


		# The first thing we need to do is add the custom properties to our character
		create_custom_properties(self, character_obj)

		# Create the image plane
		plane_obj = add_image_plane(image_path)

		#Create the text object using the category name
		text_obj = create_text_object(category_name)

		# Create a new collection for Shape Key Selectors if it doesn't exist
		selectors_collection = bpy.data.collections.get("Shape Key Selectors")

		if not selectors_collection:
			selectors_collection = bpy.data.collections.new("Shape Key Selectors")
			bpy.context.scene.collection.children.link(selectors_collection)


		# Parent the plane to the empty (hopefully this method will work nicer than setting the parent manually)
		set_object_parent(plane_obj, text_obj)

		# Check if the selected category has .L and .R shape keys
		selected_category = bpy.context.scene.category_name  # Replace with the actual way you select the category

		left_selector = None
		right_selector = None

		# Initialize a flag to check if we find ".L" or ".R" keys
		has_left_right_keys = False

		# Get the directory of the current script (main_script.py)
		script_directory = os.path.dirname(os.path.realpath(__file__))

		# Iterate through all shape keys of the character object
		for key in character_obj.data.shape_keys.key_blocks:
			if selected_category in key.name and (".L" in key.name or ".R" in key.name):
				has_left_right_keys = True
				break  # Exit the loop if we find at least one left or right key

		if has_left_right_keys:

			# Build the file path to the Selector.json file
			left_selector_file_path = os.path.join(script_directory, "Lselector.json")
			right_selector_file_path = os.path.join(script_directory, "Rselector.json")

			left_selector = import_json_as_model(left_selector_file_path, "Selector Icon.L")
			right_selector = import_json_as_model(right_selector_file_path, "Selector Icon.R")

			selectors = [left_selector, right_selector]
		else:

			# Build the file path to the Selector.json file
			selector_file_path = os.path.join(script_directory, "selector.json")

			selected_expression_selector = import_json_as_model(selector_file_path, "Selector Icon")

			selectors = [selected_expression_selector]

		for i in range(len(selectors)):
			selected_expression_selector = selectors[i]

			#If we successfully created the selector icon
			if selected_expression_selector:

				# Create a new Limit Location constraint
				limit_location_constraint = selected_expression_selector.constraints.new(type='LIMIT_LOCATION')

				# Set the constraint properties as needed
				limit_location_constraint.use_min_z = True
				limit_location_constraint.use_max_z = True
				limit_location_constraint.min_z = 0
				limit_location_constraint.max_z = 0
				limit_location_constraint.owner_space = 'LOCAL'
				limit_location_constraint.use_transform_limit = True


				# Set the newly created selector icon as the selected expression selector for our scene
				bpy.context.scene.selected_expression_selector = selected_expression_selector.name

				#And parent the selector to the text object
				set_object_parent(selected_expression_selector, text_obj)

			# Clear the Parent Inverse (this was the important bit, this will remove all
			# of the parent's transforms, but leave the relative transform
			plane_obj.select_set(True)
			bpy.ops.object.parent_clear(type='CLEAR_INVERSE')

			bpy.ops.object.select_all(action='DESELECT')
			# Select the selector and rotate it 90 degrees on the X-axis
			bpy.context.view_layer.objects.active = selected_expression_selector
			selected_expression_selector.select_set(True)
			bpy.ops.transform.rotate(value=1.5708, orient_axis='X')

		# Link the objects to the "Shape Key Selectors" collection
		collection_objects = [plane_obj, text_obj] + selectors

		for obj in collection_objects:
			# Check if the object is already in a collection, unlink it
			if obj.users_collection:
				old_collection = obj.users_collection[0]
				old_collection.objects.unlink(obj)

			# Link the object to the "Shape Key Selectors" collection
			selectors_collection.objects.link(obj)

		return {'FINISHED'}


def create_camera(category_name):
	# Check if the "Shape Key Cameras" collection exists, create it if not
	camera_collection = bpy.data.collections.get("Shape Key Cameras")

	if not camera_collection:
		camera_collection = bpy.data.collections.new("Shape Key Cameras")
		bpy.context.scene.collection.children.link(camera_collection)

	# Check if a camera with the given category name already exists
	existing_camera = bpy.data.objects.get(category_name + " Camera")

	if existing_camera:
		print(f"Camera with the name '{category_name} Camera' already exists.")
		return existing_camera

	# Create a new camera
	bpy.ops.object.camera_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), rotation=(0, 0, 0))
	new_camera = bpy.context.active_object

	# Set the camera name
	new_camera.name = category_name + " Camera"

	# Rotate the camera 90 degrees on the X axis
	bpy.context.view_layer.objects.active = new_camera
	bpy.ops.transform.rotate(value=-1.5708, orient_axis='X')

	# Set the viewport display size to 0.2m
	new_camera.data.display_size = 0.2

	# Check if the camera is already in a collection, unlink it
	if new_camera.users_collection:
		old_collection = new_camera.users_collection[0]
		old_collection.objects.unlink(new_camera)

	# Assign the camera to the "Shape Key Cameras" collection
	camera_collection.objects.link(new_camera)

	print(f"Camera '{category_name} Camera' created, rotated, viewport display size set, and added to 'Shape Key Cameras' collection.")

	return new_camera


# The Add Expressions function adds an image plane with the selected image,
# and along with that, adds the necessary drivers to the shape keys
class AddExpressionOperator(bpy.types.Operator):
	bl_idname = "expressions.add_expression"
	bl_label = "Add Single Image"
	bl_description = "Add an expression for your character. This will add the expression image to your scene, add the driver to the shape keys, and set up all of the necessary values"

	image_path: bpy.props.StringProperty(
		name="Image Path",
		subtype='FILE_PATH',
	)
	def execute(self, context):
		# Access the selected image path, character, expression selector, and shape key

		selected_character = context.scene.selected_character
		character_obj = bpy.data.objects[selected_character]
		# The first thing we need to do is add the custom properties to our character
		create_custom_properties(self, character_obj)

		result = user_error_check(self, context)
		if result == {'CANCELLED'}:
			return {'CANCELLED'}  # Operator is cancelled due to errors

		# Get the text from the "Category Name" property
		category_name = context.scene.category_name

		# Check if there's an text object by name
		text_name = category_name
		text_obj = bpy.data.objects.get(text_name)

		if not text_obj:
			set_error_text(f"Category: '{category_name}' does not exist. Please setup the Category first", "ERROR")
			return {'CANCELLED'}

		image_path = self.image_path
		if not image_path:
			image_path = bpy.context.scene.image_path
		else:
			image_path = self.image_path
		# Check if an object with the same name as the image already exists as a child of the text object
		image_name = os.path.splitext(os.path.basename(image_path))[0]

		# Loop through the children to find the object with a matching base name
		existing_image_obj = None
		for child_obj in text_obj.children:
			# Get the base name by removing ".L" or ".R" suffix from the child object name
			base_name = child_obj.name
			if base_name.endswith(".L") or base_name.endswith(".R"):
				base_name = base_name[:-2]  # Remove the last two characters (".L" or ".R")

			# Check for a match with the base name or the full name
			if base_name == image_name or child_obj.name == image_name:
				existing_image_obj = child_obj
				break

		if existing_image_obj:
			set_error_text(f"'{image_name}' already exists in the category '{category_name}'.", "ERROR")
			return {'CANCELLED'}


		# If the image path that we're providing doesn't end with .png
		if not image_path.endswith(".png"):
			# Then find the selected shape key and append it to the path
			selected_shape_key = bpy.context.scene.selected_shape_key
			normalized_shape_key_name = selected_shape_key.replace(".L", "").replace(".R", "")

			# Generate the image path based on the shape key name
			generated_image_path = os.path.join(image_path, f"{normalized_shape_key_name}.png")

			# Check if the file exists
			if not os.path.exists(generated_image_path):
				# Print an error to the console
				set_error_text(f"Image file does not exist at path: {generated_image_path}", "ERROR")
				# You can also raise an exception or handle the error in some way
				return {'CANCELLED'}

			# Set the image path to the generated path
			image_path = generated_image_path



		# Create the image plane
		plane_obj = add_image_plane(image_path)

		# Create a new collection for Shape Key Selectors if it doesn't exist
		selectors_collection = bpy.data.collections.get("Shape Key Selectors")

		# Link the plane_obj to the "Shape Key Selectors" collection
		if plane_obj:
			# Check if the object is already in a collection, unlink it
			if plane_obj.users_collection:
				old_collection = plane_obj.users_collection[0]
				old_collection.objects.unlink(plane_obj)

			# Link the object to the "Shape Key Selectors" collection
			selectors_collection.objects.link(plane_obj)

		left_selector = None
		right_selector = None

		# Initialize a flag to check if we find ".L" or ".R" keys
		has_left_right_keys = False

		selectors = []

		# Loop through children of text_obj and find all Selector Icon objects
		for child in text_obj.children:
			# Remove trailing numbers and periods and check if the name starts with "Selector Icon"
			#This might need to change, if someone has numbers after their expression it will break
			name_without_numbers = ''.join(filter(str.isalpha, child.name))

			if name_without_numbers == "SelectorIconL":
				left_selector = child
				selectors.append(left_selector)
				print("Added left selector to list")

			elif name_without_numbers == "SelectorIconR":
				right_selector = child
				selectors.append(right_selector)
				print("Added right selector to list")

			elif name_without_numbers == "SelectorIcon":
				selectors.append(child)
				print("Added single selector to list")

		selected_shape_key = context.scene.selected_shape_key
		selected_character = context.scene.selected_character

		# Loop through the found selector icons
		for selector_icon in selectors:
			# Set the selected expression selector to the child object's name
			context.scene.selected_expression_selector = selector_icon.name

			selected_expression_selector = context.scene.selected_expression_selector

			# Remove ".L" or ".R" at the end to get the actual name
			if selected_shape_key.endswith(".L") or selected_shape_key.endswith(".R"):
				actual_name = selected_shape_key[:-2]  # Remove the last two characters (".L" or ".R")
				left_shape_key = actual_name + ".L"
				right_shape_key = actual_name + ".R"

			else:
				selected_shape_key = context.scene.selected_shape_key


			print("Looping through selector icons")

			# Define a regex pattern to match ".L", ".R", or ".001" at the end of the string
			pattern = r'\.(L|R|\d+)$'

			# Set up a driver for the selected custom property on the character model
			if selected_character and selected_shape_key:

				obj = bpy.data.objects[selected_character]
				print("Object:", obj.name)

				if obj.type == 'MESH' and obj.data:
					print("Object type is MESH and has data")
					# Check if the custom property exists on the character object

					if selected_shape_key in obj.data:
						print(f"Custom property '{selected_shape_key}' exists on the object")

						# Define a regex pattern to match digits followed by a full stop at the end of the string
						pattern = r'\.\d+$'

						# Use re.sub to remove the matched pattern
						name_without_numbers = re.sub(pattern, '', selector_icon.name)

						#If the selector icon ends with .L
						if (name_without_numbers.endswith(".L")):
							selected_shape_key = left_shape_key

						elif (name_without_numbers.endswith(".R")):
							selected_shape_key = right_shape_key

						result = setup_shape_key_driver(obj, selected_shape_key, selected_expression_selector, plane_obj)
						print(f"The result after adding the drivers is: {result}")
						if result == {'CANCELLED'}:
							# Delete the plane_obj
							bpy.data.objects.remove(plane_obj, do_unlink=True)
							return {'CANCELLED'}  # Operator is cancelled due to errors

					else:
						print(f"Custom property '{selected_shape_key}' not found on the object")
				else:
					print("Object is not of type MESH or has no data")



		if text_obj:

			#If the text object exists, then we can remove the error message
			set_error_text("", "DEFAULT")

			selected_shape_key = context.scene.selected_shape_key

			# Initialize an offset variable
			offset_x = 0.0
			offset_y = 0.0

			# Set the maximum number of columns and spacing between rows and columns
			max_columns = img_column_count
			col_spacing = 0.11
			row_spacing = 0.11
			num_children = 0

			#If there's a left and right selector we need to move back one space, otherwise it will be two away from the previous one
			if selected_shape_key.endswith(".L") or selected_shape_key.endswith(".R"):
				# Calculate the offset based on the number of children
				num_children = len(text_obj.children)-2

			#Otherwise offset it only one unit away from the last image
			else:
				# Calculate the offset based on the number of children
				num_children = len(text_obj.children)-1

			print(f"Setting position for image: {num_children}")

			# Calculate the row and column based on the number of children
			row = num_children // max_columns
			col = num_children % max_columns

			print(f"Row: {row}, Column: {col}")

			# Update the offset for the next image
			offset_x = col * col_spacing
			offset_y = row * row_spacing

			# Move the plane to the calculated offset
			plane_obj.location.x += offset_x
			plane_obj.location.y -= offset_y

			# Parent the plane to the empty
			set_object_parent(plane_obj, text_obj)

			# Clear the Parent Inverse (this was the important bit, this will remove all
			# of the parent's transforms, but leave the relative transform
			plane_obj.select_set(True)
			bpy.ops.object.parent_clear(type='CLEAR_INVERSE')

		return {'FINISHED'}



# The Bulk Add Expressions function will add expressions matching shape keys
# from the specified image path
class BulkAddExpressionsOperator(bpy.types.Operator):
	bl_idname = "expressions.bulk_add_expressions"
	bl_label = "Add Category"
	bl_description = "Bulk add expressions for the provided Category. If the image name matches the shape key name exactly, it will add that expression"

	def execute(self, context):

		result = user_error_check(self, context)
		if result == {'CANCELLED'}:
			return {'CANCELLED'}  # Operator is cancelled due to errors

		bpy.ops.expressions.add_neutral()

		# Access the selected image path and character
		image_path = context.scene.image_path
		selected_character_name = context.scene.selected_character
		selected_character = bpy.data.objects.get(selected_character_name)

		# Specify the directory containing PNG files
		image_path_without_image = os.path.dirname(image_path)

		# Get a list of image files in the specified paths
		image_files = glob.glob(image_path_without_image + "/*.png")  # Adjust the file extension as needed

		# Print the shape keys
		shape_keys = selected_character.data.shape_keys.key_blocks
		print("Shape Keys:")
		for shape_key in shape_keys:
			print(shape_key.name)

		# Print the image filenames
		for image_file in image_files:
			# Extract the image name without extension
			image_name = os.path.splitext(os.path.basename(image_file))[0]

			# Check if the category name exists in the image name
			category_name = context.scene.category_name
			print(f"Category name: {category_name.lower()}, Image category: {image_name.lower().split('-')[0].replace(' ','')}")

			if not category_name.lower().replace(' ','') == image_name.lower().split('-')[0].replace(' ',''):
				print(f"Skipping image '{image_name}' as it does not belong to the selected category.")
				continue

			else:
				# Check if the image name matches any of the shape keys
				for shape_key in shape_keys:
					# Normalize the shape key name by removing ".L" or ".R" suffixes
					normalized_shape_key_name = shape_key.name.replace(".L", "").replace(".R", "")

					if image_name == normalized_shape_key_name:
						print(f"Matched: {image_name}")
						print(f"Setting selected shape key to: {shape_key.name}")
						# Set the selected shape key to the current image name
						context.scene.selected_shape_key = shape_key.name

						# Set the image to use before calling the "Add Expression" operator
						self.image_to_use = image_file
						print(f"It's trying to use: {self.image_to_use} as the image")

						# Call the "Add Expression" operator to add the expression
						bpy.ops.expressions.add_expression(image_path=self.image_to_use)
		return {'FINISHED'}



class BulkAddAllExpressionsOperator(bpy.types.Operator):
	bl_idname = "expressions.bulk_add_all_expressions"
	bl_label = "Add ALL Images"
	bl_description = "Bulk add ALL expressions. This will set up categories for all of the images that you have in your folder"

	def execute(self, context):

		selected_character = context.scene.selected_character

		if selected_character == "":
			set_error_text(f"No model selected, please select a model with shape keys", "INFO")
			self.report({'INFO'}, "No model selected, please select a model with shape keys")
			return {'CANCELLED'}

		selected_shape_key = context.scene.selected_shape_key
		if selected_shape_key == "":
			set_error_text("This model has no shape keys. Please select a valid model", "INFO")
			self.report({'INFO'}, "This model has no shape keys. Please select a valid model")
			return {'CANCELLED'}

		# Access the selected image path
		image_path = context.scene.image_path
		if not image_path:
			set_error_text(f"No folder selected, please select a folder", "INFO")
			self.report({'INFO'}, "No folder selected, please select a folder")
			return {'CANCELLED'}

		image_path = context.scene.image_path

		# Specify the directory containing PNG files
		image_path_without_image = os.path.dirname(image_path)

		# Get a list of image files in the specified paths
		image_files = glob.glob(image_path_without_image + "/*.png")  # Adjust the file extension as needed

		# Check if there are any image files in the folder
		if not image_files:
			set_error_text("No image files found in the specified folder", "ERROR")
			return {'CANCELLED'}

		# Get the list of categories from shape keys
		shape_key_categories = FindCategoriesInShapeKeys()

		# Create a set to store unique categories
		categories = set()

		# Iterate through image filenames
		for image_file in image_files:
			# Extract the image name without extension
			image_name = os.path.splitext(os.path.basename(image_file))[0]

			# Split the image name by space and take the first word as the category
			category = image_name.split(" - ")[0]

            #Check that the categories in the folder match the shape keys, we can't add a category that doesn't have a matching shape key
			if category in shape_key_categories:
				# Add the category to the set
				categories.add(category)

		for i in categories:
			print(f"Found categories: {i}")

		# Initialize a Z location offset so the categories won't be placed on top of one another
		z_offset = 0

		# Now, you have a set of unique categories
		# Iterate through the categories and add expressions for each one
		for category in categories:
			print(f"Category: {category}")

			# Assign the category based on the categories in your image file names
			context.scene.category_name = category
			print(f"Setting category name to: {context.scene.category_name}")

			bpy.ops.expressions.add_neutral()

			selected_character_name = context.scene.selected_character
			selected_character = bpy.data.objects.get(selected_character_name)

			# Print the shape keys
			shape_keys = selected_character.data.shape_keys.key_blocks

			# Get the number of images for the current category
			num_images_for_category = len([image_file for image_file in image_files if category.lower() in os.path.splitext(os.path.basename(image_file))[0].lower()])

			# Calculate the number of rows for the current category
			num_rows = (num_images_for_category - 1) // img_column_count + 1

			# Loop through the image files
			print("Image Files:")
			for image_file in image_files:
				# Extract the image name without extension
				image_name = os.path.splitext(os.path.basename(image_file))[0]
				print(image_name)

				# Check if the image name matches any of the shape keys
				for shape_key in shape_keys:
					# Normalize the shape key name by removing ".L" or ".R" suffixes
					normalized_shape_key_name = shape_key.name.replace(".L", "").replace(".R", "")

					if image_name == normalized_shape_key_name and category.lower() == normalized_shape_key_name.lower().split(' - ')[0]:
						print(f"Matched: {image_name}")
						print(f"Setting selected shape key to: {shape_key.name}")
						# Set the selected shape key to the current image name
						context.scene.selected_shape_key = shape_key.name

						# Set the image to use before calling the "Add Expression" operator
						self.image_to_use = image_file
						print(f"It's trying to use: {self.image_to_use} as the image")

						# Call the "Add Expression" operator to add the expression
						bpy.ops.expressions.add_expression(image_path=self.image_to_use)



						# Offset the Z location for the Text object based on the number of rows
						text_object = bpy.data.objects[category]
						text_object.location.z = z_offset

						# Deselect all objects
						bpy.ops.object.select_all(action='DESELECT')

			# Increment the Z offset for the next category
			z_offset -= num_rows * 0.11

		return {'FINISHED'}


# Simply adds an image plane to the scene using the image that we selected
def add_image_plane(image_path):
	"""
	This function adds a plane with the image that's provided as the material

	Args:
		image_path: The image file that we've selected.

	Returns:
		plane_obj: The created plane object
	"""

	image_texture = None

	# Try to load the image # Extract the image name from the path
	image_name = os.path.splitext(os.path.basename(image_path))[0] + ".png"
	print(image_name)

	# Check if the image already exists in Blender
	existing_image = bpy.data.images.get(image_name)
	if existing_image:
		image_texture = existing_image
	else:
		# Load the image into Blender
		image_texture = bpy.data.images.load(image_path)

	# Extract the shape key name from the image path
	shape_key_name = os.path.splitext(os.path.basename(image_path))[0]

	# Check if a material with the shape key name already exists
	mat = bpy.data.materials.get(shape_key_name)
	if not mat:
		# Create a new material
		mat = bpy.data.materials.new(name=shape_key_name)
		mat.use_nodes = True

		# Create an Image Texture node and assign the selected image
		image_texture_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
		image_texture_node.image = image_texture

		# Link the Image Texture node to the Material Output node
		shader_output_node = mat.node_tree.nodes["Material Output"]
		mat.node_tree.links.new(image_texture_node.outputs["Color"], shader_output_node.inputs["Surface"])

		# Update the view layer to ensure changes are applied
		bpy.context.view_layer.update()

	# Create a new plane
	bpy.ops.mesh.primitive_plane_add(size=globalScale, enter_editmode=False, align='WORLD', location=(0, 0, 0))
	# Set the plane object equal to the active object
	plane_obj = bpy.context.active_object

	# Rename the plane to match the shape key name
	plane_obj.name = shape_key_name

	# Assign the material to the plane
	plane_obj.data.materials.append(mat)

	# Snap the plane on the X and Y axis
	driver_snap_location(plane_obj, 0, 'LOC_X', 'round(var*10)/10')
	driver_snap_location(plane_obj, 1, 'LOC_Y', 'round(var*10)/10')

	# Create a new Limit Location constraint
	limit_location_constraint = plane_obj.constraints.new(type='LIMIT_LOCATION')

	# Set the constraint properties as needed
	limit_location_constraint.use_min_z = True
	limit_location_constraint.use_max_z = True
	limit_location_constraint.min_z = 0
	limit_location_constraint.max_z = 0
	limit_location_constraint.owner_space = 'LOCAL'
	limit_location_constraint.use_transform_limit = True

	# Deselect all objects
	bpy.ops.object.select_all(action='DESELECT')

	return plane_obj


def driver_snap_location(obj, property_index, transform_type, expression):
	"""
	This function takes in an object and makes it snap to the grid using location drivers

	Args:
		obj: The object you want to snap
		property_index: The property index represents the axis, 0-X, 1-Y, 2-Z
		transform_type: The type of transform we want to affect, so which transform, e.g. 'LOC_X'
	"""

	existing_driver = None
	if obj.animation_data is not None:
		for driver in obj.animation_data.drivers:
			if driver.data_path == f'location[{property_index}]':
				existing_driver = driver
				break

	# Remove the existing driver if it exists
	if existing_driver:
		obj.driver_remove(f'location[{property_index}]', -1)

	# Add a driver to the given axis
	dr = obj.driver_add("location", property_index)

	#if dr.modifiers[0] is not None:
		# Remove any modifiers
		#dr.modifiers.remove(dr.modifiers[0])

	# Add a variable to the driver
	var = dr.driver.variables.new()

	# Set the driver to be a Scripted Expression
	dr.driver.type = 'SCRIPTED'

	# Set the driver name
	var.name = 'var'  # You can give it a meaningful name

	# Set the expression for the driver variable
	var.type = 'TRANSFORMS'

	# Set the object field for the driver equal to the object that we pass in
	object1 = var.targets[0]
	object1.id = bpy.data.objects.get(obj.name)

	# Set the transform axis of the variable
	object1.transform_type = transform_type

	# Set the transform space of the variable
	object1.transform_space = 'TRANSFORM_SPACE'

	# Add the driver to the driver expression
	# round(var*10)/10 snaps the driver to increments of 0.1
	# but the scale of our images is 0.1 so really this is a scale of 1
	dr.driver.expression = f'{expression}'


def setup_shape_key_driver(character_obj, prop, expression_selector_obj, plane_obj):
	"""
	Add the driver to the custom property, setting the type to Averaged Value,
	and inserting keyframes to determine the value of the driver.

	Args:
		character_obj: This is the character object that contains the custom properties.
		prop: This is the property that we want to affect (e.g., "Mouth - Angry").
		expression_selector_obj: This is our Selector Icon object.
		plane_obj: This is the image plane object (i.e., our expression).
	"""

	# Check if the character object exists
	if character_obj:

		if prop in character_obj.data:

			# Set up the data path for the custom property
			data_path = f'["{prop}"]'

			# Create a driver for the custom property
			dr = character_obj.data.driver_add(data_path)

			for modifier in dr.modifiers:
				dr.modifiers.remove(modifier)

			#Remove any potential variables
			for var in dr.driver.variables:
				set_error_text(f"Shape key driver for '{prop}' already exists", "INFO")

				#We've found a matching driver, but the image has been deleted, so we just need to reassign it
				if var.targets[1].id == None:
					set_error_text(f"Shape key driver '{prop}' exists but the image has been deleted", "INFO")

					var.name = 'var'
					dr.driver.type = 'AVERAGE'
					#Assign the selector
					var.targets[0].id = bpy.data.objects.get(expression_selector_obj)
					#Assign the plane object
					var.targets[1].id = bpy.data.objects.get(plane_obj.name)
					return {'FINISHED'}

				# Set the type of the Driver to Averaged Value
				dr.driver.type = 'AVERAGE'
				return {'CANCELLED'}


			# Create a new variable
			var = dr.driver.variables.new()

			# Set the type of the Driver to Averaged Value
			dr.driver.type = 'AVERAGE'

			# Set the name of the driver variable
			var.name = 'var'

			# Set the type to 'SINGLE_PROP' for the custom property
			var.type = 'LOC_DIFF'

			# Set the targets for the custom property
			object1 = var.targets[0]
			object2 = var.targets[1]

			# Set object1 to be the Selector Icon and Object 2 to be the image plane
			object1.id = bpy.data.objects.get(expression_selector_obj)
			object2.id = bpy.data.objects.get(plane_obj.name)

			# Set the transform space to 'TRANSFORM_SPACE' for both targets
			object1.transform_space = 'TRANSFORM_SPACE'
			object2.transform_space = 'TRANSFORM_SPACE'

			# Insert keyframes for the custom property driver
			dr.keyframe_points.insert(-globalScale, 0)
			dr.keyframe_points.insert(0, 1)
			dr.keyframe_points.insert(globalScale, 0)

	return {'FINISHED'}


def import_json_as_model(file_path, name):
	"""
	This function loads in a JSON file as a model in our scene.
	In this case, it loads the selector icon from the JSON file.
	The selector icon is located in the E:/ Directory, this can be changed later

	Returns:
		object: This returns the Selector Icon model
	"""

	# Specify the path to your JSON file containing model data
	json_file_path = file_path

	with open(json_file_path, 'r') as json_file:
		model_data = json.load(json_file)

	# Retrieve the vertices, faces, material indices, and materials from the loaded data
	vertices = model_data.get('vertices', [])
	faces = model_data.get('faces', [])
	material_indices = model_data.get('material_indices', [])
	materials = model_data.get('materials', [])

	# Create a mesh and link it to the scene
	mesh = bpy.data.meshes.new(name)
	mesh.from_pydata(vertices, [], faces)

	# Create a new object and link it to the scene
	obj = bpy.data.objects.new(name, mesh)
	bpy.context.scene.collection.objects.link(obj)

	# Create materials and assign them to the object's material slots
	for material_data in materials:
		material_name = material_data.get('name', '')

		# Check if the material already exists
		material = bpy.data.materials.get(material_name)
		if not material:
			# Material does not exist, create a new one
			material = bpy.data.materials.new(material_name)
			material.diffuse_color = material_data.get('diffuse_color', [1, 1, 1, 1])  # Default color if not specified

			# Set the specular intensity component
			material.specular_intensity = material_data.get('specular_intensity', 0.0)  # Default to 0.0 if not specified

			# Add more material properties as needed

		# Assign the material to the object's material slots
		obj.data.materials.append(material)

	# Assign the materials to the object's faces based on material indices
	for face_index, material_index in enumerate(material_indices):
		if material_index < len(obj.data.materials):
			obj.data.polygons[face_index].material_index = material_index

	return obj


def set_error_text(error_message, error_type):
	"""
	This function simply outputs an error/info message to the UI, and we can give it an icon

	Args:
		error_message (str): The error message to display to the user
		error_type (str): The icon, this can one of three: "DEFAULT"(No Icon), "INFO", "ERROR"
	"""

	#Set the error message
	bpy.context.scene.error_message = error_message
	#Set the error icon
	bpy.context.scene.error_type = error_type

	#Print the error message to the console
	print(error_message)



def find_neutral_image(directory, category_name):
	"""
	This function will locate the neutral image in the folder

	Args:
		directory: The directory to search in
		category_name: The name of the category that the image should be added to (this might need to change, because if your image doesn't match the Category name, it doesn't do anything)

	Returns:
		object: This returns the location of the Neutral image
	"""
	# List all files in the specified directory
	files = os.listdir(directory)

	# Normalize the category name for searching (remove spaces and make it lowercase)
	normalized_category_name = category_name.replace(" ", "").lower()

	# Search for an image file containing both the category name and "Neutral" in its name
	for file in files:
		# Normalize the file name for searching (remove spaces and make it lowercase)
		normalized_file_name = file.replace(" ", "").lower()

		if normalized_category_name in normalized_file_name and "neutral" in normalized_file_name:
			return os.path.join(directory, file)

	return None


def create_text_object(name):
	"""
	This function will create a text object in the scene with the given name

	Args:
		name: This will be the name of the object and the body of the text

	Returns:
		text_obj: This returns the text object that we've created
	"""
	# Create a text object
	bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0,0,0), rotation=(1.5708, 0, 0))
	text_obj = bpy.context.active_object
	text_obj.data.offset_x = -0.07
	text_obj.name = name # You can choose a suitable name for the text object

	# Set the text content
	text_obj.data.body = name  # Replace with your desired text

	# Set the text size and other properties (you can adjust these as needed)
	text_obj.data.size = 0.05
	text_obj.data.align_x = 'RIGHT'
	text_obj.data.align_y = 'CENTER'

	# Add a custom property to the object, default is 5, which is the 5th Snapping option
	text_obj["snapping_increment"] = 1

	return text_obj


def set_object_parent(object_to_parent, parent_object):
	"""
	This function will parent an object to another object

	Args:
		object_to_parent: This is the object we want to be parented
		parent_object: This will be the parent object
	"""

	# Parent the plane to the empty (hopefully this method will work nicer than setting the parent manually)
	object_to_parent.select_set(True)
	parent_object.select_set(True)
	bpy.context.view_layer.objects.active = parent_object
	bpy.ops.object.parent_set(type='OBJECT')

# Define a callback function that will be called when the image path is updated
def image_path_updated_callback(self, context):
	# Access the selected image path
	image_path = context.scene.image_path

	# Extract the image name without extension
	image_name = os.path.splitext(os.path.basename(image_path))[0]

	# Access the selected character object
	selected_character = context.scene.selected_character

	# Check if a character is selected
	if selected_character:
		obj = bpy.data.objects[selected_character]

		# Check if the character is a mesh and has shape keys
		if obj.type == 'MESH' and obj.data.shape_keys:
			shape_keys = obj.data.shape_keys.key_blocks

			# Iterate through shape keys to find a matching one
			for shape_key in shape_keys:
				# Normalize the shape key name for comparison
				normalized_shape_key_name = shape_key.name.lower().replace(" ", "")

				# Normalize the image name for comparison
				normalized_image_name = image_name.lower().replace(" ", "")

				# Check if the normalized shape key name contains the normalized image name
				if normalized_image_name in normalized_shape_key_name:
					# Set the selected shape key to the matching shape key
					context.scene.selected_shape_key = shape_key.name
					return

	# If no matching shape key is found, set the selected shape key to an empty string
	context.scene.selected_shape_key = ""


def create_custom_properties(self, character_obj):

	# Iterate through shape keys
	for shape_key in character_obj.data.shape_keys.key_blocks:
		# Check if the custom property already exists

		if shape_key.name not in character_obj:
			if shape_key.name != "Basis" and not shape_key.name.isupper():
				# Create a custom property for the shape key
				character_obj.data[shape_key.name] = 0.0
				id_props = character_obj.data.id_properties_ui(shape_key.name)
				id_props.update(min=0.0, max=1.0,)

def user_error_check(self, context):
	selected_character = context.scene.selected_character

	if selected_character == "":
		set_error_text(f"No model selected, please select a model with shape keys", "INFO")
		self.report({'INFO'}, "No model selected, please select a model with shape keys")
		return {'CANCELLED'}

	selected_shape_key = context.scene.selected_shape_key
	if selected_shape_key == "":
		set_error_text("This model has no shape keys. Please select a valid model", "INFO")
		self.report({'INFO'}, "This model has no shape keys. Please select a valid model")
		return {'CANCELLED'}


	# Access the selected image path
	image_path = context.scene.image_path
	if not image_path:
		set_error_text(f"No folder selected, please select a folder", "INFO")
		self.report({'INFO'}, "No folder selected, please select a folder")
		return {'CANCELLED'}

	# Get the selected category
	current_category = context.scene.category_name

	# Check if a category is selected
	if not current_category:
		set_error_text(f"Please select a category", "ERROR")
		self.report({'INFO'}, "Please select a category")
		return {'CANCELLED'}

	return {'FINISHED'}

classes = (CreateExampleShapeKeysOperator,
		   MainPanel,
		   RequiredPanel,
		   ManualPanel1,
		   ManualPanel2,
		   OptionalPanel,
		   RenameShapeKeysOperator,
		   ExtrasPanel,
		   RenderALLOperator,
		   CreateCamerasOperator,
		   RenderCategoryOperator,
		   RenderSingleImageOperator,
		   InsertKeyframesOperator,
		   InsertAllKeyframesOperator,
		   SeparateLROperator,
		   AddNeutralOperator,
		   AddExpressionOperator,
		   BulkAddExpressionsOperator,
		   BulkAddAllExpressionsOperator)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.types.Object.before_loc = bpy.props.FloatVectorProperty(name="before_loc",
																subtype="TRANSLATION")
	#The prop funciton now updates
	bpy.types.Scene.prop = PointerProperty(
		type=bpy.types.Object,
		name = "Model",
		update=update_selected_character,
		description = "Select your character model that contains shape keys")

	# Populate the shape key dropdown dynamically
	bpy.types.Scene.selected_shape_key = bpy.props.EnumProperty(
		name="Shape Key",
		items=RequiredPanel.populate_shape_key_items,
	)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)


	del bpy.types.Object.before_loc

if __name__ == "__main__":
	register()

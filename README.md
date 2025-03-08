# Shape Keys Widget

Visual Shape Key selector for the 3D View in Blender.

Based on "Shape Key Selector V1.0" by Vertex Arcade.

## Usage

This add-on is Work In Progress.

Currently, it offers only conversion from characters already setup with the
"Shape Key Selector V1.0" add-on to a regular rig which doesn't rely on any script.  
This way, multiple characters can be added to the same shot, shape keys can be animated
in pose mode along with the bones, files can be sent to render farms without scripts,
and the "Shape Key Selector V1.0" add-on can be disabled to regain stability and performance.

### Converting an existing setup with Shape Key Selector V1.0 to a rig

In the `3D View` `Sidebar` (`N` key) shows a tab for `Shape Keys Widget`.  
Under `Migration from SKS` there is an operator with inputs for the names of an already existing character and shape keys.  
The operator will try to find existing thumbnail, text and cursor objects to delete them and re-create them as bones in an existing rig for the character.  
If the shape key widgets are the only rig wanted, create a new armature object with a single bone and parent the mesh to it.

1. Save first :)
2. Follow the tooltips and possible error messages of the operator until it manages to find all the different things to connect.
3. The operator is safe to re-run until there's no errors.
4. Confirm that moving a shape key widget in the `3D View` in `Pose Mode` will deform the character as expected and that the result looks good in the `Outliner`.
5. Save again!
6. The "Shape Key Selector V1.0" add-on should be disabled as it is no longer needed and it has stability and performance issues just by being enabled.
7. The character can now be animated by keying the cursor bones along with other bones of the rig.


### Creating a rig with visual shape key selectors without Shape Key Selector V1.0

Not implemented yet. Very much planned!


## Installation


### Installing as Extension

Note: this add-on is available as an extension, but is not on [extensions.blender.org](https://extensions.blender.org) since it's very work-in-progress still.

1. Download the [latest extension release from GitHub](https://github.com/britalmeida/push_to_talk/releases).
2. `Drag&drop` the ZIP into Blender.

### Installing as Legacy Add-on

1. Download the latest extension release or the repository as ZIP file.
2. In Blender's `Edit > Preferences > Add-ons`, click `Install` and select the ZIP.

### Updating

1. Remove a previous version if installed as an add-on:  
   In Blender's `Edit > Preferences > Add-ons`, find this add-on, expand it, and click `Remove`.
2. Download and install a new version as an extension.  
   New versions of an extension can simply be installed on top without needing to manually delete the previous version.
   This add-on is still provided as "Legacy Add-on" for versions of Blender 4.1 and older.


### Compatibility

| Blender Version   | Status      |
|-------------------|-------------|
| 4.3, 4.4, 4.5     | Supported   |
| 4.2 LTS           | Supported   |
| 3.6 LTS           | Supported   |
| 3.3 LTS and older | Unsupported |


## Development

This add-on is Work In Progress.

Currently, it has fully functional from a "Shape Key Selector V1.0" setup to a regular rig.

Next up, the plan is to make a workflow to create a rig setup from shape keys with new UI&UX.

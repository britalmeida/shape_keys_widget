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

In the `3D View` `Sidebar` (`N` key) shows a tab for `Shape Key Widgets`.  
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

1. Download this repository as ZIP file.
2. In Blender's `Edit > Preferences > Add-ons`, click `Install` and select the ZIP.

### Updating

1. Download the newest version ZIP.
2. In Blender's `Edit > Preferences > Add-ons`, find this add-on, expand it, and click `Remove`.
3. Click `Install` and select the ZIP.

**Alternatively:** this git repository can be **cloned** to a folder on disk and that folder linked to the `scripts/addons` folder of the Blender executable. This way, the add-on and be kept up to date with `git pull` without the need to remove/install it.

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

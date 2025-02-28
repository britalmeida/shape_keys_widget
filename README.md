# Shape Keys Widget

Visual Shape Key selector for the 3D View in Blender.

Based on "Shape Key Selector V1.0" by Vertex Arcade.

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

Currently, it has fully functional conversion from characters already setup with the
"Shape Key Selector V1.0" addon to a regular rig which doesn't rely on any script.  
This way, multiple characters can be added to the same shot, shape keys can be animated
in pose mode along with the bones, files can be sent to render farms without scripts,
and the "Shape Key Selector V1.0" add-on can be disabled to regain stability and performance.

Next up, the plan is to make a workflow to create a rig setup from shape keys with new UI&UX.

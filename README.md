# LP Script Box
LP Script Box is a Blender addon to help speed up Blender scripting workflow.
Manage, search, edit, run big collections of python scripts.

<!--toc:start-->
- [Features](#features)
- [Usage](#usage)
  - [Configuration](#configuration)
  - [Main Panel](#main-panel)
  - [Pinned Scripts](#pinned-scripts)
  - [Quick Access](#quick-access)
    - [Quick Run](#quick-run)
    - [Pinned Scripts Pie Menu](#pinned-scripts-pie-menu)
- [Installation](#installation)
<!--toc:end-->

## Features

- Manage, list and filter scripts in folder
- Run scripts without having to load them into text editor
- Quick open scripts to edit in internal or external editor
- Fuzzy search for scripts to either run, edit or create new
- Pin scripts for quick access
- Pie menu for quick execution while using mouse
- All features are made hotkey-friendly and easy to add to quick favorites menu

## Usage

### Configuration

- Select the directory where you want to save/load your scripts.
You can set this either from LP Script Box panel (3D Viewport > Sidebar > LP Tools):

	![](doc/script-dir-panel.jpg)

	Or from Addon Preferences:

	![](doc/preferences.jpg)

- Set external editor's path in Preferences if you want to use "Edit with External Editor" button.
For example: `nvim`, `subl`, `c:/vscode/code.exe`, etc.

### Main Panel

![](doc/buttons.jpg)

- Edit: open selected script in a floating internal editor window
- Run: run the selected script. Execution context is the current 3D Viewport.
- Edit with External Editor: open the selected script in an external text editor (specified in addon preferences). This button is disabled when external editor path is not set.
- Open Script Folder: open the directory in OS's default file explorer.

### Pinned Scripts

![](doc/pinned.jpg)

Use the Pin Script button to pin the currently selected script to this panel.
There's also a Pin button next to each script item in the list.

Each pinned script will become a button that can be assigned hotkeys or added to Quick Favorites menu.

Pinned scripts can be reordered using the Up/Down arrow buttons.
This is mostly intended to adjust scripts' positions within the [Pinned Scripts Pie Menu](#pinned-scripts-pie-menu)

### Quick Access

#### Quick Run
This operator (button) is intended for use with a hotkey/quick favorites. 

Press the assigned hotkey and type to instantly find and run scripts with fuzzy-matching suggestions.

![](doc/quick-run.gif)

If a script with matching name doesn't exist in the script directory,
open Blender's internal text editor to create a script with that name.

![](doc/quick-create-new.gif)

#### Pinned Scripts Pie Menu
This operator is intended for use with a hotkey.

Press the assigned hotkey to open a pie menu with the first 8 pinned scripts.
This allows quick execution while using mouse.

![](doc/pinned-pie.gif)

## Installation
Install the addon like you would install any legacy addon with a zip file.
Should be compatible with all version of Blender since 3.6.
Tested in Blender 3.6-4.4.

Edit > Preferences > Addons > Install from Disk > Select the zip file > Done

![](doc/install.jpg)


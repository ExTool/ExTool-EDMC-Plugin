# ExTool-EDMC-Plugin
A plugin for EDMC.

# Dependencies
Windows has no dependencies. The Win32 extensions do not need to be installed.
OS X needs the pyobjc-core and pyobjc module installed (in that order).
Linux needs the python3-xlib (or python-xlib for Python 2) module installed.

# Installation
Download the [latest release](https://github.com/ExTool/ExTool-EDMC-Plugin/releases/latest), open the archive (zip) and extract the folder to your EDMC plugin folder.

Rename the folder to ExTool

* Windows: `%LOCALAPPDATA%\EDMarketConnector\plugins` (usually `C:\Users\you\AppData\Local\EDMarketConnector\plugins`).
* Mac: `~/Library/Application Support/EDMarketConnector/plugins` (in Finder hold ⌥ and choose Go &rarr; Library to open your `~/Library` folder).
* Linux: `$XDG_DATA_HOME/EDMarketConnector/plugins`, or `~/.local/share/EDMarketConnector/plugins` if `$XDG_DATA_HOME` is unset.

You will need to re-start EDMC for it to notice the plugin.

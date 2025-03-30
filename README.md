# OBS via Python

## Installation

- Install `python` and `python-tk`
  - For macOS try: `brew install python@3.11 python-tk@3.11`, 3.12 is not supported in OBS for macOS when last checked.
- In OBS, go to **Tools** - **WebSocket Server Settings** and enable the WebSocket server. Generate a strong password, and then make a note of it as well as the proper port, which is `4455` by default.
- Copy `example.env` to your home directory as `.obs_scripts.env` and then update the password, image path, and anything else that you require.

```bash
python3.11 -m pip install --upgrade pip
pip3.11 install dotenv python-dotenv obs-websocket-py websocket-client Pillow FreeSimpleGUI
```

### For Windows and Linux

If you are not on macOS, you can use this script from within OBS, by taking the following steps.

- In OBS, you will need to open **Tools** - **Scripts** and:
  - Ensure that Python is configured and loaded. For the macOS example above, you would set the Python path to `/opt/homebrew/Cellar/python@3.11/3.11.11/Frameworks/` (but again this script won't work in macOS. It will crash OBS.)
- Restart OBS and then go ahead and navigate back to **Tools** - **Scripts** and load the `obs-rec-indicator.py` script.

If all goes well, it should work. If it doesn't work you should see the script logs in a new window, which you can use to troubleshoot.

### For macOS

If you are on macOS, you will need to run a script outside of OBS as integrating this feature directly within OBS using the Python scripting environment is problematic due to issues with GUI elements in multithreaded applications on macOS.

- Open up a terminal, navigate to the directory that contains this README file, and run the following command:

```bash
python ./ext-obs-rec-indicator.py
```

If all goes well, it should work. If it doesn't work you should see the script logs, which you can use to troubleshoot.

## Attribution

Initial code from: https://www.reddit.com/r/obs/comments/1eozoye/integrating_a_custom_recording_indicator_with_obs/

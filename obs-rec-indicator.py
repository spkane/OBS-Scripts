#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dotenv import load_dotenv
from obswebsocket import obsws, events
from PIL import Image
import FreeSimpleGUI as sg
import os

# Load the .env file
# This is necessary to get the password for the websocket connection
from pathlib import Path
home = Path.home()
load_dotenv(home / ".obs_scripts.env")

# OBS WebSocket connection settings
# Ensure you have a .env file with the following variables:
OBS_HOST = os.getenv('OBS_WS_HOST')
OBS_PORT = os.getenv('OBS_WS_PORT')
OBS_PASSWORD = os.getenv('OBS_WS_PW')
REC_ICON_PATH = os.getenv('OBS_REC_ICON_PATH')
PAUSE_ICON_PATH = os.getenv('OBS_PAUSE_ICON_PATH')

recording = False
pause = False
window = None
ws = None

def show_recording_indicator(type="recording"):
    """Create and display the recording indicator window in the top right corner with a slight gap."""
    screen_width, screen_height = sg.Window.get_screen_size()

    # Load the image to get its actual size using PIL
    if type == "recording":
        ICON_PATH = REC_ICON_PATH
    elif type == "paused":
        ICON_PATH = PAUSE_ICON_PATH
    with Image.open(ICON_PATH) as img:
        icon_width, icon_height = img.size

    # Calculate the position to place it in the top right corner with a gap
    x_position = screen_width - icon_width - (screen_width * .50)  # Adjusted to create a small gap on the right side
    y_position = 0  # Top alignment is fine

    layout = [[sg.Image(ICON_PATH, size=(255,255))]]
    window = sg.Window(
        'Recording Indicator',
        layout,
        no_titlebar=True,
        alpha_channel=0.8,
        keep_on_top=True,
        grab_anywhere=True,
        transparent_color=sg.theme_background_color(),
        location=(x_position, y_position)  # Position at top right with a gap
    )
    window.finalize()  # Ensure the window is properly rendered before use
    return window

def connect_to_obs():
    """Connect to OBS WebSocket server."""
    global ws
    ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
    try:
        ws.connect()
        print("Connected to OBS WebSocket server.")
    except Exception as e:
        print(f"Failed to connect to OBS WebSocket server: {e}")
        raise

def on_event(message):
    global recording, window
    print(f"Received event: {message}")

    if isinstance(message, events.RecordStateChanged):
        print(f"Handling RecordStateChanged event: {message}")
        if message.datain['outputState'] == 'OBS_WEBSOCKET_OUTPUT_STARTED':
            print("Recording started.")
            if not recording:
                recording = True
                window = show_recording_indicator(type="recording")
                window.read(timeout=10)
        if message.datain['outputState'] == 'OBS_WEBSOCKET_OUTPUT_PAUSED':
            print("Recording paused.")
            if recording:
                recording = False
            if not pause:
                pause = True
                if window:
                    window.close()
                    window = show_recording_indicator(type="paused")
                    window.read(timeout=10)
        if message.datain['outputState'] == 'OBS_WEBSOCKET_OUTPUT_RESUMED':
            print("Recording resumed.")
            if pause:
                pause = False
            if not recording:
                recording = True
                window.close()
                window = show_recording_indicator(type="recording")
        elif message.datain['outputState'] == 'OBS_WEBSOCKET_OUTPUT_STOPPED':
            print("Recording stopped.")
            if recording or pause:
                recording = False
                pause = False
                if window:
                    window.close()
                    window = None
    else:
        print(f"Unhandled event: {type(message)}")

def script_description():
    return "Display recording indicator when OBS starts/stops/pauses recording."

def script_load(settings):
    """Called on script load."""
    connect_to_obs()
    ws.register(on_event)

def script_unload():
    """Called when the script is unloaded."""
    global ws
    if ws:
        ws.disconnect()

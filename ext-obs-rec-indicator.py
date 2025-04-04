#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dotenv import load_dotenv
from obswebsocket import obsws, requests, events
from PIL import Image
import FreeSimpleGUI as sg
import os
import queue
import threading
import time

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

# Queue to handle communication between threads
event_queue = queue.Queue()

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
    x_position = screen_width - icon_width - (screen_width * .85)  # Adjusted to create a small gap on the right side
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
    ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
    try:
        ws.connect()
        print("Connected to OBS WebSocket server.")
    except Exception as e:
        print(f"Failed to connect to OBS WebSocket server: {e}")
        raise
    return ws

def handle_obs_events(ws):
    def on_event(message):
        print(f"Received event: {message}")
        event_queue.put(message)

    ws.register(on_event)

def process_gui_events(window, recording, pause):
    """Handle GUI events on the main thread."""
    while True:
        try:
            message = event_queue.get(timeout=1)  # Wait for a message from the queue
        except queue.Empty:
            continue

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
                    window.read(timeout=10)
            elif message.datain['outputState'] == 'OBS_WEBSOCKET_OUTPUT_STOPPED':
                print("Recording stopped.")
                if recording or pause:
                    recording = False
                    pause = False
                    if window:
                        window.close()
                        window = None

def main():
    recording = False
    pause = False
    window = None

    ws = connect_to_obs()

    # Start handling OBS events in the main thread
    threading.Thread(target=handle_obs_events, args=(ws,)).start()

    # Process GUI events on the main thread
    process_gui_events(window, recording, pause)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Script terminated by user.")
    finally:
        ws.disconnect()

if __name__ == "__main__":
    main(),

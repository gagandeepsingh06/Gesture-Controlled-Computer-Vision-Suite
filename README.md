# Gesture-Controlled Media Player

A lightweight Python application that maps simple hand gestures to media-control actions (play/pause, next/previous track, volume adjustments, mute) using your webcam.

This project combines real-time hand landmark detection with OS-level media key presses so you can control audio or video playback without touching the keyboard.

---

## Key Capabilities

- Detects single-hand poses and converts them to media actions.
- Supports: Play/Pause, Next Track, Previous Track, Volume Up, Volume Down, Mute.
- Low-latency capture using a background thread and small frame queue.
- On-screen feedback shows the current detected gesture.

---

## What You Need

- A webcam (built-in or USB).
- Python 3.8+.
- The libraries listed in `requirements.txt`.

---

## Install

1. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate      # Windows

# AGENTS.md

## Cursor Cloud specific instructions

### Overview

This is a single-file Python desktop tool (**Mouse Recorder**) that records and replays mouse operations. The entire application is `mouse_sequence_recorder.py`. Dependencies are listed in `requirements.txt`.

### Running in headless/cloud environments

- `pyautogui` and `pynput` require an X display. Start Xvfb before running:
  ```
  Xvfb :99 -screen 0 1280x1024x24 &
  export DISPLAY=:99
  ```
- System packages `python3-tk`, `python3-dev`, and `scrot` must be installed for `pyautogui` to work (these are pre-installed in the snapshot).

### Running the application

```bash
export DISPLAY=:99
python3 mouse_sequence_recorder.py
```

The app is interactive (waits for mouse/keyboard input). For programmatic testing, import `MouseRecorder`, `MouseEvent`, and `MouseAction` from the module and call methods directly.

### Testing

There is no automated test suite. To verify the core functionality programmatically, create `MouseEvent` objects, call `recorder.save_positions(events)` to test JSON serialization, and `recorder.execute_sequence(events, num_loops=1)` to test replay on the virtual display.

### Lint

No linter is configured in this project.

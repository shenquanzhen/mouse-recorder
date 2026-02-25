import importlib
import json
import sys
import types


def _import_recorder_with_stubs(monkeypatch):
    pyautogui = types.ModuleType("pyautogui")
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0

    def _noop(*_args, **_kwargs):
        return None

    pyautogui.position = lambda: (0, 0)
    pyautogui.moveTo = _noop
    pyautogui.click = _noop
    pyautogui.rightClick = _noop
    pyautogui.doubleClick = _noop

    keyboard = types.ModuleType("pynput.keyboard")

    class Key:
        esc = object()
        cmd = object()

    class KeyCode:
        @staticmethod
        def from_char(c):
            return ("char", c)

    class Listener:
        def __init__(self, *args, **kwargs):
            self.running = True

        def start(self):
            return None

        def stop(self):
            self.running = False
            return None

    keyboard.Key = Key
    keyboard.KeyCode = KeyCode
    keyboard.Listener = Listener

    mouse = types.ModuleType("pynput.mouse")

    class Button:
        left = object()
        right = object()

    mouse.Button = Button
    mouse.Listener = Listener

    pynput = types.ModuleType("pynput")
    pynput.keyboard = keyboard
    pynput.mouse = mouse

    monkeypatch.setitem(sys.modules, "pyautogui", pyautogui)
    monkeypatch.setitem(sys.modules, "pynput", pynput)
    monkeypatch.setitem(sys.modules, "pynput.keyboard", keyboard)
    monkeypatch.setitem(sys.modules, "pynput.mouse", mouse)

    sys.modules.pop("mouse_sequence_recorder", None)
    return importlib.import_module("mouse_sequence_recorder")


def test_on_mouse_click_double_click(monkeypatch):
    mod = _import_recorder_with_stubs(monkeypatch)
    recorder = mod.MouseRecorder()

    now = {"t": 1000.0}
    monkeypatch.setattr(mod.time, "time", lambda: now["t"])

    recorder.on_mouse_click(10, 20, mod.mouse.Button.left, True)
    now["t"] += 0.1
    recorder.on_mouse_click(10, 20, mod.mouse.Button.left, True)

    assert [e.action_type for e in recorder.recorded_events] == [
        mod.MouseAction.LEFT_CLICK,
        mod.MouseAction.DOUBLE_CLICK,
    ]


def test_on_mouse_click_right_click(monkeypatch):
    mod = _import_recorder_with_stubs(monkeypatch)
    recorder = mod.MouseRecorder()

    monkeypatch.setattr(mod.time, "time", lambda: 2000.0)
    recorder.on_mouse_click(7, 8, mod.mouse.Button.right, True)

    assert len(recorder.recorded_events) == 1
    assert recorder.recorded_events[0].action_type == mod.MouseAction.RIGHT_CLICK
    assert recorder.recorded_events[0].position == (7, 8)


def test_save_positions_writes_json(tmp_path, monkeypatch):
    mod = _import_recorder_with_stubs(monkeypatch)
    recorder = mod.MouseRecorder()

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(recorder, "get_current_time", lambda: "2026-02-25 00:00:00.000")
    monkeypatch.setattr(mod.time, "time", lambda: 111.0)

    events = [
        mod.MouseEvent(mod.MouseAction.MOVE, (1, 2)),
        mod.MouseEvent(mod.MouseAction.LEFT_CLICK, (3, 4)),
    ]
    recorder.save_positions(events)

    output_path = tmp_path / "mouse_actions_2026-02-25 00-00-00.000.json"
    assert output_path.exists()

    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data == [
        {"action_type": "move", "position": [1, 2], "timestamp": 111.0},
        {"action_type": "left_click", "position": [3, 4], "timestamp": 111.0},
    ]

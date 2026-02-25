import pyautogui
from pynput import keyboard, mouse
import time
from datetime import datetime
import sys
import signal
import threading
import json
import select
from enum import Enum

class MouseAction(Enum):
    MOVE = "move"
    LEFT_CLICK = "left_click"
    RIGHT_CLICK = "right_click"
    DOUBLE_CLICK = "double_click"

class MouseEvent:
    def __init__(self, action_type, position):
        self.action_type = action_type
        self.position = position
        self.timestamp = time.time()

class MouseRecorder:
    def __init__(self):
        self.running = True
        self.recorded_events = []
        self.keyboard_listener = None
        self.mouse_listener = None
        self.last_click_time = 0
        self.last_click_position = None
        self.last_move_time = 0
        self.last_move_position = None
        self.DOUBLE_CLICK_TIME = 0.3  # 双击判定时间间隔（秒）
        self.POSITION_RECORD_TIME = 3.0  # 停留记录时间（秒）
        
        # 设置pyautogui的安全特性
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        self.Y_OFFSET = 27
#       self.Y_OFFSET = 27  原来配合fyiddler的代码，现在不需要了，因为微信调整置顶，


    def get_current_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    def log_action(self, action):
        print(f"[{self.get_current_time()}] {action}")

    def update_coordinate_display(self):
        while self.running:
            try:
                x, y = pyautogui.position()
                current_time = time.time()
                
                # 检查鼠标是否在同一位置停留足够长的时间
                if (self.last_move_position and 
                    self.last_move_position == (x, y) and 
                    current_time - self.last_move_time >= self.POSITION_RECORD_TIME):
                    # 只有当最后一个事件不是移动事件或位置不同时才记录
                    if (not self.recorded_events or 
                        self.recorded_events[-1].action_type != MouseAction.MOVE or 
                        self.recorded_events[-1].position != (x, y)):
                        self.recorded_events.append(MouseEvent(MouseAction.MOVE, (x, y)))
                        self.log_action(f"记录停留位置: ({x}, {y})")
                        # 重置时间，避免重复记录
                        self.last_move_time = current_time
                
                print(f"\r当前坐标 - X: {x}, Y: {y}    ", end='')
                time.sleep(0.1)
            except:
                pass

    def on_keyboard_press(self, key):
        try:
            if key == keyboard.Key.esc or key == keyboard.Key.cmd or \
               key == keyboard.KeyCode.from_char('q'):
                self._stop_recording()
                return False
        except AttributeError:
            pass

    def on_mouse_click(self, x, y, button, pressed):
        if not pressed or not self.running:
            return
        
        current_time = time.time()
        current_position = (x, y)
        
        if button == mouse.Button.left:
            # 检查是否是双击
            if (self.last_click_position == current_position and 
                current_time - self.last_click_time < self.DOUBLE_CLICK_TIME):
                self.recorded_events.append(MouseEvent(MouseAction.DOUBLE_CLICK, current_position))
                self.log_action(f"记录双击: {current_position}")
            else:
                self.recorded_events.append(MouseEvent(MouseAction.LEFT_CLICK, current_position))
                self.log_action(f"记录左键单击: {current_position}")
            
            self.last_click_time = current_time
            self.last_click_position = current_position
            
        elif button == mouse.Button.right:
            self.recorded_events.append(MouseEvent(MouseAction.RIGHT_CLICK, current_position))
            self.log_action(f"记录右键单击: {current_position}")

    def on_mouse_move(self, x, y):
        if not self.running:
            return
        current_time = time.time()
        current_position = (x, y)
        
        # 更新最后移动时间和位置
        if self.last_move_position != current_position:
            self.last_move_time = current_time
            self.last_move_position = current_position

    def _stop_recording(self, signum=None, frame=None):
        """统一的停止录制方法，可由信号、键盘监听或终端输入触发"""
        if self.running:
            print("\n用户触发停止记录")
            self.running = False

    def _stdin_watch_thread(self):
        """监听终端回车键作为备用退出方式"""
        while self.running:
            try:
                if select.select([sys.stdin], [], [], 0.5)[0]:
                    sys.stdin.readline()
                    self._stop_recording()
                    return
            except Exception:
                return

    def record_positions(self):
        self.recorded_events = []
        self.running = True
        self.keyboard_listener = None
        self.mouse_listener = None
        self.last_move_time = time.time()
        self.last_move_position = None

        original_sigint = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self._stop_recording)
        
        try:
            self.keyboard_listener = keyboard.Listener(on_press=self.on_keyboard_press)
            self.mouse_listener = mouse.Listener(
                on_click=self.on_mouse_click,
                on_move=self.on_mouse_move
            )
            
            self.keyboard_listener.start()
            self.mouse_listener.start()
            
            stdin_thread = threading.Thread(target=self._stdin_watch_thread)
            stdin_thread.daemon = True
            stdin_thread.start()

            coord_thread = threading.Thread(target=self.update_coordinate_display)
            coord_thread.daemon = True
            coord_thread.start()
            
            print("\n=== 鼠标操作记录工具 ===")
            print("支持的操作：")
            print("1. 鼠标停留3秒自动记录位置")
            print("2. 左键单击")
            print("3. 右键单击")
            print("4. 双击（快速连续两次左键）")
            print("\n注意：")
            print("- 鼠标在任意位置停留3秒将自动记录该位置")
            print("- 所有点击操作都会被自动记录")
            print("- 按ESC/Q键结束记录，或在终端按回车/Ctrl+C结束记录")
            
            while self.running:
                time.sleep(0.5)
            
        except (KeyboardInterrupt, SystemExit):
            self.running = False
        finally:
            signal.signal(signal.SIGINT, original_sigint)
            if self.keyboard_listener:
                try:
                    self.keyboard_listener.stop()
                except Exception:
                    pass
                self.keyboard_listener = None
            if self.mouse_listener:
                try:
                    self.mouse_listener.stop()
                except Exception:
                    pass
                self.mouse_listener = None
            self.running = False
            return self.recorded_events

    def execute_sequence(self, events, num_loops=1):
        try:
            print(f"\n开始执行操作序列，循环次数: {num_loops}")
            print("注意：执行过程中按ESC/Q/Command键可以终止操作")
            
            execute_listener = None
            try:
                execute_listener = keyboard.Listener(on_press=lambda key: 
                    self.on_execute_key_press(key, execute_listener))
                execute_listener.start()
                
                for loop in range(num_loops):
                    if not execute_listener.running:
                        break
                    
                    print(f"\n=== 第 {loop + 1} 次循环 ===")
                    
                    for i, event in enumerate(events):
                        if not execute_listener.running:
                            break
                        
                        pos = event.position
                        y_offset = loop * self.Y_OFFSET if i == 0 else 0
                        new_pos = (pos[0], pos[1] + y_offset)
                        
                        # 执行不同类型的鼠标操作
                        if event.action_type == MouseAction.MOVE:
                            pyautogui.moveTo(new_pos[0], new_pos[1], duration=0.5)
                            self.log_action(f"移动到位置: {new_pos}")
                        elif event.action_type == MouseAction.LEFT_CLICK:
                            pyautogui.click(new_pos[0], new_pos[1])
                            self.log_action(f"左键单击位置: {new_pos}")
                        elif event.action_type == MouseAction.RIGHT_CLICK:
                            pyautogui.rightClick(new_pos[0], new_pos[1])
                            self.log_action(f"右键单击位置: {new_pos}")
                        elif event.action_type == MouseAction.DOUBLE_CLICK:
                            pyautogui.doubleClick(new_pos[0], new_pos[1])
                            self.log_action(f"双击位置: {new_pos}")
                        
                        time.sleep(0.5)  # 操作间隔
                    
                    time.sleep(1)  # 循环间隔
            
            finally:
                if execute_listener and execute_listener.running:
                    execute_listener.stop()

        except Exception as e:
            self.log_action(f"执行过程中发生错误: {str(e)}")
            sys.exit(1)

    def save_positions(self, events):
        try:
            filename = f"mouse_actions_{self.get_current_time().replace(':', '-')}.json"
            events_data = [
                {
                    "action_type": event.action_type.value,
                    "position": event.position,
                    "timestamp": event.timestamp
                }
                for event in events
            ]
            with open(filename, 'w') as f:
                json.dump(events_data, f, indent=2)
            print(f"\n操作序列已保存到: {filename}")
        except Exception as e:
            print(f"保存操作序列时发生错误: {e}")

    def on_execute_key_press(self, key, listener):
        if key == keyboard.Key.esc or key == keyboard.Key.cmd or \
           key == keyboard.KeyCode.from_char('q'):
            print("\n用户终止执行")
            if listener:
                listener.stop()
            return False

    def run(self):
        print("鼠标操作记录和重放工具")
        print("注意: 将光标移动到屏幕左上角可以触发故障安全机制，终止程序")
        print("停止录制方式: ESC键/Q键 | 终端按回车 | Ctrl+C")
        
        try:
            # 确保开始新的记录前重置所有状态
            self.keyboard_listener = None
            self.mouse_listener = None
            self.running = True
            self.waiting_for_enter = True
            
            events = self.record_positions()
            
            if events and len(events) > 0:
                self.save_positions(events)
                
                # 确保所有监听器都已停止并等待一小段时间
                if self.keyboard_listener:
                    self.keyboard_listener.stop()
                    self.keyboard_listener = None
                if self.mouse_listener:
                    self.mouse_listener.stop()
                    self.mouse_listener = None
                
                # 等待一小段时间确保监听器完全停止
                time.sleep(0.5)
                
                # 使用简单的输入方式，避免使用监听器
                while True:
                    user_input = input("\n是否要执行重放？(y/n): ").lower().strip()
                    if user_input in ['y', 'n']:
                        break
                    print("请输入 y 或 n")
                
                if user_input == 'y':
                    while True:
                        try:
                            num_loops = int(input("请输入要重复执行的次数："))
                            if num_loops > 0:
                                self.execute_sequence(events, num_loops)
                                break
                            else:
                                print("请输入大于0的数字")
                        except ValueError:
                            print("输入无效，请输入一个正整数")
            
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            if self.keyboard_listener:
                try:
                    self.keyboard_listener.stop()
                except Exception:
                    pass
            if self.mouse_listener:
                try:
                    self.mouse_listener.stop()
                except Exception:
                    pass
            print("\n程序结束")

if __name__ == "__main__":
    recorder = MouseRecorder()
    recorder.run()
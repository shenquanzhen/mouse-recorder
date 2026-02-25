# Mouse Recorder

一个简单但功能强大的鼠标操作记录和重放工具。

## 功能特点

- 自动记录鼠标停留位置（停留3秒自动记录）
- 记录多种鼠标操作：
  - 左键单击
  - 右键单击
  - 双击
- 支持保存和重放操作序列
- 支持多次重放

## 使用方法

1. 运行程序：
   ```bash
   python mouse_sequence_recorder.py
   ```

2. 记录操作：
   - 将鼠标移动到目标位置并停留3秒，位置会被自动记录
   - 执行需要的鼠标操作（单击、右键、双击），操作会被自动记录
   - 按 ESC/Q/Command 键结束记录

3. 重放操作：
   - 记录结束后选择是否重放 (y/n)
   - 输入重复执行的次数
   - 观察自动执行过程
   - 可随时按 ESC/Q/Command 键终止重放

## 依赖项

- Python 3.x
- pyautogui
- pynput

## 安装依赖

```bash
pip install pyautogui pynput
```

## 开发与测试

### 本地电脑（有桌面/图形界面）运行

在你的本地电脑终端、项目根目录执行：

```bash
pip install -r requirements.txt
python mouse_sequence_recorder.py
```

预期正确反馈：
- 终端打印“鼠标操作记录工具/坐标信息”等提示，并开始监听鼠标/键盘事件。

预期错误反馈（常见）：
- `ModuleNotFoundError`：说明依赖未安装或安装到其它 Python 环境。
- Linux 下提示找不到 `DISPLAY`：说明当前环境无图形界面（需要在有桌面环境的机器运行）。

### 阿里云服务器/CI（无 GUI 环境）运行单元测试

在阿里云服务器终端（或 CI）、项目根目录执行：

```bash
pip install -r requirements-dev.txt
pytest -q
```

预期正确反馈：
- `pytest` 返回退出码 0，并显示类似 `3 passed` 的结果。

说明：
- 单元测试通过 stub 隔离了 `pyautogui/pynput`，因此无需图形界面也能验证“双击判定/JSON 保存”等核心逻辑。

## 注意事项

- 将鼠标移动到屏幕左上角可触发安全机制，终止程序
- 所有操作序列会自动保存为 JSON 文件，方便后续使用
- 重放过程中可随时终止 
# Quick Start

Windows 桌面应用程序，用于快速启动应用程序和脚本。

## 功能特性

- **分组管理**：将应用程序按组分类组织
- **批量启动**：一键启动分组内的所有应用
- **系统扫描**：自动扫描 Windows 已安装的应用程序
- **快速搜索**：从扫描结果中快速筛选应用

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

或双击 `run.bat`

## 构建 EXE

```bash
pyinstaller --onefile --windowed --icon=icon.ico --name="Quick Start" main.py
```

生成的文件在 `dist/Quick Start.exe`

## 技术栈

- Python 3.12
- PyQt5
- Windows Registry (winreg)

## 项目结构

```
quick-start/
├── main.py              # 入口文件
├── app/
│   ├── main_window.py   # 主窗口 UI
│   ├── config.py        # 配置文件读写
│   ├── launcher.py      # 应用启动器
│   ├── app_scanner.py   # 系统应用扫描
│   └── app_selector.py  # 应用选择对话框
├── config.json          # 用户配置（自动生成）
├── icon.ico             # 应用图标
└── run.bat              # 快捷启动脚本
```

## 许可证

MIT License

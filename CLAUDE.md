# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Quick Start is a Windows desktop application built with PyQt5 for launching applications and scripts. Users can organize applications into groups and launch them individually or all at once.

## Tech Stack

- Python 3.12
- PyQt5 for GUI
- Windows Registry for app scanning (`winreg`)

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
# or
run.bat
```

## Architecture

- `main.py` - Entry point, creates QApplication and MainWindow
- `app/main_window.py` - Main UI with group list (left) and app table (right), handles all user interactions
- `app/config.py` - JSON config I/O for `config.json`, generates short UUIDs for new items
- `app/launcher.py` - Launches apps via `subprocess.Popen` (for .exe) or `os.startfile` (for other files)
- `app/app_scanner.py` - Scans Windows Registry for installed applications
- `app/app_selector.py` - Dialog for selecting apps from scanned results with search/filter

## Data Model

`config.json` stores groups, each containing items with `id`, `name`, and `script_path`. IDs are 8-char UUIDs.

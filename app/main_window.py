import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,
    QPushButton, QInputDialog, QFileDialog, QMessageBox,
    QHeaderView, QAbstractItemView, QStatusBar, QGroupBox,
    QSplitter, QMenu, QAction, QDialog,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from .config import load_config, save_config, new_id
from .launcher import run_script, run_scripts
from .app_scanner import scan_installed_apps
from .app_selector import AppSelectorDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quick Start")
        self.setMinimumSize(750, 500)
        self.config = load_config()
        self.current_group_idx = None
        self._init_ui()
        self._load_groups()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - groups
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        group_label = QWidget()
        group_label_layout = QHBoxLayout(group_label)
        group_label_layout.setContentsMargins(0, 0, 0, 0)
        from PyQt5.QtWidgets import QLabel
        lbl = QLabel("分组")
        lbl.setStyleSheet("font-weight: bold; font-size: 14px;")
        group_label_layout.addWidget(lbl)
        left_layout.addWidget(group_label)

        self.group_list = QListWidget()
        self.group_list.currentRowChanged.connect(self._on_group_selected)
        self.group_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.group_list.customContextMenuRequested.connect(self._group_context_menu)
        left_layout.addWidget(self.group_list)

        btn_row = QWidget()
        btn_layout = QHBoxLayout(btn_row)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        self.btn_add_group = QPushButton("+ 添加分组")
        self.btn_edit_group = QPushButton("编辑")
        self.btn_del_group = QPushButton("删除")
        btn_layout.addWidget(self.btn_add_group)
        btn_layout.addWidget(self.btn_edit_group)
        btn_layout.addWidget(self.btn_del_group)
        left_layout.addWidget(btn_row)

        self.btn_add_group.clicked.connect(self._add_group)
        self.btn_edit_group.clicked.connect(self._edit_group)
        self.btn_del_group.clicked.connect(self._delete_group)

        splitter.addWidget(left_panel)

        # Right panel - apps
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        from PyQt5.QtWidgets import QLabel
        app_lbl = QLabel("应用列表")
        app_lbl.setStyleSheet("font-weight: bold; font-size: 14px;")
        right_layout.addWidget(app_lbl)

        self.app_table = QTableWidget()
        self.app_table.setColumnCount(3)
        self.app_table.setHorizontalHeaderLabels(["名称", "脚本路径", "操作"])
        self.app_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.app_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.app_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.app_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.app_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.app_table.cellDoubleClicked.connect(self._on_app_double_click)
        right_layout.addWidget(self.app_table)

        btn_row2 = QWidget()
        btn_layout2 = QHBoxLayout(btn_row2)
        btn_layout2.setContentsMargins(0, 0, 0, 0)
        self.btn_add_app = QPushButton("+ 添加应用")
        self.btn_add_from_system = QPushButton("从系统选择")
        self.btn_launch_all = QPushButton("▶ 启动全部")
        self.btn_launch_all.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 6px 16px; }"
            "QPushButton:hover { background-color: #45a049; }"
        )
        btn_layout2.addWidget(self.btn_add_app)
        btn_layout2.addWidget(self.btn_add_from_system)
        btn_layout2.addStretch()
        btn_layout2.addWidget(self.btn_launch_all)
        right_layout.addWidget(btn_row2)

        self.btn_add_app.clicked.connect(self._add_app)
        self.btn_add_from_system.clicked.connect(self._add_from_system)
        self.btn_launch_all.clicked.connect(self._launch_all)

        splitter.addWidget(right_panel)
        splitter.setSizes([200, 550])

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

    def _load_groups(self):
        self.group_list.clear()
        for g in self.config["groups"]:
            self.group_list.addItem(g["name"])
        if self.config["groups"]:
            self.group_list.setCurrentRow(0)

    def _on_group_selected(self, row):
        self.current_group_idx = row
        self._load_apps()

    def _load_apps(self):
        self.app_table.setRowCount(0)
        if self.current_group_idx is None or self.current_group_idx >= len(self.config["groups"]):
            return
        group = self.config["groups"][self.current_group_idx]
        items = group.get("items", [])
        self.app_table.setRowCount(len(items))
        for i, item in enumerate(items):
            name_item = QTableWidgetItem(item["name"])
            path_item = QTableWidgetItem(item["script_path"])
            self.app_table.setItem(i, 0, name_item)
            self.app_table.setItem(i, 1, path_item)

            del_btn = QPushButton("删除")
            del_btn.clicked.connect(lambda _, idx=i: self._delete_app(idx))
            self.app_table.setCellWidget(i, 2, del_btn)

    def _add_group(self):
        name, ok = QInputDialog.getText(self, "添加分组", "分组名称:")
        if ok and name.strip():
            self.config["groups"].append({
                "id": new_id(),
                "name": name.strip(),
                "items": [],
            })
            save_config(self.config)
            self._load_groups()
            self.group_list.setCurrentRow(len(self.config["groups"]) - 1)
            self.status_bar.showMessage(f"已添加分组: {name.strip()}")

    def _edit_group(self):
        row = self.group_list.currentRow()
        if row < 0:
            return
        old_name = self.config["groups"][row]["name"]
        name, ok = QInputDialog.getText(self, "编辑分组", "分组名称:", text=old_name)
        if ok and name.strip():
            self.config["groups"][row]["name"] = name.strip()
            save_config(self.config)
            self._load_groups()
            self.group_list.setCurrentRow(row)
            self.status_bar.showMessage(f"已重命名分组: {name.strip()}")

    def _delete_group(self):
        row = self.group_list.currentRow()
        if row < 0:
            return
        name = self.config["groups"][row]["name"]
        reply = QMessageBox.question(
            self, "确认删除", f"确定删除分组「{name}」及其所有应用？",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.config["groups"].pop(row)
            save_config(self.config)
            self.current_group_idx = None
            self._load_groups()
            self.status_bar.showMessage(f"已删除分组: {name}")

    def _add_app(self):
        if self.current_group_idx is None:
            QMessageBox.warning(self, "提示", "请先选择一个分组")
            return
        script_path, _ = QFileDialog.getOpenFileName(
            self, "选择脚本文件", "",
            "脚本文件 (*.bat *.vbs *.cmd *.exe);;所有文件 (*)",
        )
        if not script_path:
            return
        # 从文件名提取应用名称（去掉扩展名）
        name = os.path.splitext(os.path.basename(script_path))[0]
        self.config["groups"][self.current_group_idx]["items"].append({
            "id": new_id(),
            "name": name,
            "script_path": script_path,
        })
        save_config(self.config)
        self._load_apps()
        self.status_bar.showMessage(f"已添加应用: {name}")

    def _add_from_system(self):
        try:
            if self.current_group_idx is None:
                QMessageBox.warning(self, "提示", "请先选择一个分组")
                return
            self.status_bar.showMessage("正在扫描已安装应用...")
            apps = scan_installed_apps()
            if not apps:
                QMessageBox.information(self, "提示", "未找到已安装的应用")
                self.status_bar.showMessage("就绪")
                return
            dialog = AppSelectorDialog(apps, self)
            if dialog.exec_() != QDialog.Accepted:
                self.status_bar.showMessage("就绪")
                return
            selected = dialog.get_selected_apps()
            if not selected:
                self.status_bar.showMessage("未选择任何应用")
                return
            group = self.config["groups"][self.current_group_idx]
            for app in selected:
                group["items"].append({
                    "id": new_id(),
                    "name": app["name"],
                    "script_path": app["exe"],
                })
            save_config(self.config)
            self._load_apps()
            self.status_bar.showMessage(f"已添加 {len(selected)} 个应用")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"发生错误:\n{e}")
            self.status_bar.showMessage("就绪")

    def _delete_app(self, idx):
        group = self.config["groups"][self.current_group_idx]
        name = group["items"][idx]["name"]
        group["items"].pop(idx)
        save_config(self.config)
        self._load_apps()
        self.status_bar.showMessage(f"已删除应用: {name}")

    def _on_app_double_click(self, row, col):
        if self.current_group_idx is None:
            return
        group = self.config["groups"][self.current_group_idx]
        if row >= len(group["items"]):
            return
        item = group["items"][row]
        ok, msg = run_script(item["script_path"])
        self.status_bar.showMessage(msg)

    def _launch_all(self):
        if self.current_group_idx is None:
            QMessageBox.warning(self, "提示", "请先选择一个分组")
            return
        group = self.config["groups"][self.current_group_idx]
        items = group.get("items", [])
        if not items:
            self.status_bar.showMessage("当前分组没有应用")
            return
        paths = [item["script_path"] for item in items]
        results = run_scripts(paths)
        success = sum(1 for ok, _ in results if ok)
        total = len(results)
        self.status_bar.showMessage(f"启动完成: {success}/{total} 成功")

    def _group_context_menu(self, pos):
        row = self.group_list.row(self.group_list.itemAt(pos))
        if row < 0:
            return
        menu = QMenu(self)
        edit_action = QAction("编辑", self)
        del_action = QAction("删除", self)
        edit_action.triggered.connect(lambda: (self.group_list.setCurrentRow(row), self._edit_group()))
        del_action.triggered.connect(lambda: (self.group_list.setCurrentRow(row), self._delete_group()))
        menu.addAction(edit_action)
        menu.addAction(del_action)
        menu.exec_(self.group_list.mapToGlobal(pos))

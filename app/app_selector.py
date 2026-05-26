from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QCheckBox, QLabel,
)
from PyQt5.QtCore import Qt


class AppSelectorDialog(QDialog):
    def __init__(self, apps, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择应用")
        self.setMinimumSize(600, 500)
        self.apps = apps
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入应用名称过滤...")
        self.search_input.textChanged.connect(self._filter_list)
        filter_row.addWidget(self.search_input)
        layout.addLayout(filter_row)

        self.select_all_cb = QCheckBox("全选 / 取消全选")
        self.select_all_cb.stateChanged.connect(self._toggle_all)
        layout.addWidget(self.select_all_cb)

        self.app_table = QTableWidget()
        self.app_table.setColumnCount(3)
        self.app_table.setHorizontalHeaderLabels(["", "应用名称", "路径"])
        self.app_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.app_table.setColumnWidth(0, 30)
        self.app_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.app_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.app_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.app_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.app_table.verticalHeader().setVisible(False)
        layout.addWidget(self.app_table)

        self.count_label = QLabel(f"共 {len(self.apps)} 个应用")
        layout.addWidget(self.count_label)

        self._populate_table()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def _populate_table(self):
        self.app_table.setRowCount(len(self.apps))
        for i, app in enumerate(self.apps):
            cb = QCheckBox()
            self.app_table.setCellWidget(i, 0, cb)
            self.app_table.setItem(i, 1, QTableWidgetItem(app["name"]))
            self.app_table.setItem(i, 2, QTableWidgetItem(app["exe"]))
        self.app_table.cellClicked.connect(self._on_cell_clicked)

    def _on_cell_clicked(self, row, col):
        if col != 0:
            cb = self.app_table.cellWidget(row, 0)
            if cb:
                cb.setChecked(not cb.isChecked())

    def _toggle_all(self, state):
        checked = state == Qt.Checked
        for i in range(self.app_table.rowCount()):
            if not self.app_table.isRowHidden(i):
                cb = self.app_table.cellWidget(i, 0)
                if cb:
                    cb.setChecked(checked)

    def _filter_list(self, text):
        text = text.lower()
        visible = 0
        for i in range(self.app_table.rowCount()):
            name = self.app_table.item(i, 1).text().lower()
            path = self.app_table.item(i, 2).text().lower()
            match = text in name or text in path
            self.app_table.setRowHidden(i, not match)
            if match:
                visible += 1
        self.count_label.setText(f"显示 {visible}/{len(self.apps)} 个应用")

    def get_selected_apps(self):
        selected = []
        for i in range(self.app_table.rowCount()):
            if self.app_table.isRowHidden(i):
                continue
            cb = self.app_table.cellWidget(i, 0)
            if cb and cb.isChecked():
                selected.append(self.apps[i])
        return selected

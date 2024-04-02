import os
import sys
from PySide6.QtGui import QIcon, Qt, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, \
    QCheckBox, QPushButton, QStatusBar, QHBoxLayout
import openloot


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('BigTime 充能沙漏管理器')
        self.setGeometry(100, 100, 680, 400)
        self.table_widget = QTableWidget()
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setup_in_game_table()

        self.flush_button = QPushButton('刷新游戏物品', self)
        self.move_button = QPushButton('转移到市场', self)
        self.flush_button.setMinimumHeight(40)
        self.move_button.setMinimumHeight(40)
        self.flush_button.clicked.connect(self.flush_item)
        self.move_button.clicked.connect(self.move_item)

        layout_main = QHBoxLayout()

        # 游戏物品窗口 垂直布局
        layout_ingame = QVBoxLayout()
        layout_ingame.addWidget(self.table_widget)

        # 按钮部分 横向布局
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.flush_button)
        button_layout.addWidget(self.move_button)

        # 按钮布局加入主窗口
        layout_ingame.addLayout(button_layout)
        layout_main.addLayout(layout_ingame)
        self.setLayout(layout_main)

        # 设置对其
        central_widget = QWidget()
        central_widget.setLayout(layout_main)
        self.setCentralWidget(central_widget)

        # 设置状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def setup_in_game_table(self):
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(["ID", "资产", "剩余时间"])

        self.table_widget.setColumnWidth(0, 300)
        self.table_widget.setColumnWidth(1, 260)
        self.table_widget.setColumnWidth(2, 80)

    def move_item(self):
        item_list = []
        for row in range(self.table_widget.rowCount()):
            checkbox = self.table_widget.cellWidget(row, 0)
            if isinstance(checkbox, QCheckBox):
                if checkbox.isChecked():
                    item_list.append(checkbox.text())
        if len(item_list) > 0:
            try:
                r = openloot.move_items_to_market(item_list, 3)
                self.status_bar.showMessage(f'转移成功')
                for row in range(self.table_widget.rowCount()):
                    checkbox = self.table_widget.cellWidget(row, 0)
                    if isinstance(checkbox, QCheckBox):
                        if checkbox.isChecked():
                            self.table_widget.removeRow(row)
            except Exception as e:
                print(e)
                self.status_bar.showMessage(f'错误: 物品转移失败')

    def clear_table(self):
        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)

    def flush_item(self):
        self.clear_table()
        try:
            r = openloot.get_in_game_items(1, 3)
            self.status_bar.showMessage(f'获取成功')
        except Exception as e:
            print(e)
            self.status_bar.showMessage(f'错误: 获取仓库失败')

        items = r.json()
        for item in items['items']:
            item_id = item['id']
            issued_id = item['issuedId']
            name = item['metadata']['name']
            remaining = '0'
            if item['extra'] is not None and "attributes" in item["extra"]:
                for attr in item['extra']['attributes']:
                    if attr['name'] == "TimeRemaining":
                        remaining = attr['value']
            image_path = os.path.join(os.path.dirname(__file__), "resources", item['metadata']['optionName'] + '.png')
            pixmap = QPixmap(image_path)

            row = self.table_widget.rowCount()
            self.table_widget.insertRow(row)
            checkbox = QCheckBox(item_id)
            self.table_widget.setCellWidget(row, 0, checkbox)
            item = QTableWidgetItem(f'{name} (#{issued_id})')
            item.setData(Qt.DecorationRole, QIcon(pixmap))
            self.table_widget.setItem(row, 1, item)
            item = QTableWidgetItem(remaining)
            self.table_widget.setItem(row, 2, item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app_icon = QIcon("resources/favicon.ico")
    app.setWindowIcon(app_icon)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())

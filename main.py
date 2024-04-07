import os
import sys
from PySide6.QtGui import QIcon, Qt, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, \
    QCheckBox, QPushButton, QStatusBar, QWidget, QHBoxLayout, QTabWidget
import openloot


class GameItemsTab(QWidget):
    def __init__(self, status_bar):
        super().__init__()

        self.status_bar = status_bar

        self.table_widget = QTableWidget()
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setup_in_game_table()

        self.flush_button = QPushButton('刷新游戏物品', self)
        self.move_button = QPushButton('转移到市场', self)
        self.flush_button.setMinimumHeight(40)
        self.move_button.setMinimumHeight(40)
        self.flush_button.clicked.connect(self.flush_item)
        self.move_button.clicked.connect(self.move_item)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.flush_button)
        button_layout.addWidget(self.move_button)

        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.setStyleSheet("""
        QPushButton {
            background-color: #34495e; 
            border: 2px solid #2c3e50; 
            color: white; 
            border-radius: 5px; 
        }

        QPushButton:hover {
            background-color: #2c3e50; 
        }

        QPushButton:pressed {
            background-color: #2980b9; 
            border-color: #2980b9; 
        }
    """)

    def setup_in_game_table(self):
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(["ID", "资产", "剩余时间"])
        self.table_widget.setColumnWidth(0, 260)
        self.table_widget.setColumnWidth(1, 240)
        self.table_widget.setColumnWidth(2, 76)

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
                rows_count = self.table_widget.rowCount()
                for row in range(rows_count):
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
            print(r.content)
        except Exception as e:
            print(e)
            self.status_bar.showMessage(f'错误: 获取仓库失败')
            return
        items = r.json()
        if "code" in items is not None and items['code'] == 'Error':
            self.status_bar.showMessage(f'返回错误: ' + items['message'])
            return
        
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
            checkbox.clicked = True if int(remaining) >=2160 else False
            self.table_widget.setCellWidget(row, 0, checkbox)
            item = QTableWidgetItem(f'{name} (#{issued_id})')
            item.setData(Qt.DecorationRole, QIcon(pixmap))
            self.table_widget.setItem(row, 1, item)
            item = QTableWidgetItem(remaining)
            self.table_widget.setItem(row, 2, item)


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('BigTime 充能沙漏管理器')
        self.setGeometry(100, 100, 680, 400)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.game_items_tab = GameItemsTab(self.status_bar)

        self.setCentralWidget(self.game_items_tab)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app_icon = QIcon("resources/favicon.ico")
    app.setWindowIcon(app_icon)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
import os
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import openloot
from decimal import Decimal

style_str = """
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
    """

class MarketItemsTab(QWidget):
    def __init__(self, status_bar):
        super().__init__()
        self.status_bar = status_bar

        self.flush_button = QPushButton('刷新市场物品', self)
        self.flush_button.setMinimumHeight(40)
        self.flush_button.clicked.connect(self.flush_item)

        self.sell_edit = QLineEdit()
        self.sell_edit.setPlaceholderText("每小时单价")
        self.sell_edit.setMinimumHeight(40)
        self.sell_edit.setFixedWidth(80)

        self.sell_price_button = QPushButton('生成价格', self)
        self.sell_price_button.setMinimumHeight(40)
        self.sell_price_button.clicked.connect(self.make_price)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.flush_button)
        button_layout.addWidget(self.sell_edit)
        button_layout.addWidget(self.sell_price_button)
        
        self.table_widget = QTableWidget()
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setup_table()

        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.setStyleSheet(style_str)

    def setup_table(self):
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["ID", "资产", "剩余时间", "价格"])
        self.table_widget.setColumnWidth(0, 260)
        self.table_widget.setColumnWidth(1, 240)
        self.table_widget.setColumnWidth(2, 76)
        self.table_widget.setColumnWidth(3, 76)

    def clear_table(self):
        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)

    def make_price(self):
        for row in range(self.table_widget.rowCount()):
            remaining = self.table_widget.item(row, 2)
            if remaining is not None:
                time = Decimal(remaining.text()) / Decimal(60)
                per = Decimal(self.sell_edit.text())
                result = time * per
                result = result.quantize(Decimal('0.00'))
                print(result)
                item = QTableWidgetItem(str(result))
                self.table_widget.setItem(row, 3, item)

    def flush_item(self):
        self.clear_table()
        totalPages = 1 
        page = 1
        while(True):
            try:
                self.status_bar.showMessage(f'正在获取: {page} 页')
                r = openloot.get_market_items(page, 3)
                self.status_bar.showMessage(f'获取成功')
                print(r.content)
            except Exception as e:
                print(e)
                self.status_bar.showMessage(f'错误: 获取仓库失败')
                continue
            items = r.json()
            if "code" in items is not None and items['code'] == 'Error':
                self.status_bar.showMessage(f'返回错误: ' + items['message'])
                continue
            
            totalPages = items['totalPages']
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
                item = QTableWidgetItem(f'{item_id}')
                self.table_widget.setItem(row, 0, item)
                item = QTableWidgetItem(f'{name} (#{issued_id})')
                item.setData(Qt.DecorationRole, QIcon(pixmap))
                self.table_widget.setItem(row, 1, item)
                item = QTableWidgetItem(remaining)
                self.table_widget.setItem(row, 2, item)

            if page == totalPages or totalPages == 0:
                break
            page += 1


class GameItemsTab(QWidget):
    def __init__(self, status_bar):
        super().__init__()

        self.status_bar = status_bar

        self.flush_button = QPushButton('刷新游戏物品', self)
        self.flush_button.setMinimumHeight(40)
        self.flush_button.clicked.connect(self.flush_item)

        self.move_button = QPushButton('转移到市场', self)
        self.move_button.setMinimumHeight(40)
        self.move_button.clicked.connect(self.move_item)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.flush_button)
        button_layout.addWidget(self.move_button)

        self.table_widget = QTableWidget()
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setup_table()

        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.setStyleSheet(style_str)

    def setup_table(self):
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
        totalPages = 1 
        page = 1
        while(True):
            try:
                self.status_bar.showMessage(f'正在获取: {page} 页')
                r = openloot.get_in_game_items(page, 3)
                self.status_bar.showMessage(f'获取成功')
                print(r.content)
            except Exception as e:
                print(e)
                self.status_bar.showMessage(f'错误: 获取仓库失败')
                continue
            items = r.json()
            if "code" in items is not None and items['code'] == 'Error':
                self.status_bar.showMessage(f'返回错误: ' + items['message'])
                continue
            
            totalPages = items['totalPages']
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

            if page == totalPages:
                break
            page += 1


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('BigTime 充能沙漏管理器')
        self.setGeometry(100, 100, 720, 400)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.tab_widget = QTabWidget()

        self.game_items_tab = GameItemsTab(self.status_bar)
        self.market_items_tab = MarketItemsTab(self.status_bar)

        self.tab_widget.addTab(self.game_items_tab, "游戏物品")
        self.tab_widget.addTab(self.market_items_tab, "市场物品")

        self.setCentralWidget(self.tab_widget)

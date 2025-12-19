# 文件名: ui/cashier_page.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QMessageBox, QSpinBox, QAbstractItemView)
from PyQt6.QtCore import Qt
from services.product_service import ProductService
from services.sale_service import SaleService

class CashierPage(QWidget):
    def __init__(self):
        super().__init__()
        self.cart = [] # 购物车数据：[{'product': obj, 'qty': 1}, ...]
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # --- 1. 顶部输入区 ---
        input_layout = QHBoxLayout()
        
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("在此输入条码并回车 (模拟扫码)")
        self.id_input.setStyleSheet("font-size: 16px; padding: 5px;")
        self.id_input.returnPressed.connect(self.add_product_to_cart) # 回车触发
        
        self.qty_input = QSpinBox()
        self.qty_input.setRange(1, 100)
        self.qty_input.setValue(1)
        self.qty_input.setPrefix("数量: ")
        
        btn_add = QPushButton("加入清单")
        btn_add.clicked.connect(self.add_product_to_cart)

        input_layout.addWidget(self.id_input, stretch=3)
        input_layout.addWidget(self.qty_input, stretch=1)
        input_layout.addWidget(btn_add, stretch=1)
        
        layout.addLayout(input_layout)

        # --- 2. 中间购物车表格 ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["编号", "名称", "单价", "数量", "小计"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # 不可编辑
        layout.addWidget(self.table)

        # --- 3. 底部结算区 ---
        bottom_layout = QHBoxLayout()
        
        self.total_label = QLabel("总金额: 0.00 元")
        self.total_label.setStyleSheet("font-size: 24px; color: red; font-weight: bold;")
        
        self.btn_clear = QPushButton("清空")
        self.btn_clear.clicked.connect(self.clear_cart)
        
        self.btn_checkout = QPushButton("确认结算")
        self.btn_checkout.setStyleSheet("background-color: #0078d7; color: white; font-size: 18px; padding: 10px;")
        self.btn_checkout.clicked.connect(self.handle_checkout)

        bottom_layout.addWidget(self.btn_clear)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.total_label)
        bottom_layout.addWidget(self.btn_checkout)
        
        layout.addLayout(bottom_layout)
        self.setLayout(layout)

    def add_product_to_cart(self):
        pid = self.id_input.text().strip()
        if not pid: return

        # 查询商品
        product = ProductService.get_product_by_id(pid)
        if not product:
            QMessageBox.warning(self, "提示", "未找到该商品！")
            self.id_input.selectAll()
            return

        qty = self.qty_input.value()

        # 检查是否已经在购物车里 -> 如果在，增加数量
        found = False
        for item in self.cart:
            if item['id'] == pid:
                item['qty'] += qty
                found = True
                break
        
        if not found:
            self.cart.append({
                'id': pid,
                'name': product.name,
                'price': product.sell_price,
                'qty': qty
            })

        self.update_table()
        self.id_input.clear() # 清空输入框方便下一次扫码
        self.qty_input.setValue(1) # 重置数量
        self.id_input.setFocus() # 焦点回到输入框

    def update_table(self):
        """刷新购物车表格和总金额"""
        self.table.setRowCount(0)
        total_money = 0.0
        
        for idx, item in enumerate(self.cart):
            subtotal = item['price'] * item['qty']
            total_money += subtotal
            
            self.table.insertRow(idx)
            self.table.setItem(idx, 0, QTableWidgetItem(str(item['id'])))
            self.table.setItem(idx, 1, QTableWidgetItem(str(item['name'])))
            self.table.setItem(idx, 2, QTableWidgetItem(f"{item['price']:.2f}"))
            self.table.setItem(idx, 3, QTableWidgetItem(str(item['qty'])))
            self.table.setItem(idx, 4, QTableWidgetItem(f"{subtotal:.2f}"))
        
        self.total_label.setText(f"总金额: {total_money:.2f} 元")

    def clear_cart(self):
        self.cart = []
        self.update_table()

    def handle_checkout(self):
        if not self.cart:
            QMessageBox.warning(self, "提示", "购物车是空的！")
            return
            
        confirm = QMessageBox.question(self, "结算", f"确定进行结算吗？\n{self.total_label.text()}", 
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            # 调用 Service
            success, msg = SaleService.checkout(self.cart)
            if success:
                QMessageBox.information(self, "成功", "交易完成！")
                self.clear_cart()
            else:
                QMessageBox.critical(self, "失败", f"结算失败: {msg}")
# 文件名: ui/replenish_page.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QSpinBox, QAbstractItemView, QGroupBox, QDoubleSpinBox)
from PyQt6.QtCore import Qt
from services.product_service import ProductService

class ReplenishPage(QWidget):
    def __init__(self):
        super().__init__()
        self.cart = []  # 待进货清单
        self.init_ui()

    def init_ui(self):
        # 主布局采用垂直布局：上部是搜索区，下部是进货清单区
        main_layout = QVBoxLayout()

        # 1. 初始化上半部分：商品搜索区
        self.init_search_area(main_layout)

        # 2. 初始化下半部分：待进货清单区
        self.init_cart_area(main_layout)

        self.setLayout(main_layout)

    def init_search_area(self, parent_layout):
        """初始化商品搜索区域"""
        group_box = QGroupBox("商品检索")
        layout = QVBoxLayout()

        # --- 顶部搜索栏 ---
        search_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入商品编号 (扫码) 或名称关键字...")
        self.search_input.returnPressed.connect(self.perform_search)

        btn_search = QPushButton("搜索")
        btn_search.clicked.connect(self.perform_search)

        search_bar.addWidget(self.search_input)
        search_bar.addWidget(btn_search)
        layout.addLayout(search_bar)

        # --- 搜索结果表格 ---
        self.search_table = QTableWidget()
        self.search_table.setColumnCount(6)
        self.search_table.setHorizontalHeaderLabels(["编号", "名称", "类别", "当前进价", "当前库存", "操作"])
        self.search_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.search_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.search_table)

        group_box.setLayout(layout)
        parent_layout.addWidget(group_box, stretch=4)

    def init_cart_area(self, parent_layout):
        """初始化待进货清单区域"""
        group_box = QGroupBox("待进货清单")
        layout = QVBoxLayout()

        # --- 进货清单表格 ---
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["编号", "名称", "进货数量", "进价", "操作"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cart_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.cart_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.cart_table)

        # --- 底部操作栏 ---
        bottom_layout = QHBoxLayout()

        btn_clear = QPushButton("清空清单")
        btn_clear.clicked.connect(self.clear_cart)

        btn_confirm = QPushButton("确认进货")
        btn_confirm.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 5px 15px;")
        btn_confirm.clicked.connect(self.handle_confirm)

        bottom_layout.addWidget(btn_clear)
        bottom_layout.addStretch()
        bottom_layout.addWidget(btn_confirm)

        layout.addLayout(bottom_layout)
        group_box.setLayout(layout)
        parent_layout.addWidget(group_box, stretch=6)

    # --- 逻辑功能区 ---

    def perform_search(self):
        """执行搜索（支持扫码或模糊搜索）"""
        keyword = self.search_input.text().strip()
        if not keyword:
            return

        # 先尝试按编号精确查找
        product = ProductService.get_product_by_id(keyword)
        if product:
            products = [product]
        else:
            # 按名称模糊搜索
            products = ProductService.search_products_by_name(keyword)

        self.search_table.setRowCount(0)

        for row_idx, p in enumerate(products):
            self.search_table.insertRow(row_idx)

            # 文本信息
            self.search_table.setItem(row_idx, 0, QTableWidgetItem(str(p.id)))
            self.search_table.setItem(row_idx, 1, QTableWidgetItem(str(p.name)))
            self.search_table.setItem(row_idx, 2, QTableWidgetItem(str(p.category)))
            self.search_table.setItem(row_idx, 3, QTableWidgetItem(f"{p.cost_price:.2f}"))
            self.search_table.setItem(row_idx, 4, QTableWidgetItem(str(p.stock)))

            # 添加到进货单按钮
            btn = QPushButton("加入进货单")
            btn.setStyleSheet("color: blue;")
            btn.clicked.connect(lambda checked, product=p: self.add_to_cart(product))
            self.search_table.setCellWidget(row_idx, 5, btn)

    def add_to_cart(self, product):
        """将商品加入待进货清单"""
        # 检查是否已在清单中
        for item in self.cart:
            if item['product_id'] == product.id:
                QMessageBox.warning(self, "提示", "该商品已在进货清单中！")
                return

        # 添加到清单
        self.cart.append({
            'product_id': product.id,
            'name': product.name,
            'quantity': 1,  # 默认进货数量为1
            'cost_price': product.cost_price  # 默认使用当前进价
        })

        self.update_cart_table()

    def update_cart_table(self):
        """刷新待进货清单表格"""
        self.cart_table.setRowCount(0)

        for idx, item in enumerate(self.cart):
            self.cart_table.insertRow(idx)

            # 设置不可编辑的列
            id_item = QTableWidgetItem(str(item['product_id']))
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.cart_table.setItem(idx, 0, id_item)

            name_item = QTableWidgetItem(str(item['name']))
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.cart_table.setItem(idx, 1, name_item)

            # 进货数量使用SpinBox
            qty_spin = QSpinBox()
            qty_spin.setRange(1, 10000)
            qty_spin.setValue(item['quantity'])
            qty_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
            qty_spin.valueChanged.connect(lambda value, i=idx: self.update_quantity(i, value))
            self.cart_table.setCellWidget(idx, 2, qty_spin)

            # 进价使用DoubleSpinBox
            price_spin = QDoubleSpinBox()
            price_spin.setRange(0.01, 99999.99)
            price_spin.setDecimals(2)
            price_spin.setValue(item['cost_price'])
            price_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
            price_spin.valueChanged.connect(lambda value, i=idx: self.update_cost_price(i, value))
            self.cart_table.setCellWidget(idx, 3, price_spin)

            # 删除按钮
            btn_remove = QPushButton("移除")
            btn_remove.setStyleSheet("color: red;")
            btn_remove.clicked.connect(lambda checked, i=idx: self.remove_from_cart(i))
            self.cart_table.setCellWidget(idx, 4, btn_remove)

    def update_quantity(self, cart_index, new_qty):
        """更新进货数量"""
        if cart_index < len(self.cart):
            self.cart[cart_index]['quantity'] = new_qty

    def update_cost_price(self, cart_index, new_price):
        """更新进价"""
        if cart_index < len(self.cart):
            self.cart[cart_index]['cost_price'] = new_price

    def remove_from_cart(self, cart_index):
        """从进货清单中移除商品"""
        if cart_index < len(self.cart):
            del self.cart[cart_index]
            self.update_cart_table()

    def clear_cart(self):
        """清空进货清单"""
        self.cart = []
        self.update_cart_table()

    def handle_confirm(self):
        """确认进货"""
        if not self.cart:
            QMessageBox.warning(self, "提示", "进货清单是空的！")
            return

        # 显示确认信息
        confirm_msg = "确定进货以下商品吗？\n\n"
        for item in self.cart:
            confirm_msg += f"{item['name']} x {item['quantity']} (进价: {item['cost_price']:.2f})\n"

        confirm = QMessageBox.question(self, "确认进货", confirm_msg,
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm == QMessageBox.StandardButton.Yes:
            success, msg = ProductService.replenish_stock(self.cart)
            if success:
                QMessageBox.information(self, "成功", "进货成功！")
                self.clear_cart()
                # 清空搜索结果
                self.search_table.setRowCount(0)
                self.search_input.clear()
            else:
                QMessageBox.critical(self, "失败", f"进货失败: {msg}")

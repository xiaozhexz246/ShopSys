# 文件名: ui/cashier_page.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QSpinBox, QAbstractItemView, QGroupBox, QDoubleSpinBox)
from PyQt6.QtCore import Qt
from services.product_service import ProductService
from services.sale_service import SaleService

class CashierPage(QWidget):
    def __init__(self):
        super().__init__()
        self.cart = [] # 购物车数据
        self.init_ui()

    def init_ui(self):
        # 主布局采用垂直布局：上部是搜索区，下部是结算区
        main_layout = QVBoxLayout()
        
        # 1. 初始化上半部分：模糊搜索区
        self.init_search_area(main_layout)
        
        # 2. 初始化下半部分：购物车结算区
        self.init_cart_area(main_layout)

        self.setLayout(main_layout)

    def init_search_area(self, parent_layout):
        """初始化搜索结果区域 (新功能)"""
        group_box = QGroupBox("🔍 商品检索与快速添加")
        layout = QVBoxLayout()

        # --- 顶部搜索栏 ---
        search_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入商品名称关键字 (如: 可乐)...")
        self.search_input.returnPressed.connect(self.perform_search) # 回车搜索

        btn_search = QPushButton("搜索")
        btn_search.setFixedSize(80, 32)
        btn_search.clicked.connect(self.perform_search)

        search_bar.addWidget(self.search_input)
        search_bar.addWidget(btn_search)
        search_bar.addStretch()
        layout.addLayout(search_bar)

        # --- 搜索结果表格 ---
        self.search_table = QTableWidget()
        self.search_table.setColumnCount(7)  # v2.0: 增加类别、进价、售价列
        self.search_table.setHorizontalHeaderLabels(["编号", "名称", "类别", "进价", "售价", "库存", "操作"])
        self.search_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # 设置进价和售价列宽度为80px
        self.search_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.search_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.search_table.setColumnWidth(3, 80)  # 进价列
        self.search_table.setColumnWidth(4, 80)  # 售价列
        # 操作列自适应内容
        self.search_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.search_table.verticalHeader().setDefaultSectionSize(45)  # 设置默认行高
        layout.addWidget(self.search_table)

        group_box.setLayout(layout)
        # 将搜索区添加到主布局，设置伸缩因子为 2 (稍微占大一点空间，或者与下面 1:1)
        parent_layout.addWidget(group_box, stretch=4)

    def init_cart_area(self, parent_layout):
        """初始化购物车区域 (原有功能重构)"""
        group_box = QGroupBox("🛒 当前购物清单")
        layout = QVBoxLayout()

        # --- 顶部快速扫码栏 (保留原有功能) ---
        scan_layout = QHBoxLayout()
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("在此扫码 (输入ID回车)")
        self.id_input.returnPressed.connect(self.handle_manual_scan)
        
        scan_layout.addWidget(QLabel("扫码枪输入:"))
        scan_layout.addWidget(self.id_input)
        layout.addLayout(scan_layout)

        # --- 购物车表格 ---
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(6)  # 增加实付金额列
        self.cart_table.setHorizontalHeaderLabels(["编号", "名称", "单价", "实付金额", "数量", "小计"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cart_table.verticalHeader().setDefaultSectionSize(45)  # 设置默认行高
        # v1.4: 移除 NoEditTriggers，允许编辑数量列
        self.cart_table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.EditKeyPressed)
        # 连接 itemChanged 信号以监听数量列的修改
        self.cart_table.itemChanged.connect(self.on_cart_item_changed)
        layout.addWidget(self.cart_table)

        # --- 底部结算栏 ---
        bottom_layout = QHBoxLayout()
        self.total_label = QLabel("总金额: 0.00 元")
        self.total_label.setStyleSheet("font-size: 18px; color: #F56C6C; font-weight: bold;")

        btn_clear = QPushButton("清空清单")
        btn_clear.setFixedSize(100, 35)
        btn_clear.clicked.connect(self.clear_cart)

        btn_checkout = QPushButton("确认结算")
        btn_checkout.setProperty("class", "primary")
        btn_checkout.setFixedSize(140, 45)
        btn_checkout.clicked.connect(self.handle_checkout)

        bottom_layout.addWidget(btn_clear)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.total_label)
        bottom_layout.addWidget(btn_checkout)
        
        layout.addLayout(bottom_layout)
        group_box.setLayout(layout)
        parent_layout.addWidget(group_box, stretch=6) # 购物车区占稍微大一点

    # --- 逻辑功能区 ---

    def perform_search(self):
        """执行模糊搜索"""
        keyword = self.search_input.text().strip()
        if not keyword:
            return

        products = ProductService.search_products_by_name(keyword)
        self.search_table.setRowCount(0) # 清空旧结果

        for row_idx, p in enumerate(products):
            self.search_table.insertRow(row_idx)

            # v2.0: 扩展列信息 - 添加类别、进价、售价
            self.search_table.setItem(row_idx, 0, QTableWidgetItem(str(p.id)))
            self.search_table.setItem(row_idx, 1, QTableWidgetItem(str(p.name)))
            self.search_table.setItem(row_idx, 2, QTableWidgetItem(str(p.category)))
            self.search_table.setItem(row_idx, 3, QTableWidgetItem(f"{p.cost_price:.2f}"))  # 进价
            self.search_table.setItem(row_idx, 4, QTableWidgetItem(f"{p.sell_price:.2f}"))  # 售价
            self.search_table.setItem(row_idx, 5, QTableWidgetItem(str(p.stock)))

            # 创建容器包裹按钮，防止按钮填满单元格
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            btn = QPushButton("添加")
            btn.setProperty("class", "primary")
            btn.clicked.connect(lambda checked, p=p: self.add_from_search_result(p))

            btn_layout.addWidget(btn)
            self.search_table.setCellWidget(row_idx, 6, btn_widget)  # v2.0: 操作列移到第6列

    def add_from_search_result(self, product):
        """从搜索表格点击添加按钮触发 (v1.4: 默认数量为1)"""
        self.add_to_cart_logic(product, 1)

    def handle_manual_scan(self):
        """处理扫码枪输入"""
        pid = self.id_input.text().strip()
        if not pid: return

        product = ProductService.get_product_by_id(pid)
        if product:
            self.add_to_cart_logic(product, 1) # 扫码默认数量为 1
            self.id_input.clear() # 清空扫码框方便下次输入
        else:
            QMessageBox.warning(self, "提示", "未找到该商品编号！")

    def add_to_cart_logic(self, product, qty):
        """核心逻辑：将商品加入购物车列表"""
        # 1. 检查库存预警 (前端简单检查，后端结算时会再次严查)
        if product.stock < qty:
            QMessageBox.warning(self, "库存不足", f"商品 {product.name} 库存仅剩 {product.stock}")
            return

        # 2. 检查是否已在购物车
        found = False
        for item in self.cart:
            if item['id'] == product.id:
                item['qty'] += qty
                found = True
                break

        if not found:
            self.cart.append({
                'id': product.id,
                'name': product.name,
                'price': product.sell_price,
                'cost_price': product.cost_price,  # 记录进价用于限制
                'actual_price': product.sell_price,  # 实付金额，默认等于售价
                'qty': qty
            })

        self.update_cart_table()

    def update_cart_table(self):
        """刷新下方购物车表格"""
        # v1.4: 使用 blockSignals 防止触发 itemChanged 信号导致死循环
        self.cart_table.blockSignals(True)
        self.cart_table.setRowCount(0)
        total_money = 0.0

        for idx, item in enumerate(self.cart):
            subtotal = item['actual_price'] * item['qty']  # 使用实付金额计算
            total_money += subtotal

            self.cart_table.insertRow(idx)

            # 设置不可编辑的列
            id_item = QTableWidgetItem(str(item['id']))
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.cart_table.setItem(idx, 0, id_item)

            name_item = QTableWidgetItem(str(item['name']))
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.cart_table.setItem(idx, 1, name_item)

            price_item = QTableWidgetItem(f"{item['price']:.2f}")
            price_item.setFlags(price_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.cart_table.setItem(idx, 2, price_item)

            # 实付金额使用可编辑的SpinBox（保留原有功能）
            actual_price_spin = QDoubleSpinBox()
            actual_price_spin.setRange(item['cost_price'], item['price'])  # 范围：进价到售价
            actual_price_spin.setDecimals(2)
            actual_price_spin.setValue(item['actual_price'])
            actual_price_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # 当值改变时，只更新数据和总金额，不重新刷新整个表格
            actual_price_spin.valueChanged.connect(lambda value, i=idx: self.update_actual_price_only(i, value))
            self.cart_table.setCellWidget(idx, 3, actual_price_spin)

            # v1.4: 数量列设置为可编辑
            qty_item = QTableWidgetItem(str(item['qty']))
            qty_item.setFlags(qty_item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.cart_table.setItem(idx, 4, qty_item)

            # 小计列不可编辑
            subtotal_item = QTableWidgetItem(f"{subtotal:.2f}")
            subtotal_item.setFlags(subtotal_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.cart_table.setItem(idx, 5, subtotal_item)

        self.total_label.setText(f"总金额: {total_money:.2f} 元")
        self.cart_table.blockSignals(False)

    def update_actual_price_only(self, cart_index, new_price):
        """仅更新实付金额，不刷新整个表格（避免无限循环）"""
        if cart_index < len(self.cart):
            self.cart[cart_index]['actual_price'] = new_price
            # 只更新小计和总金额
            subtotal = new_price * self.cart[cart_index]['qty']
            subtotal_item = QTableWidgetItem(f"{subtotal:.2f}")
            subtotal_item.setFlags(subtotal_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.cart_table.blockSignals(True)
            self.cart_table.setItem(cart_index, 5, subtotal_item)
            self.cart_table.blockSignals(False)
            # 重新计算总金额
            total_money = sum(item['actual_price'] * item['qty'] for item in self.cart)
            self.total_label.setText(f"总金额: {total_money:.2f} 元")

    def on_cart_item_changed(self, item):
        """监听购物车表格单元格变化 (v1.4)"""
        # 只处理数量列（第4列）的修改
        if item.column() != 4:
            return

        row = item.row()
        if row >= len(self.cart):
            return

        try:
            # 获取用户输入的新数量
            new_qty_text = item.text().strip()
            new_qty = int(new_qty_text)

            # 校验：必须是正整数
            if new_qty <= 0:
                raise ValueError("数量必须大于0")

            # 更新购物车数据
            self.cart[row]['qty'] = new_qty

            # 重新计算小计
            subtotal = self.cart[row]['actual_price'] * new_qty
            subtotal_item = QTableWidgetItem(f"{subtotal:.2f}")
            subtotal_item.setFlags(subtotal_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            # 使用 blockSignals 防止触发 itemChanged
            self.cart_table.blockSignals(True)
            self.cart_table.setItem(row, 5, subtotal_item)
            self.cart_table.blockSignals(False)

            # 重新计算总金额
            total_money = sum(item['actual_price'] * item['qty'] for item in self.cart)
            self.total_label.setText(f"总金额: {total_money:.2f} 元")

        except ValueError as e:
            # 输入无效，恢复原值
            QMessageBox.warning(self, "输入错误", f"请输入有效的正整数！\n{str(e)}")
            # 恢复原来的数量
            self.cart_table.blockSignals(True)
            item.setText(str(self.cart[row]['qty']))
            self.cart_table.blockSignals(False)

    def clear_cart(self):
        self.cart = []
        self.update_cart_table()

    def handle_checkout(self):
        if not self.cart:
            QMessageBox.warning(self, "提示", "购物车是空的！")
            return
            
        confirm = QMessageBox.question(self, "结算", f"确定进行结算吗？\n{self.total_label.text()}", 
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            success, msg = SaleService.checkout(self.cart)
            if success:
                QMessageBox.information(self, "成功", "交易完成！")
                self.clear_cart()
                # 交易完成后，如果有搜索结果，建议刷新一下搜索结果（因为库存变了）
                # 但为了简便，这里可以清空搜索结果
                self.search_table.setRowCount(0)
                self.search_input.clear()
            else:
                QMessageBox.critical(self, "失败", f"结算失败: {msg}")
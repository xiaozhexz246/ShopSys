# 文件名: ui/inventory_page.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QAbstractItemView, QLineEdit)
from PyQt6.QtCore import Qt
from services.product_service import ProductService
from ui.product_dialog import ProductDialog  # 导入刚才写的弹窗

class InventoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.show_cost_price = False  # 默认不显示进价
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()

        # --- 顶部按钮区 ---
        btn_layout = QHBoxLayout()

        self.btn_add = QPushButton("➕ 新增商品")
        self.btn_delete = QPushButton("🗑️ 删除选中")
        self.btn_refresh = QPushButton("🔄 刷新列表")

        # 美化一下按钮
        self.btn_add.setStyleSheet("background-color: #28a745; color: white;")
        self.btn_delete.setStyleSheet("background-color: #dc3545; color: white;")

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_refresh)

        # 搜索栏
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入商品名称搜索...")
        self.search_input.setMaximumWidth(200)
        self.search_input.textChanged.connect(self.search_products)  # 实时搜索
        btn_layout.addWidget(self.search_input)

        # 进价显示切换按钮
        self.btn_toggle_cost = QPushButton("显示进价")
        self.btn_toggle_cost.setStyleSheet("background-color: #6c757d; color: white; opacity: 0.6;")  # 低饱和度
        self.btn_toggle_cost.clicked.connect(self.toggle_cost_display)
        btn_layout.addWidget(self.btn_toggle_cost)

        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # --- 中间表格区 ---
        self.table = QTableWidget()
        self.table.setColumnCount(7)  # 增加类别和位置列
        self.update_table_headers()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # 设置表格行为：整行选中、不可编辑
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # v1.4: 启用表格排序
        self.table.setSortingEnabled(True)

        layout.addWidget(self.table)
        self.setLayout(layout)

        # --- 绑定事件 ---
        self.btn_add.clicked.connect(self.open_add_dialog)
        self.btn_delete.clicked.connect(self.delete_selected)
        self.btn_refresh.clicked.connect(self.load_data)

    def update_table_headers(self):
        """更新表格列头"""
        if self.show_cost_price:
            self.table.setHorizontalHeaderLabels(["编号", "名称", "类别", "位置", "进价", "售价", "库存"])
        else:
            self.table.setHorizontalHeaderLabels(["编号", "名称", "类别", "位置", "售价", "库存", ""])
            self.table.setColumnHidden(6, True)  # 隐藏最后一列

    def load_data(self, products=None):
        """加载商品数据到表格"""
        # 处理按钮信号传入的布尔值参数
        if products is None or isinstance(products, bool):
            products = ProductService.get_all_products()

        # v1.4: 在加载数据时禁用排序，加载完成后再启用，提升性能
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)

        for row_idx, p in enumerate(products):
            self.table.insertRow(row_idx)
            col = 0

            # 文本列
            self.table.setItem(row_idx, col, QTableWidgetItem(str(p.id)))
            col += 1
            self.table.setItem(row_idx, col, QTableWidgetItem(str(p.name)))
            col += 1
            self.table.setItem(row_idx, col, QTableWidgetItem(str(p.category)))
            col += 1
            self.table.setItem(row_idx, col, QTableWidgetItem(str(p.location)))
            col += 1

            if self.show_cost_price:
                # v1.4: 进价列使用 DisplayRole 存储数值
                cost_item = QTableWidgetItem()
                cost_item.setData(Qt.ItemDataRole.DisplayRole, p.cost_price)
                self.table.setItem(row_idx, col, cost_item)
                col += 1

            # v1.4: 售价列使用 DisplayRole 存储数值
            price_item = QTableWidgetItem()
            price_item.setData(Qt.ItemDataRole.DisplayRole, p.sell_price)
            self.table.setItem(row_idx, col, price_item)
            col += 1

            # v1.4: 库存列使用 DisplayRole 存储数值
            stock_item = QTableWidgetItem()
            stock_item.setData(Qt.ItemDataRole.DisplayRole, p.stock)
            self.table.setItem(row_idx, col, stock_item)

        # v1.4: 加载完成后重新启用排序
        self.table.setSortingEnabled(True)

    def open_add_dialog(self):
        """打开新增商品弹窗"""
        dialog = ProductDialog(self)
        if dialog.exec(): # 如果用户点击了 OK
            data = dialog.get_data()
            # 调用 Service 保存到数据库
            success, msg = ProductService.add_product(**data)
            if success:
                QMessageBox.information(self, "成功", "商品已添加")
                self.load_data() # 刷新表格
            else:
                QMessageBox.critical(self, "错误", f"添加失败: {msg}")

    def delete_selected(self):
        """删除选中的商品"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请先选择一行商品")
            return

        # 获取选中行的商品编号 (第0列)
        row = selected_rows[0].row()
        pid = self.table.item(row, 0).text()

        # 二次确认
        confirm = QMessageBox.question(
            self, "确认删除", f"确定要删除商品【{pid}】吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            success, msg = ProductService.delete_product(pid)
            if success:
                self.load_data()
            else:
                QMessageBox.warning(self, "错误", msg)

    def search_products(self):
        """搜索商品"""
        keyword = self.search_input.text().strip()
        if not keyword:
            # 如果搜索框为空，显示所有商品
            self.load_data()
            return

        # 模糊查询
        products = ProductService.search_products_by_name(keyword)
        self.load_data(products)

    def toggle_cost_display(self):
        """切换进价显示"""
        self.show_cost_price = not self.show_cost_price

        # 更新按钮样式
        if self.show_cost_price:
            self.btn_toggle_cost.setText("隐藏进价")
            self.btn_toggle_cost.setStyleSheet("background-color: #28a745; color: white;")  # 正常饱和度
        else:
            self.btn_toggle_cost.setText("显示进价")
            self.btn_toggle_cost.setStyleSheet("background-color: #6c757d; color: white; opacity: 0.6;")  # 低饱和度

        # 更新表头和数据
        self.update_table_headers()
        self.load_data()
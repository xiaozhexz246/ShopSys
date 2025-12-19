# 文件名: ui/inventory_page.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QAbstractItemView)
from services.product_service import ProductService
from ui.product_dialog import ProductDialog # 导入刚才写的弹窗

class InventoryPage(QWidget):
    def __init__(self):
        super().__init__()
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
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # --- 中间表格区 ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["编号", "名称", "进价", "售价", "库存"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # 设置表格行为：整行选中、不可编辑
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        self.setLayout(layout)

        # --- 绑定事件 ---
        self.btn_add.clicked.connect(self.open_add_dialog)
        self.btn_delete.clicked.connect(self.delete_selected)
        self.btn_refresh.clicked.connect(self.load_data)

    def load_data(self):
        products = ProductService.get_all_products()
        self.table.setRowCount(0)
        for row_idx, p in enumerate(products):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(p.id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(p.name)))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"{p.cost_price:.2f}"))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"{p.sell_price:.2f}"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(p.stock)))

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
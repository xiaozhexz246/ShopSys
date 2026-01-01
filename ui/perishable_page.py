# 文件名: ui/perishable_page.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QSpinBox, QGroupBox, QFormLayout, QDateEdit,
                             QDialog, QDialogButtonBox, QAbstractItemView)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor
from services.product_service import ProductService
from services.perishable_service import PerishableService
from datetime import datetime, timedelta

class PerishablePage(QWidget):
    def __init__(self):
        super().__init__()
        self.current_product = None  # 当前选中的商品
        self.init_ui()
        self.load_batches()  # 加载批次数据

    def init_ui(self):
        # v1.6: 主布局改为垂直布局：上部是录入区，下部是监控区
        main_layout = QVBoxLayout()

        # 1. 初始化上部：录入区
        self.init_input_area(main_layout)

        # 2. 初始化下部：监控区
        self.init_monitor_area(main_layout)

        self.setLayout(main_layout)

    def init_input_area(self, parent_layout):
        """v1.6: 初始化上部录入区,固定高度"""
        group_box = QGroupBox("批次录入")
        group_box.setMaximumHeight(200)  # v1.6: 固定最大高度
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        # --- 商品编号输入框 ---
        self.product_id_input = QLineEdit()
        self.product_id_input.setPlaceholderText("扫码或输入商品编号...")
        self.product_id_input.returnPressed.connect(self.load_product_info)
        form_layout.addRow("商品编号:", self.product_id_input)

        # --- 商品名称显示 (只读) ---
        self.product_name_label = QLineEdit()
        self.product_name_label.setReadOnly(True)
        self.product_name_label.setPlaceholderText("自动填充")
        form_layout.addRow("商品名称:", self.product_name_label)

        # --- 生产日期选择 ---
        self.production_date_input = QDateEdit()
        self.production_date_input.setCalendarPopup(True)
        self.production_date_input.setDate(QDate.currentDate())  # 默认今天
        self.production_date_input.dateChanged.connect(self.update_expiration_date)
        form_layout.addRow("生产日期:", self.production_date_input)

        # --- 保质期输入 (天数) ---
        self.shelf_life_input = QSpinBox()
        self.shelf_life_input.setRange(1, 3650)  # 1天到10年
        self.shelf_life_input.setValue(30)  # 默认30天
        self.shelf_life_input.setSuffix(" 天")
        self.shelf_life_input.valueChanged.connect(self.update_expiration_date)
        form_layout.addRow("保质期:", self.shelf_life_input)

        # --- 过期日期显示 (自动计算) ---
        self.expiration_date_label = QLabel()
        self.expiration_date_label.setStyleSheet("font-weight: bold; color: #dc3545;")
        self.update_expiration_date()  # 初始化显示
        form_layout.addRow("过期日期:", self.expiration_date_label)

        # --- 批次数量 ---
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 10000)
        self.quantity_input.setValue(1)
        form_layout.addRow("批次数量:", self.quantity_input)

        layout.addLayout(form_layout)

        # --- 登记按钮 ---
        btn_register = QPushButton("登记批次")
        btn_register.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 8px;")
        btn_register.clicked.connect(self.register_batch)
        layout.addWidget(btn_register)

        group_box.setLayout(layout)
        parent_layout.addWidget(group_box)  # v1.6: 不使用stretch,固定大小

    def init_monitor_area(self, parent_layout):
        """v1.6: 初始化下部监控区,占据剩余空间"""
        group_box = QGroupBox("批次监控")
        layout = QVBoxLayout()

        # v1.6: 顶部按钮区
        btn_layout = QHBoxLayout()

        btn_delete = QPushButton("🗑️ 删除选中批次")
        btn_delete.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold;")
        btn_delete.clicked.connect(self.delete_selected_batch)
        btn_layout.addWidget(btn_delete)

        btn_refresh = QPushButton("🔄 刷新列表")
        btn_refresh.clicked.connect(self.load_batches)
        btn_layout.addWidget(btn_refresh)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # --- 批次表格 ---
        self.batch_table = QTableWidget()
        self.batch_table.setColumnCount(7)  # v1.6: 添加操作列
        self.batch_table.setHorizontalHeaderLabels(["商品名称", "生产日期", "保质期(天)", "过期日期", "数量", "状态", "操作"])
        self.batch_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.batch_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        # v1.6: 设置表格选择行为
        self.batch_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.batch_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.batch_table)

        group_box.setLayout(layout)
        parent_layout.addWidget(group_box, stretch=1)  # v1.6: 占据剩余空间

    # --- 逻辑功能区 ---

    def load_product_info(self):
        """
        当用户输入商品编号并回车时触发
        核心逻辑：
        1. 查询商品名称
        2. 查询该商品最近一次录入的保质期
        3. 自动填充到界面
        """
        product_id = self.product_id_input.text().strip()
        if not product_id:
            return

        # 第一步：查询商品
        product = ProductService.get_product_by_id(product_id)
        if not product:
            QMessageBox.warning(self, "错误", f"商品编号 {product_id} 不存在！")
            self.product_name_label.clear()
            self.current_product = None
            return

        # 保存当前商品
        self.current_product = product

        # 填充商品名称
        self.product_name_label.setText(product.name)

        # 第二步：查询最近一次的保质期
        last_shelf_life = PerishableService.get_last_shelf_life(product_id)

        if last_shelf_life:
            # 自动填充保质期
            self.shelf_life_input.setValue(last_shelf_life)
            # 提示用户
            self.product_name_label.setStyleSheet("background-color: #d4edda;")  # 绿色背景提示
        else:
            # 没有历史记录，保持默认值，提示用户手动输入
            self.product_name_label.setStyleSheet("background-color: #fff3cd;")  # 黄色背景提示

        # 更新过期日期显示
        self.update_expiration_date()

    def update_expiration_date(self):
        """
        当生产日期或保质期改变时，实时计算并显示过期日期
        """
        prod_date = self.production_date_input.date().toPyDate()
        shelf_life = self.shelf_life_input.value()

        # 计算过期日期
        exp_date = prod_date + timedelta(days=shelf_life)

        # 显示
        self.expiration_date_label.setText(exp_date.strftime("%Y-%m-%d"))

        # 根据剩余天数调整颜色
        days_left = (exp_date - datetime.now().date()).days
        if days_left < 0:
            self.expiration_date_label.setStyleSheet("font-weight: bold; color: #dc3545;")  # 红色-已过期
        elif days_left <= 7:
            self.expiration_date_label.setStyleSheet("font-weight: bold; color: #ffc107;")  # 黄色-临期
        else:
            self.expiration_date_label.setStyleSheet("font-weight: bold; color: #28a745;")  # 绿色-正常

    def register_batch(self):
        """登记批次"""
        if not self.current_product:
            QMessageBox.warning(self, "提示", "请先输入商品编号！")
            return

        product_id = self.current_product.id
        prod_date = self.production_date_input.date().toPyDate()
        shelf_life = self.shelf_life_input.value()
        quantity = self.quantity_input.value()

        # 调用 Service 登记批次
        success, msg = PerishableService.add_batch(product_id, prod_date, shelf_life, quantity)

        if success:
            QMessageBox.information(self, "成功", "批次登记成功！")
            # 清空输入框
            self.product_id_input.clear()
            self.product_name_label.clear()
            self.product_name_label.setStyleSheet("")
            self.production_date_input.setDate(QDate.currentDate())
            self.shelf_life_input.setValue(30)
            self.quantity_input.setValue(1)
            self.current_product = None
            # 刷新批次列表
            self.load_batches()
        else:
            QMessageBox.critical(self, "失败", f"登记失败: {msg}")

    def load_batches(self):
        """v1.6: 加载并显示所有批次"""
        batches = PerishableService.check_expirations()
        self.batch_table.setRowCount(0)

        for row_idx, batch in enumerate(batches):
            self.batch_table.insertRow(row_idx)

            # 填充数据
            self.batch_table.setItem(row_idx, 0, QTableWidgetItem(batch['product_name']))
            self.batch_table.setItem(row_idx, 1, QTableWidgetItem(batch['production_date'].strftime("%Y-%m-%d")))
            self.batch_table.setItem(row_idx, 2, QTableWidgetItem(str(batch['shelf_life'])))
            self.batch_table.setItem(row_idx, 3, QTableWidgetItem(batch['expiration_date'].strftime("%Y-%m-%d")))
            self.batch_table.setItem(row_idx, 4, QTableWidgetItem(str(batch['quantity'])))

            # 状态列带颜色
            status_item = QTableWidgetItem(batch['status'])
            if batch['status'] == "已过期":
                status_item.setForeground(QColor(220, 53, 69))  # 红色
                status_item.setBackground(QColor(248, 215, 218))  # 浅红背景
            elif batch['status'] == "临期":
                status_item.setForeground(QColor(255, 193, 7))  # 黄色
                status_item.setBackground(QColor(255, 243, 205))  # 浅黄背景
            else:
                status_item.setForeground(QColor(40, 167, 69))  # 绿色

            self.batch_table.setItem(row_idx, 5, status_item)

            # v1.6: 添加编辑按钮
            btn_edit = QPushButton("✏️ 编辑")
            btn_edit.setStyleSheet("background-color: #007bff; color: white;")
            btn_edit.clicked.connect(lambda checked, b=batch: self.open_edit_dialog(b))
            self.batch_table.setCellWidget(row_idx, 6, btn_edit)

    def delete_selected_batch(self):
        """v1.6: 删除选中的批次"""
        selected_rows = self.batch_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请先选择一个批次！")
            return

        # 获取选中行的索引
        row = selected_rows[0].row()

        # 获取该行的批次ID (需要在load_batches时存储)
        # 由于我们没有直接在表格中显示batch_id,我们需要重新获取
        batches = PerishableService.check_expirations()
        if row >= len(batches):
            QMessageBox.warning(self, "错误", "无法获取批次信息！")
            return

        batch = batches[row]
        batch_id = batch['batch_id']
        product_name = batch['product_name']

        # 二次确认
        confirm = QMessageBox.question(
            self, "确认删除",
            f"确定要删除批次【{product_name}】吗？\n生产日期: {batch['production_date'].strftime('%Y-%m-%d')}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            success, msg = PerishableService.delete_batch(batch_id)
            if success:
                QMessageBox.information(self, "成功", msg)
                self.load_batches()  # 刷新表格
            else:
                QMessageBox.critical(self, "失败", msg)

    def open_edit_dialog(self, batch):
        """v1.6: 打开编辑批次的弹窗"""
        dialog = BatchEditDialog(self, batch)
        if dialog.exec():
            # 获取编辑后的数据
            data = dialog.get_data()
            # 调用Service更新
            success, msg = PerishableService.update_batch(
                batch_id=batch['batch_id'],
                production_date=data['production_date'],
                shelf_life=data['shelf_life'],
                quantity=data['quantity']
            )
            if success:
                QMessageBox.information(self, "成功", msg)
                self.load_batches()  # 刷新表格
            else:
                QMessageBox.critical(self, "失败", msg)


# v1.6: 批次编辑弹窗
class BatchEditDialog(QDialog):
    def __init__(self, parent=None, batch=None):
        super().__init__(parent)
        self.batch = batch
        self.setWindowTitle("编辑批次")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # 商品名称(只读显示)
        self.product_name_label = QLabel(self.batch['product_name'])
        self.product_name_label.setStyleSheet("font-weight: bold; color: #007bff;")
        form_layout.addRow("商品名称:", self.product_name_label)

        # 生产日期
        self.production_date_input = QDateEdit()
        self.production_date_input.setCalendarPopup(True)
        # 将字符串日期转换为QDate
        prod_date = self.batch['production_date']
        self.production_date_input.setDate(QDate(prod_date.year, prod_date.month, prod_date.day))
        form_layout.addRow("生产日期:", self.production_date_input)

        # 保质期
        self.shelf_life_input = QSpinBox()
        self.shelf_life_input.setRange(1, 3650)
        self.shelf_life_input.setValue(self.batch['shelf_life'])
        self.shelf_life_input.setSuffix(" 天")
        form_layout.addRow("保质期:", self.shelf_life_input)

        # 数量
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 10000)
        self.quantity_input.setValue(self.batch['quantity'])
        form_layout.addRow("批次数量:", self.quantity_input)

        layout.addLayout(form_layout)

        # 按钮区
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_data(self):
        """获取编辑后的数据"""
        return {
            'production_date': self.production_date_input.date().toPyDate(),
            'shelf_life': self.shelf_life_input.value(),
            'quantity': self.quantity_input.value()
        }

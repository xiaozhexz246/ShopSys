# 文件名: ui/perishable_page.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox, QGroupBox, QAbstractItemView,
                             QDialog, QDialogButtonBox, QFormLayout, QSpinBox, QDateEdit, QLabel)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QCursor
from services.perishable_service import PerishableService
from ui.batch_dialog import BatchInputDialog

class PerishablePage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_batches()  # 加载批次数据

    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout()

        # 批次监控区域
        self.init_monitor_area(main_layout)

        self.setLayout(main_layout)

    def init_monitor_area(self, parent_layout):
        """初始化监控区,占据所有空间"""
        group_box = QGroupBox("批次监控")
        layout = QVBoxLayout()

        # 顶部按钮区
        btn_layout = QHBoxLayout()

        # 新增批次按钮
        btn_add = QPushButton("➕ 新增批次")
        btn_add.setProperty("class", "primary")
        btn_add.setFixedSize(120, 32)
        btn_add.clicked.connect(self.open_add_dialog)
        btn_layout.addWidget(btn_add)

        btn_delete = QPushButton("🗑️ 删除选中批次")
        btn_delete.setProperty("class", "danger")
        btn_delete.setFixedSize(130, 32)
        btn_delete.clicked.connect(self.delete_selected_batch)
        btn_layout.addWidget(btn_delete)

        btn_refresh = QPushButton("🔄 刷新列表")
        btn_refresh.setFixedSize(100, 32)
        btn_refresh.clicked.connect(self.load_batches)
        btn_layout.addWidget(btn_refresh)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 批次表格
        self.batch_table = QTableWidget()
        self.batch_table.setColumnCount(7)
        self.batch_table.setHorizontalHeaderLabels(["商品名称", "生产日期", "保质期(天)", "过期日期", "数量", "状态", "操作"])
        self.batch_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.batch_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.batch_table.verticalHeader().setDefaultSectionSize(45)  # 设置默认行高
        # 设置表格选择行为
        self.batch_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.batch_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.batch_table)

        group_box.setLayout(layout)
        parent_layout.addWidget(group_box)

    def open_add_dialog(self):
        """打开新增批次对话框"""
        dialog = BatchInputDialog(self)
        if dialog.exec():
            # 对话框中已经保存成功，直接刷新列表
            self.load_batches()

    def load_batches(self):
        """加载并显示所有批次"""
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

            # v1.9: 添加编辑按钮 - 使用扁平按钮样式
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            btn_edit = QPushButton("编辑")
            btn_edit.setProperty("class", "table-btn")
            btn_edit.setFlat(True)
            btn_edit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_edit.clicked.connect(lambda checked, b=batch: self.open_edit_dialog(b))

            btn_layout.addWidget(btn_edit)
            self.batch_table.setCellWidget(row_idx, 6, btn_widget)

    def delete_selected_batch(self):
        """删除选中的批次"""
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
        """打开编辑批次的弹窗"""
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


# 批次编辑弹窗
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

# 文件名: ui/batch_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QDialogButtonBox, QMessageBox, QSpinBox, QDateEdit, QLabel)
from PyQt6.QtCore import QDate, Qt
from services.product_service import ProductService
from services.perishable_service import PerishableService
from datetime import datetime, timedelta

class BatchInputDialog(QDialog):
    def __init__(self, parent=None):
        """
        批次录入对话框
        :param parent: 父窗口
        """
        super().__init__(parent)
        self.current_product = None  # 当前选中的商品
        self.setWindowTitle("新增批次")
        self.setFixedSize(400, 350)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # --- 商品编号输入框 ---
        self.product_id_input = QLineEdit()
        self.product_id_input.setPlaceholderText("扫码或输入商品编号...")
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

        # 3. 确定/取消 按钮组
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.validate_and_accept)  # 点击OK先校验
        self.buttons.rejected.connect(self.reject)

        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def keyPressEvent(self, event):
        """重写键盘事件，拦截扫码枪在商品编号框的回车"""
        # 1. 检测是否是回车键 (支持大键盘 Enter 和小键盘 Return)
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # 2. 检查焦点是否在"商品编号"输入框
            if self.product_id_input.hasFocus():
                # 3. 核心：只转移焦点，不提交
                print("检测到扫码枪回车，拦截提交，跳转焦点")  # debug用
                self.load_product_info()  # 加载商品信息
                self.production_date_input.setFocus()  # 跳转到生产日期输入框
                event.accept()  # 标记事件已处理
                return  # 强制结束，不再传递给父类(QDialog)

        # 4. 其他情况（如在确认按钮上按回车），交给父类处理（即正常提交）
        super().keyPressEvent(event)

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

    def validate_and_accept(self):
        """简单校验：必须先选择商品"""
        if not self.current_product:
            QMessageBox.warning(self, "警告", "请先输入商品编号！")
            return

        product_id = self.current_product.id
        prod_date = self.production_date_input.date().toPyDate()
        shelf_life = self.shelf_life_input.value()
        quantity = self.quantity_input.value()

        # 调用 Service 登记批次
        success, msg = PerishableService.add_batch(product_id, prod_date, shelf_life, quantity)

        if success:
            QMessageBox.information(self, "成功", "批次登记成功！")
            self.accept()  # 关闭弹窗并返回 Accepted 状态
        else:
            QMessageBox.critical(self, "失败", f"登记失败: {msg}")

    def get_data(self):
        """返回用户输入的数据（如果需要在外部使用）"""
        return {
            "product_id": self.current_product.id if self.current_product else None,
            "production_date": self.production_date_input.date().toPyDate(),
            "shelf_life": self.shelf_life_input.value(),
            "quantity": self.quantity_input.value()
        }

# 文件名: ui/product_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QDialogButtonBox, QDoubleSpinBox, QSpinBox, QMessageBox, QComboBox)
from PyQt6.QtCore import Qt

class ProductDialog(QDialog):
    def __init__(self, parent=None, product=None):
        """
        商品对话框
        :param parent: 父窗口
        :param product: Product对象，如果提供则为编辑模式，否则为新增模式
        """
        super().__init__(parent)
        self.product = product
        self.is_edit_mode = product is not None

        if self.is_edit_mode:
            self.setWindowTitle("编辑商品")
        else:
            self.setWindowTitle("新增商品")

        self.setFixedSize(350, 350)  # 增加高度以适应新字段
        self.setup_ui()

        # 如果是编辑模式，回显数据
        if self.is_edit_mode:
            self.load_product_data()

    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # 1. 定义输入控件
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("扫描或输入条码")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("商品名称")

        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0, 100000) # 范围
        self.cost_input.setDecimals(2)      # 小数点后两位

        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 100000)
        self.price_input.setDecimals(2)

        self.stock_input = QSpinBox()
        self.stock_input.setRange(0, 99999)

        # 商品类别下拉框 (可编辑)
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.addItems(["香烟", "酒水", "饮料", "零食", "日用品", "未设置"])
        self.category_input.setCurrentText("未设置")

        # 存放位置下拉框 (可编辑)
        self.location_input = QComboBox()
        self.location_input.setEditable(True)
        self.location_input.addItems(["一楼", "二楼", "楼梯", "未设置"])
        self.location_input.setCurrentText("未设置")

        # 2. 添加到表单布局
        form_layout.addRow("商品编号:", self.id_input)
        form_layout.addRow("商品名称:", self.name_input)
        form_layout.addRow("商品类别:", self.category_input)
        form_layout.addRow("存放位置:", self.location_input)
        form_layout.addRow("进货价:", self.cost_input)
        form_layout.addRow("零售价:", self.price_input)
        form_layout.addRow("库存量:", self.stock_input)

        layout.addLayout(form_layout)

        # 3. 确定/取消 按钮组
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.validate_and_accept) # 点击OK先校验
        self.buttons.rejected.connect(self.reject)
        
        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def validate_and_accept(self):
        """简单校验：编号和名称不能为空"""
        if not self.id_input.text().strip():
            QMessageBox.warning(self, "警告", "商品编号不能为空")
            return
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "警告", "商品名称不能为空")
            return

        self.accept() # 关闭弹窗并返回 Accepted 状态

    def load_product_data(self):
        """加载商品数据到输入框（编辑模式）"""
        if self.product:
            self.id_input.setText(str(self.product.id))
            self.id_input.setReadOnly(True)  # 编辑模式下编号不可修改
            self.name_input.setText(str(self.product.name))
            self.category_input.setCurrentText(str(self.product.category))
            self.location_input.setCurrentText(str(self.product.location))
            self.cost_input.setValue(self.product.cost_price)
            self.price_input.setValue(self.product.sell_price)
            self.stock_input.setValue(self.product.stock)
            self.stock_input.setReadOnly(True)  # 编辑模式下库存不可修改（通过进货/出售改变）

    def keyPressEvent(self, event):
        """重写键盘事件，拦截扫码枪在商品编号框的回车"""
        # 1. 检测是否是回车键 (支持大键盘 Enter 和小键盘 Return)
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # 2. 检查焦点是否在"商品编号"输入框
            if self.id_input.hasFocus():
                # 3. 核心：只转移焦点，不提交
                print("检测到扫码枪回车，拦截提交，跳转焦点")  # debug用
                self.name_input.setFocus()  # 跳转到下一个框
                event.accept()  # 标记事件已处理
                return  # 强制结束，不再传递给父类(QDialog)

        # 4. 其他情况（如在确认按钮上按回车），交给父类处理（即正常提交）
        super().keyPressEvent(event)

    def get_data(self):
        """返回用户输入的数据"""
        return {
            "id": self.id_input.text().strip(),
            "name": self.name_input.text().strip(),
            "category": self.category_input.currentText().strip(),
            "location": self.location_input.currentText().strip(),
            "cost": self.cost_input.value(),
            "price": self.price_input.value(),
            "stock": self.stock_input.value()
        }
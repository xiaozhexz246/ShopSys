# 文件名: ui/product_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QDialogButtonBox, QDoubleSpinBox, QSpinBox, QMessageBox, QComboBox)

class ProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新增商品")
        self.setFixedSize(350, 350)  # 增加高度以适应新字段
        self.setup_ui()

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
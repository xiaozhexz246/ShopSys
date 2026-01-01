# 超市售货系统 UI 优化清单 (v1.7 Clean Version)

**目标**: 在不破坏布局的前提下，通过 Python 代码约束控件尺寸，配合简约的 QSS 样式，打造清爽、紧凑的界面。

---

## 🎨 Phase 1: 基础样式定义 (Safe QSS)
建立一套清爽、扁平化的视觉规范，避免兼容性报错。

- [ ] **创建/更新 `assets/styles.qss`**
    * **全局字体**: `Microsoft YaHei`, 10pt (比之前大一点，但不过分)。
    * **QPushButton (通用)**:
        * 背景: 白色 `#FFFFFF`。
        * 边框: 1px 实线灰色 `#DCDFE6`。
        * 圆角: 4px。
        * 尺寸: `min-width: 80px`, `min-height: 30px` (保证最小点击区域)。
        * Padding: `5px 15px`。
        * Hover: 边框变蓝 `#409EFF`，文字变蓝。
    * **Primary Button (强调按钮)**:
        * 定义一个 `.primary` 类（用于结算、进货、查询）。
        * 背景: 蓝色 `#409EFF`，文字: 白色，无边框。
        * Hover: 背景略深 `#66B1FF`。
    * **Danger Button (危险按钮)**:
        * 定义一个 `.danger` 类（用于删除）。
        * 背景: 红色 `#F56C6C`，文字: 白色。
    * **QTableWidget**:
        * 选中行背景色: `#ECF5FF` (淡蓝)。
        * 选中行文字色: `#000000` (保持黑色，清晰)。
        * 行高: 默认设为 35px (通过代码设置，非 QSS)。

---

## 📏 Phase 2: 布局与尺寸约束 (Layout Constraints)
**核心思想**: 使用 `addStretch()` 弹簧来挤压控件，防止它们变大。

- [ ] **优化 `ui/cashier_page.py` (收银台)**
    * **底部结算栏**:
        * 使用 `QHBoxLayout`。
        * **顺序**: `[清空按钮] -> [addStretch() 弹簧] -> [总金额标签] -> [确认结算按钮]`。
        * *效果*: 弹簧会占满中间所有空白，把清空按钮挤到最左，把金额和结算挤到最右。
    * **确认结算按钮**:
        * `setFixedSize(140, 45)`。大小适中，不用太大。
        * 样式设为 Primary。

- [ ] **优化 `ui/perishable_page.py` (易过期管理)**
    * **上半部分 (录入区)**:
        * 将“登记批次”按钮放入一个水平布局 `QHBoxLayout`。
        * **顺序**: `[addStretch() 弹簧] -> [登记按钮]`。
        * *效果*: 按钮固定在右侧，不会横跨全屏。
        * 按钮尺寸: `setFixedSize(120, 35)`。

- [ ] **优化 `ui/inventory_page.py` (商品管理)**
    * **顶部搜索栏**:
        * 确保所有输入框和按钮都在一个 `QHBoxLayout` 里。
        * 结尾加上 `addStretch()`，确保它们紧凑地靠左排列。

---

## 🧩 Phase 3: 表格按钮精致化 (Table Cells)
解决“按钮填满单元格”的问题。

- [ ] **通用表格优化逻辑**
    * 在所有包含操作按钮的表格 (`inventory`, `perishable`, `replenish`) 中应用以下逻辑：
    * **不要**直接 `setCellWidget(btn)`。
    * **改为**:
        1. 创建 `widget = QWidget()`。
        2. `layout = QHBoxLayout(widget)`。
        3. `layout.setContentsMargins(5, 2, 5, 2)` (关键：设置留白)。
        4. `layout.setAlignment(Qt.AlignmentFlag.AlignCenter)` (关键：居中)。
        5. `btn.setFixedSize(60, 25)` (关键：小巧的固定尺寸)。
        6. `layout.addWidget(btn)`。
        7. `table.setCellWidget(widget)`。
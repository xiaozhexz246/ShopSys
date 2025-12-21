# 超市售货系统 v1.4 升级任务清单 (Todo List)

**目标**: 增加销售明细查询与 Excel 导出功能，重构收银台数量修改逻辑，并增强商品列表的排序体验。

---

## 🛠️ Phase 1: 后端服务升级 (Stats & Export)
我们需要支持查询“原始销售记录”而不仅是“统计结果”，并实现文件导出逻辑。

- [ ] **更新 `services/stats_service.py`**
    * 新增方法 `get_raw_sales_records(start_date, end_date)`:
        * 联表查询 `SaleRecord` 和 `Product`。
        * 返回 DataFrame，包含字段：`[流水号, 商品名称, 类别, 单价, 数量, 总金额, 利润, 时间]`。
    * 新增方法 `export_to_excel(dataframe)`:
        * **路径检查**: 检查 `backups/sells/` 文件夹是否存在，不存在则创建。
        * **文件命名**: 使用时间戳，例如 `sales_record_20251221_153022.xlsx`。
        * **保存**: 调用 `df.to_excel()` 保存文件，并返回保存后的完整路径。

---

## 📊 Phase 2: 销售报表界面升级 (UI - Stats Page)
在左侧 Tab 中添加详单页，并整合导出功能。

- [ ] **修改 `ui/stats_page.py`**
    * **Tab 结构调整**:
        * 在 `QTabWidget` 的 index 0 位置插入一个新 Tab，命名为 **"📜 销售明细"**。
        * 原来的趋势图、占比图顺延。
    * **"销售明细" Tab 布局**:
        * 顶部：一个按钮 **"📤 导出当前记录为 Excel"**。
        * 主体：一个 `QTableWidget`，显示 Phase 1 查询到的原始数据。
    * **联动逻辑**:
        * 当右侧点击“查询”时，同时刷新这个 Table 的数据。
        * 点击“导出”按钮时，将当前 Table 对应的数据传给 Service 进行导出，成功后弹窗提示文件位置。

---

## 🛒 Phase 3: 收银台逻辑重构 (UI - Cashier Page)
简化搜索操作，增强购物车操作。

- [ ] **修改 `ui/cashier_page.py` - 上半部分 (搜索区)**
    * **移除控件**: 删除搜索结果表格中的 `SpinBox` (数量调节框)。
    * **逻辑变更**: 点击“添加”按钮时，不再读取 SpinBox，而是默认数量 `1` 直接加入购物车。

- [ ] **修改 `ui/cashier_page.py` - 下半部分 (购物车)**
    * **开启编辑**: 将购物车表格的“数量”列设置为 **可编辑** (`setFlags` 包含 `ItemIsEditable`)。
    * **监听变更**: 连接 `itemChanged` 或 `cellChanged` 信号。
    * **重算逻辑**:
        * 当用户修改数量列时：
            1. 校验输入是否为正整数。
            2. 更新 `self.cart` 列表中对应商品的 `qty`。
            3. 重新计算该行的“小计”。
            4. 重新计算底部的“总金额”。
            5. **注意**: 使用 `blockSignals(True)` 防止代码更新表格时触发死循环。

---

## 📦 Phase 4: 商品管理排序优化 (UI - Inventory Page)
一行代码实现排序。

- [ ] **修改 `ui/inventory_page.py`**
    * 在初始化表格时，调用 `self.table.setSortingEnabled(True)`。
    * **注意**: 确保数字列（进价、售价、库存）使用的是 `Qt.UserRole` 存储数值或重写排序逻辑，否则默认会按字符串排序（即 "10" 会排在 "2" 前面）。
    * *Claude 提示*: "请确保数字列能按数值大小排序，而不是按字符顺序排序（使用 QTableWidgetItem 的 setData(Qt.ItemDataRole.DisplayRole, value)）"。

特别注意： 在修改 ui/inventory_page.py 时，插入表格数据时请使用 item.setData(Qt.ItemDataRole.DisplayRole, number_value) 而不是直接 QTableWidgetItem(str(number_value))。 这样 setSortingEnabled(True) 才能正确地按数值大小进行排序，而不是按字符串排序。
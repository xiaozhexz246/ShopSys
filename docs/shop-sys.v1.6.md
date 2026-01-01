# 超市售货系统 v1.6 优化任务清单 (Todo List)

**目标**: 优化进货管理的数据安全性，增强商品管理的搜索与编辑体验，重构易过期管理的布局与操作逻辑（采用弹窗编辑）。

---

## 🚚 Phase 1: 进货管理优化 (ReplenishPage UI Fix)
修复上半部分数据可编辑的安全隐患，保留下半部分的灵活度。

- [ ] **修改 `ui/replenish_page.py`**
    * **上半部分 (搜索结果表)**:
        * 设置表格属性 `setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)`，彻底禁止用户修改搜索结果。
    * **下半部分 (待进货清单)**:
        * 保持“进货数量”和“进价”列可编辑（使用 SpinBox），允许用户根据实际进货情况调整。
        * 锁定“商品名称”、“编号”等其他列为只读。

---

## 📦 Phase 2: 商品管理增强 (InventoryPage Upgrade)
提升搜索效率，统一操作入口。

- [ ] **修改 `ui/inventory_page.py` - 搜索栏**
    * 在顶部的搜索区域，新增一个 `QLineEdit` (placeholder="输入编号精准搜索")。
    * **交互逻辑**: 输入编号回车 -> 调用 `ProductService.get_product_by_id` -> 过滤表格只显示该商品。
    * *注意*: 保留原有的“名称模糊搜索”框，两者共存。

- [ ] **修改 `ui/inventory_page.py` - 编辑按钮**
    * **逻辑修正**: 将“编辑按钮”的渲染逻辑移出 `if show_cost:` 判断块。
    * **效果**: 无论是否显示进价，表格最后一列始终显示“✏️ 编辑”按钮。
    * 优化列宽，防止按钮显示不全。

---

## 🥛 Phase 3: 易过期管理重构 (PerishablePage Refactor)
布局大改版 + 弹窗编辑 + 删除功能。

- [ ] **布局重构 (Layout Change)**
    * **修改 `ui/perishable_page.py`**:
        * 将主布局从 `QHBoxLayout` (左右) 改为 `QVBoxLayout` (上下)。
        * **上半区 (录入区)**: 高度固定（如 160px），包含输入框和“登记”按钮。
        * **下半区 (监控区)**: 放置表格和功能按钮，占据剩余空间。

- [ ] **后端服务升级 (Service)**
    * **修改 `services/perishable_service.py`**:
        * 新增 `delete_batch(batch_id)`: 根据 ID 删除批次。
        * 新增 `update_batch(batch_id, production_date, shelf_life, quantity)`: 更新批次信息。

- [ ] **删除功能 (Delete)**
    * 在监控区顶部添加一个红色按钮 "🗑️ 删除选中批次"。
    * **逻辑**: 获取表格当前选中行 -> 拿到 Batch ID -> 弹窗确认 -> 调用 Service 删除 -> 刷新表格。

- [ ] **弹窗编辑功能 (Popup Edit)**
    * **新建 `BatchEditDialog` 类** (可放在 `ui/perishable_page.py` 内部或新文件):
        * 继承自 `QDialog`。
        * 包含表单：生产日期 (`QDateEdit`)、保质期 (`QSpinBox`)、数量 (`QSpinBox`)。
        * *注意*: 商品名称通常不可改，仅作显示。
    * **集成到表格**:
        * 在表格最后一列添加 "✏️ 编辑" 按钮。
        * **交互逻辑**: 点击按钮 -> 弹出 `BatchEditDialog` (回显当前行数据) -> 用户修改确认 -> 调用 Service 更新 -> 刷新表格。

---

## 🚀 Phase 4: 测试与验证
- [ ] **进
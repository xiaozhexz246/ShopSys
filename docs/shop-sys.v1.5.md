# 超市售货系统 v1.5 升级任务清单 (Todo List)

**目标**: 完善供应链进货管理、补充商品编辑功能，并构建独立的易过期商品批次追踪系统（基于批次记忆保质期）。

---

## 🛠️ Phase 1: 数据库架构升级 (Schema Migration)
引入进货记录表和易过期批次表，注意 `Product` 表结构保持相对稳定。

- [ ] **修改 `models.py`**
    * **新增 `PurchaseRecord` (进货记录表)**:
        * `id`: Integer, PK
        * `product_id`: String, FK -> products.id
        * `quantity`: Integer (进货数量)
        * `cost_price`: Float (当时的进价)
        * `purchase_time`: DateTime (进货时间, default=now)

    * **新增 `PerishableBatch` (易过期批次表)**:
        * `id`: Integer, PK
        * `product_id`: String, FK -> products.id
        * `production_date`: Date (生产日期)
        * `shelf_life`: Integer (保质期天数)  <-- *注意：字段存在这里*
        * `expiration_date`: Date (过期日期, 计算字段)
        * `quantity`: Integer (该批次数量)
        * `created_at`: DateTime (记录创建时间，用于查找最近一次记录)

- [ ] **编写数据库迁移脚本 (`migrate_v1.5.py`)**
    * 自动创建 `purchase_records` 和 `perishable_batches` 两张新表。
    * *注意：不需要修改 Product 表结构。*

---

## 🚚 Phase 2: 进货管理模块 (Replenishment)
实现“先搜索确认，再批量入库”的流程。

- [ ] **更新 `services/product_service.py`**
    * 新增 `replenish_stock(cart_items)`:
        * 遍历进货清单。
        * 更新 `Product.stock += quantity`。
        * 更新 `Product.cost_price` 为最新进价（如果变动）。
        * 插入记录到 `PurchaseRecord` 表。

- [ ] **新建 `ui/replenish_page.py` (进货页面)**
    * **布局**: 上下分栏 (`QVBoxLayout`)。
    * **上半部 (搜索源)**:
        * 复用收银台的搜索逻辑 (支持扫码/模糊搜索)。
        * 显示: `[编号, 名称, 类别, 当前进价, 当前库存]`。
        * 操作: "⬇️ 加入进货单" 按钮。
    * **下半部 (待进货区)**:
        * 表格显示: `[编号, 名称, 进货数量(SpinBox), 进价(DoubleSpinBox)]`。
        * 底部: "✅ 确认进货" 按钮。

---

## 📝 Phase 3: 商品编辑功能 (Product Editing)
补全商品管理能力。

- [ ] **修改 `services/product_service.py`**
    * 新增 `update_product(product_id, name, category, location, cost, price)`:
        * 根据 ID 更新商品基础信息。

- [ ] **修改 `ui/inventory_page.py`**
    * 在表格每一行增加 "✏️ 编辑" 按钮。
    * 点击后复用 `ProductDialog`，回显当前数据。
    * Dialog 保存时，根据模式（新增/编辑）调用不同的 Service 方法。

---

## 🥛 Phase 4: 易过期商品管理 (Perishable Management)
独立的批次追踪系统，支持“智能回填”。

- [ ] **新建 `services/perishable_service.py`**
    * `add_batch(product_id, prod_date, shelf_life, qty)`:
        * 计算 `expiration_date = prod_date + days(shelf_life)`。
        * 插入数据库。
    * `get_latest_batch_info(product_id)`:
        * **核心逻辑**: 查询该商品 ID 在 `PerishableBatch` 表中**最近添加的一条记录**。
        * 返回该记录的 `shelf_life`，用于自动填充。
    * `check_expirations()`:
        * 查询所有批次，计算剩余天数。
        * 返回状态列表。

- [ ] **新建 `ui/perishable_page.py` (易过期管理)**
    * **布局**: 左右布局。
    * **左侧 (录入区)**:
        * **输入框 1**: 商品编号 (支持扫码/输入回车)。
        * **联动逻辑 (重点)**:
            1. 输入编号回车 -> 查 `Product` 表 -> 填入“商品名称”。
            2. 同时查 `PerishableBatch` 表 -> 找最近一次记录 -> 填入“保质期(天)”。
            3. 如果是第一次录入（找不到历史），保质期留空，让用户填。
        * **输入框 2**: 生产日期 (`QDateEdit`, 默认今天)。
        * **输入框 3**: 保质期 (`QSpinBox`, 天)。
        * **显示**: 过期日期 (根据生产日期+保质期实时计算显示)。
        * 按钮: "➕ 登记批次"。
    * **右侧 (监控区)**:
        * 表格显示: `[商品名称, 生产日期, 保质期, 过期日期, 状态]`。
        * 状态列根据日期自动标红(已过期)或标黄(临期)。

---

## 🚀 Phase 5: 优化与集成
- [ ] **优化出售逻辑**: 确保 `SaleService` 当库存为 0 时不删除商品条目。
- [ ] **入口集成**: 在 `MainWindow` 增加“进货管理”和“易过期管理”入口。
- [ ] **过期提醒**: 启动软件时自动检测一次过期商品并弹窗提示。
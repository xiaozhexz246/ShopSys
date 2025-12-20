# 超市售货系统 v1.1 优化任务清单 (Todo List)

**目标**: 在 v1.0 基础上增加隐藏系统入口、优化收银台搜索体验。
**策略**: 先完成核心逻辑与布局更改，最后进行全局样式美化。

---

## 🛠️ Phase 1: 核心服务层升级 (Backend Logic)
在此阶段，我们需要为新功能准备好后台逻辑，特别是模糊搜索。

- [ ] **更新 `services/product_service.py`**
    * 新增方法 `search_products_by_name(keyword)`:
    * 使用 SQL 的 `LIKE %keyword%` 语法进行模糊查询。
    * 返回匹配的商品列表。

- [ ] **更新 `services/auth_service.py`**
    * 修改 `login` 方法或新增逻辑，支持识别“特权账号”。
    * 设定一个硬编码的特权账号（例如：user: `root`, pass: `123456`）.
    * 登录成功后，返回不仅仅是 True/False，还要返回 `is_admin`  标识。

---

## 🕵️ Phase 2: 隐藏系统入口 (Hidden System Feature)
实现通过特定账号进入不同功能区的功能。

- [ ] **修改 `ui/login_window.py`**
    * 接收 `auth_service` 返回的身份标识。
    * 在初始化 `MainWindow` 时，将这个身份标识（`is_hidden_mode`）传递进去。

- [ ] **修改 `ui/main_window.py`**
    * 修改 `__init__` 方法，增加参数 `is_hidden_mode=False`。
    * **逻辑判断**:
        * 如果 `is_hidden_mode` 为 `True`，在侧边栏或顶部导航栏额外添加一个“🔧 高级功能”或“隐藏系统”的 Tab/Action。
    * **新建 `ui/hidden_page.py`**:
        * 创建一个简单的页面（占位符），上面放几个待定功能的按钮（如“数据清洗”、“系统重置”），目前点击仅弹窗提示“功能开发中”。
        * 将此页面挂载到 `MainWindow` 的 `QStackedWidget` 中。

---

## 🛒 Phase 3: 收银台搜索增强 (Cashier Logic Upgrade)
这是本次改动的核心，涉及复杂的 UI 交互。

- [ ] **重构 `ui/cashier_page.py` 布局**
    * 将界面垂直分为两个主要区域：
        1.  **上部 (新)**: `SearchArea` - 包含搜索结果列表。
        2.  **下部 (旧)**: `CartArea` - 现有的购物车表格和结算区。
    * 在顶部的输入框旁边，增加一个“🔍 搜索名称”按钮（或监听输入框变化）。

- [ ] **实现搜索结果区域**
    * 使用一个新的 `QTableWidget` 来显示模糊搜索结果。
    * **表格列设计**: `[商品编号, 名称, 单价, 购买数量(SpinBox), 操作(添加按钮)]`。
    * **交互逻辑**:
        1.  用户在顶部输入“可乐”，点击搜索。
        2.  调用 `ProductService.search_products_by_name`。
        3.  将结果填入搜索结果表格。
        4.  用户在表格行内调整 `SpinBox` 的数量。
        5.  点击该行的“添加”按钮，将商品直接加入下方的**购物车**（复用现有的 `add_product_to_cart` 逻辑）。

---

## 🚀 Phase 5: 测试与打包
- [ ] **回归测试**
    * 测试普通账号登录是否还能正常收银。
    * 测试特权账号是否能看到隐藏页面。
    * 测试收银台模糊搜索 -> 添加购物车 -> 结算的全流程。

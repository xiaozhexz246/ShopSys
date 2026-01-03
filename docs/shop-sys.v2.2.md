# 超市售货系统 v2.2 操作日志与审计系统

**目标**: 建立全局操作日志记录机制，覆盖商品、收银、进货及**易过期管理（增删改）**，并提供可视化的日志查询界面。

---

## 🗄️ Phase 1: 数据库层建设 (Model)
**修改 `models.py`**，新增日志表结构。

- [ ] **添加 `OperationLog` 类**
    ```python
    class OperationLog(Base):
        __tablename__ = 'operation_logs'

        id = Column(Integer, primary_key=True, autoincrement=True)
        username = Column(String, nullable=False)   # 操作人 (如: admin)
        module = Column(String, nullable=False)     # 模块 (如: 易过期管理)
        action = Column(String, nullable=False)     # 动作 (如: 修改批次)
        content = Column(String)                    # 详情 (如: 批次#5 数量 10 -> 8)
        log_time = Column(DateTime, default=datetime.now, index=True) # 时间
    ```
- [ ] **数据库初始化**: 运行 `init.py` 确保新表被创建。

---

## 🧠 Phase 2: 全局上下文与日志服务 (Core Service)
让系统“记住”当前是谁在操作，并提供写入接口。

- [ ] **改造 `services/auth_service.py` (全局单例)**
    * 添加类变量 `current_user` (默认为 None)。
    * **Login**: 登录成功时赋值 `AuthService.current_user = username`。
    * **Logout**: 退出时重置 `AuthService.current_user = None`。

- [ ] **新建 `services/log_service.py`**
    * **引入依赖**: `from services.auth_service import AuthService`。
    * **方法 `add_log(module, action, content)`**:
        * 获取用户: `user = AuthService.current_user or "系统/未登录"`。
        * 写入 `OperationLog` 表。
    * **方法 `get_logs(keyword=None)`**:
        * 查询数据库，按 `log_time` 倒序排列，支持关键词筛选。
* **方法 `export_logs_to_excel(save_path)`**: <--- 新增
        * 查询所有日志数据。
        * 使用 `pandas` 转换为 DataFrame。
        * 列名映射: `{'log_time': '操作时间', 'username': '操作人', ...}`。
        * 调用 `df.to_excel(save_path, index=False)` 保存文件。
---

## 🔌 Phase 3: 全局业务埋点 (Integration)
在关键操作点插入日志代码。

- [ ] **易过期管理埋点 (`services/perishable_service.py`)** (重点)
    * **登记批次 (`add_batch`)**:
        * 成功后记录: `LogService.add_log("易过期管理", "登记", f"新增批次: 商品{pid} 生产日期{date}")`。
    * **修改批次 (`update_batch`)**: <--- 新增
        * 成功后记录: `LogService.add_log("易过期管理", "修改", f"更新批次ID:{batch_id} (可能修改了数量或日期)")`。
    * **删除批次 (`delete_batch`)**:
        * 成功后记录: `LogService.add_log("易过期管理", "删除", f"移除批次ID:{batch_id}")`。

- [ ] **商品管理埋点 (`services/product_service.py`)**
    * **新增**: `add_log("商品管理", "新增", f"新增商品: {name}")`。
    * **改价**: `add_log("商品管理", "修改", f"商品{pid} 价格变动...")`。
    * **删除**: `add_log("商品管理", "删除", f"删除商品: {pid}")`。
    * **进货**: `add_log("进货管理", "入库", f"商品{pid} 进货 {qty} 件")`。

- [ ] **收银埋点 (`services/sale_service.py`)**
    * **结算**: `add_log("收银台", "销售", f"订单结算: 金额 {total} 元")`。

---

## 🖥️ Phase 4: 系统日志界面 (UI - LogPage)
**新建 `ui/log_page.py`**。

- [ ] **界面布局**
    * **顶部**: 搜索框 + 刷新按钮。
    * **表格**: `["时间", "操作人", "模块", "动作", "详细内容"]`。
    * **样式**: 
        * 引用 `styles.qss`。
        * 表格行高 45px (保持 v1.9 标准)。
        * 时间列宽 160px。

- [ ] **功能逻辑**
    * 初始化加载最近 100 条日志。
    * 搜索框支持按“操作人”或“动作”过滤。
- [ ] **交互逻辑**
    * **导出功能**:
        * 点击按钮 -> 弹出 `QFileDialog.getSaveFileName`。
        * 获取路径 -> 调用 `LogService.export_logs_to_excel(path)`。
        * 成功后弹出 `QMessageBox` 提示。
---

## 🚀 Phase 5: 入口集成 (Main Window)
- [ ] **修改 `ui/main_window.py`**
    * 顶部导航栏增加按钮: **"📜 系统日志"**。
    * 点击跳转到 `LogPage`。
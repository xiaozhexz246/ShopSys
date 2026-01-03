# 文件名: test_log_system.py
# v2.2: 测试日志系统功能
from database import Base, engine
from services.auth_service import AuthService
from services.log_service import LogService
from services.product_service import ProductService
from services.perishable_service import PerishableService
from services.sale_service import SaleService
from datetime import date

def test_log_system():
    """测试日志系统的各项功能"""

    print("=" * 60)
    print("开始测试 v2.2 日志系统")
    print("=" * 60)

    # 1. 创建日志表 (如果不存在)
    print("\n1. 创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("   表创建成功!")

    # 2. 模拟登录
    print("\n2. 模拟用户登录...")
    success, is_root = AuthService.login("admin", "admin")
    if success:
        print(f"   登录成功! 当前用户: {AuthService.current_user}")
    else:
        print("   登录失败,使用默认用户进行测试")
        AuthService.current_user = "测试用户"

    # 3. 测试直接添加日志
    print("\n3. 测试直接添加日志...")
    LogService.add_log("测试模块", "测试操作", "这是一条测试日志")
    print("   日志添加成功!")

    # 4. 测试添加测试商品
    print("\n4. 添加测试商品...")
    ProductService.add_product("TEST001", "测试商品A", 5.0, 10.0, 100, "测试类别", "测试位置")
    ProductService.add_product("TEST002", "测试商品B", 8.0, 15.0, 50, "测试类别", "测试位置")
    print("   测试商品已添加!")

    # 5. 测试进货日志 (详细记录)
    print("\n5. 测试进货日志 (包含商品名称、进价、数量)...")
    purchase_items = [
        {"product_id": "TEST001", "quantity": 20, "cost_price": 5.5},
        {"product_id": "TEST002", "quantity": 15, "cost_price": 8.5}
    ]
    success, msg = ProductService.replenish_stock(purchase_items)
    if success:
        print(f"   进货成功: {msg}")
    else:
        print(f"   进货失败: {msg}")

    # 6. 测试收银日志 (详细记录)
    print("\n6. 测试收银日志 (包含商品名称、售价、数量)...")
    cart_items = [
        {"id": "TEST001", "qty": 3, "price": 10.0, "actual_price": 9.5},
        {"id": "TEST002", "qty": 2, "price": 15.0, "actual_price": 15.0}
    ]
    success, msg = SaleService.checkout(cart_items)
    if success:
        print(f"   结算成功: {msg}")
    else:
        print(f"   结算失败: {msg}")

    # 7. 查询所有日志记录
    print("\n7. 查询所有日志记录...")
    logs = LogService.get_logs(limit=20)
    print(f"   找到 {len(logs)} 条日志记录:")
    for log in logs:
        print(f"   - [{log.log_time.strftime('%Y-%m-%d %H:%M:%S')}] "
              f"{log.username} | {log.module} | {log.action}")
        print(f"     内容: {log.content}")

    # 8. 测试关键词搜索
    print("\n8. 测试关键词搜索...")
    search_logs = LogService.get_logs(keyword="测试商品A")
    print(f"   搜索'测试商品A'关键词,找到 {len(search_logs)} 条记录")

    # 9. 测试退出登录
    print("\n9. 测试退出登录...")
    AuthService.logout()
    print(f"   退出成功! 当前用户: {AuthService.current_user}")

    print("\n" + "=" * 60)
    print("日志系统测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    test_log_system()

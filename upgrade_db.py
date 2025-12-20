# 文件名: upgrade_db.py
"""
数据库升级脚本 v1.1 -> v1.2
用于在不丢失现有数据的情况下,为商品表添加 category 和 location 字段
"""

import sqlite3
import os
import shutil
from datetime import datetime

def backup_database(db_path="shop.db"):
    """备份数据库"""
    if os.path.exists(db_path):
        backup_name = f"shop_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(db_path, backup_name)
        print(f"✅ 数据库已备份至: {backup_name}")
        return True
    else:
        print("⚠️ 未找到数据库文件,无需备份")
        return False

def check_column_exists(cursor, table_name, column_name):
    """检查列是否已存在"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    return column_name in columns

def upgrade_database(db_path="shop.db"):
    """升级数据库结构"""
    print("=" * 50)
    print("数据库升级工具 v1.1 -> v1.2")
    print("=" * 50)

    # 1. 备份数据库
    print("\n[步骤 1/3] 备份数据库...")
    backup_database(db_path)

    # 2. 连接数据库
    print("\n[步骤 2/3] 连接数据库...")
    if not os.path.exists(db_path):
        print(f"❌ 错误: 数据库文件 {db_path} 不存在!")
        print("请先运行 python init.py 初始化数据库")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("✅ 数据库连接成功")

    # 3. 检查并添加新字段
    print("\n[步骤 3/3] 升级表结构...")

    try:
        # 检查 category 字段
        if check_column_exists(cursor, "products", "category"):
            print("ℹ️  字段 'category' 已存在,跳过")
        else:
            cursor.execute("ALTER TABLE products ADD COLUMN category TEXT DEFAULT '未设置'")
            print("✅ 已添加字段: category (商品类别)")

        # 检查 location 字段
        if check_column_exists(cursor, "products", "location"):
            print("ℹ️  字段 'location' 已存在,跳过")
        else:
            cursor.execute("ALTER TABLE products ADD COLUMN location TEXT DEFAULT '未设置'")
            print("✅ 已添加字段: location (存放位置)")

        # 提交更改
        conn.commit()
        print("\n" + "=" * 50)
        print("🎉 数据库升级完成!")
        print("=" * 50)
        print("\n现在可以运行 python main.py 启动系统了")

        # 显示统计信息
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        print(f"\n📊 当前商品数量: {product_count}")

        return True

    except Exception as e:
        conn.rollback()
        print(f"\n❌ 升级失败: {str(e)}")
        print("数据库已回滚,请检查错误后重试")
        return False

    finally:
        conn.close()
        print("\n数据库连接已关闭")

if __name__ == "__main__":
    print("\n⚠️  警告: 升级前请确保已关闭所有正在运行的系统实例")
    input("按回车键继续...")

    success = upgrade_database()

    if success:
        print("\n✅ 升级成功!")
    else:
        print("\n❌ 升级失败,请查看上方错误信息")

    input("\n按回车键退出...")

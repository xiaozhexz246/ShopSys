# 文件名: migrate_v1.5.py
# -*- coding: utf-8 -*-
"""
数据库迁移脚本 v1.5
自动创建 purchase_records 和 perishable_batches 两张新表
"""

import sys
import io

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from database import engine, Base
from models import PurchaseRecord, PerishableBatch

def migrate():
    """执行数据库迁移"""
    print("开始执行 v1.5 数据库迁移...")

    try:
        # 创建新表（只创建不存在的表）
        Base.metadata.create_all(bind=engine)
        print("成功创建新表: purchase_records, perishable_batches")
        print("v1.5 数据库迁移完成！")
        return True
    except Exception as e:
        print(f"迁移失败: {str(e)}")
        return False

if __name__ == "__main__":
    migrate()

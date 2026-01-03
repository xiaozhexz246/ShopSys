# 检查日志内容
from services.log_service import LogService

logs = LogService.get_logs(limit=20)
print(f"Total logs: {len(logs)}\n")

for log in logs:
    print(f"[{log.log_time.strftime('%Y-%m-%d %H:%M:%S')}]")
    print(f"User: {log.username}")
    print(f"Module: {log.module}")
    print(f"Action: {log.action}")
    print(f"Content: {log.content}")
    print("-" * 80)

# utils/data_handler.py
import json
from datetime import datetime, date
import os

class DataHandler:
    def __init__(self, file_path="data/tasks.json"):
        self.file_path = file_path
        self.ensure_data_directory()

    def ensure_data_directory(self):
        """確保數據目錄存在"""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def date_handler(self, obj):
        """處理日期序列化"""
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return obj

    def save_tasks(self, tasks):
        """保存任務數據到文件"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, default=self.date_handler, indent=2)

    def load_tasks(self):
        """從文件加載任務數據"""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    tasks = json.load(f)
                    # 轉換日期字符串回日期對象
                    for task in tasks:
                        task['Start'] = datetime.fromisoformat(task['Start']).date()
                        task['Finish'] = datetime.fromisoformat(task['Finish']).date()
                    return tasks
            return []
        except Exception as e:
            print(f"加載數據時出錯: {e}")
            return []

    def add_task(self, tasks, new_task):
        """添加新任務並保存"""
        tasks.append(new_task)
        self.save_tasks(tasks)
        return tasks

    def update_task(self, tasks, task_id, updates):
        """更新任務並保存"""
        for task in tasks:
            if task['id'] == task_id:
                task.update(updates)
                task['last_modified'] = datetime.now().isoformat()
                break
        self.save_tasks(tasks)
        return tasks

    def delete_task(self, tasks, task_id):
        """刪除任務並保存"""
        tasks = [task for task in tasks if task['id'] != task_id]
        self.save_tasks(tasks)
        return tasks
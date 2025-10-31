"""
SQLite-based conversation memory store
"""

import sqlite3
from datetime import datetime
from typing import List, Dict

class MemoryStore:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        """Initialize database tables"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT NOT NULL,
                description TEXT NOT NULL,
                scheduled_time DATETIME,
                completed BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (role, content) VALUES (?, ?)",
            (role, content)
        )
        self.conn.commit()
    
    def get_recent_context(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation context"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT role, content FROM conversations ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        # Reverse to get chronological order
        return [{"role": row[0], "content": row[1]} for row in reversed(rows)]
    
    def clear_history(self):
        """Clear all conversation history"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM conversations")
        self.conn.commit()
    
    def add_task(self, task_type: str, description: str, scheduled_time=None):
        """Add a scheduled task"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (task_type, description, scheduled_time) VALUES (?, ?, ?)",
            (task_type, description, scheduled_time)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_pending_tasks(self) -> List[Dict]:
        """Get all pending tasks"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, task_type, description, scheduled_time FROM tasks WHERE completed = 0"
        )
        rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "type": row[1],
                "description": row[2],
                "scheduled_time": row[3]
            }
            for row in rows
        ]
    
    def complete_task(self, task_id: int):
        """Mark a task as completed"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
        self.conn.commit()
    
    def close(self):
        """Close database connection"""
        self.conn.close()
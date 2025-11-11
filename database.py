import sqlite3
from datetime import datetime, date
from typing import List, Tuple, Optional

class ActivityDatabase:
    def __init__(self, db_path: str = "activity_tracker.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table for activity sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_seconds INTEGER DEFAULT 0,
                is_work INTEGER DEFAULT 1,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # Table for daily summaries
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE NOT NULL,
                total_work_seconds INTEGER DEFAULT 0,
                total_idle_seconds INTEGER DEFAULT 0,
                total_seconds INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_session(self, is_work: bool = True) -> int:
        """Start a new activity session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        cursor.execute('''
            INSERT INTO activity_sessions (date, start_time, is_work, is_active)
            VALUES (?, ?, ?, 1)
        ''', (date_str, time_str, 1 if is_work else 0))
        
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return session_id
    
    def update_session(self, session_id: int, duration_seconds: int, is_work: bool):
        """Update session duration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        
        cursor.execute('''
            UPDATE activity_sessions 
            SET end_time = ?, duration_seconds = ?, is_work = ?
            WHERE id = ?
        ''', (time_str, duration_seconds, 1 if is_work else 0, session_id))
        
        conn.commit()
        conn.close()
    
    def end_session(self, session_id: int):
        """End an activity session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE activity_sessions 
            SET is_active = 0
            WHERE id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
    
    def get_today_stats(self) -> Tuple[int, int]:
        """Return today's work and leisure seconds"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = date.today().strftime("%Y-%m-%d")
        
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN is_work = 1 THEN duration_seconds ELSE 0 END) as work_time,
                SUM(CASE WHEN is_work = 0 THEN duration_seconds ELSE 0 END) as idle_time
            FROM activity_sessions
            WHERE date = ?
        ''', (today,))
        
        result = cursor.fetchone()
        conn.close()
        
        work_time = result[0] if result[0] else 0
        idle_time = result[1] if result[1] else 0
        
        return work_time, idle_time
    
    def get_daily_stats(self, days: int = 7) -> List[Tuple[str, int, int]]:
        """Return statistics for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                date,
                SUM(CASE WHEN is_work = 1 THEN duration_seconds ELSE 0 END) as work_time,
                SUM(CASE WHEN is_work = 0 THEN duration_seconds ELSE 0 END) as idle_time
            FROM activity_sessions
            WHERE date >= date('now', '-' || ? || ' days')
            GROUP BY date
            ORDER BY date DESC
        ''', (days,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_weekly_stats(self, weeks: int = 4) -> List[Tuple[str, int, int]]:
        """Return weekly statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                strftime('%Y-W%W', date) as week,
                SUM(CASE WHEN is_work = 1 THEN duration_seconds ELSE 0 END) as work_time,
                SUM(CASE WHEN is_work = 0 THEN duration_seconds ELSE 0 END) as idle_time
            FROM activity_sessions
            WHERE date >= date('now', '-' || ? || ' days')
            GROUP BY week
            ORDER BY week DESC
        ''', (weeks * 7,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results

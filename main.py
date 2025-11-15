import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QCheckBox, 
                             QTabWidget, QTableWidget, QTableWidgetItem, 
                             QSystemTrayIcon, QMenu, QAction, QGraphicsDropShadowEffect,
                             QStackedWidget, QMessageBox, QSlider, QSpinBox, QScrollArea)
from PyQt5.QtCore import QTimer, Qt, QTime, QPoint, QPropertyAnimation, QEasingCurve, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QPixmap, QPainter, QLinearGradient
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from database import ActivityDatabase
from tracker import ActivityTracker

class AnalyticsWindow(QMainWindow):
    """Advanced Analytics Window with multiple chart types"""
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("📈 Advanced Analytics")
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet(self.get_stylesheet())
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # Create tabs for different chart types
        tabs = QTabWidget()
        tabs.setStyleSheet("QTabWidget::pane { border: 1px solid #3b82f6; } QTabBar::tab { background: #1e293b; color: white; padding: 8px 20px; }")
        
        # Tab 1: Daily stats (fixed - now shows daily hours, not cumulative)
        tabs.addTab(self.create_cumulative_chart(), "📊 Daily Hours")
        
        # Tab 2: Pie charts
        tabs.addTab(self.create_pie_charts(), "🥧 Distribution")
        
        # Tab 3: Timeline
        tabs.addTab(self.create_timeline_chart(), "📅 Timeline")
        
        # Tab 4: Pause analysis
        tabs.addTab(self.create_pause_analysis(), "⏸ Pause Analysis")
        
        # Tab 5: Weekly averages
        tabs.addTab(self.create_weekly_analysis(), "📈 Weekly Trends")
        
        layout.addWidget(tabs)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Analytics")
        refresh_btn.clicked.connect(self.refresh_all)
        refresh_btn.setStyleSheet("QPushButton { background: #3b82f6; color: white; padding: 10px; border-radius: 5px; font-weight: bold; }")
        layout.addWidget(refresh_btn)
    
    def get_stylesheet(self):
        return """
        QMainWindow { background: #0f172a; }
        QWidget { background: #0f172a; color: white; }
        QTabBar::tab:selected { background: #1e293b; border-bottom: 3px solid #3b82f6; }
        QTabBar::tab { background: #0f172a; }
        """
    
    def create_cumulative_chart(self):
        """Daily work/leisure hours over time (NOT cumulative, shows daily totals)"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        stats = self.db.get_daily_stats(90)  # Last 90 days
        if not stats:
            layout.addWidget(QLabel("No data available"))
            widget.setLayout(layout)
            return widget
        
        dates = [s[0] for s in stats]
        work_hours = [s[1] / 3600 for s in stats]
        leisure_hours = [s[2] / 3600 for s in stats]
        
        fig = Figure(figsize=(12, 5), facecolor='#1e293b')
        ax = fig.add_subplot(111, facecolor='#1e293b')
        
        # Plot daily hours (not cumulative)
        x = range(len(dates))
        ax.plot(x, work_hours, marker='o', color='#10b981', linewidth=2, markersize=4, label='Work Hours/Day')
        ax.plot(x, leisure_hours, marker='s', color='#f59e0b', linewidth=2, markersize=4, label='Leisure Hours/Day')
        
        # Fill area under curves
        ax.fill_between(x, work_hours, alpha=0.3, color='#10b981')
        ax.fill_between(x, leisure_hours, alpha=0.3, color='#f59e0b')
        
        # Add horizontal line at 24 hours for reference
        ax.axhline(y=24, color='red', linestyle='--', linewidth=1, alpha=0.5, label='24h limit')
        
        ax.set_title('Daily Work & Leisure Hours (90 Days)', color='white', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', color='white')
        ax.set_ylabel('Hours per Day', color='white')
        
        # Set x-axis labels - show every Nth date to avoid clutter
        step = max(1, len(dates) // 15)  # Show ~15 labels max
        ax.set_xticks([i for i in range(0, len(dates), step)])
        ax.set_xticklabels([dates[i] for i in range(0, len(dates), step)], rotation=45, ha='right')
        
        ax.tick_params(colors='white')
        ax.legend(loc='upper left', facecolor='#0f172a', edgecolor='white')
        ax.grid(True, alpha=0.2, color='white')
        
        # Set y-axis to show 0-24+ hours
        ax.set_ylim(bottom=0)
        
        for spine in ax.spines.values():
            spine.set_color('white')
        
        fig.tight_layout()
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        widget.setLayout(layout)
        return widget
    
    def create_pie_charts(self):
        """Pie charts for work/leisure/pause distribution"""
        widget = QWidget()
        layout = QHBoxLayout()
        
        stats = self.db.get_daily_stats(30)
        pauses = self.db.get_pause_periods(days=30)
        
        total_work = sum(s[1] for s in stats) / 3600
        total_leisure = sum(s[2] for s in stats) / 3600
        total_pauses = sum(p[2] for p in pauses) / 3600
        
        fig = Figure(figsize=(12, 5), facecolor='#1e293b')
        
        # Work vs Leisure pie
        ax1 = fig.add_subplot(121, facecolor='#1e293b')
        colors1 = ['#10b981', '#f59e0b']
        ax1.pie([total_work, total_leisure], labels=['Work', 'Leisure'], autopct='%1.1f%%',
                colors=colors1, textprops={'color': 'white', 'fontweight': 'bold'})
        ax1.set_title('Work vs Leisure (30 Days)', color='white', fontsize=12, fontweight='bold')
        
        # All three pie
        ax2 = fig.add_subplot(122, facecolor='#1e293b')
        colors2 = ['#10b981', '#f59e0b', '#8b5cf6']
        ax2.pie([total_work, total_leisure, total_pauses], labels=['Work', 'Leisure', 'Pauses'],
                autopct='%1.1f%%', colors=colors2, textprops={'color': 'white', 'fontweight': 'bold'})
        ax2.set_title('All Activity Types (30 Days)', color='white', fontsize=12, fontweight='bold')
        
        fig.tight_layout()
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        widget.setLayout(layout)
        return widget
    
    def create_timeline_chart(self):
        """Daily activity timeline with stacked bars"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        stats = self.db.get_daily_stats(30)
        pauses = self.db.get_pause_periods(days=30)
        
        if not stats:
            layout.addWidget(QLabel("No data available"))
            widget.setLayout(layout)
            return widget
        
        dates = [s[0] for s in stats]
        work_hours = [s[1] / 3600 for s in stats]
        leisure_hours = [s[2] / 3600 for s in stats]
        
        pause_by_date = {}
        for p in pauses:
            if p[0] not in pause_by_date:
                pause_by_date[p[0]] = 0
            pause_by_date[p[0]] += p[2]
        
        pause_hours = [pause_by_date.get(d, 0) / 3600 for d in dates]
        
        fig = Figure(figsize=(12, 5), facecolor='#1e293b')
        ax = fig.add_subplot(111, facecolor='#1e293b')
        
        x = range(len(dates))
        width = 0.8
        
        ax.bar(x, work_hours, width, label='Work', color='#10b981', alpha=0.85)
        ax.bar(x, leisure_hours, width, bottom=work_hours, label='Leisure', color='#f59e0b', alpha=0.85)
        ax.bar(x, pause_hours, width, bottom=[w+l for w,l in zip(work_hours, leisure_hours)], 
               label='Pauses', color='#8b5cf6', alpha=0.85)
        
        ax.set_title('Daily Activity Stacked (30 Days)', color='white', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', color='white')
        ax.set_ylabel('Hours', color='white')
        ax.set_xticks(x[::3] if len(dates) > 10 else x)
        ax.set_xticklabels([dates[i] for i in (x[::3] if len(dates) > 10 else x)], rotation=45, color='white')
        ax.tick_params(colors='white')
        ax.legend(loc='upper left', facecolor='#0f172a', edgecolor='white')
        ax.grid(True, alpha=0.2, color='white', axis='y')
        
        for spine in ax.spines.values():
            spine.set_color('white')
        
        fig.tight_layout()
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        widget.setLayout(layout)
        return widget
    
    def create_pause_analysis(self):
        """Pause duration distribution and frequency"""
        widget = QWidget()
        layout = QHBoxLayout()
        
        pauses = self.db.get_pause_periods(days=90)
        
        if not pauses:
            layout.addWidget(QLabel("No pause data available"))
            widget.setLayout(layout)
            return widget
        
        durations = [p[2] / 60 for p in pauses]  # Convert to minutes
        dates = [p[0] for p in pauses]
        
        pause_by_date = {}
        for d in dates:
            pause_by_date[d] = pause_by_date.get(d, 0) + 1
        
        fig = Figure(figsize=(12, 5), facecolor='#1e293b')
        
        # Histogram of pause durations
        ax1 = fig.add_subplot(121, facecolor='#1e293b')
        ax1.hist(durations, bins=15, color='#8b5cf6', alpha=0.7, edgecolor='white')
        ax1.set_title('Pause Duration Distribution', color='white', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Minutes', color='white')
        ax1.set_ylabel('Frequency', color='white')
        ax1.tick_params(colors='white')
        
        # Pauses per day trend
        ax2 = fig.add_subplot(122, facecolor='#1e293b')
        sorted_dates = sorted(pause_by_date.keys())
        pause_counts = [pause_by_date[d] for d in sorted_dates]
        ax2.plot(sorted_dates, pause_counts, marker='o', color='#8b5cf6', linewidth=2, markersize=5)
        ax2.set_title('Pauses Per Day Trend', color='white', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Date', color='white')
        ax2.set_ylabel('Count', color='white')
        ax2.tick_params(colors='white')
        ax2.grid(True, alpha=0.2, color='white')
        
        for ax in [ax1, ax2]:
            for spine in ax.spines.values():
                spine.set_color('white')
        
        fig.tight_layout()
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        widget.setLayout(layout)
        return widget
    
    def create_weekly_analysis(self):
        """Weekly average work/leisure/pause hours with trend lines"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        stats = self.db.get_daily_stats(90)
        pauses = self.db.get_pause_periods(days=90)
        
        if not stats:
            layout.addWidget(QLabel("No data available"))
            widget.setLayout(layout)
            return widget
        
        # Group data by week
        weekly_work = {}
        weekly_leisure = {}
        weekly_pauses = {}
        
        for date_str, work_secs, leisure_secs in stats:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            week_num = date_obj.isocalendar()[1]
            year = date_obj.year
            week_key = f"W{week_num}"
            
            if week_key not in weekly_work:
                weekly_work[week_key] = []
                weekly_leisure[week_key] = []
            
            weekly_work[week_key].append(work_secs / 3600)
            weekly_leisure[week_key].append(leisure_secs / 3600)
        
        # Group pauses by week
        for date_str, pause_start, duration in pauses:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            week_num = date_obj.isocalendar()[1]
            week_key = f"W{week_num}"
            
            if week_key not in weekly_pauses:
                weekly_pauses[week_key] = []
            
            weekly_pauses[week_key].append(duration / 3600)
        
        # Calculate weekly averages
        weeks = sorted(weekly_work.keys(), key=lambda x: int(x[1:]))
        avg_work = [sum(weekly_work[w]) / len(weekly_work[w]) for w in weeks]
        avg_leisure = [sum(weekly_leisure[w]) / len(weekly_leisure[w]) for w in weeks]
        avg_pauses = [sum(weekly_pauses.get(w, [0])) / len(weekly_pauses.get(w, [1])) for w in weeks]
        
        fig = Figure(figsize=(12, 5), facecolor='#1e293b')
        ax = fig.add_subplot(111, facecolor='#1e293b')
        
        x = range(len(weeks))
        width = 0.25
        
        # Plot bars
        bars1 = ax.bar([i - width for i in x], avg_work, width, label='Work', color='#10b981', alpha=0.85)
        bars2 = ax.bar(x, avg_leisure, width, label='Leisure', color='#f59e0b', alpha=0.85)
        bars3 = ax.bar([i + width for i in x], avg_pauses, width, label='Pauses', color='#8b5cf6', alpha=0.85)
        
        # Add trend lines
        z_work = np.polyfit(x, avg_work, 2) if len(x) > 2 else None
        z_leisure = np.polyfit(x, avg_leisure, 2) if len(x) > 2 else None
        
        if z_work:
            p_work = np.poly1d(z_work)
            x_smooth = np.linspace(0, len(weeks)-1, 100)
            ax.plot(x_smooth, p_work(x_smooth), '--', color='#059669', linewidth=2, alpha=0.7, label='Work Trend')
        
        if z_leisure:
            p_leisure = np.poly1d(z_leisure)
            x_smooth = np.linspace(0, len(weeks)-1, 100)
            ax.plot(x_smooth, p_leisure(x_smooth), '--', color='#d97706', linewidth=2, alpha=0.7, label='Leisure Trend')
        
        ax.set_title('Weekly Average Activity Hours (90 Days)', color='white', fontsize=14, fontweight='bold')
        ax.set_xlabel('Week', color='white')
        ax.set_ylabel('Hours', color='white')
        ax.set_xticks(x)
        ax.set_xticklabels(weeks, rotation=45, color='white')
        ax.tick_params(colors='white')
        ax.legend(loc='upper left', facecolor='#0f172a', edgecolor='white')
        ax.grid(True, alpha=0.2, color='white', axis='y')
        
        for spine in ax.spines.values():
            spine.set_color('white')
        
        fig.tight_layout()
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        widget.setLayout(layout)
        return widget
    
    def refresh_all(self):
        """Refresh all charts"""
        self.close()
        new_window = AnalyticsWindow(self.db)
        new_window.show()


class ModernStopwatchWidget(QMainWindow):
    # Signal for thread-safe pause detection
    pause_detected_signal = pyqtSignal(float)
    
    def __init__(self):
        super().__init__()
        
        # Determine app directory (works for both script and executable)
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            self.app_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            self.app_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Use database in the same directory as the executable
        db_path = os.path.join(self.app_dir, "activity_tracker.db")
        self.db = ActivityDatabase(db_path=db_path)
        
        # Load saved settings
        self.idle_threshold = self.load_settings()
        self.tracker = ActivityTracker(idle_threshold=self.idle_threshold)
        
        # Connect the pause signal to the handler (thread-safe)
        self.pause_detected_signal.connect(self.on_pause_detected_safe)
        
        self.session_id = None
        self.session_start_time = None
        self.work_seconds = 0
        self.idle_seconds = 0
        self.is_working = True  # True = work, False = leisure
        
        # Pause tracking
        self.pause_seconds = 0  # Total pause time today
        self.pause_count = 0     # Number of pauses today
        
        # Track current date for midnight rollover
        self.current_date = datetime.now().date()
        
        # For dragging the window
        self.dragging = False
        self.drag_position = None
        
        self.init_ui()
        self.init_timer()
        self.init_tray()
        
        # Set callback for pause logging
        self.tracker.set_idle_callback(self.on_pause_detected)
        self.tracker.start()
        
        # Load today's data
        self.load_today_data()
                # Apply modern stylesheet
        self.apply_modern_style()
    
    def load_settings(self):
        """Load settings from file, or return default"""
        try:
            settings_path = os.path.join(self.app_dir, "app_settings.txt")
            if os.path.exists(settings_path):
                with open(settings_path, "r") as f:
                    for line in f:
                        if line.startswith("idle_threshold="):
                            return int(line.split("=")[1].strip())
        except:
            pass
        return 60  # Default 60 seconds
    def init_ui(self):
        """Initialize the user interface with modern design"""
        self.setWindowTitle("⚡ Activity Tracker")
        
        # Frameless window for custom title bar
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set window icon for taskbar
        icon = QIcon("icon.ico")
        self.setWindowIcon(icon)
        
        # Window size - wider to avoid scrolling in tables
        self.setGeometry(100, 100, 520, 600)
        
        # Central widget with dark background
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)
        
        # Custom title bar
        title_bar = self.create_title_bar()
        main_layout.addWidget(title_bar)
        
        # Content area
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 15, 20, 20)
        content_layout.setSpacing(15)
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)
        
        # Button navigation bar (instead of tabs)
        button_bar = QWidget()
        button_bar.setObjectName("buttonBar")
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 10)
        button_layout.setSpacing(10)
        button_bar.setLayout(button_layout)
        content_layout.addWidget(button_bar)
        
        # Navigation buttons
        self.btn_timer = QPushButton("⏱ Timer")
        self.btn_timer.setObjectName("navButton")
        self.btn_timer.setCheckable(True)
        self.btn_timer.setChecked(True)
        self.btn_timer.setMaximumWidth(95)
        self.btn_timer.clicked.connect(lambda: self.switch_page(0))
        button_layout.addWidget(self.btn_timer)
        
        self.btn_history = QPushButton("📊 History")
        self.btn_history.setObjectName("navButton")
        self.btn_history.setCheckable(True)
        self.btn_history.setMaximumWidth(95)
        self.btn_history.clicked.connect(lambda: self.switch_page(1))
        button_layout.addWidget(self.btn_history)
        
        self.btn_charts = QPushButton("📈 Charts")
        self.btn_charts.setObjectName("navButton")
        self.btn_charts.setCheckable(True)
        self.btn_charts.setMaximumWidth(95)
        self.btn_charts.clicked.connect(lambda: self.switch_page(2))
        button_layout.addWidget(self.btn_charts)
        
        # Settings button
        self.btn_settings = QPushButton("⚙️ Settings")
        self.btn_settings.setObjectName("navButton")
        self.btn_settings.setCheckable(True)
        self.btn_settings.setMaximumWidth(95)
        self.btn_settings.clicked.connect(lambda: self.switch_page(3))
        button_layout.addWidget(self.btn_settings)
        
        # Info button (moved from History tab)
        info_btn = QPushButton("ℹ️ Info")
        info_btn.setObjectName("navButton")
        info_btn.setMaximumWidth(75)
        info_btn.clicked.connect(self.show_info_dialog)
        button_layout.addWidget(info_btn)
        
        # Add stretch to center buttons
        button_layout.insertStretch(0)
        button_layout.addStretch()
        
        # Store buttons in list for easy access
        self.nav_buttons = [self.btn_timer, self.btn_history, self.btn_charts, self.btn_settings]
        
        # Stacked widget to hold pages
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("stackedWidget")
        content_layout.addWidget(self.stacked_widget)
        
        # Create pages
        page_timer = self.create_stopwatch_tab()
        self.stacked_widget.addWidget(page_timer)
        
        page_history = self.create_history_tab()
        self.stacked_widget.addWidget(page_history)
        
        page_charts = self.create_charts_tab()
        self.stacked_widget.addWidget(page_charts)
        
        page_settings = self.create_settings_tab()
        self.stacked_widget.addWidget(page_settings)
    
    def switch_page(self, index):
        """Switch between pages"""
        self.stacked_widget.setCurrentIndex(index)
        # Update button states
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
    
    def create_title_bar(self):
        """Create custom title bar with dark theme"""
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(45)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 0, 10, 0)
        layout.setSpacing(10)
        title_bar.setLayout(layout)
        
        # App icon
        icon_label = QLabel()
        icon_pixmap = QPixmap("icon.ico")
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            icon_label.setText("⚡")
            icon_label.setFont(QFont("Segoe UI", 14))
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel("Activity Tracker")
        title_label.setObjectName("titleLabel")
        title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Minimize button - centered icon
        min_button = QPushButton("−")
        min_button.setObjectName("minButton")
        min_button.setFixedSize(35, 35)
        min_button.setFont(QFont("Segoe UI", 20, QFont.Bold))
        min_button.setStyleSheet("padding-bottom: 5px;")  # Adjust vertical alignment
        min_button.clicked.connect(self.showMinimized)
        min_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(min_button)
        
        # Close button - centered icon
        close_button = QPushButton("×")
        close_button.setObjectName("closeButton")
        close_button.setFixedSize(35, 35)
        close_button.setFont(QFont("Segoe UI", 22, QFont.Bold))
        close_button.setStyleSheet("padding-bottom: 4px;")  # Adjust vertical alignment
        close_button.clicked.connect(self.close)
        close_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(close_button)
        
        return title_bar
    
    def create_stopwatch_tab(self):
        """Create the modern stopwatch tab"""
        widget = QWidget()
        widget.setObjectName("tabContent")
        layout = QVBoxLayout()
        layout.setSpacing(20)
        widget.setLayout(layout)
        
        # Status indicator
        self.status_label = QLabel("⚫ Waiting for activity...")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Work time card
        work_card = self.create_time_card(
            "💼 Work Time",
            "workCard",
            "#10b981",  # Green
            "#059669"
        )
        self.work_time_display = work_card.findChild(QLabel, "timeDisplay")
        layout.addWidget(work_card)
        
        # Leisure time card
        leisure_card = self.create_time_card(
            "🎮 Leisure Time",
            "leisureCard",
            "#f59e0b",  # Orange
            "#d97706"
        )
        self.idle_time_display = leisure_card.findChild(QLabel, "timeDisplay")
        layout.addWidget(leisure_card)
        
        # Pause time card
        pause_card = self.create_time_card(
            "⏸ Pause Time",
            "pauseCard",
            "#a855f7",  # Purple
            "#9333ea",
            subtitle="0 pauses"
        )
        self.pause_time_display = pause_card.findChild(QLabel, "timeDisplay")
        self.pause_count_display = pause_card.findChild(QLabel, "subtitle")
        layout.addWidget(pause_card)
        
        # Total time card
        total_card = self.create_time_card(
            "🖥 Total Time",
            "totalCard",
            "#3b82f6",  # Blue
            "#2563eb"
        )
        self.total_time_display = total_card.findChild(QLabel, "timeDisplay")
        layout.addWidget(total_card)
        
        # Leisure mode checkbox
        self.idle_checkbox = QCheckBox("🎮 I'm on leisure mode")
        self.idle_checkbox.setObjectName("leisureCheckbox")
        self.idle_checkbox.setFont(QFont("Segoe UI", 10))
        self.idle_checkbox.stateChanged.connect(self.on_idle_checkbox_changed)
        layout.addWidget(self.idle_checkbox)
        
        layout.addStretch()
        
        return widget
    
    def create_time_card(self, title, object_name, color1, color2, subtitle=None):
        """Create a modern time display card with gradient"""
        card = QWidget()
        card.setObjectName(object_name)
        card.setStyleSheet(f"""
            QWidget#{object_name} {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color1}, stop:1 {color2});
                border-radius: 15px;
                padding: 15px;
            }}
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 60))
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout()
        card_layout.setSpacing(5)
        card.setLayout(card_layout)
        
        # Title - centered
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title_label.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        title_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title_label)
        
        # Time display - centered
        time_display = QLabel("00:00:00")
        time_display.setObjectName("timeDisplay")
        time_display.setFont(QFont("Segoe UI", 28, QFont.Bold))
        time_display.setStyleSheet("color: white;")
        time_display.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(time_display)
        
        # Optional subtitle (for pause count)
        if subtitle is not None:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setObjectName("subtitle")
            subtitle_label.setFont(QFont("Segoe UI", 9))
            subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
            subtitle_label.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(subtitle_label)
        
        return card
    
    def create_history_tab(self):
        """Create the history tab"""
        widget = QWidget()
        widget.setObjectName("tabContent")
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(15, 15, 15, 15)
        widget.setLayout(layout)
        
        # Activity section title
        activity_title = QLabel("📅 Activity Sessions")
        activity_title.setObjectName("sectionTitle")
        activity_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        layout.addWidget(activity_title)
        
        # Activity Table with Start/End times
        self.history_table = QTableWidget()
        self.history_table.setObjectName("modernTable")
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Date", "Start Time", "End Time", "Duration", "Type"])
        self.history_table.horizontalHeader().setStretchLastSection(False)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setRowHeight(0, 30)
        # Set column widths
        self.history_table.setColumnWidth(0, 90)   # Date
        self.history_table.setColumnWidth(1, 85)   # Start Time
        self.history_table.setColumnWidth(2, 85)   # End Time
        self.history_table.setColumnWidth(3, 90)   # Duration
        self.history_table.setColumnWidth(4, 80)   # Type
        self.history_table.setMaximumHeight(300)
        self.history_table.setStyleSheet(self.history_table.styleSheet() + """
            QTableWidget {
                gridline-color: #404040;
                background-color: #1e1e1e;
            }
            QHeaderView::section {
                padding: 6px;
                background-color: #2d2d2d;
                border: 1px solid #404040;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 6px;
                height: 30px;
            }
        """)
        layout.addWidget(self.history_table)
        
        # Pauses section title
        pauses_title = QLabel("⏸️ Pause History")
        pauses_title.setObjectName("sectionTitle")
        pauses_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        layout.addWidget(pauses_title)
        
        # Pauses table with Start/End times
        self.pauses_table = QTableWidget()
        self.pauses_table.setObjectName("modernTable")
        self.pauses_table.setColumnCount(4)
        self.pauses_table.setHorizontalHeaderLabels(["Date", "Start Time", "End Time", "Duration"])
        self.pauses_table.horizontalHeader().setStretchLastSection(False)
        self.pauses_table.verticalHeader().setVisible(False)
        self.pauses_table.setAlternatingRowColors(True)
        self.pauses_table.setRowHeight(0, 30)
        # Set column widths
        self.pauses_table.setColumnWidth(0, 90)   # Date
        self.pauses_table.setColumnWidth(1, 85)   # Start Time
        self.pauses_table.setColumnWidth(2, 85)   # End Time
        self.pauses_table.setColumnWidth(3, 90)   # Duration
        self.pauses_table.setMaximumHeight(280)
        self.pauses_table.setStyleSheet(self.pauses_table.styleSheet() + """
            QTableWidget {
                gridline-color: #404040;
                background-color: #1e1e1e;
            }
            QHeaderView::section {
                padding: 6px;
                background-color: #2d2d2d;
                border: 1px solid #404040;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 6px;
                height: 30px;
            }
        """)
        layout.addWidget(self.pauses_table)
        
        # Stretch to fill remaining space
        layout.addStretch()
        
        # Button container
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Refresh button
        refresh_btn = QPushButton("� Refresh History")
        refresh_btn.setObjectName("modernButton")
        refresh_btn.clicked.connect(self.refresh_history)
        refresh_btn.setMaximumWidth(150)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        return widget
    
    def create_charts_tab(self):
        """Create the charts tab"""
        widget = QWidget()
        widget.setObjectName("tabContent")
        layout = QVBoxLayout()
        layout.setSpacing(15)
        widget.setLayout(layout)
        
        # Title
        title = QLabel("📊 Activity Overview")
        title.setObjectName("sectionTitle")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Create scroll area for the chart (allows scrolling when many days)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #1e1e1e;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #3b82f6;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #2563eb;
            }
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_content.setLayout(scroll_layout)
        
        # Initialize matplotlib figure with larger size
        self.figure = Figure(figsize=(8, 8), facecolor='#1e293b')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(600)  # Minimum height to see content
        scroll_layout.addWidget(self.canvas)
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Charts")
        refresh_btn.setObjectName("modernButton")
        refresh_btn.clicked.connect(self.refresh_charts)
        buttons_layout.addWidget(refresh_btn)
        
        # Advanced Analytics button
        analytics_btn = QPushButton("📈 Advanced Analytics")
        analytics_btn.setObjectName("modernButton")
        analytics_btn.clicked.connect(self.open_analytics)
        buttons_layout.addWidget(analytics_btn)
        
        layout.addLayout(buttons_layout)
        
        return widget
    
    
    def create_settings_tab(self):
        """Create the settings tab"""
        widget = QWidget()
        widget.setObjectName("tabContent")
        layout = QVBoxLayout()
        layout.setSpacing(15)
        widget.setLayout(layout)
        
        # Title
        title = QLabel("⚙️ Settings")
        title.setObjectName("sectionTitle")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Idle Timeout Setting
        timeout_group = QWidget()
        timeout_layout = QVBoxLayout()
        timeout_layout.setSpacing(10)
        
        timeout_label = QLabel("Idle Timeout (Inactivity Detection)")
        timeout_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        timeout_layout.addWidget(timeout_label)
        
        timeout_desc = QLabel("Set how many seconds of inactivity before stopping the timer:")
        timeout_desc.setFont(QFont("Segoe UI", 10))
        timeout_desc.setObjectName("descriptionText")
        timeout_layout.addWidget(timeout_desc)
        
        # Spinbox only (no slider)
        spinbox_layout = QHBoxLayout()
        spinbox_layout.setSpacing(10)
        
        # Minus button
        minus_btn = QPushButton("−")
        minus_btn.setObjectName("modernButton")
        minus_btn.setFixedWidth(40)
        minus_btn.clicked.connect(lambda: self.timeout_spinbox.setValue(self.timeout_spinbox.value() - 5))
        spinbox_layout.addWidget(minus_btn)
        
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setMinimum(10)
        self.timeout_spinbox.setMaximum(999999)  # No practical upper limit
        self.timeout_spinbox.setValue(self.tracker.idle_threshold)
        self.timeout_spinbox.setSuffix(" seconds")
        self.timeout_spinbox.setFixedWidth(160)  # Increased width
        self.timeout_spinbox.setSingleStep(5)  # Increment by 5
        self.timeout_spinbox.setButtonSymbols(QSpinBox.UpDownArrows)  # Show up/down arrows
        spinbox_layout.addWidget(self.timeout_spinbox)
        
        # Plus button
        plus_btn = QPushButton("+")
        plus_btn.setObjectName("modernButton")
        plus_btn.setFixedWidth(40)
        plus_btn.clicked.connect(lambda: self.timeout_spinbox.setValue(self.timeout_spinbox.value() + 5))
        spinbox_layout.addWidget(plus_btn)
        
        spinbox_layout.addStretch()
        
        timeout_layout.addLayout(spinbox_layout)
        
        # Save button
        save_btn = QPushButton("💾 Save Settings")
        save_btn.setObjectName("modernButton")
        save_btn.clicked.connect(self.save_settings)
        timeout_layout.addWidget(save_btn)
        
        timeout_group.setLayout(timeout_layout)
        layout.addWidget(timeout_group)
        
        layout.addStretch()
        
        return widget
    
    
    def save_settings(self):
        """Save settings to tracker and database"""
        new_timeout = self.timeout_spinbox.value()
        self.tracker.idle_threshold = new_timeout
        
        # Save to file in app directory
        settings_path = os.path.join(self.app_dir, "app_settings.txt")
        with open(settings_path, "w") as f:
            f.write(f"idle_threshold={new_timeout}\n")
        
        QMessageBox.information(
            self,
            "Settings Saved",
            f"Idle timeout set to {new_timeout} seconds.\n\nChanges will take effect immediately.",
            QMessageBox.Ok
        )
    
    def init_tray(self):
        """Initialize system tray icon"""
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Create a simple icon
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(59, 130, 246))  # Blue
        painter = QPainter(pixmap)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 16, QFont.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "⏱")
        painter.end()
        
        self.tray_icon.setIcon(QIcon(pixmap))
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show Widget", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide Widget", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
    
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
    
    def hide_to_tray(self):
        """Hide window to system tray"""
        self.hide()
        self.tray_icon.showMessage(
            "Activity Tracker",
            "Widget minimized to tray. Double-click to restore.",
            QSystemTrayIcon.Information,
            2000
        )
    
    def quit_application(self):
        """Quit the application"""
        self.close()
    
    def apply_modern_style(self):
        """Apply modern dark theme stylesheet"""
        self.setStyleSheet("""
            QMainWindow {
                background: transparent;
            }
            
            QWidget#centralWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e293b, stop:1 #0f172a);
                border-radius: 15px;
            }
            
            QWidget#titleBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e293b, stop:1 #334155);
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
                border-bottom: 2px solid rgba(59, 130, 246, 0.3);
            }
            
            QLabel#titleLabel {
                color: white;
            }
            
            QPushButton#minButton {
                background: rgba(255, 255, 255, 0.08);
                color: white;
                border: none;
                border-radius: 8px;
            }
            
            QPushButton#minButton:hover {
                background: rgba(59, 130, 246, 0.4);
            }
            
            QPushButton#closeButton {
                background: rgba(255, 255, 255, 0.08);
                color: white;
                border: none;
                border-radius: 8px;
            }
            
            QPushButton#closeButton:hover {
                background: rgba(239, 68, 68, 0.6);
            }
            
            QWidget#contentWidget {
                background: transparent;
            }
            
            QLabel#statusLabel {
                color: rgba(255, 255, 255, 0.7);
                padding: 10px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
            }
            
            QCheckBox#leisureCheckbox {
                color: white;
                padding: 12px;
                background: rgba(245, 158, 11, 0.15);
                border-radius: 10px;
            }
            
            QCheckBox#leisureCheckbox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 5px;
                border: 2px solid rgba(245, 158, 11, 0.5);
                background: rgba(255, 255, 255, 0.1);
            }
            
            QCheckBox#leisureCheckbox::indicator:checked {
                background: #f59e0b;
                border-color: #f59e0b;
            }
            
            QWidget#buttonBar {
                background: transparent;
            }
            
            QPushButton#navButton {
                background: rgba(255, 255, 255, 0.05);
                color: rgba(255, 255, 255, 0.7);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 14px 15px;
                font-weight: bold;
                font-size: 11px;
                max-width: 95px;
            }
            
            QPushButton#navButton:hover {
                background: rgba(255, 255, 255, 0.1);
                border-color: rgba(59, 130, 246, 0.3);
            }
            
            QPushButton#navButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(59, 130, 246, 0.4), stop:1 rgba(99, 102, 241, 0.4));
                color: white;
                border-color: rgba(59, 130, 246, 0.6);
            }
            
            QStackedWidget#stackedWidget {
                background: rgba(255, 255, 255, 0.03);
                border-radius: 15px;
                padding: 5px;
            }
            
            QWidget#tabContent {
                background: transparent;
            }
            
            QLabel#sectionTitle {
                color: #ffffff;
                background: transparent;
            }
            
            QTableWidget#modernTable {
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 10px;
                color: #e2e8f0;
                gridline-color: rgba(255, 255, 255, 0.1);
                font-size: 11px;
                alternate-background-color: rgba(30, 41, 59, 0.5);
            }
            
            QTableWidget#modernTable::item {
                padding: 10px;
                border: none;
                color: #e2e8f0;
            }
            
            QTableWidget#modernTable::item:alternate {
                background: rgba(30, 41, 59, 0.5);
            }
            
            QTableWidget#modernTable::item:selected {
                background: rgba(59, 130, 246, 0.4);
                color: white;
            }
            
            QHeaderView::section {
                background: rgba(30, 41, 59, 0.9);
                color: #ffffff;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 11px;
            }
            
            QPushButton#infoButton {
                background: rgba(59, 130, 246, 0.3);
                color: white;
                border: 2px solid rgba(59, 130, 246, 0.5);
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 11px;
            }
            
            QPushButton#infoButton:hover {
                background: rgba(59, 130, 246, 0.5);
                border-color: rgba(59, 130, 246, 0.8);
            }
            
            QPushButton#modernButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #2563eb);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-weight: bold;
                font-size: 11px;
            }
            
            QPushButton#modernButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb, stop:1 #1d4ed8);
            }
            
            QPushButton#modernButton:pressed {
                background: #1e40af;
            }
            
            QPushButton#dangerButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(239, 68, 68, 0.6), stop:1 rgba(220, 38, 38, 0.6));
                color: white;
                border: 2px solid rgba(239, 68, 68, 0.5);
                border-radius: 10px;
                padding: 12px;
                font-weight: bold;
                font-size: 11px;
            }
            
            QPushButton#dangerButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ef4444, stop:1 #dc2626);
                border-color: #ef4444;
            }
            
            QPushButton#dangerButton:pressed {
                background: #991b1b;
            }
            
            QScrollBar:vertical {
                background: transparent;
                width: 0px;
                border-radius: 0px;
            }
            
            QScrollBar::handle:vertical {
                background: transparent;
                border-radius: 0px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: transparent;
            }
        """)
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.LeftButton:
            # Check if clicking on title bar area (top 45px)
            if event.pos().y() < 45:
                self.dragging = True
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if event.buttons() == Qt.LeftButton and self.dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
    
    def init_timer(self):
        """Initialize timer to update UI"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)  # Update every second
        
        # Auto-save timer - saves to database every minute
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.auto_save_to_db)
        self.autosave_timer.start(60000)  # Save every 60 seconds (1 minute)
        
        # Date check timer - checks for midnight rollover every minute
        self.date_check_timer = QTimer()
        self.date_check_timer.timeout.connect(self.check_date_change)
        self.date_check_timer.start(60000)  # Check every minute
    
    def check_date_change(self):
        """Check if date has changed (midnight rollover) and reset daily counters"""
        new_date = datetime.now().date()
        if new_date != self.current_date:
            print(f"[DATE CHANGE] Detected date change from {self.current_date} to {new_date}")
            
            # Close current session if active
            if self.session_id is not None:
                self.db.end_session(self.session_id)
                self.session_id = None
                self.session_start_time = None
            
            # Reset daily counters
            self.work_seconds = 0
            self.idle_seconds = 0
            self.pause_seconds = 0
            self.pause_count = 0
            
            # Update current date
            self.current_date = new_date
            
            # Refresh UI
            self.update_display()
            self.refresh_history()
            self.refresh_charts()
            
            print(f"[DATE CHANGE] Counters reset for new day: {new_date}")
    
    def load_today_data(self):
        """Load today's data from database"""
        work, idle = self.db.get_today_stats()
        self.work_seconds = work
        self.idle_seconds = idle
        
        # Load pause data
        pause_seconds, pause_count = self.db.get_today_pause_stats()
        self.pause_seconds = pause_seconds
        self.pause_count = pause_count
        
        self.update_display()
    
    def on_idle_checkbox_changed(self, state):
        """Handle leisure checkbox state change"""
        # Close current session if active
        if self.session_id is not None:
            # Save the current session time
            current_session_seconds = (datetime.now() - self.session_start_time).total_seconds()
            self.db.update_session(self.session_id, int(current_session_seconds), self.is_working)
            self.db.end_session(self.session_id)
            
            # Update the counters with completed session
            if self.is_working:
                self.work_seconds += int(current_session_seconds)
            else:
                self.idle_seconds += int(current_session_seconds)
            
            # Reset session
            self.session_id = None
            self.session_start_time = None
        
        # Switch mode
        self.is_working = not self.idle_checkbox.isChecked()
        
        # If user is still active, start new session with new mode
        if self.tracker.is_user_active():
            self.session_id = self.db.start_session(self.is_working)
            self.session_start_time = datetime.now()
    
    def auto_save_to_db(self):
        """Auto-save current session to database every minute"""
        if self.session_id is not None and self.tracker.is_user_active():
            current_session_seconds = (datetime.now() - self.session_start_time).total_seconds()
            self.db.update_session(self.session_id, int(current_session_seconds), self.is_working)
            # Log for debugging
            print(f"[Auto-save] Session {self.session_id} saved: {int(current_session_seconds)} seconds")
    
    def update_display(self):
        """Update the timer displays"""
        # Check if user is active
        if self.tracker.is_user_active():
            # Create new session if needed
            if self.session_id is None:
                self.session_id = self.db.start_session(self.is_working)
                self.session_start_time = datetime.now()
            
            # Calculate current session time from session start
            if self.session_start_time:
                current_session_seconds = (datetime.now() - self.session_start_time).total_seconds()
            else:
                current_session_seconds = 0
            
            # Ensure we don't get negative time
            if current_session_seconds < 0:
                current_session_seconds = 0
            
            # Update database
            self.db.update_session(self.session_id, int(current_session_seconds), self.is_working)
            
            # Update counters
            if self.is_working:
                display_work = self.work_seconds + int(current_session_seconds)
                display_idle = self.idle_seconds
            else:
                display_work = self.work_seconds
                display_idle = self.idle_seconds + int(current_session_seconds)
            
            mode = "Work" if self.is_working else "Leisure"
            self.status_label.setText(f"🟢 Active - {mode} Mode")
            self.status_label.setStyleSheet("""
                color: white;
                padding: 10px;
                background: rgba(16, 185, 129, 0.2);
                border-radius: 10px;
            """)
        else:
            # User is idle - DO NOT ACCUMULATE TIME
            if self.session_id is not None:
                # Close the active session
                self.db.end_session(self.session_id)
                # Reload data
                work, idle = self.db.get_today_stats()
                self.work_seconds = work
                self.idle_seconds = idle
                
                # Reload pause data
                pause_seconds, pause_count = self.db.get_today_pause_stats()
                self.pause_seconds = pause_seconds
                self.pause_count = pause_count
                
                self.session_id = None
                self.session_start_time = None
            
            # During inactivity, display accumulated time only (no counting)
            display_work = self.work_seconds
            display_idle = self.idle_seconds
            self.status_label.setText("⚫ Inactive")
            self.status_label.setStyleSheet("""
                color: rgba(255, 255, 255, 0.7);
                padding: 10px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
            """)
        
        # Update displays - always show pause time and count
        self.work_time_display.setText(self.format_seconds(display_work))
        self.idle_time_display.setText(self.format_seconds(display_idle))
        self.pause_time_display.setText(self.format_seconds(self.pause_seconds))
        self.pause_count_display.setText(f"{self.pause_count} pause{'s' if self.pause_count != 1 else ''}")
        self.total_time_display.setText(self.format_seconds(display_work + display_idle))
    
    def format_seconds(self, seconds):
        """Format seconds as HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{int(hours):02d}:{int(minutes):02d}:{int(secs):02d}"
    
    def refresh_history(self):
        """Refresh history table - show all individual sessions"""
        # Get all activity sessions (work and leisure)
        sessions = self.db.get_all_sessions(days=365)  # Get last year of data
        
        self.history_table.setRowCount(len(sessions))
        
        for i, (date, start_time, end_time, duration, session_type) in enumerate(sessions):
            self.history_table.setItem(i, 0, QTableWidgetItem(date))
            self.history_table.setItem(i, 1, QTableWidgetItem(start_time))
            self.history_table.setItem(i, 2, QTableWidgetItem(end_time))
            self.history_table.setItem(i, 3, QTableWidgetItem(self.format_seconds(duration)))
            
            # Add colored type indicator
            type_item = QTableWidgetItem(session_type)
            if session_type == "Work":
                type_item.setForeground(QColor("#10b981"))  # Green
            else:
                type_item.setForeground(QColor("#f59e0b"))  # Orange
            self.history_table.setItem(i, 4, type_item)
        
        # Refresh pauses table with detailed times
        pauses = self.db.get_all_pauses_detailed(days=365)
        self.pauses_table.setRowCount(len(pauses))
        
        for i, (date, pause_start, pause_end, duration) in enumerate(pauses):
            self.pauses_table.setItem(i, 0, QTableWidgetItem(date))
            self.pauses_table.setItem(i, 1, QTableWidgetItem(pause_start))
            self.pauses_table.setItem(i, 2, QTableWidgetItem(pause_end))
            
            # Add colored duration
            duration_item = QTableWidgetItem(self.format_seconds(duration))
            duration_item.setForeground(QColor("#a855f7"))  # Purple
            self.pauses_table.setItem(i, 3, duration_item)
    
    def show_info_dialog(self):
        """Show information dialog about how the tracker works"""
        msg = QMessageBox(self)
        msg.setWindowTitle("How Activity Tracker Works")
        msg.setIcon(QMessageBox.Information)
        
        info_text = """
<h3 style='color: #3b82f6;'>⏱️ How Activity Tracking Works</h3>

<p><b style='color: #10b981;'>Automatic Timer Start:</b><br>
• The timer starts automatically when you move your mouse or press any key<br>
• It detects your activity in real-time</p>

<p><b style='color: #f59e0b;'>Automatic Timer Stop:</b><br>
• The timer stops automatically after <b>60 seconds of inactivity</b><br>
• Inactivity = no mouse movement, clicks, or keyboard input</p>

<p><b style='color: #3b82f6;'>Work Mode vs Leisure Mode:</b><br>
• <b>Work Mode (default):</b> Time is counted as productive work<br>
• <b>Leisure Mode:</b> Check the box to track break/leisure time<br>
• Switch modes anytime - times are kept separate</p>

<p><b style='color: #8b5cf6;'>Data Persistence:</b><br>
• Your activity is automatically saved every 60 seconds<br>
• Data is stored in a local database<br>
• View your history and charts anytime</p>
        """
        
        msg.setText(info_text)
        
        # Apply modern style to message box
        msg.setStyleSheet("""
            QMessageBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e293b, stop:1 #0f172a);
                border-radius: 15px;
            }
            QMessageBox QLabel {
                color: white;
                min-width: 450px;
                background: transparent;
            }
            QMessageBox QWidget {
                background: transparent;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #2563eb);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 25px;
                font-weight: bold;
                min-width: 100px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb, stop:1 #1d4ed8);
            }
        """)
        
        msg.exec_()
    
    
    def on_pause_detected(self, pause_duration):
        """Callback from tracker thread - MUST be thread-safe, only emit signal"""
        print(f"[TRACKER THREAD] Pause detected: {pause_duration:.1f}s - emitting signal")
        # Emit signal to handle in main thread (thread-safe)
        self.pause_detected_signal.emit(pause_duration)
    
    def on_pause_detected_safe(self, pause_duration):
        """Thread-safe handler for pause detection - runs in main Qt thread"""
        print(f"\n[MAIN THREAD] ⏸️ PAUSE DETECTED! Duration: {pause_duration:.1f}s ({pause_duration/60:.1f} minutes)")
        print(f"[MAIN THREAD] Current pause stats BEFORE: seconds={self.pause_seconds}, count={self.pause_count}")
        
        try:
            # Log to database
            self.db.log_pause(int(pause_duration))
            print(f"[MAIN THREAD] ✅ Pause logged to database successfully")
            
            # Update pause counters in memory
            self.pause_seconds += int(pause_duration)
            self.pause_count += 1
            
            print(f"[MAIN THREAD] Current pause stats AFTER: seconds={self.pause_seconds}, count={self.pause_count}")
            
            # Force UI update (safe because we're in main thread)
            self.update_display()
            
        except Exception as e:
            print(f"[MAIN THREAD ERROR] ❌ Failed to log pause: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def open_analytics(self):
        """Open advanced analytics window"""
        self.analytics_window = AnalyticsWindow(self.db)
        self.analytics_window.show()
    
    def refresh_charts(self):
        """Refresh charts with work, leisure, and pause data"""
        stats = self.db.get_daily_stats(30)  # Last 30 days for better history view
        pauses = self.db.get_pause_periods(days=30)  # Get pauses for 30 days
        
        if not stats:
            return
        
        # Prepare daily stats
        dates = [s[0] for s in reversed(stats)]
        work_hours = [s[1] / 3600 for s in reversed(stats)]  # Convert to hours
        leisure_hours = [s[2] / 3600 for s in reversed(stats)]
        
        # Count pauses per day
        pause_count_by_date = {}
        total_pause_duration_by_date = {}
        
        for date, pause_time, duration in pauses:
            if date not in pause_count_by_date:
                pause_count_by_date[date] = 0
                total_pause_duration_by_date[date] = 0
            pause_count_by_date[date] += 1
            total_pause_duration_by_date[date] += duration
        
        # Convert pause durations to hours and align with dates
        pause_hours = [total_pause_duration_by_date.get(d, 0) / 3600 for d in dates]
        
        # Clear figure
        self.figure.clear()
        
        # Determine figure height based on number of days (for scrolling)
        num_days = len(dates)
        fig_height = max(4, 3 + (num_days * 0.15))  # Scale height with number of days
        self.figure.set_figheight(fig_height)
        
        # Create subplot with dark theme
        ax = self.figure.add_subplot(111, facecolor='#1e293b')
        
        # Bar positions and width (side-by-side bars)
        x = range(num_days)
        width = 0.26  # Slightly narrower for many bars
        
        # Create side-by-side bars: work, leisure, pauses
        bars1 = ax.bar([i - width for i in x], work_hours, width, 
                       label='Work', color='#10b981', alpha=0.85)
        bars2 = ax.bar([i for i in x], leisure_hours, width,
                       label='Leisure', color='#f59e0b', alpha=0.85)
        bars3 = ax.bar([i + width for i in x], pause_hours, width, 
                       label='Pauses', color='#8b5cf6', alpha=0.85)
        
        # Labels and title
        ax.set_xlabel('Date', color='white', fontweight='bold', fontsize=11)
        ax.set_ylabel('Hours', color='white', fontweight='bold', fontsize=11)
        
        # Dynamic title based on number of days
        if num_days <= 7:
            title = f'Activity Overview - Last {num_days} Days'
        elif num_days <= 30:
            title = f'Activity Overview - Last {num_days} Days'
        else:
            title = 'Activity Overview'
        
        ax.set_title(title, color='white', fontweight='bold', pad=15, fontsize=12)
        
        # X-axis configuration for better readability with many dates
        ax.set_xticks(x)
        if num_days > 14:
            # Show every other date if more than 14 days
            ax.set_xticklabels([dates[i] if i % 2 == 0 else '' for i in range(num_days)], 
                               rotation=45, ha='right', color='white', fontsize=9)
        else:
            ax.set_xticklabels(dates, rotation=45, ha='right', color='white', fontsize=10)
        
        ax.tick_params(colors='white', labelsize=9)
        
        # Set Y-axis with smart scaling
        max_value = max(max(work_hours + [0]), max(leisure_hours + [0]), max(pause_hours + [0]))
        if max_value > 0:
            ax.set_ylim(0, max_value * 1.1)  # 10% padding at top
        
        # Legend
        legend = ax.legend(facecolor='#0f172a', edgecolor='white', framealpha=0.9, 
                          loc='upper left', fontsize=10)
        for text in legend.get_texts():
            text.set_color('white')
        
        # Grid
        ax.grid(True, alpha=0.15, color='white', axis='y', linestyle='--')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('white')
        ax.spines['left'].set_linewidth(0.5)
        ax.spines['bottom'].set_linewidth(0.5)
        
        # Better margins for many dates
        left_margin = 0.12
        right_margin = 0.95
        top_margin = 0.93
        bottom_margin = 0.25 if num_days > 10 else 0.2
        
        self.figure.subplots_adjust(left=left_margin, right=right_margin, 
                                    top=top_margin, bottom=bottom_margin)
        
        # Add interactive tooltips
        self.add_bar_tooltips(ax, bars1, bars2, bars3, dates, work_hours, leisure_hours, pause_hours)
        
        # Update canvas
        self.canvas.draw()
    
    def add_bar_tooltips(self, ax, bars1, bars2, bars3, dates, work_hours, leisure_hours, pause_hours):
        """Add interactive tooltips to bar chart"""
        # Create annotation object (initially invisible)
        self.chart_annotation = ax.annotate(
            '', xy=(0, 0), xytext=(15, 15),
            textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='#1e293b', edgecolor='white', alpha=0.95),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='white'),
            color='white',
            fontsize=10,
            fontweight='bold',
            visible=False,
            zorder=1000
        )
        
        def format_time(hours):
            """Convert hours to HH:MM:SS format"""
            total_seconds = int(hours * 3600)
            h = total_seconds // 3600
            m = (total_seconds % 3600) // 60
            s = total_seconds % 60
            return f"{h:02d}:{m:02d}:{s:02d}"
        
        def on_hover(event):
            """Handle mouse hover events"""
            if event.inaxes != ax:
                self.chart_annotation.set_visible(False)
                self.canvas.draw_idle()
                return
            
            # Check if mouse is over any bar
            found = False
            for bars, hours, label, color in [
                (bars1, work_hours, 'Work', '#10b981'),
                (bars2, leisure_hours, 'Leisure', '#f59e0b'),
                (bars3, pause_hours, 'Pauses', '#8b5cf6')
            ]:
                for i, (bar, hour) in enumerate(zip(bars, hours)):
                    if bar.contains(event)[0]:
                        # Get bar position
                        x = bar.get_x() + bar.get_width() / 2
                        y = bar.get_height()
                        
                        # Format tooltip text
                        time_str = format_time(hour)
                        text = f"{dates[i]}\n{label}: {time_str}\n({hour:.2f}h)"
                        
                        # Update annotation
                        self.chart_annotation.xy = (x, y)
                        self.chart_annotation.set_text(text)
                        self.chart_annotation.get_bbox_patch().set_facecolor(color)
                        self.chart_annotation.get_bbox_patch().set_alpha(0.9)
                        self.chart_annotation.set_visible(True)
                        found = True
                        break
                
                if found:
                    break
            
            if not found:
                self.chart_annotation.set_visible(False)
            
            self.canvas.draw_idle()
        
        # Connect hover event
        self.canvas.mpl_connect('motion_notify_event', on_hover)
    
    def closeEvent(self, event):
        """Handle application close"""
        if self.session_id:
            self.db.end_session(self.session_id)
        self.tracker.stop()
        self.tray_icon.hide()
        event.accept()


def main():
    # Set Windows taskbar icon (MUST be before QApplication!)
    try:
        import ctypes
        # Use simple, universal AppUserModelID
        myappid = 'ActivityTracker'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception as e:
        print(f"Warning: Could not set app model ID: {e}")
    
    # Create app with minimal overhead
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Load icon
    icon_path = 'icon.ico'
    if not os.path.exists(icon_path) and hasattr(sys, '_MEIPASS'):
        icon_path = os.path.join(sys._MEIPASS, 'icon.ico')
    
    app_icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()
    app.setWindowIcon(app_icon)
    
    # Set dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 41, 59))
    palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(palette)
    
    # Create and show window
    window = ModernStopwatchWidget()
    window.setWindowIcon(app_icon)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

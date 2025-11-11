import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QCheckBox, 
                             QTabWidget, QTableWidget, QTableWidgetItem, 
                             QSystemTrayIcon, QMenu, QAction, QGraphicsDropShadowEffect,
                             QStackedWidget, QMessageBox)
from PyQt5.QtCore import QTimer, Qt, QTime, QPoint, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QPixmap, QPainter, QLinearGradient
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from database import ActivityDatabase
from tracker import ActivityTracker

class ModernStopwatchWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = ActivityDatabase()
        self.tracker = ActivityTracker(idle_threshold=60)
        
        self.session_id = None
        self.session_start_time = None
        self.work_seconds = 0
        self.idle_seconds = 0
        self.is_working = True  # True = work, False = leisure
        
        # For dragging the window
        self.dragging = False
        self.drag_position = None
        
        self.init_ui()
        self.init_timer()
        self.init_tray()
        self.tracker.start()
        
        # Load today's data
        self.load_today_data()
        
        # Apply modern stylesheet
        self.apply_modern_style()
    
    def init_ui(self):
        """Initialize the user interface with modern design"""
        self.setWindowTitle("⚡ Activity Tracker")
        
        # Frameless window for custom title bar
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set window icon for taskbar
        icon = QIcon("icon.ico")
        self.setWindowIcon(icon)
        
        # Wider window size to accommodate non-scrollable tabs
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
        self.btn_timer.clicked.connect(lambda: self.switch_page(0))
        button_layout.addWidget(self.btn_timer)
        
        self.btn_history = QPushButton("📊 History")
        self.btn_history.setObjectName("navButton")
        self.btn_history.setCheckable(True)
        self.btn_history.clicked.connect(lambda: self.switch_page(1))
        button_layout.addWidget(self.btn_history)
        
        self.btn_charts = QPushButton("📈 Charts")
        self.btn_charts.setObjectName("navButton")
        self.btn_charts.setCheckable(True)
        self.btn_charts.clicked.connect(lambda: self.switch_page(2))
        button_layout.addWidget(self.btn_charts)
        
        # Store buttons in list for easy access
        self.nav_buttons = [self.btn_timer, self.btn_history, self.btn_charts]
        
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
    
    def create_time_card(self, title, object_name, color1, color2):
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
        
        return card
    
    def create_history_tab(self):
        """Create the history tab"""
        widget = QWidget()
        widget.setObjectName("tabContent")
        layout = QVBoxLayout()
        layout.setSpacing(15)
        widget.setLayout(layout)
        
        # Title with info button
        header_layout = QHBoxLayout()
        title = QLabel("📅 Activity History (All Records)")
        title.setObjectName("sectionTitle")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Info button
        info_btn = QPushButton("ℹ️ Info")
        info_btn.setObjectName("infoButton")
        info_btn.clicked.connect(self.show_info_dialog)
        header_layout.addWidget(info_btn)
        
        layout.addLayout(header_layout)
        
        # Table
        self.history_table = QTableWidget()
        self.history_table.setObjectName("modernTable")
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Date", "Work Time", "Leisure Time", "Total Time"])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setAlternatingRowColors(True)
        layout.addWidget(self.history_table)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh History")
        refresh_btn.setObjectName("modernButton")
        refresh_btn.clicked.connect(self.refresh_history)
        layout.addWidget(refresh_btn)
        
        return widget
    
    def create_charts_tab(self):
        """Create the charts tab"""
        widget = QWidget()
        widget.setObjectName("tabContent")
        layout = QVBoxLayout()
        layout.setSpacing(15)
        widget.setLayout(layout)
        
        # Title
        title = QLabel("📊 Weekly Overview")
        title.setObjectName("sectionTitle")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Matplotlib canvas with dark theme
        self.figure = Figure(figsize=(6, 4), facecolor='#1e293b')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Charts")
        refresh_btn.setObjectName("modernButton")
        refresh_btn.clicked.connect(self.refresh_charts)
        layout.addWidget(refresh_btn)
        
        return widget
    
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
                padding: 14px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 140px;
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
            }
            
            QTableWidget#modernTable::item {
                padding: 10px;
                border: none;
                color: #e2e8f0;
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
            
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.05);
                width: 10px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:vertical {
                background: rgba(59, 130, 246, 0.5);
                border-radius: 5px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: rgba(59, 130, 246, 0.7);
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
    
    def load_today_data(self):
        """Load today's data from database"""
        work, idle = self.db.get_today_stats()
        self.work_seconds = work
        self.idle_seconds = idle
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
            
            # Calculate current session time
            current_session_seconds = (datetime.now() - self.session_start_time).total_seconds()
            
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
            # User is idle, close session if open
            if self.session_id is not None:
                self.db.end_session(self.session_id)
                # Reload data
                work, idle = self.db.get_today_stats()
                self.work_seconds = work
                self.idle_seconds = idle
                self.session_id = None
                self.session_start_time = None
            
            display_work = self.work_seconds
            display_idle = self.idle_seconds
            self.status_label.setText("⚫ Inactive")
            self.status_label.setStyleSheet("""
                color: rgba(255, 255, 255, 0.7);
                padding: 10px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
            """)
        
        # Update displays
        self.work_time_display.setText(self.format_seconds(display_work))
        self.idle_time_display.setText(self.format_seconds(display_idle))
        self.total_time_display.setText(self.format_seconds(display_work + display_idle))
    
    def format_seconds(self, seconds):
        """Format seconds as HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{int(hours):02d}:{int(minutes):02d}:{int(secs):02d}"
    
    def refresh_history(self):
        """Refresh history table - show all records"""
        stats = self.db.get_daily_stats(365)  # Get last year of data (all records)
        
        self.history_table.setRowCount(len(stats))
        
        for i, (date, work, idle) in enumerate(stats):
            total = work + idle
            
            self.history_table.setItem(i, 0, QTableWidgetItem(date))
            self.history_table.setItem(i, 1, QTableWidgetItem(self.format_seconds(work)))
            self.history_table.setItem(i, 2, QTableWidgetItem(self.format_seconds(idle)))
            self.history_table.setItem(i, 3, QTableWidgetItem(self.format_seconds(total)))
    
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
        msg.setStyleSheet("""
            QMessageBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e293b, stop:1 #0f172a);
            }
            QLabel {
                color: white;
                min-width: 450px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #2563eb);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb, stop:1 #1d4ed8);
            }
        """)
        
        msg.exec_()
    
    def refresh_charts(self):
        """Refresh weekly charts"""
        stats = self.db.get_daily_stats(28)  # Last 28 days
        
        if not stats:
            return
        
        # Prepare data
        dates = [s[0] for s in reversed(stats)]
        work_hours = [s[1] / 3600 for s in reversed(stats)]  # Convert to hours
        idle_hours = [s[2] / 3600 for s in reversed(stats)]
        
        # Clear figure
        self.figure.clear()
        
        # Create subplot with dark theme
        ax = self.figure.add_subplot(111, facecolor='#1e293b')
        
        # Bar width
        x = range(len(dates))
        width = 0.35
        
        # Create bars
        bars1 = ax.bar([i - width/2 for i in x], work_hours, width, 
                       label='Work', color='#10b981', alpha=0.8)
        bars2 = ax.bar([i + width/2 for i in x], idle_hours, width, 
                       label='Leisure', color='#f59e0b', alpha=0.8)
        
        # Labels and title
        ax.set_xlabel('Date', color='white', fontweight='bold')
        ax.set_ylabel('Hours', color='white', fontweight='bold')
        ax.set_title('PC Activity - Last 28 Days', color='white', fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(dates, rotation=45, ha='right', color='white')
        ax.tick_params(colors='white')
        
        # Legend
        legend = ax.legend(facecolor='#0f172a', edgecolor='white', framealpha=0.8)
        for text in legend.get_texts():
            text.set_color('white')
        
        # Grid
        ax.grid(True, alpha=0.2, color='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
        
        # Adjust layout
        self.figure.tight_layout()
        
        # Update canvas
        self.canvas.draw()
    
    def closeEvent(self, event):
        """Handle application close"""
        if self.session_id:
            self.db.end_session(self.session_id)
        self.tracker.stop()
        self.tray_icon.hide()
        event.accept()


def main():
    # Set Windows taskbar icon (must be before QApplication)
    try:
        import ctypes
        myappid = 'activitytracker.desktop.widget.1.0'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except:
        pass
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern style
    
    # Set application icon
    app.setWindowIcon(QIcon('icon.ico'))
    
    # Set dark palette for better integration
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 41, 59))
    palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(palette)
    
    window = ModernStopwatchWidget()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

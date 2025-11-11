import time
from datetime import datetime
from pynput import mouse, keyboard
from threading import Thread, Lock
import logging

class ActivityTracker:
    def __init__(self, idle_threshold: int = 60):
        """
        User activity tracker
        
        Args:
            idle_threshold: seconds of inactivity before considering user idle
        """
        self.idle_threshold = idle_threshold
        self.last_activity = time.time()
        self.is_active = False
        self.total_active_time = 0
        self.session_start = None
        self.idle_start = None  # Track when idle period started
        self.lock = Lock()
        self.running = False
        
        # Callback for pause detection
        self.on_idle_callback = None
        
        # Listeners for mouse and keyboard
        self.mouse_listener = None
        self.keyboard_listener = None
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def set_idle_callback(self, callback):
        """Set callback to be called when user becomes idle with idle duration"""
        self.on_idle_callback = callback
    
    def on_activity(self):
        """Callback called when activity is detected"""
        with self.lock:
            self.last_activity = time.time()
            if not self.is_active:
                # User became active after idle period
                if self.idle_start is not None:
                    # Calculate idle duration and trigger callback
                    idle_duration = time.time() - self.idle_start
                    print(f"[TRACKER] Calling callback with duration: {idle_duration:.1f}s")
                    if self.on_idle_callback:
                        # Call callback with idle duration in seconds
                        self.on_idle_callback(idle_duration)
                    self.idle_start = None
                    self.logger.info(f"User active again after {idle_duration:.0f}s pause")
                else:
                    self.logger.info("User active")
                
                self.is_active = True
                self.session_start = time.time()
    
    def on_mouse_move(self, x, y):
        """Callback for mouse movement"""
        self.on_activity()
    
    def on_mouse_click(self, x, y, button, pressed):
        """Callback for mouse click"""
        if pressed:
            self.on_activity()
    
    def on_mouse_scroll(self, x, y, dx, dy):
        """Callback for mouse scroll"""
        self.on_activity()
    
    def on_keyboard_press(self, key):
        """Callback for key press"""
        self.on_activity()
    
    def start(self):
        """Start activity tracking"""
        if self.running:
            return
        
        self.running = True
        self.last_activity = time.time()
        
        # Start listeners
        self.mouse_listener = mouse.Listener(
            on_move=self.on_mouse_move,
            on_click=self.on_mouse_click,
            on_scroll=self.on_mouse_scroll
        )
        
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_keyboard_press
        )
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
        
        # Thread to check idle state
        self.check_thread = Thread(target=self._check_idle, daemon=True)
        self.check_thread.start()
        
        self.logger.info("Activity tracker started")
    
    def stop(self):
        """Stop activity tracking"""
        self.running = False
        
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        self.logger.info("Activity tracker stopped")
    
    def _check_idle(self):
        """Thread that checks if user is idle"""
        while self.running:
            time.sleep(1)
            
            with self.lock:
                idle_time = time.time() - self.last_activity
                
                if idle_time > self.idle_threshold and self.is_active:
                    # User became idle
                    if self.session_start:
                        self.total_active_time += time.time() - self.session_start
                    
                    # Start tracking idle period if not already tracking
                    if self.idle_start is None:
                        self.idle_start = time.time()
                    
                    self.is_active = False
                    self.session_start = None
                    self.logger.info("User idle")
    
    def get_current_session_time(self) -> float:
        """Return current session time in seconds"""
        with self.lock:
            if self.is_active and self.session_start:
                return time.time() - self.session_start
            return 0
    
    def get_total_active_time(self) -> float:
        """Return total active time in seconds"""
        with self.lock:
            total = self.total_active_time
            if self.is_active and self.session_start:
                total += time.time() - self.session_start
            return total
    
    def is_user_active(self) -> bool:
        """Return True if user is currently active"""
        with self.lock:
            return self.is_active
    
    def reset_daily_stats(self):
        """Reset daily statistics"""
        with self.lock:
            self.total_active_time = 0
            self.session_start = time.time() if self.is_active else None

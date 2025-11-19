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
        
        # Track pending pause from system suspend/resume
        self.pending_pause = None  # Tuple: (duration, pause_start, work_end)
        
        # Listeners for mouse and keyboard
        self.mouse_listener = None
        self.keyboard_listener = None
        
        # Track last check time to detect system suspend/resume
        self.last_check_time = time.time()
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def set_idle_callback(self, callback):
        """Set callback to be called when user becomes idle with idle duration"""
        self.on_idle_callback = callback
    
    def on_activity(self):
        """Callback called when activity is detected"""
        with self.lock:
            current_time = time.time()
            
            # Check if there's a pending pause from system suspend
            if self.pending_pause:
                suspend_duration, suspend_start_time, work_end_time = self.pending_pause
                print(f"[TRACKER] User returned after system suspend. Logging pause now.")
                print(f"[TRACKER] Pause duration: {suspend_duration:.1f}s, started at: {suspend_start_time}, work ended at: {work_end_time}")
                
                # Calculate actual pause end time (now, when user returns)
                # Adjust duration to be from suspend_start to current_time
                actual_duration = current_time - suspend_start_time
                
                if self.on_idle_callback:
                    try:
                        self.on_idle_callback(actual_duration, suspend_start_time, work_end_time)
                    except Exception as e:
                        print(f"[TRACKER ERROR] Callback failed: {e}")
                
                self.pending_pause = None  # Clear pending pause
                self.logger.info(f"System suspend pause logged: {actual_duration:.0f}s")
            
            # Check if user was idle (idle_start is set)
            was_idle = (self.idle_start is not None)
            idle_start_time = self.idle_start  # Save before resetting
            
            # Update last activity time
            self.last_activity = current_time
            
            # If user was idle and now is active, trigger callback
            if was_idle:
                # Calculate idle duration
                idle_duration = current_time - idle_start_time
                print(f"[TRACKER] User returned from pause. Duration: {idle_duration:.1f}s (threshold: {self.idle_threshold}s)")
                
                # Only log if idle duration exceeded threshold
                if idle_duration >= self.idle_threshold:
                    # The work session ended at last_activity time (before pause started)
                    work_end_time = idle_start_time - self.idle_threshold
                    
                    # Call callback BEFORE resetting state
                    # Pass duration, pause_start timestamp, and work_end timestamp
                    if self.on_idle_callback:
                        print(f"[TRACKER] Calling callback with duration: {idle_duration:.1f}s, pause_start: {idle_start_time}, work_end: {work_end_time}")
                        try:
                            self.on_idle_callback(idle_duration, idle_start_time, work_end_time)
                        except Exception as e:
                            print(f"[TRACKER ERROR] Callback failed: {e}")
                    
                    self.logger.info(f"User active again after {idle_duration:.0f}s pause")
                else:
                    print(f"[TRACKER] Idle duration {idle_duration:.1f}s below threshold {self.idle_threshold}s - not logging")
                
                # Reset idle tracking
                self.idle_start = None
            
            # Mark user as active if they weren't
            if not self.is_active:
                self.is_active = True
                self.session_start = current_time
                self.logger.info("User active")
    
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
        self.last_check_time = time.time()  # Initialize check time
        
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
        last_log_time = 0
        while self.running:
            time.sleep(0.5)  # Check every 500ms for more responsiveness
            
            with self.lock:
                current_time = time.time()
                
                # Check for system suspend/resume
                # If more than 5 seconds passed since last check, system was likely suspended
                time_since_last_check = current_time - self.last_check_time
                if time_since_last_check > 5.0:
                    # System was suspended!
                    suspend_duration = time_since_last_check
                    print(f"[TRACKER] 🛏️ System suspend detected! Duration: {suspend_duration:.1f}s")
                    
                    # If we were active before suspend, save pause info but don't log yet
                    if self.is_active:
                        # Calculate when suspend started (approximately last_check_time)
                        suspend_start_time = self.last_check_time
                        
                        # The work session should end at last_activity time (when user stopped working)
                        work_end_time = self.last_activity
                        
                        # Only log if suspend duration exceeded threshold
                        if suspend_duration >= self.idle_threshold:
                            # Calculate actual pause end time (when user returns)
                            # We'll wait for first activity to register this
                            print(f"[TRACKER] Saving pending pause: {suspend_duration:.1f}s")
                            print(f"[TRACKER] Work ended at: {work_end_time}, Suspend at: {suspend_start_time}")
                            
                            # Save pending pause to be logged when user returns
                            self.pending_pause = (suspend_duration, suspend_start_time, work_end_time)
                            
                            self.logger.info(f"System suspend detected: {suspend_duration:.0f}s - will log when user returns")
                        
                        # Mark user as inactive
                        if self.session_start:
                            self.total_active_time += self.last_check_time - self.session_start
                        
                        self.is_active = False
                        self.session_start = None
                        self.idle_start = None  # Clear idle tracking
                    
                    # Reset last_activity to current time (after resume)
                    self.last_activity = current_time
                
                # Update last check time
                self.last_check_time = current_time
                
                idle_time = current_time - self.last_activity
                
                # Debug log every 10 seconds when approaching idle threshold
                if idle_time > (self.idle_threshold * 0.8) and (current_time - last_log_time) > 10:
                    print(f"[TRACKER CHECK] Idle time: {idle_time:.1f}s / {self.idle_threshold}s (threshold), is_active={self.is_active}")
                    last_log_time = current_time
                
                # User has been idle long enough
                if idle_time > self.idle_threshold and self.is_active:
                    # Mark user as inactive
                    if self.session_start:
                        self.total_active_time += current_time - self.session_start
                    
                    # Start tracking idle period if not already tracking
                    if self.idle_start is None:
                        self.idle_start = current_time
                        print(f"[TRACKER] ⏸️ User became IDLE after {idle_time:.1f}s of inactivity (threshold: {self.idle_threshold}s)")
                    
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

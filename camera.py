"""
Threaded Camera Capture Module.
Provides zero-latency, fresh-frame webcam capture on Windows.
"""
import cv2
import threading
import time
import numpy as np
import config

class ThreadedCamera:
    def __init__(self, camera_index=config.CAMERA_INDEX, width=config.FRAME_WIDTH, height=config.FRAME_HEIGHT):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None
        self.running = False
        self.lock = threading.Lock()
        self.frame = None
        self.is_synthetic = False
        self.thread = None
        self._init_camera()

    def _init_camera(self):
        # On Windows, cv2.CAP_DSHOW starts in milliseconds and avoids MFT frame buffering
        print(f"[Camera] Connecting to camera index {self.camera_index} via DirectShow...")
        try:
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        except Exception:
            self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap or not self.cap.isOpened():
            # Try default index 0 without DSHOW if failed
            print(f"[Camera] Index {self.camera_index} failed, trying default index 0...")
            self.cap = cv2.VideoCapture(0)

        if self.cap and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, config.FPS_TARGET)
            # Minimize buffer size to 1 to eliminate latency
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            ret, test_frame = self.cap.read()
            if ret and test_frame is not None:
                self.frame = test_frame
                self.running = True
                self.thread = threading.Thread(target=self._capture_loop, daemon=True)
                self.thread.start()
                print(f"[Camera] Hardware camera initialized successfully ({self.frame.shape[1]}x{self.frame.shape[0]})")
                return

        # If no webcam is accessible, activate synthetic test camera so app never crashes
        print("[Camera] No physical webcam detected or camera in use. Activating Synthetic Test Camera...")
        self.is_synthetic = True
        self.running = True
        self.frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.thread = threading.Thread(target=self._synthetic_loop, daemon=True)
        self.thread.start()

    def _capture_loop(self):
        while self.running:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    # Mirror horizontally for natural interactive mirror feel
                    flipped = cv2.flip(frame, 1)
                    with self.lock:
                        self.frame = flipped
                else:
                    time.sleep(0.005)
            else:
                time.sleep(0.01)

    def _synthetic_loop(self):
        """Simulates camera feed with ambient room background if no webcam is connected."""
        t0 = time.time()
        while self.running:
            t = time.time() - t0
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            # Create a stylized dark tech background
            frame[:] = (20, 22, 28)
            # Add subtle grid lines
            for x in range(0, self.width, 80):
                cv2.line(frame, (x, 0), (x, self.height), (28, 32, 40), 1)
            for y in range(0, self.height, 80):
                cv2.line(frame, (0, y), (self.width, y), (28, 32, 40), 1)
            # Show simulated webcam status banner
            cv2.putText(frame, "[TEST MODE: NO WEBCAM DETECTED - CONNECT CAMERA OR PRESS 'C']", 
                        (self.width // 2 - 350, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 180, 255), 1, cv2.LINE_AA)
            with self.lock:
                self.frame = frame
            time.sleep(0.033)

    def read(self):
        with self.lock:
            if self.frame is not None:
                return True, self.frame.copy()
            return False, None

    def release(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()

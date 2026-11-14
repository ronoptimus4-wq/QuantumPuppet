"""
Ultra-Responsive Hand Tracking & Human Gesture Recognition Engine.
Detects human finger commands (Running, Punching, Jumping, Waving, Dancing, Meditating, Flying)
using 3D invariant Euclidean metrics for foolproof, lightning-fast detection.
"""
import time
import math
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
import config

class HandTracker:
    def __init__(self, model_path=config.MODEL_PATH):
        self.model_path = model_path
        self.detector = None
        self.smoothed_landmarks = None
        self.prev_time = time.time()
        self.prev_palm = None
        self.palm_history_x = []
        self.hand_velocity = 0.0
        self.current_gesture = "IDLE"
        self.status_label = "IDLE HOVER // SYSTEM ONLINE"
        self.hud_state = "[awaiting instruction]"
        self.last_run_time = 0.0
        self.stride_count = 0
        self.prev_stride_lead = 0 # 0 for index, 1 for middle
        self._init_detector()

    def _init_detector(self):
        print(f"[Tracker] Loading MediaPipe HandLandmarker from {self.model_path}...")
        base_options = mp_python.BaseOptions(model_asset_path=self.model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_hand_presence_confidence=config.MIN_PRESENCE_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        print("[Tracker] HandLandmarker loaded! Human action gestures armed.")

    def process(self, frame_bgr):
        h, w, _ = frame_bgr.shape
        now = time.time()
        dt = max(0.001, now - self.prev_time)
        self.prev_time = now

        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        result = self.detector.detect(mp_image)

        if not result.hand_landmarks or len(result.hand_landmarks) == 0:
            self.hand_velocity *= 0.8
            return {
                "detected": False,
                "landmarks": None,
                "fingertips": None,
                "palm": None,
                "gesture": "NO_HAND",
                "status_label": "SEARCHING FOR PILOT...",
                "hud_state": "[awaiting pilot connection]",
                "velocity": self.hand_velocity,
                "finger_states": [False, False, False, False, False]
            }

        raw_lms = result.hand_landmarks[0]
        pts_norm = np.array([[lm.x, lm.y, lm.z] for lm in raw_lms], dtype=np.float32)

        pts_px = np.zeros((21, 2), dtype=np.float32)
        pts_px[:, 0] = pts_norm[:, 0] * w
        pts_px[:, 1] = pts_norm[:, 1] * h

        curr_palm = pts_px[9].copy()
        if self.prev_palm is not None:
            dist = np.linalg.norm(curr_palm - self.prev_palm)
            inst_vel = (dist / w) / dt
            self.hand_velocity = 0.6 * self.hand_velocity + 0.4 * inst_vel
        self.prev_palm = curr_palm

        # Track horizontal palm motion for wave detection
        self.palm_history_x.append((now, curr_palm[0]))
        self.palm_history_x = [(t, x) for t, x in self.palm_history_x if now - t < 0.8]

        # One-Euro adaptive smoothing
        if self.smoothed_landmarks is None:
            self.smoothed_landmarks = pts_px.copy()
        else:
            vel_norm = min(1.0, self.hand_velocity / config.VELOCITY_THRESHOLD)
            alpha = config.SMOOTH_FACTOR_SLOW + vel_norm * (config.SMOOTH_FACTOR_FAST - config.SMOOTH_FACTOR_SLOW)
            self.smoothed_landmarks = (1.0 - alpha) * self.smoothed_landmarks + alpha * pts_px

        landmarks = self.smoothed_landmarks.astype(np.int32)
        wrist = landmarks[0]
        palm_center = ((landmarks[0] + landmarks[9]) // 2)

        # Palm scale
        palm_scale = max(20.0, np.linalg.norm(pts_px[9] - pts_px[0]))

        # 3D Invariant Finger Extension Checks
        # Index
        d_idx_tip = np.linalg.norm(pts_px[8] - pts_px[0])
        d_idx_pip = np.linalg.norm(pts_px[6] - pts_px[0])
        index_open = d_idx_tip > (d_idx_pip * 1.15) and d_idx_tip > (palm_scale * 0.90)

        # Middle
        d_mid_tip = np.linalg.norm(pts_px[12] - pts_px[0])
        d_mid_pip = np.linalg.norm(pts_px[10] - pts_px[0])
        middle_open = d_mid_tip > (d_mid_pip * 1.15) and d_mid_tip > (palm_scale * 0.95)

        # Ring
        d_rng_tip = np.linalg.norm(pts_px[16] - pts_px[0])
        d_rng_pip = np.linalg.norm(pts_px[14] - pts_px[0])
        ring_open = d_rng_tip > (d_rng_pip * 1.15) and d_rng_tip > (palm_scale * 0.85)

        # Pinky
        d_pky_tip = np.linalg.norm(pts_px[20] - pts_px[0])
        d_pky_pip = np.linalg.norm(pts_px[18] - pts_px[0])
        pinky_open = d_pky_tip > (d_pky_pip * 1.15) and d_pky_tip > (palm_scale * 0.75)

        # Thumb
        d_thb_tip = np.linalg.norm(pts_px[4] - pts_px[17])
        d_thb_mcp = np.linalg.norm(pts_px[2] - pts_px[17])
        thumb_open = d_thb_tip > (d_thb_mcp * 1.25)

        # Thumb upward check (for Thumbs Up gesture)
        thumb_upward = (pts_px[4, 1] < pts_px[2, 1] - 18) and (pts_px[4, 1] < pts_px[0, 1] - 25)

        # Pinch detection (Thumb tip to Index tip)
        pinch_dist = np.linalg.norm(pts_px[4] - pts_px[8])
        is_pinching = (pinch_dist / palm_scale) < 0.35

        # Check for Blade Hand / Military Salute (all 4 fingers straight together, thumb tucked)
        d_8_12 = np.linalg.norm(pts_px[8] - pts_px[12])
        d_12_16 = np.linalg.norm(pts_px[12] - pts_px[16])
        d_16_20 = np.linalg.norm(pts_px[16] - pts_px[20])
        avg_finger_gap = (d_8_12 + d_12_16 + d_16_20) / 3.0
        is_blade_hand = (not thumb_open) and (avg_finger_gap / palm_scale < 0.28) and (index_open and middle_open and ring_open and pinky_open)

        # Check for L-Sign / Thinking (Thumb + Index at ~90 deg, others curled)
        v_thb = pts_px[4] - pts_px[0]
        v_idx = pts_px[8] - pts_px[0]
        norm_thb = np.linalg.norm(v_thb)
        norm_idx = np.linalg.norm(v_idx)
        dot = np.dot(v_thb, v_idx) / max(0.001, norm_thb * norm_idx)
        angle_thb_idx = math.degrees(math.acos(np.clip(dot, -1.0, 1.0)))
        is_thinking_l = thumb_open and index_open and (35.0 <= angle_thb_idx <= 125.0) and not middle_open and not ring_open and not pinky_open

        # Check for Waving (Palm swaying side to side)
        is_waving = False
        if len(self.palm_history_x) >= 6:
            xs = [x for _, x in self.palm_history_x]
            x_range = max(xs) - min(xs)
            if x_range > (w * 0.07) and (index_open and middle_open and ring_open):
                is_waving = True

        finger_states = [thumb_open, index_open, middle_open, ring_open, pinky_open]
        open_count = sum([index_open, middle_open, ring_open, pinky_open])

        # Walking / Running stride persistence check
        is_running_fingers = (index_open and middle_open and not ring_open and not pinky_open)
        if is_running_fingers:
            self.last_run_time = now
            # Detect alternating stride steps
            lead = 0 if pts_px[8, 1] < pts_px[12, 1] else 1
            if lead != self.prev_stride_lead:
                self.stride_count += 1
                self.prev_stride_lead = lead
        elif (now - self.last_run_time < 0.35) and (index_open or middle_open) and not ring_open and not pinky_open:
            # Maintain active running cadence between alternating stride footsteps
            is_running_fingers = True

        # ==============================================================
        # HUMAN FUNCTION GESTURE CLASSIFIER (12 ACTIONS)
        # ==============================================================
        if is_waving:
            # 1. Waving Hand -> WAVING HELLO
            self.current_gesture = "WAVING"
            self.status_label = "HUMAN ACTION: WAVING HELLO // GREETING"
            self.hud_state = "[greeting: wave hello]"
        elif is_pinching and (middle_open and ring_open and pinky_open):
            # 2. OK Gesture -> Zen Meditation & Recovery
            self.current_gesture = "MEDITATING"
            self.status_label = "HUMAN ACTION: ZEN MEDITATION // RECHARGING"
            self.hud_state = "[meditation: biometric calm 100%]"
        elif is_blade_hand:
            # 3. Flat Blade Hand -> Military Salute / Honor
            self.current_gesture = "SALUTE"
            self.status_label = "HUMAN ACTION: MILITARY SALUTE // RESPECT"
            self.hud_state = "[protocol: salute - at ease commander]"
        elif thumb_upward and not index_open and not middle_open and not ring_open and not pinky_open:
            # 4. Thumbs Up -> Approval / Like
            self.current_gesture = "THUMBS_UP"
            self.status_label = "HUMAN ACTION: THUMBS UP // MISSION APPROVED"
            self.hud_state = "[approval: mission approved +100xp]"
        elif is_thinking_l:
            # 5. L-Sign / Finger to Chin -> Deep Thinking / Problem Solving
            self.current_gesture = "THINKING"
            self.status_label = "HUMAN ACTION: DEEP THINKING // BRAINSTORM"
            self.hud_state = "[cognition: quantum solver active]"
        elif thumb_open and pinky_open and not index_open and not middle_open and not ring_open:
            # 6. Shaka / Hang Loose -> Victory Party Dance
            self.current_gesture = "DANCING"
            self.status_label = "HUMAN ACTION: VICTORY DANCE // GROOVING"
            self.hud_state = "[celebrating: victory groove]"
        elif index_open and pinky_open and not middle_open and not ring_open:
            # 7. Rock On / Horns -> Athletic Jump / Parkour
            self.current_gesture = "JUMPING"
            self.status_label = "HUMAN ACTION: ATHLETIC JUMP // LEAP"
            self.hud_state = "[vertical leap: apex +180px]"
        elif is_running_fingers:
            # 8. Scissors / Walking Fingers -> SPRINTING / RUNNING
            self.current_gesture = "RUNNING"
            self.status_label = "HUMAN ACTION: SPRINTING // RUN PROTOCOL"
            self.hud_state = f"[running: stride count {self.stride_count}]"
        elif open_count == 0:
            # 9. Clenched Fist -> BOXING / PUNCHING
            self.current_gesture = "PUNCHING"
            self.status_label = "HUMAN ACTION: BOXING // RAPID PUNCH"
            self.hud_state = "[boxing combo: jab-cross 950N]"
        elif is_pinching:
            # 10. Pinch -> Hexagonal Force Shield
            self.current_gesture = "DEFENSIVE_SHIELD"
            self.status_label = "HUMAN ACTION: DEFENSIVE SHIELD // BLOCK"
            self.hud_state = "[defensive barrier: active]"
        elif index_open and not middle_open and not ring_open and not pinky_open:
            # 11. Single Pointing Finger -> SUPERSONIC FLIGHT
            self.current_gesture = "FLYING"
            self.status_label = "HUMAN ACTION: SUPERSONIC FLIGHT // BEAM"
            self.hud_state = "[flight vector: active]"
        elif open_count >= 4:
            # 12. Open Hand -> REPULSOR BLAST / PLASMA BURST
            self.current_gesture = "OPEN_HAND"
            self.status_label = "HUMAN ACTION: REPULSOR BURST // ACTIVE"
            self.hud_state = "[energy discharge: 100%]"
        else:
            self.current_gesture = "IDLE"
            self.status_label = "HUMAN ACTION: IDLE // BREATHING"
            self.hud_state = "[awaiting human instruction]"

        fingertips = [landmarks[4], landmarks[8], landmarks[12], landmarks[16], landmarks[20]]

        return {
            "detected": True,
            "landmarks": landmarks,
            "fingertips": fingertips,
            "palm": palm_center,
            "wrist": wrist,
            "gesture": self.current_gesture,
            "status_label": self.status_label,
            "hud_state": self.hud_state,
            "velocity": self.hand_velocity,
            "is_pinching": is_pinching,
            "palm_scale": palm_scale,
            "finger_states": finger_states
        }

    def close(self):
        if self.detector:
            self.detector.close()

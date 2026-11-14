"""
Cinematic Visual Rendering & Humanoid Action Engine.
Executes real-time human animations (Running, Punching, Jumping, Waving, Dancing, Meditating, Flying)
on the large glassy alien suit avatar with dynamic puppet strings and Stark/Alien HUD.
"""
import math
import os
import time
import numpy as np
import cv2
import config

class VisualEngine:
    def __init__(self, width=config.FRAME_WIDTH, height=config.FRAME_HEIGHT):
        self.w = width
        self.h = height
        self.start_time = time.time()
        
        self.avatar_mode = config.DEFAULT_AVATAR # "alien", "ironman", "mech"
        self.sprites = {}
        self._load_sprites()
        
        # Responsive Digital Puppet Tracking Physics
        self.avatar_current_x = float(self.w * 0.22)
        self.avatar_current_y = float(self.h * 0.48)
        self.avatar_vel_x = 0.0
        self.avatar_vel_y = 0.0
        self.avatar_tilt = 0.0
        
        # Human Action State Variables
        self.action_start_time = time.time()
        self.last_action = "IDLE"
        
        # Terminal log state
        self.terminal_lines = [
            "kal@gestural-agentic:~$ alien --link-neural",
            "[ok] human kinematic bridge - online",
            "stride_cadence: 180 spm - sprint protocol ok",
            "boxing_daemon: rapid jab-cross armed (950N)",
            "vertical_leap: gravitational dampening active",
            "greeting_protocol: handshake handshake ok",
            "thumbs_up_daemon: mission approved (+100xp)",
            "cognitive_core: quantum problem solver active",
            "military_salute: honor protocol verified",
            "victory_groove: bpm 128 - audio sync ok",
            "zen_meditation: tachyon core calming 100%",
            "shield_generator: hexagonal lattice active",
            "flight_avionics: mach 2.4 vector engaged",
            "repulsor_flux: 1.21 gigawatts output ok",
            "IDEA 11: task queue as choreography",
            "running world_indexer",
            "running string_solver",
            "running gesture_compiler****** ok",
            "IDEA 12: puppets that dream when idle",
            "lifting: quantum tachyon flux (96GB)",
            "done - 96GB in 2.3s",
            "lifting: compact crystalline heap (1.8G)",
            "done - 1.8G in 1.5s",
            "lifting: train epoch 12/40 (512 batches)",
            "done - 512 batches in 5.2s",
            "running puppet_daemon******* ok"
        ]
        self.log_scroll_idx = 0
        self.last_log_time = time.time()
        self.cursor_blink = True
        self.last_blink_time = time.time()

    def _load_sprites(self):
        """Loads and pre-scales suit sprites."""
        disp_w = config.AVATAR_WIDTH
        disp_h = config.AVATAR_HEIGHT

        # Alien Sprites
        alien_idle = cv2.imread(os.path.join(config.ASSETS_DIR, "alien_suit_idle.png"), cv2.IMREAD_UNCHANGED)
        alien_point = cv2.imread(os.path.join(config.ASSETS_DIR, "alien_suit_pointing.png"), cv2.IMREAD_UNCHANGED)
        
        # Iron Man Sprites
        im_idle = cv2.imread(os.path.join(config.ASSETS_DIR, "ironman_idle.png"), cv2.IMREAD_UNCHANGED)
        im_point = cv2.imread(os.path.join(config.ASSETS_DIR, "ironman_pointing.png"), cv2.IMREAD_UNCHANGED)

        # Mech Sprite
        mech_idle = cv2.imread(os.path.join(config.ASSETS_DIR, "robot_idle.png"), cv2.IMREAD_UNCHANGED)

        if alien_idle is not None:
            self.sprites["alien_idle"] = cv2.resize(alien_idle, (disp_w, disp_h), interpolation=cv2.INTER_AREA)
        if alien_point is not None:
            self.sprites["alien_pointing"] = cv2.resize(alien_point, (disp_w, disp_h), interpolation=cv2.INTER_AREA)
            
        if im_idle is not None:
            self.sprites["ironman_idle"] = cv2.resize(im_idle, (disp_w, disp_h), interpolation=cv2.INTER_AREA)
        if im_point is not None:
            self.sprites["ironman_pointing"] = cv2.resize(im_point, (disp_w, disp_h), interpolation=cv2.INTER_AREA)
            
        if mech_idle is not None:
            self.sprites["mech_idle"] = cv2.resize(mech_idle, (disp_w, disp_h), interpolation=cv2.INTER_AREA)

        print(f"[Visuals] Loaded sprites ({disp_w}x{disp_h}): {list(self.sprites.keys())}")

    def render(self, frame, hand_data, show_hud=True):
        t = time.time() - self.start_time
        out = frame.copy()

        # Update terminal scrolling
        if time.time() - self.last_log_time > 0.7:
            self.log_scroll_idx = (self.log_scroll_idx + 1) % len(self.terminal_lines)
            self.last_log_time = time.time()

        if time.time() - self.last_blink_time > 0.4:
            self.cursor_blink = not self.cursor_blink
            self.last_blink_time = time.time()

        # Track gesture transitions
        curr_gesture = hand_data.get("gesture", "IDLE")
        if curr_gesture != self.last_action:
            self.last_action = curr_gesture
            self.action_start_time = time.time()

        # Update Avatar Dynamic Hand-Following Physics
        self._update_avatar_physics(hand_data, t)

        # 1. Draw Glowing Neural Puppet Strings
        if hand_data["detected"]:
            self._draw_puppet_strings(out, hand_data, t)

        # 2. Draw Large Glassy Holographic Suit with Human Action Kinematics
        if show_hud:
            self._draw_avatar_hud(out, hand_data, t)

        # 3. Draw Glowing Fingertip and Palm Orbs
        if hand_data["detected"]:
            self._draw_hand_orbs(out, hand_data, t)

        # 4. Draw Cyberpunk Terminal HUD Window
        if show_hud:
            self._draw_terminal_hud(out, hand_data, t)

        # 5. Draw Live Gesture Feedback Banner
        self._draw_gesture_banner(out, hand_data)

        return out

    def _update_avatar_physics(self, hand_data, t):
        """Dynamic Digital Puppet Physics: suit follows hand across the screen."""
        hover_offset = math.sin(t * 2.5) * 8.0

        gesture = hand_data.get("gesture", "IDLE")

        if hand_data["detected"] and hand_data["palm"] is not None:
            palm_x, palm_y = hand_data["palm"]

            # When RUNNING: suit sprints and matches hand movement faster
            if gesture == "RUNNING":
                # Stride vertical bounce
                run_bounce = abs(math.sin(t * 14.0)) * 20.0
                target_y = palm_y + run_bounce
                # Sprints forward alongside hand
                target_x = palm_x - int(config.AVATAR_WIDTH * 0.65)
                k = 0.30
                damp = 0.70
            elif gesture == "JUMPING":
                # Athletic jump arc
                jump_phase = (time.time() - self.action_start_time) * 3.0
                jump_y = -math.sin(min(math.pi, jump_phase)) * 160.0
                target_y = palm_y + jump_y
                target_x = palm_x - int(config.AVATAR_WIDTH * 0.75)
                k = 0.28
                damp = 0.72
            elif gesture == "PUNCHING":
                # Forward thrust
                target_y = palm_y
                target_x = palm_x - int(config.AVATAR_WIDTH * 0.60) + (15.0 if math.sin(t * 16.0) > 0 else -10.0)
                k = 0.35
                damp = 0.65
            else:
                target_y = palm_y + hover_offset
                desired_x = palm_x - int(config.AVATAR_WIDTH * 0.75)
                target_x = desired_x
                k = 0.22
                damp = 0.75

            # Screen bounds clamping
            target_y = max(int(config.AVATAR_HEIGHT * 0.40), min(self.h - int(config.AVATAR_HEIGHT * 0.40), target_y))
            target_x = max(int(config.AVATAR_WIDTH * 0.45), min(self.w - int(config.AVATAR_WIDTH * 0.45), target_x))
        else:
            target_x = float(self.w * 0.24)
            target_y = float(self.h * 0.50) + hover_offset
            k = 0.08
            damp = 0.85

        self.avatar_vel_x = (self.avatar_vel_x + (target_x - self.avatar_current_x) * k) * damp
        self.avatar_vel_y = (self.avatar_vel_y + (target_y - self.avatar_current_y) * k) * damp
        self.avatar_current_x += self.avatar_vel_x
        self.avatar_current_y += self.avatar_vel_y

        # Velocity tilt
        if gesture == "RUNNING":
            self.avatar_tilt = -14.0 # Forward sprinter lean!
        elif gesture == "FLYING":
            self.avatar_tilt = -22.0 # Supersonic flight angle
        elif gesture == "DANCING":
            self.avatar_tilt = math.sin(t * 7.0) * 14.0 # Groovy dance sway!
        elif gesture == "THINKING":
            self.avatar_tilt = 6.0 # Pondering head tilt
        elif gesture == "SALUTE":
            self.avatar_tilt = 0.0 # Rigid military attention
        elif gesture == "THUMBS_UP":
            self.avatar_tilt = -4.0 # Confident chest-out pose
        else:
            self.avatar_tilt = np.clip(self.avatar_vel_x * -0.6, -10.0, 10.0)

    def _draw_hand_orbs(self, frame, hand_data, t):
        """Draws glowing cyan and golden orbs on fingertips and palm."""
        overlay = frame.copy()
        pulse = math.sin(t * 8.0) * 2.0

        points = hand_data["fingertips"] + [hand_data["palm"]]

        for i, pt in enumerate(points):
            px, py = int(pt[0]), int(pt[1])
            is_palm = (i == len(points) - 1)
            glow_r = int((22 + pulse) if not is_palm else (32 + pulse))
            outer_r = int((38 + pulse*2) if not is_palm else (52 + pulse*2))

            cv2.circle(overlay, (px, py), outer_r, (255, 210, 30), -1, cv2.LINE_AA)
            cv2.circle(overlay, (px, py), glow_r, (255, 245, 80), -1, cv2.LINE_AA)

        cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)

        for i, pt in enumerate(points):
            px, py = int(pt[0]), int(pt[1])
            is_palm = (i == len(points) - 1)
            core_r = 7 if not is_palm else 11

            cv2.circle(frame, (px, py), core_r + 3, (40, 210, 255), 1, cv2.LINE_AA)
            cv2.circle(frame, (px, py), core_r + 1, (255, 240, 80), -1, cv2.LINE_AA)
            cv2.circle(frame, (px, py), core_r, (255, 255, 255), -1, cv2.LINE_AA)

            if is_palm:
                cv2.drawMarker(frame, (px, py), (40, 220, 255), cv2.MARKER_CROSS, 24, 1, cv2.LINE_AA)

    def _draw_puppet_strings(self, frame, hand_data, t):
        """Draws dynamic cubic Bézier golden-cyan neural strings from hand to suit joints."""
        ax = int(self.avatar_current_x)
        ay = int(self.avatar_current_y)
        h_half = config.AVATAR_HEIGHT // 2

        avatar_targets = [
            (ax - 65, ay - int(h_half * 0.45)),  # Left shoulder
            (ax, ay - int(h_half * 0.32)),       # Quantum Core
            (ax + 65, ay - int(h_half * 0.45)),  # Right shoulder
            (ax - 95, ay + int(h_half * 0.10)),  # Left palm
            (ax + 95, ay + int(h_half * 0.10)),  # Right palm
            (ax, ay - int(h_half * 0.65))        # Helmet crest
        ]

        fingertips = hand_data["fingertips"]
        palm = hand_data["palm"]
        all_sources = fingertips + [palm]

        overlay = frame.copy()

        for s_idx, src in enumerate(all_sources):
            sx, sy = float(src[0]), float(src[1])
            target = avatar_targets[s_idx % len(avatar_targets)]
            tx, ty = float(target[0]), float(target[1])

            dx = tx - sx
            dy = ty - sy
            dist = math.hypot(dx, dy)

            sag = max(10.0, config.STRING_SAG * (1.0 - min(0.65, dist / self.w)))

            num_tendrils = 3 if s_idx < 5 else 4
            for tendril in range(num_tendrils):
                offset_sag = sag + (tendril - 1) * 10.0
                wave_phase = t * config.STRING_WAVE_SPEED + tendril * 0.7 + s_idx * 0.3
                wave_amp = 4.5 if hand_data["velocity"] > 0.05 else 1.8

                p0 = (sx, sy)
                p1 = (sx + dx * 0.35, sy + dy * 0.35 + offset_sag)
                p2 = (sx + dx * 0.70, sy + dy * 0.70 + offset_sag * 0.7)
                p3 = (tx, ty)

                num_steps = 22
                curve_pts = []
                for step in range(num_steps + 1):
                    s = step / float(num_steps)
                    bx = ((1-s)**3 * p0[0] + 
                          3*(1-s)**2 * s * p1[0] + 
                          3*(1-s) * s**2 * p2[0] + 
                          s**3 * p3[0])
                    by = ((1-s)**3 * p0[1] + 
                          3*(1-s)**2 * s * p1[1] + 
                          3*(1-s) * s**2 * p2[1] + 
                          s**3 * p3[1])
                    
                    wave = math.sin(wave_phase - s * 9.0) * math.sin(s * math.pi) * wave_amp
                    by += wave
                    curve_pts.append([int(bx), int(by)])

                pts_np = np.array(curve_pts, np.int32).reshape((-1, 1, 2))
                cv2.polylines(overlay, [pts_np], False, (255, 190, 30), 3, cv2.LINE_AA)
                cv2.polylines(frame, [pts_np], False, (160, 240, 255), 1, cv2.LINE_AA)

        cv2.addWeighted(overlay, 0.42, frame, 0.58, 0, frame)

    def _draw_avatar_hud(self, frame, hand_data, t):
        """Renders the Large Glassy Alien Suit with Human Action Animation Kinematics."""
        ax = int(self.avatar_current_x)
        ay = int(self.avatar_current_y)
        gesture = hand_data["gesture"]
        status = hand_data["status_label"]

        # Select base sprite
        raised_arm_gestures = ["WAVING", "FLYING", "SALUTE", "THUMBS_UP", "THINKING"]
        if self.avatar_mode == "alien":
            sprite_key = "alien_pointing" if gesture in raised_arm_gestures else "alien_idle"
        elif self.avatar_mode == "ironman":
            sprite_key = "ironman_pointing" if gesture in raised_arm_gestures else "ironman_idle"
        else:
            sprite_key = "mech_idle"

        base_sprite = self.sprites.get(sprite_key, None)
        if base_sprite is None:
            return

        sw, sh = config.AVATAR_WIDTH, config.AVATAR_HEIGHT
        sprite = base_sprite.copy()

        # ==============================================================
        # HUMAN ACTION PROCEDURAL KINEMATICS & VFX OVERLAYS
        # ==============================================================
        effects_overlay = frame.copy()

        # 1. RUNNING ACTION
        if gesture == "RUNNING":
            # Speed lines streaming past runner
            for i in range(8):
                line_y = int(ay - sh * 0.4 + i * 65 + math.sin(t * 18 + i) * 20)
                line_len = 160 + int(math.sin(t * 15 + i) * 60)
                line_x_start = ax - sw // 2 - 140 - int((i * 45 + t * 600) % 280)
                line_x_end = line_x_start + line_len
                cv2.line(effects_overlay, (line_x_start, line_y), (line_x_end, line_y), 
                         (255, 230, 40), 2, cv2.LINE_AA)

            # Ground thruster spark bursts under feet
            stride_phase = math.sin(t * 14.0)
            for foot_x in [ax - 50 + int(stride_phase * 40), ax + 50 - int(stride_phase * 40)]:
                foot_y = ay + sh // 2 - 10
                cv2.ellipse(effects_overlay, (foot_x, foot_y), (35, 12), 0, 0, 360, (255, 210, 30), 2, cv2.LINE_AA)
                cv2.circle(effects_overlay, (foot_x, foot_y), 9, (255, 255, 255), -1, cv2.LINE_AA)

            # Cadence banner
            cv2.putText(effects_overlay, "SPRINT: 24.8 KM/H // CADENCE: 180 SPM", 
                        (ax - 130, ay + sh // 2 + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 230, 40), 1, cv2.LINE_AA)

        # 2. BOXING / PUNCHING ACTION
        elif gesture == "PUNCHING":
            punch_cycle = math.sin(t * 16.0)
            is_right_fist = (punch_cycle > 0)
            fist_x = ax + (sw // 2 + 20 if is_right_fist else -sw // 2 - 20)
            fist_y = ay - int(sh * 0.08)
            r_burst = int(abs(punch_cycle) * 70)

            if r_burst > 15:
                cv2.circle(effects_overlay, (fist_x, fist_y), r_burst, (255, 220, 0), 3, cv2.LINE_AA)
                cv2.circle(effects_overlay, (fist_x, fist_y), r_burst // 2, (255, 255, 255), 2, cv2.LINE_AA)
                for deg in range(0, 360, 40):
                    rad = math.radians(deg)
                    x1 = int(fist_x + math.cos(rad) * (r_burst * 0.5))
                    y1 = int(fist_y + math.sin(rad) * (r_burst * 0.5))
                    x2 = int(fist_x + math.cos(rad) * (r_burst * 1.3))
                    y2 = int(fist_y + math.sin(rad) * (r_burst * 1.3))
                    cv2.line(effects_overlay, (x1, y1), (x2, y2), (255, 255, 200), 2, cv2.LINE_AA)
                cv2.putText(effects_overlay, "950N COMBAT IMPACT!", (fist_x - 60, fist_y - r_burst - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 240, 80), 2, cv2.LINE_AA)

        # 3. JUMPING ACTION
        elif gesture == "JUMPING":
            # Giant vertical thruster columns firing down into ground
            for bx in [ax - 55, ax + 55]:
                by = ay + sh // 2 - 15
                for flame_y in range(by + 10, min(self.h - 5, by + 140), 10):
                    rad = max(4, 26 - (flame_y - by) // 5)
                    cv2.circle(effects_overlay, (bx, flame_y), rad, (255, 220, 30), -1, cv2.LINE_AA)
                    cv2.circle(effects_overlay, (bx, flame_y), rad // 2, (255, 255, 255), -1, cv2.LINE_AA)
            cv2.ellipse(effects_overlay, (ax, min(self.h - 15, ay + sh // 2 + 100)), (120, 25), 0, 0, 360, (255, 210, 40), 2, cv2.LINE_AA)

        # 4. WAVING ACTION
        elif gesture == "WAVING":
            wx = ax + sw // 2 - 10
            wy = ay - sh // 2 + 30
            sparkle_r = int(24 + math.sin(t * 12.0) * 8)
            cv2.circle(effects_overlay, (wx, wy), sparkle_r, (255, 230, 40), 2, cv2.LINE_AA)
            cv2.circle(effects_overlay, (wx, wy), sparkle_r // 2, (255, 255, 255), -1, cv2.LINE_AA)
            # Friendly greeting badge
            cv2.rectangle(effects_overlay, (wx + 20, wy - 22), (wx + 130, wy + 16), (15, 20, 35), -1)
            cv2.rectangle(effects_overlay, (wx + 20, wy - 22), (wx + 130, wy + 16), (255, 220, 40), 1, cv2.LINE_AA)
            cv2.putText(effects_overlay, "HELLO! :)", (wx + 28, wy + 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 245, 90), 2, cv2.LINE_AA)

        # 5. THUMBS UP ACTION (Approval / Mission Passed)
        elif gesture == "THUMBS_UP":
            hx = ax + sw // 2 + 25
            hy = ay - int(sh * 0.12)
            # Radiant golden starburst
            for ray_deg in range(0, 360, 30):
                rad = math.radians(ray_deg + t * 40.0)
                rx1 = int(hx + math.cos(rad) * 20)
                ry1 = int(hy + math.sin(rad) * 20)
                rx2 = int(hx + math.cos(rad) * 55)
                ry2 = int(hy + math.sin(rad) * 55)
                cv2.line(effects_overlay, (rx1, ry1), (rx2, ry2), (255, 240, 60), 2, cv2.LINE_AA)
            cv2.circle(effects_overlay, (hx, hy), 28, (255, 210, 30), -1, cv2.LINE_AA)
            cv2.circle(effects_overlay, (hx, hy), 22, (255, 255, 255), -1, cv2.LINE_AA)
            cv2.putText(effects_overlay, "UP", (hx - 14, hy + 6), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (20, 20, 20), 2, cv2.LINE_AA)
            # Big holographic approval seal
            cv2.rectangle(effects_overlay, (ax - 150, ay - sh // 2 - 85), (ax + 150, ay - sh // 2 - 45), (10, 25, 15), -1)
            cv2.rectangle(effects_overlay, (ax - 150, ay - sh // 2 - 85), (ax + 150, ay - sh // 2 - 45), (60, 255, 120), 2, cv2.LINE_AA)
            cv2.putText(effects_overlay, "[ MISSION APPROVED! +100 XP ]", (ax - 138, ay - sh // 2 - 58),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.52, (80, 255, 140), 2, cv2.LINE_AA)

        # 6. DEEP THINKING / BRAINSTORM ACTION
        elif gesture == "THINKING":
            # Quantum idea lightbulb above helmet
            bx = ax
            by = ay - sh // 2 - 25
            bulb_r = int(22 + math.sin(t * 8.0) * 4)
            cv2.circle(effects_overlay, (bx, by), bulb_r + 6, (255, 240, 80), 2, cv2.LINE_AA)
            cv2.circle(effects_overlay, (bx, by), bulb_r, (255, 255, 180), -1, cv2.LINE_AA)
            # Orbiting equations
            equations = ["E=mc^2", "f(x)=s(Wx+b)", "V*B=0", "Psi(r,t)"]
            for eq_i, eq_txt in enumerate(equations):
                eq_angle = math.radians(eq_i * 90 + t * 45.0)
                eq_x = int(ax + math.cos(eq_angle) * 110)
                eq_y = int(by + math.sin(eq_angle) * 45)
                cv2.rectangle(effects_overlay, (eq_x - 38, eq_y - 12), (eq_x + 38, eq_y + 12), (20, 30, 50), -1)
                cv2.rectangle(effects_overlay, (eq_x - 38, eq_y - 12), (eq_x + 38, eq_y + 12), (40, 210, 255), 1, cv2.LINE_AA)
                cv2.putText(effects_overlay, eq_txt, (eq_x - 34, eq_y + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (180, 240, 255), 1, cv2.LINE_AA)

        # 7. MILITARY SALUTE ACTION
        elif gesture == "SALUTE":
            # Tactical HUD lock reticle
            sx = ax + sw // 2 - 30
            sy = ay - sh // 2 + 50
            cv2.circle(effects_overlay, (sx, sy), 30, (40, 220, 255), 2, cv2.LINE_AA)
            cv2.drawMarker(effects_overlay, (sx, sy), (255, 240, 80), cv2.MARKER_CROSS, 44, 2, cv2.LINE_AA)
            # Honor banner
            cv2.rectangle(effects_overlay, (ax - 160, ay - sh // 2 - 80), (ax + 160, ay - sh // 2 - 45), (15, 20, 35), -1)
            cv2.rectangle(effects_overlay, (ax - 160, ay - sh // 2 - 80), (ax + 160, ay - sh // 2 - 45), (255, 210, 40), 2, cv2.LINE_AA)
            cv2.putText(effects_overlay, "RESPECT // AT EASE COMMANDER", (ax - 145, ay - sh // 2 - 58),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 235, 90), 2, cv2.LINE_AA)

        # 8. DANCING ACTION
        elif gesture == "DANCING":
            # Floating musical notes
            for ni in range(5):
                nx = int(ax + (ni - 2.0) * 75 + math.sin(t * 6 + ni) * 20)
                ny = int(ay - sh * 0.35 - (t * 80 + ni * 40) % 130)
                if 0 <= nx < self.w and 0 <= ny < self.h:
                    cv2.circle(effects_overlay, (nx, ny), 10, (255, 220, 40), -1, cv2.LINE_AA)
                    cv2.line(effects_overlay, (nx + 8, ny), (nx + 8, ny - 26), (255, 255, 255), 3, cv2.LINE_AA)
                    cv2.line(effects_overlay, (nx + 8, ny - 26), (nx + 18, ny - 22), (255, 255, 255), 3, cv2.LINE_AA)
            # Dynamic floor equalizer audio bars
            eq_base_y = min(self.h - 10, ay + sh // 2 + 30)
            for bar_i in range(16):
                bar_x = ax - 120 + bar_i * 16
                bar_h = int(abs(math.sin(t * 12.0 + bar_i * 0.5)) * 38) + 6
                cv2.rectangle(effects_overlay, (bar_x, eq_base_y - bar_h), (bar_x + 10, eq_base_y), 
                              (255, int(150 + bar_i * 6), 40), -1)

        # 9. MEDITATING ACTION
        elif gesture == "MEDITATING":
            # Sacred geometry concentric mandala rings
            core_cy = ay - int(sh * 0.16)
            for m_rad in [65, 100, 140, 180]:
                cv2.circle(effects_overlay, (ax, core_cy), m_rad, (255, 230, 50), 1, cv2.LINE_AA)
            cv2.ellipse(effects_overlay, (ax, core_cy), (155, 155), t * 30, 0, 360, (255, 245, 100), 2, cv2.LINE_AA)
            cv2.putText(effects_overlay, "ZEN PROTOCOL: 100% CALM", (ax - 110, core_cy + 195),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.44, (255, 240, 80), 1, cv2.LINE_AA)

        # 10. DEFENSIVE SHIELD ACTION
        elif gesture == "DEFENSIVE_SHIELD":
            # Expanding hexagonal forcefield barrier
            hex_pts = []
            shield_r = int(sw * 0.65)
            for h_deg in range(0, 360, 60):
                h_rad = math.radians(h_deg + t * 25.0)
                hx = int(ax + math.cos(h_rad) * shield_r)
                hy = int(ay + math.sin(h_rad) * shield_r * 1.25)
                hex_pts.append([hx, hy])
            pts_shield = np.array(hex_pts, np.int32).reshape((-1, 1, 2))
            cv2.polylines(effects_overlay, [pts_shield], True, (255, 240, 60), 3, cv2.LINE_AA)
            cv2.fillPoly(effects_overlay, [pts_shield], (255, 200, 30))

        # 11. SUPERSONIC FLIGHT ACTION
        elif gesture == "FLYING":
            # Supersonic Mach vapor cone
            cone_w = int(sw * 0.75)
            cv2.ellipse(effects_overlay, (ax, ay - int(sh * 0.3)), (cone_w, 35), -22.0, 0, 360, (255, 240, 100), 2, cv2.LINE_AA)
            # Twin ion engine exhaust trails
            for ex in [ax - 45, ax + 45]:
                ey = ay + sh // 2 - 20
                for trail_i in range(12):
                    ty = ey + trail_i * 12
                    tx = ex + int(math.sin(t * 20 + trail_i) * 8)
                    cv2.circle(effects_overlay, (tx, ty), max(2, 16 - trail_i), (255, 210, 30), -1, cv2.LINE_AA)
                    cv2.circle(effects_overlay, (tx, ty), max(1, 8 - trail_i // 2), (255, 255, 255), -1, cv2.LINE_AA)

        # 12. REPULSOR BLAST ACTION
        elif gesture == "OPEN_HAND":
            # Dual palm repulsor bursts & electric arcs
            for rx in [ax - int(sw * 0.38), ax + int(sw * 0.38)]:
                ry = ay + int(sh * 0.10)
                pulse_r = int(28 + math.sin(t * 15.0) * 8)
                cv2.circle(effects_overlay, (rx, ry), pulse_r, (255, 220, 40), 3, cv2.LINE_AA)
                cv2.circle(effects_overlay, (rx, ry), pulse_r // 2, (255, 255, 255), -1, cv2.LINE_AA)
            core_cy = ay - int(sh * 0.16)
            cv2.circle(effects_overlay, (ax, core_cy), 48, (255, 240, 60), 3, cv2.LINE_AA)
            cv2.circle(effects_overlay, (ax, core_cy), 25, (255, 255, 255), -1, cv2.LINE_AA)

        # Blend effects overlay
        cv2.addWeighted(effects_overlay, 0.40, frame, 0.60, 0, frame)

        # Rotate sprite according to avatar_tilt
        if abs(self.avatar_tilt) > 0.5:
            M_rot = cv2.getRotationMatrix2D((sw // 2, sh // 2), self.avatar_tilt, 1.0)
            sprite = cv2.warpAffine(sprite, M_rot, (sw, sh), flags=cv2.INTER_LINEAR)

        # Composite Big Suit with Glass Translucency
        top_left_x = ax - sw // 2
        top_left_y = ay - sh // 2

        x1 = max(0, top_left_x)
        y1 = max(0, top_left_y)
        x2 = min(self.w, top_left_x + sw)
        y2 = min(self.h, top_left_y + sh)

        sx1 = x1 - top_left_x
        sy1 = y1 - top_left_y
        sx2 = sx1 + (x2 - x1)
        sy2 = sy1 + (y2 - y1)

        if x2 > x1 and y2 > y1:
            crop_sprite = sprite[sy1:sy2, sx1:sx2]
            alpha = (crop_sprite[:, :, 3] / 255.0)[:, :, None]
            flicker = 0.96 + 0.04 * math.sin(t * 18.0)
            alpha = alpha * flicker

            roi = frame[y1:y2, x1:x2].astype(float)
            rgb = crop_sprite[:, :, :3].astype(float)

            if gesture == "OPEN_HAND":
                rgb[:, :, 0] = np.clip(rgb[:, :, 0] * 1.3, 0, 255)
                rgb[:, :, 1] = np.clip(rgb[:, :, 1] * 1.25, 0, 255)

            blended = roi * (1.0 - alpha) + rgb * alpha
            frame[y1:y2, x1:x2] = blended.astype(np.uint8)

        # Top HUD Status Banner
        hud_box_w = 330
        hud_box_h = 48
        bx1 = ax - hud_box_w // 2
        by1 = max(10, ay - sh // 2 - 55)
        bx2 = bx1 + hud_box_w
        by2 = by1 + hud_box_h

        if bx1 >= 0 and bx2 <= self.w and by1 >= 0 and by2 <= self.h:
            hud_roi = frame[by1:by2, bx1:bx2].copy()
            cv2.rectangle(hud_roi, (0, 0), (hud_box_w, hud_box_h), config.COLOR_HUD_BG, -1)
            cv2.addWeighted(hud_roi, 0.78, frame[by1:by2, bx1:bx2], 0.22, 0, frame[by1:by2, bx1:bx2])
            cv2.rectangle(frame, (bx1, by1), (bx2, by2), (255, 200, 40), 1, cv2.LINE_AA)

            avatar_label = "A.L.I.E.N. // HUMAN BRIDGE" if self.avatar_mode == "alien" else f"AGENT: {config.AGENT_NAME}"
            cv2.putText(frame, avatar_label, (bx1 + 12, by1 + 18), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.44, (40, 210, 255), 1, cv2.LINE_AA)

            status_color = (255, 240, 100) if gesture in ["RUNNING", "FLYING", "JUMPING"] else (80, 240, 120)
            cv2.putText(frame, f"{status}", (bx1 + 12, by1 + 38), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, status_color, 1, cv2.LINE_AA)

        # Bottom Telemetry Bar
        btn_y = min(self.h - 20, ay + sh // 2 + 20)
        telemetry_txt = f"CADENCE: {180 if gesture == 'RUNNING' else 0} SPM // FLUX: {hand_data['velocity']*60:.1f} TW // SYNC: 99.8%"
        cv2.putText(frame, telemetry_txt, (max(10, ax - 140), min(self.h - 5, btn_y + 18)), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.34, (160, 200, 220), 1, cv2.LINE_AA)

    def _draw_terminal_hud(self, frame, hand_data, t):
        """Renders the authentic futuristic terminal HUD window on the right side."""
        tw = 380
        th = 430
        tx1 = self.w - tw - 30
        ty1 = 110
        tx2 = tx1 + tw
        ty2 = ty1 + th

        term_roi = frame[ty1:ty2, tx1:tx2].copy()
        cv2.rectangle(term_roi, (0, 0), (tw, th), config.COLOR_HUD_BG, -1)
        cv2.addWeighted(term_roi, 0.82, frame[ty1:ty2, tx1:tx2], 0.18, 0, frame[ty1:ty2, tx1:tx2])

        cv2.rectangle(frame, (tx1, ty1), (tx2, ty2), (230, 230, 240), 1, cv2.LINE_AA)
        cv2.line(frame, (tx1, ty1 + 46), (tx2, ty1 + 46), (120, 140, 160), 1, cv2.LINE_AA)
        cv2.line(frame, (tx1, ty1 + 78), (tx2, ty1 + 78), (120, 140, 160), 1, cv2.LINE_AA)

        cv2.putText(frame, f"{config.USER_TAG} human_ops --watch", (tx1 + 14, ty1 + 22), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.44, (40, 180, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, "[ok] neural puppet bridge - linked", (tx1 + 14, ty1 + 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (230, 230, 230), 1, cv2.LINE_AA)

        cv2.putText(frame, f"status: {hand_data['hud_state']}", (tx1 + 14, ty1 + 66), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.44, (40, 180, 255), 1, cv2.LINE_AA)

        max_visible_lines = 14
        start = self.log_scroll_idx
        y_offset = ty1 + 102

        for i in range(max_visible_lines):
            line_idx = (start + i) % len(self.terminal_lines)
            line = self.terminal_lines[line_idx]

            text_color = (200, 210, 220)
            if "stride" in line or "boxing" in line or "vertical" in line or "greeting" in line or "victory" in line:
                text_color = (80, 240, 120)
            elif "IDEA" in line:
                text_color = (40, 180, 255)
            elif "done" in line:
                text_color = (100, 240, 130)
            elif "lifting" in line:
                text_color = (255, 230, 90)

            prefix = "$" if i % 2 == 0 else "*"
            cv2.putText(frame, f"{prefix} {line}", (tx1 + 14, y_offset), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.36, text_color, 1, cv2.LINE_AA)
            y_offset += 22

        if self.cursor_blink:
            cv2.putText(frame, "_", (tx1 + 14, y_offset), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (40, 180, 255), 1, cv2.LINE_AA)

        cv2.putText(frame, "[Q] Quit  [A] Toggle Avatar  [H] Toggle HUD  [F] Fullscreen", 
                    (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 200, 220), 1, cv2.LINE_AA)

    def _draw_gesture_banner(self, frame, hand_data):
        """Displays real-time human command feedback banner at top center."""
        if not hand_data["detected"]:
            return

        gesture = hand_data["gesture"]
        text = f"HUMAN COMMAND: >>> {gesture} <<<"

        bx = self.w // 2 - 210
        by = 18
        bw = 420
        bh = 34

        banner_roi = frame[by:by+bh, bx:bx+bw].copy()
        cv2.rectangle(banner_roi, (0, 0), (bw, bh), (10, 15, 25), -1)
        cv2.addWeighted(banner_roi, 0.75, frame[by:by+bh, bx:bx+bw], 0.25, 0, frame[by:by+bh, bx:bx+bw])
        cv2.rectangle(frame, (bx, by), (bx + bw, by + bh), (255, 220, 40), 1, cv2.LINE_AA)

        col = (255, 240, 80) if gesture in ["RUNNING", "PUNCHING", "JUMPING", "WAVING", "DANCING", "THUMBS_UP", "THINKING", "SALUTE"] else (80, 240, 120)
        cv2.putText(frame, text, (bx + 18, by + 23), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.50, col, 1, cv2.LINE_AA)

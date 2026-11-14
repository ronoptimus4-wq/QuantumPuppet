"""
Main Application: Stark OS Gestural Agentic Iron Man Animation.
Run this script in VS Code with Python 3.10+ to experience the real-time hand-puppet animation.
"""
import time
import cv2
import config
from camera import ThreadedCamera
from tracker import HandTracker
from visuals import VisualEngine

def main():
    print("=" * 72)
    print("  ALIEN TECH & IRON MAN SUIT // GESTURAL HUMAN KINEMATICS ENGINE")
    print("=" * 72)
    print("  HUMAN FINGER COMMANDS:")
    print("    ✌️  [Walking / Scissors] -> RUNNING / SPRINTING (Lean, bounce, speed trails)")
    print("    👊 [Clenched Fist]       -> BOXING / PUNCHING (Rapid jab-cross, 950N shockwaves)")
    print("    🤘 [Rock On / Horns]     -> ATHLETIC JUMP (Vertical leap + ground rocket blast)")
    print("    👋 [Waving Hand]         -> WAVING HELLO (Arm raised, friendly HELLO greeting)")
    print("    👍 [Thumbs Up]           -> MISSION APPROVED (Approval seal, +100 XP stamp)")
    print("    👆 [L-Sign / To Chin]    -> DEEP THINKING (Quantum idea bulb & orbiting math)")
    print("    🤙 [Shaka / Hang Loose]  -> VICTORY DANCE (Rhythmic sway, notes & equalizer)")
    print("    👌 [OK Sign]             -> ZEN MEDITATION (Lotus levitation & mandala aura)")
    print("    🫱 [Blade Hand]          -> MILITARY SALUTE (Attention, brow salute & reticle)")
    print("    🤏 [Pinch]               -> DEFENSIVE SHIELD (Hexagonal forcefield dome)")
    print("    ☝️  [Pointing Finger]    -> SUPERSONIC FLIGHT (Banked dive & Mach vapor cone)")
    print("    🖐️  [Open Hand Steady]   -> REPULSOR BLAST (Dual palm beam & plasma discharge)")
    print("-" * 72)
    print("  Keyboard Shortcuts:")
    print("    [Q] / [ESC] - Quit Application")
    print("    [A]         - Toggle Avatar (Glassy Alien <-> Iron Man <-> Cyber Mech)")
    print("    [H]         - Toggle HUD & Terminal Overlay")
    print("    [F]         - Toggle Fullscreen Window")
    print("    [S]         - Save High-Res Screenshot")
    print("=" * 72)

    # Initialize Camera, Hand Tracker, and Visual Renderer
    cam = ThreadedCamera(
        camera_index=config.CAMERA_INDEX, 
        width=config.FRAME_WIDTH, 
        height=config.FRAME_HEIGHT
    )
    
    tracker = HandTracker(model_path=config.MODEL_PATH)
    engine = VisualEngine(width=config.FRAME_WIDTH, height=config.FRAME_HEIGHT)

    window_name = "Stark OS // Gestural Agentic Iron Man"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, config.FRAME_WIDTH, config.FRAME_HEIGHT)

    show_hud = True
    is_fullscreen = False

    fps_count = 0
    fps_time = time.time()
    fps_display = "60 FPS"

    try:
        while True:
            ret, frame = cam.read()
            if not ret or frame is None:
                time.sleep(0.005)
                continue

            # Ensure frame matches target size
            if frame.shape[1] != config.FRAME_WIDTH or frame.shape[0] != config.FRAME_HEIGHT:
                frame = cv2.resize(frame, (config.FRAME_WIDTH, config.FRAME_HEIGHT))

            # 1. Track Hand with Ultra-Sensitive MediaPipe Pipeline
            hand_data = tracker.process(frame)

            # 2. Render Animation (Strings, Orbs, Avatar, Stark HUD, Terminal)
            output = engine.render(frame, hand_data, show_hud=show_hud)

            # 3. Calculate & Display FPS
            fps_count += 1
            if time.time() - fps_time >= 1.0:
                fps_display = f"{fps_count} FPS"
                fps_count = 0
                fps_time = time.time()

            # Render FPS in top-right corner
            cv2.putText(output, fps_display, (config.FRAME_WIDTH - 110, 32), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 120), 1, cv2.LINE_AA)

            # Display Frame
            cv2.imshow(window_name, output)

            # Check if user clicked window 'X' close button
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                print("[Main] Window closed by user.")
                break

            # Key Handling
            key = cv2.waitKey(1) & 0xFF
            if key in [ord('q'), ord('Q'), 27]: # 27 is ESC
                print("[Main] Exiting...")
                break
            elif key in [ord('a'), ord('A')]:
                modes = ["alien", "ironman", "mech"]
                current_idx = modes.index(engine.avatar_mode) if engine.avatar_mode in modes else 0
                engine.avatar_mode = modes[(current_idx + 1) % len(modes)]
                print(f"[Main] Switched avatar mode to: {engine.avatar_mode.upper()}")
            elif key in [ord('h'), ord('H')]:
                show_hud = not show_hud
                print(f"[Main] HUD visibility: {show_hud}")
            elif key in [ord('f'), ord('F')]:
                is_fullscreen = not is_fullscreen
                prop = cv2.WINDOW_FULLSCREEN if is_fullscreen else cv2.WINDOW_NORMAL
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, prop)
            elif key in [ord('s'), ord('S')]:
                shot_name = f"screenshot_{int(time.time())}.png"
                cv2.imwrite(shot_name, output)
                print(f"[Main] Screenshot saved to: {shot_name}")

    except KeyboardInterrupt:
        print("[Main] Interrupted by user.")
    finally:
        cam.release()
        tracker.close()
        cv2.destroyAllWindows()
        print("[Main] Clean shutdown complete.")

if __name__ == "__main__":
    main()

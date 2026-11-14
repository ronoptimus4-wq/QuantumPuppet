# A.L.I.E.N. // Gestural Quantum Puppet Animation

An ultra-responsive, real-time hand-puppet animation system inspired by the viral *"This Is What AI Agentic Coding Looks Like"* demo. Customized with a **Glassy Bluish Alien-Tech Suit Avatar**, **Stark OS / Quantum HUD**, and **3D-Invariant Hand Following**.

---

## 🚀 How to Run in VS Code

1. **Open the project folder in VS Code:**
   Open the folder `project x` in VS Code.

2. **Select your Python Interpreter:**
   - Press `Ctrl + Shift + P`
   - Type `Python: Select Interpreter`
   - Select your Python environment (Python 3.10+).

3. **Run the Application:**
   - Open `main.py`
   - Click the **Run** button (▶) in the top-right corner of VS Code, or open the integrated terminal (`Ctrl + ~`) and run:
     ```bash
     python main.py
     ```

---

## ✋ Human Action Finger Commands

The suit responds in real time to your finger commands, transforming into an expressive humanoid that performs realistic human actions:

| Finger Command | Human Action | Suit Animation & Visual Kinematics | Real-Time Telemetry |
| :--- | :--- | :--- | :--- |
| ✌️ **Walking / Scissors Fingers** *(Index + Middle extended)* | **Running / Sprinting** | Sprinter forward lean ($-14^\circ$), rapid stride bounce ($14\text{ Hz}$), streaming speed lines, dual foot thruster ground spark flares | `SPRINT: 24.8 KM/H // CADENCE: 180 SPM` |
| 👊 **Clenched Fist** *(All 5 fingers closed)* | **Boxing / Punching** | Rapid alternating left/right jab-cross punches, expanding kinetic impact shockwave rings, combat flash | `950N COMBAT IMPACT // JAB-CROSS` |
| 🤘 **Rock On / Horns** *(Index + Pinky extended up)* | **Athletic Jumping** | Deep crouch compression, vertical rocket launch arc ($-180\text{px}$), twin downward flame columns, landing cushion | `VERTICAL LEAP // APEX +180PX` |
| 👋 **Waving Hand** *(Open hand swaying side-to-side)* | **Waving Hello** | Right robotic arm raised high, smooth forearm sway, friendly floating `HELLO! :)` badge with star sparkles | `GREETING PROTOCOL // WAVE HELLO` |
| 👍 **Thumbs Up** *(Thumb up, 4 fingers curled)* | **Mission Approved** | Confident heroic chest-out pose, glowing golden robotic thumbs-up halo, huge `[ MISSION APPROVED! +100 XP ]` seal | `APPROVAL // MISSION APPROVED +100XP` |
| 👆 **L-Sign** *(Thumb + Index at 90°, fingers curled)* | **Deep Thinking** | Pondering head tilt, hand to visor/chin, floating quantum idea lightbulb, rotating formulas (`E=mc²`, `f(x)=σ(Wx+b)`) | `COGNITION // QUANTUM SOLVER ACTIVE` |
| 🤙 **Shaka / Hang Loose** *(Thumb + Pinky extended)* | **Victory Dance** | Groovy hip/shoulder disco sway ($7\text{ Hz}$), floating neon musical notes, bouncing audio frequency equalizer bars | `CELEBRATING // VICTORY GROOVE` |
| 👌 **OK Sign** *(Thumb + Index circle, 3 fingers open)* | **Zen Meditation** | Lotus levitation hover, sacred geometry concentric rotating mandala rings, gentle turquoise aura breathing pulse | `ZEN MEDITATION // BIOMETRIC CALM 100%` |
| 🫱 **Blade Hand** *(4 fingers straight together, thumb tucked)* | **Military Salute** | Rigid military attention posture, crisp salute to helmet brow, tactical HUD lock crosshair, `RESPECT // AT EASE` banner | `PROTOCOL // SALUTE AT EASE COMMANDER` |
| 🤏 **Pinch** *(Thumb + Index touching, fingers curled)* | **Defensive Shield** | Braced defensive stance, expanding crystalline hexagonal honeycombed forcefield bubble with deflection ripples | `DEFENSIVE BARRIER // ACTIVE SHIELD` |
| ☝️ **Pointing Finger** *(Index extended upward/forward)* | **Supersonic Flight** | Banked supersonic flight angle ($-22^\circ$), blue plasma ion exhaust trails, expanding Mach vapor condensation cone | `SUPERSONIC FLIGHT // MACH 2.4 VECTOR` |
| 🖐️ **Open Hand Steady** *(All 5 fingers spread wide)* | **Repulsor Blast** | Palms forward repulsor beam discharge with ionizing electric arcs and full-suit tachyon quantum core flare | `REPULSOR BURST // ENERGY 100%` |
| 🧍 **Relaxed / Idle** *(Hand steady or resting)* | **Idle Breathing** | Smooth hovering with gentle breathing bobbing, pulsing quantum singularity core | `IDLE HOVER // SYSTEM ONLINE` |

---

## ⌨️ Keyboard Controls

- **`Q`** or **`ESC`**: Cleanly exit the application.
- **`A`**: Cycle avatar mode:
  - **`A.L.I.E.N.`**: Massive glassy bluish alien-tech suit (default).
  - **`IRON MAN`**: Crimson & Gold Mark 85 armor.
  - **`MECH`**: The original mecha from the video.
- **`H`**: Toggle holographic HUD panels on/off.
- **`F`**: Toggle Fullscreen window mode.
- **`S`**: Save a high-resolution screenshot.

---

## ⚡ Sensitivity & Tuning

To customize responsiveness, edit `config.py`:
- `AVATAR_WIDTH` & `AVATAR_HEIGHT`: Adjust the visual scale of the suit.
- `SMOOTH_FACTOR_FAST`: Adjust how fast the hand tracking snaps to rapid hand flicks.
- `STRING_SAG` & `STRING_WAVE_SPEED`: Adjust the physics and oscillation of the neural strings.

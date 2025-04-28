import cv2
import mediapipe as mp
import pyautogui
import tkinter as tk
from threading import Thread
import math
import time


# Disable PyAutoGUI FailSafe
pyautogui.FAILSAFE = False

# Global flags
running = False
calibrated_center = None
last_click_time = 0
blink_start_time = None
last_move_x = 0
last_move_y = 0
current_scroll_speed = 0 # Initialize scroll speed

# Initialize Mediapipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

screen_width, screen_height = pyautogui.size()

# Sensitivity Settings
THRESHOLD = 0.08        # Stability deadzone
BLINK_DISTANCE_THRESHOLD = 5.5 # Threshold for detecting blink (pixels)
CLICK_COOLDOWN = 0.8    # Seconds between clicks
SPEED_FACTOR = 0.1     # Speed of cursor movement

# Eye landmark indexes
LEFT_EYE_TOP = 386
LEFT_EYE_BOTTOM = 374
RIGHT_EYE_TOP = 159
RIGHT_EYE_BOTTOM = 145

# Helper function to calculate vertical eye distance
def get_eye_distance(landmarks, top_id, bottom_id, frame_width, frame_height):
    top = landmarks[top_id]
    bottom = landmarks[bottom_id]
    top_y = int(top.y * frame_height)
    bottom_y = int(bottom.y * frame_height)
    distance = abs(top_y - bottom_y)
    return distance

def start_head_control():
    global running
    running = True
    t = Thread(target=head_tracking)
    t.start()

def stop_head_control():
    global running
    running = False
def head_tracking():
    global calibrated_center, last_click_time, blink_start_time, last_move_x, last_move_y, current_scroll_speed

    cap = cv2.VideoCapture(0)

    # Thresholds
    MOVE_THRESHOLD = 0.08         # Small head move for cursor
    SCROLL_START_THRESHOLD = 0.2   # Big nod starts scrolling
    SPEED_FACTOR = 0.1             # Cursor move speed

    # Scroll parameters
    MAX_SCROLL_SPEED = 20          # Max pixels per frame scroll
    ACCELERATION_RATE = 0.5         # How fast scrolling speeds up
    DECELERATION_RATE = 0.7         # How fast scrolling slows down

    while running:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Get nose tip
                nose_tip = face_landmarks.landmark[1]

                if calibrated_center is None:
                    calibrated_center = (nose_tip.x, nose_tip.y)
                    print(f"Calibrated at: {calibrated_center}")

                diff_x = nose_tip.x - calibrated_center[0]
                diff_y = nose_tip.y - calibrated_center[1]

                # --- Move Cursor ---
                if abs(diff_x) > MOVE_THRESHOLD or abs(diff_y) > MOVE_THRESHOLD:
                    current_x, current_y = pyautogui.position()

                    move_x = int(diff_x * screen_width * SPEED_FACTOR)
                    move_y = int(diff_y * screen_height * SPEED_FACTOR)

                    # Smoother movement
                    smooth_move_x = int(0.7 * move_x + 0.3 * last_move_x)
                    smooth_move_y = int(0.7 * move_y + 0.3 * last_move_y)

                    last_move_x = smooth_move_x
                    last_move_y = smooth_move_y

                    pyautogui.moveTo(current_x + smooth_move_x, current_y + smooth_move_y)

                # --- Smooth Scrolling ---
                if diff_y > SCROLL_START_THRESHOLD:
                    # Nod Down: Scroll Down
                    current_scroll_speed += ACCELERATION_RATE
                    current_scroll_speed = min(current_scroll_speed, MAX_SCROLL_SPEED)
                    pyautogui.scroll(-int(current_scroll_speed))

                elif diff_y < -SCROLL_START_THRESHOLD:
                    # Nod Up: Scroll Up
                    current_scroll_speed += ACCELERATION_RATE
                    current_scroll_speed = min(current_scroll_speed, MAX_SCROLL_SPEED)
                    pyautogui.scroll(int(current_scroll_speed))

                else:
                    # No strong nod: Auto slow down
                    if current_scroll_speed > 0:
                        current_scroll_speed -= DECELERATION_RATE
                        current_scroll_speed = max(current_scroll_speed, 0)

                # --- Blink Detection ---
                landmarks = face_landmarks.landmark
                left_eye_distance = get_eye_distance(landmarks, LEFT_EYE_TOP, LEFT_EYE_BOTTOM, frame.shape[1], frame.shape[0])
                right_eye_distance = get_eye_distance(landmarks, RIGHT_EYE_TOP, RIGHT_EYE_BOTTOM, frame.shape[1], frame.shape[0])

                # Debugging Eye distances (optional)
                cv2.putText(frame, f'Left Eye: {left_eye_distance:.1f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)
                cv2.putText(frame, f'Right Eye: {right_eye_distance:.1f}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
                cv2.putText(frame, f'Blink Threshold: {BLINK_DISTANCE_THRESHOLD}', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

                # Blink logic
                current_time = time.time()

                if left_eye_distance < BLINK_DISTANCE_THRESHOLD and right_eye_distance < BLINK_DISTANCE_THRESHOLD:
                    if blink_start_time is None:
                        blink_start_time = current_time
                else:
                    if blink_start_time is not None:
                        blink_duration = current_time - blink_start_time
                        blink_start_time = None

                        if blink_duration >= 0.8:
                            pyautogui.click(button='right')
                            print(f"Long Blink Detected ({blink_duration:.2f}s): Right Click")
                        elif blink_duration >= 0.1:
                            pyautogui.click(button='left')
                            print(f"Normal Blink Detected ({blink_duration:.2f}s): Left Click")

        cv2.imshow("Head Mouse Control with Blink", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

def recalibrate_center():
    global calibrated_center
    calibrated_center = None
    print("Recalibration triggered! Center will reset.") 


def exit_app():
    stop_head_control()
    root.destroy()

# GUI
root = tk.Tk()
root.title("Head and Blink Mouse Control")
root.geometry("300x300")

start_button = tk.Button(root, text="Start Head Control", command=start_head_control, height=2, width=25)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop Control", command=stop_head_control, height=2, width=25)
stop_button.pack(pady=10)

exit_button = tk.Button(root, text="Exit", command=exit_app, height=2, width=25)
exit_button.pack(pady=10)

info_label = tk.Label(root, text="Left Blink = Left Click\nRight Blink = Right Click\nMove Head to Move Cursor", font=("Arial", 10))
info_label.pack(pady=10)

recalibrate_button = tk.Button(root, text="Recalibrate Center", command=recalibrate_center, height=2, width=25)
recalibrate_button.pack(pady=10)

root.mainloop()

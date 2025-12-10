import cv2
import mediapipe as mp
import pyautogui
import math
from time import sleep
import sys
import os
import warnings
import logging
import threading
from queue import Queue

# Suppress all warnings and logging
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress all TensorFlow logging
logging.getLogger('mediapipe').setLevel(logging.CRITICAL)  # Only show critical errors
logging.getLogger('tensorflow').setLevel(logging.CRITICAL)
logging.getLogger('absl').setLevel(logging.CRITICAL)

class GestureControl:
    def __init__(self):
        self.frame_queue = Queue(maxsize=2)
        self.running = True
        self.last_action = ""
        self.action_display = ""
        
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,  # Increased for better stability
            min_tracking_confidence=0.7,   # Increased for better stability
            static_image_mode=False,
            model_complexity=0
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Initialize camera with better settings
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Error: Could not open webcam")

        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # Use MJPG codec
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Enable autofocus

    def get_distance(self, lm1, lm2):
        return math.hypot(lm1.x - lm2.x, lm1.y - lm2.y)

    def capture_frames(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                if not self.frame_queue.full():
                    self.frame_queue.put(frame)
                else:
                    try:
                        self.frame_queue.get_nowait()  # Remove old frame
                        self.frame_queue.put(frame)    # Add new frame
                    except:
                        pass
            sleep(0.01)  # Small delay to prevent CPU overload

    def process_gestures(self, frame):
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0,255,0), thickness=1, circle_radius=1),
                    self.mp_draw.DrawingSpec(color=(0,0,255), thickness=1, circle_radius=1)
                )
                lm = hand_landmarks.landmark

                # Finger states
                fingers = []
                tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky

                for i, tip in enumerate(tips):
                    if i == 0:
                        fingers.append(1 if lm[tip].x < lm[tip - 1].x else 0)
                    else:
                        fingers.append(1 if lm[tip].y < lm[tip - 2].y else 0)

                try:
                    # Gesture Controls with debouncing
                    if fingers == [1, 1, 1, 1, 1] and self.last_action != 'play_pause':
                        pyautogui.press('playpause')
                        self.last_action = 'play_pause'
                        self.action_display = "Play/Pause"
                        sleep(0.5)

                    elif fingers == [0, 1, 0, 0, 0] and self.last_action != 'next':
                        pyautogui.press('nexttrack')
                        self.last_action = 'next'
                        self.action_display = "Next Track"
                        sleep(0.5)

                    elif fingers == [0, 0, 0, 0, 1] and self.last_action != 'prev':
                        pyautogui.press('prevtrack')
                        self.last_action = 'prev'
                        self.action_display = "Previous Track"
                        sleep(0.5)

                    elif fingers == [0, 0, 0, 0, 0] and self.last_action != 'mute':
                        pyautogui.press('volumemute')
                        self.last_action = 'mute'
                        self.action_display = "Mute"
                        sleep(0.5)

                    elif fingers == [0, 1, 1, 0, 0] and self.last_action != 'vol_up':
                        pyautogui.press('volumeup')
                        self.last_action = 'vol_up'
                        self.action_display = "Volume Up"
                        sleep(0.3)

                    elif fingers == [0, 1, 1, 1, 0] and self.last_action != 'vol_down':
                        pyautogui.press('volumedown')
                        self.last_action = 'vol_down'
                        self.action_display = "Volume Down"
                        sleep(0.3)

                    else:
                        if self.last_action and self.action_display:
                            self.last_action = ""

                except pyautogui.FailSafeException:
                    print("\nSafety trigger: Move mouse to corner to stop")
                    continue
                except Exception:
                    continue

        # Display current action
        if self.action_display:
            cv2.putText(frame, f"Gesture: {self.action_display}", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 2)

        return frame

    def run(self):
        # Start frame capture in a separate thread
        capture_thread = threading.Thread(target=self.capture_frames)
        capture_thread.daemon = True
        capture_thread.start()

        # Clear screen and show welcome message
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n" + "="*50)
        print("Gesture Control System".center(50))
        print("="*50)
        print("\nStarting camera...")
        print("\nAvailable gestures:")
        print("• All fingers up: Play/Pause")
        print("• Index finger up: Next track")
        print("• Pinky finger up: Previous track")
        print("• Fist: Mute")
        print("• Index + Middle up: Volume Up")
        print("• Index + Middle + Ring up: Volume Down")
        print("\nPress 'q' to quit")
        print("="*50 + "\n")

        while self.running:
            try:
                if not self.frame_queue.empty():
                    frame = self.frame_queue.get()
                    processed_frame = self.process_gestures(frame)
                    cv2.imshow("Media Control", processed_frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\nShutting down gesture control...")
                    break

            except Exception:
                break

    def cleanup(self):
        self.running = False
        if hasattr(self, 'cap'):
            self.cap.release()
        cv2.destroyAllWindows()
        print("\nGesture control system terminated.")

def main():
    try:
        gesture_control = GestureControl()
        gesture_control.run()
    except Exception as e:
        print("\nInitialization failed. Please check your camera and try again.")
        sys.exit(1)
    finally:
        if 'gesture_control' in locals():
            gesture_control.cleanup()

if __name__ == "__main__":
    main() 
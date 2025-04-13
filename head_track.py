import cv2 
import dlib as dl
import numpy as np

import pyautogui
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0
screen_w, screen_h = pyautogui.size() # init screen size
prev_x, prev_y = screen_w // 2, screen_h // 2 # init previous x and y for smooth cursor position

from collections import deque

# deque containing the previous position history
# calcuate average of recent positions -> smoother movement
position_history_x = deque(maxlen=5)  
position_history_y = deque(maxlen=5)

# gives 68 facial
# left eye: 42-47
# right eye: 36-41 
detector = dl.get_frontal_face_detector()
predictor = dl.shape_predictor('./models/shape_predictor_68_face_landmarks.dat')


class HeadTracker:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)

    def reg_cap(self):
        ret, frame = self.cap.read()
        if not ret:
            return None

    def get_head_direction(self):
        ret, frame = self.cap.read()
        if not ret:
            return None

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)
        
        for face in faces:
            landmarks = predictor(gray, face)

            for i in range(0, 68):
                x = landmarks.part(i).x
                y = landmarks.part(i).y
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

            image_points = np.array([
                (landmarks.part(30).x, landmarks.part(30).y),
                (landmarks.part(8).x, landmarks.part(8).y),
                (landmarks.part(36).x, landmarks.part(36).y),
                (landmarks.part(45).x, landmarks.part(45).y),
                (landmarks.part(48).x, landmarks.part(48).y),
                (landmarks.part(54).x, landmarks.part(54).y)
            ], dtype="double")

            model_points = np.array([
                (0.0, 0.0, 0.0),
                (0.0, -63.6, -12.5),
                (-43.3, 32.7, -26.0),
                (43.3, 32.7, -26.0),
                (-28.9, -28.9, -24.1),
                (28.9, -28.9, -24.1)
            ])

            height, width = frame.shape[:2]
            focal_length = width
            center = (width / 2, height / 2)

            camera_matrix = np.array([
                [focal_length, 0, center[0]],
                [0, focal_length, center[1]],
                [0, 0, 1]
            ], dtype="double")

            dist_coeffs = np.zeros((4, 1))
            success, rotation_vector, _ = cv2.solvePnP(
                model_points, image_points, camera_matrix, dist_coeffs
            )

            rmat, _ = cv2.Rodrigues(rotation_vector)
            angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
            yaw = angles[1]
            pitch = angles[0]

            if pitch > 90:
                pitch -= 180

            self.cursor_control(yaw, pitch)

        return frame

    def cursor_control(self, yaw, pitch, alpha=0.6, threshold=10):
        global prev_x, prev_y

        clamped_yaw = max(-30, min(30, yaw))
        clamped_pitch = max(-30, min(0, pitch))

        norm_yaw = (clamped_yaw + 30) / 60
        norm_pitch = (clamped_pitch + 20) / 20

        target_x = int(norm_yaw * screen_w)
        target_y = int(norm_pitch * screen_h)

        smoothed_x = int(prev_x + alpha * (target_x - prev_x))
        smoothed_y = int(prev_y + alpha * (target_y - prev_y))

        position_history_x.append(smoothed_x)
        position_history_y.append(smoothed_y)

        avg_x = int(sum(position_history_x) / len(position_history_x))
        avg_y = int(sum(position_history_y) / len(position_history_y))

        if abs(smoothed_x - prev_x) > threshold or abs(smoothed_y - prev_y) > threshold:
            pyautogui.moveTo(avg_x, avg_y)
            prev_x, prev_y = avg_x, avg_y

    def release(self):
        self.cap.release()
# =============================================================================
#                           Eye tracking! Yippie
# =============================================================================

"""
def midpoint(p1, p2):
    return int((p1.x + p2.x) / 2), int((p1.y + p2.y) / 2)

def get_eye(landmarks, frame):

    # drawing lines on eyeball
    left_point = landmarks.part(36).x, landmarks.part(36).y
    right_point = landmarks.part(39).x, landmarks.part(39).y

    top_point = midpoint(landmarks.part(37), landmarks.part(38))
    bot_point = midpoint(landmarks.part(40), landmarks.part(41))

    vert_line = cv2.line(frame, top_point, bot_point, (0, 0, 255), 1)
    hor_line = cv2.line(frame, left_point, right_point, (0, 0, 255), 1)

    # draw facial landmark
    for i in range(0, 68):
        x = landmarks.part(i).x
        y = landmarks.part(i).y
        cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
"""

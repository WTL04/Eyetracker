import cv2 
import dlib as dl
import numpy as np

import pyautogui
pyautogui.FAILSAFE = False
screen_w, screen_h = pyautogui.size() # init screen size
prev_x, prev_y = screen_w // 2, screen_h // 2 # init previous x and y for smooth cursor position


# gives 68 facial
# left eye: 42-47
# right eye: 36-41 
detector = dl.get_frontal_face_detector()
predictor = dl.shape_predictor('shape_predictor_68_face_landmarks.dat')

# open webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("Cannot open webcam")

# =============================================================================
#                           Eye tracking! Yippie
# =============================================================================

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

# =============================================================================
#                           Head Tracking
# =============================================================================
def get_head_direction(detector, frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    
    for face in faces:
        landmarks = predictor(gray, face)

        # test 
        get_eye(landmarks, frame)

        # draw facial landmark
        for i in range(0, 68):
            x = landmarks.part(i).x
            y = landmarks.part(i).y
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
    

        # map out major points on face
        image_points = np.array([
            (landmarks.part(30).x, landmarks.part(30).y),     # Nose tip
            (landmarks.part(8).x, landmarks.part(8).y),       # Chin
            (landmarks.part(36).x, landmarks.part(36).y),     # Left eye corner
            (landmarks.part(45).x, landmarks.part(45).y),     # Right eye corner
            (landmarks.part(48).x, landmarks.part(48).y),     # Left mouth corner
            (landmarks.part(54).x, landmarks.part(54).y)      # Right mouth corner
        ], dtype="double")

        model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -63.6, -12.5),         # Chin
            (-43.3, 32.7, -26.0),        # Left eye
            (43.3, 32.7, -26.0),         # Right eye
            (-28.9, -28.9, -24.1),       # Left mouth
            (28.9, -28.9, -24.1)         # Right mouth
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
        yaw = angles[1]  # Left/right
        pitch = angles[0]

        # Normalize pitch
        if pitch > 90:
            pitch -= 180

        # Label the head direction
        if yaw < -15:
            hor_direction = "Looking LEFT"
        elif yaw > 15:
            hor_direction = "Looking RIGHT"
        else:
            hor_direction = "Looking CENTER"

        if pitch > -10:
            ver_direction = "Looking DOWN"
        elif pitch < -15:
            ver_direction = "Looking UP"
        else:
            ver_direction = "Looking CENTER"

        cursor_control(yaw, pitch)

        # print(f"Horizontal: {hor_direction} Vertical: {ver_direction} (yaw={yaw:.2f}) (pitch={pitch:.2f})")

def cursor_control(yaw, pitch, alpha=0.8, threshold=5):
    global prev_x, prev_y

    # Clamp yaw/pitch to usable range
    clamped_yaw = max(-30, min(30, yaw))
    clamped_pitch = max(-30, min(0, pitch))

    # Normalize to [0, 1]
    norm_yaw = (clamped_yaw + 30) / 60      # -30 to +30 → 0 to 1
    norm_pitch = (clamped_pitch + 20) / 20  # -20 to 0 → 0 to 1

    # Convert to screen coordinates
    target_x = int(norm_yaw * screen_w)
    target_y = int(norm_pitch * screen_h)

    # Smooth cursor motion
    smoothed_x = int(prev_x + alpha * (target_x - prev_x))
    smoothed_y = int(prev_y + alpha * (target_y - prev_y))

    # add a threshold to detect movment, lessen jittery jumps
    if abs(smoothed_x - prev_x) > threshold or abs(smoothed_y - prev_y) > threshold:
        pyautogui.moveTo(smoothed_x, smoothed_y)
        prev_x, prev_y = smoothed_x, smoothed_y



while True:
    ret, frame = cap.read()
    if not ret:
        break

    get_head_direction(detector, frame)
    # cv2.imshow("Head + Eye Tracking", frame)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

import mediapipe as mp 
import cv2 
import pyautogui

class HeadTracker:
    def __init__(self):
        self.cam = cv2.VideoCapture(0)
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
        self.screen_w, self.screen_h = pyautogui.size()
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0
        self.sensitivity = 8  # adjust cursor sensitivity

    def process_frame(self):
        ret, frame = self.cam.read()
        if not ret:
            return None

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = self.face_mesh.process(rgb_frame)

        frame_h, frame_w, _ = frame.shape

        if output.multi_face_landmarks:
            landmarks = output.multi_face_landmarks[0].landmark

            # Right iris center (landmark 475)
            r_iris = landmarks[475]
            r_cx = r_iris.x
            r_cy = r_iris.y

            # Left iris center (landmark 469)
            l_iris = landmarks[469]
            l_cx = l_iris.x
            l_cy = l_iris.y


            # Draw circles for both eyes for visualization
            r_x = int(r_cx * frame_w)
            r_y = int(r_cy * frame_h)
            cv2.circle(frame, (r_x, r_y), 15, (0, 0, 255), -1)
    
            l_x = int(l_cx * frame_w)
            l_y = int(l_cy * frame_h)
            cv2.circle(frame, (l_x, l_y), 15, (0, 0, 255), -1)

            # Map right eye to screen coordinates
            r_dx = (r_cx - 0.5) * self.sensitivity
            r_dy = (r_cy - 0.5) * self.sensitivity
    
            # Map left eye to screen coordinates
            l_dx = (l_cx - 0.5) * self.sensitivity
            l_dy = (l_cy - 0.5) * self.sensitivity

            # get midpoint
            m_dx = (r_dx + l_dx) / 2 
            m_dy = (r_dy + l_dy) / 2 

            screen_x = self.screen_w // 2 + m_dx * self.screen_w
            screen_y = self.screen_h // 2 + m_dy * self.screen_h


            pyautogui.moveTo(screen_x, screen_y)
        
        return frame
    
        def release(self):
            self.cam.release()


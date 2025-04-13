import cv2 
import dlib as dl 

# gives 68 facial points
# left eye: 42-47
# right eye: 36-41 
detector = dl.get_frontal_face_detector()
predictor = dl.shape_predictor('shape_predictor_68_face_landmarks.dat')

# open webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("Cannot open webcam")

def midpoint(p1, p2):
    return int((p1.x + p2.x) / 2), int((p1.y + p2.y) / 2)

def get_eye(detector, frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        landmarks = predictor(gray, face)

        left_point = landmarks.part(36).x, landmarks.part(36).y
        right_point = landmarks.part(39).x, landmarks.part(39).y

        top_point = midpoint(landmarks.part(37), landmarks.part(38))
        bot_point = midpoint(landmarks.part(40), landmarks.part(41))

        # vert_line = cv2.line(frame, top_point, bot_point, (0, 0, 255), 1)
        # hor_line = cv2.line(frame, left_point, right_point, (0, 0, 255), 1)

        vert_line = cv2.circle(frame, top_point, bot_point, 2, (0, 0, 255), 1)
        hor_line = cv2.line(frame, left_point, right_point, (0, 0, 255), 1)



    cv2.imshow("Eyeball", frame)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    get_eye(detector, frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

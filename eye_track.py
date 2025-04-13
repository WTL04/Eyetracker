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

def get_left_eye(landmarks, frame):
    # get left eye coords from dlib face mapping
    x_list = [landmarks.part(i).x for i in range(36, 42)]
    y_list = [landmarks.part(i).y for i in range(36, 42)]

    # bounding box around left eye
    x_min, x_max = min(x_list), max(x_list)
    y_min, y_max = min(y_list), max(y_list)
    
    # add padding
    padding = 5
    x_min = max(x_min - padding, 0)
    y_min = max(y_min - padding, 0)
    x_max = min(x_max + padding, frame.shape[1])
    y_max = min(y_max + padding, frame.shape[0])

    # crop left eye and show
    left_eye = frame[y_min:y_max, x_min:x_max]
    resized_eye = cv2.resize(left_eye, None, fx=4, fy=4, interpolation=cv2.INTER_LINEAR)
    cv2.imshow('Left Eye', resized_eye)


def get_face(detector, frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # convert into grayscale
    faces = detector(gray)

    for face in faces:
        landmarks = predictor(gray, face)

        for i in range(0, 68):
            x = landmarks.part(i).x
            y = landmarks.part(i).y
            # draw bouding circle around eyes
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
       
        # crop out left eye
        get_left_eye(landmarks, frame)



while (True):
    ret, frame = cap.read()
    if not ret:
        break

    # get facial features     
    get_face(detector, frame)
    
    # press q to exit 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

import cv2 
import dlib as dl 

detector = dl.get_frontal_face_detector()
predictor = dl.shape_predictor('shape_predictor_68_face_landmarks.dat')

# open webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("Cannot open webcam")


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
        
        # draw bounding box around face
        cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), (255, 0, 0), 2)

while (True):
    ret, frame = cap.read()
    if not ret:
        break

    

    

    cv2.imshow('Webcam - Facial Landmarks', frame)
    
    # press q to exit 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

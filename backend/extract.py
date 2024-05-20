import cv2
import dlib
import numpy as np
import pandas as pd
from math import hypot

# Initialize dlib's face detector (HOG-based) and the facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(
    "E:/Desktopp/FYP Stuff/SDS/impSDS/backend/shape_predictor_68_face_landmarks.dat"
)

# Initialize video capture
cap = cv2.VideoCapture(0)

# Create DataFrame to store coordinates
columns = ["Frame", "LPX", "LPY", "RPX", "RPY"]
data = {"Frame": [], "LPX": [], "LPY": [], "RPX": [], "RPY": []}
df = pd.DataFrame(data, columns=columns)

frame_count = 0


def midpoint(p1, p2):
    return int((p1.x + p2.x) / 2), int((p1.y + p2.y) / 2)


font = cv2.FONT_HERSHEY_PLAIN


def get_gaze_ratio(eye_points, facial_landmarks, frame, gray):
    left_eye_region = np.array(
        [
            (
                facial_landmarks.part(eye_points[0]).x,
                facial_landmarks.part(eye_points[0]).y,
            ),
            (
                facial_landmarks.part(eye_points[1]).x,
                facial_landmarks.part(eye_points[1]).y,
            ),
            (
                facial_landmarks.part(eye_points[2]).x,
                facial_landmarks.part(eye_points[2]).y,
            ),
            (
                facial_landmarks.part(eye_points[3]).x,
                facial_landmarks.part(eye_points[3]).y,
            ),
            (
                facial_landmarks.part(eye_points[4]).x,
                facial_landmarks.part(eye_points[4]).y,
            ),
            (
                facial_landmarks.part(eye_points[5]).x,
                facial_landmarks.part(eye_points[5]).y,
            ),
        ],
        np.int32,
    )

    left_x = facial_landmarks.part(eye_points[0]).x
    left_y = facial_landmarks.part(eye_points[1]).y
    right_x = facial_landmarks.part(eye_points[3]).x
    right_y = facial_landmarks.part(eye_points[4]).y

    center_top = midpoint(
        facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2])
    )
    center_bottom = midpoint(
        facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4])
    )

    height, width, _ = frame.shape
    mask = np.zeros((height, width), np.uint8)
    cv2.polylines(mask, [left_eye_region], True, 255, 2)
    cv2.fillPoly(mask, [left_eye_region], 255)
    eye = cv2.bitwise_and(gray, gray, mask=mask)

    min_x = np.min(left_eye_region[:, 0])
    max_x = np.max(left_eye_region[:, 0])
    min_y = np.min(left_eye_region[:, 1])
    max_y = np.max(left_eye_region[:, 1])

    gray_eye = eye[min_y:max_y, min_x:max_x]
    _, threshold_eye = cv2.threshold(gray_eye, 70, 255, cv2.THRESH_BINARY)
    height, width = threshold_eye.shape

    left_side_threshold = threshold_eye[0:height, 0 : int(width / 2)]
    left_side_white = cv2.countNonZero(left_side_threshold)

    right_side_threshold = threshold_eye[0:height, int(width / 2) : width]
    right_side_white = cv2.countNonZero(right_side_threshold)

    if left_side_white == 0:
        gaze_ratio = 1
    elif right_side_white == 0:
        gaze_ratio = 5
    else:
        gaze_ratio = left_side_white / right_side_white

    return gaze_ratio


def get_blinking_ratio(eye_points, facial_landmarks):
    left_point = (
        facial_landmarks.part(eye_points[0]).x,
        facial_landmarks.part(eye_points[0]).y,
    )
    right_point = (
        facial_landmarks.part(eye_points[3]).x,
        facial_landmarks.part(eye_points[3]).y,
    )
    center_top = midpoint(
        facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2])
    )
    center_bottom = midpoint(
        facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4])
    )

    hor_line_length = hypot(
        (left_point[0] - right_point[0]), (left_point[1] - right_point[1])
    )
    ver_line_length = hypot(
        (center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1])
    )

    ratio = hor_line_length / ver_line_length

    return ratio


while True:
    ret, frame = cap.read()
    frame_count += 1

    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detector(gray)

    for face in faces:
        landmarks = predictor(gray, face)

        left_eye_x = landmarks.part(36).x
        left_eye_y = landmarks.part(36).y
        right_eye_x = landmarks.part(45).x
        right_eye_y = landmarks.part(45).y

        gaze_ratio_left_eye = get_gaze_ratio(
            (36, 37, 38, 39, 40, 41), landmarks, frame, gray
        )
        gaze_ratio_right_eye = get_gaze_ratio(
            (42, 43, 44, 45, 46, 47), landmarks, frame, gray
        )

        df = pd.concat(
            [
                df,
                pd.DataFrame(
                    {
                        "Frame": [frame_count],
                        "LPX": [int(left_eye_x + (right_eye_x - left_eye_x) * 0.3)],
                        "LPY": [int(left_eye_y + (right_eye_y - left_eye_y) * 0.3)],
                        "RPX": [int(right_eye_x + (left_eye_x - right_eye_x) * 0.3)],
                        "RPY": [int(right_eye_y + (left_eye_y - right_eye_y) * 0.3)],
                    }
                ),
            ],
            ignore_index=True,
        )

        cv2.circle(
            frame,
            (
                int(left_eye_x + (right_eye_x - left_eye_x) * 0.3),
                int(left_eye_y + (right_eye_y - left_eye_y) * 0.3),
            ),
            2,
            (0, 255, 0),
            -1,
        )
        cv2.circle(
            frame,
            (
                int(right_eye_x + (left_eye_x - right_eye_x) * 0.3),
                int(right_eye_y + (left_eye_y - right_eye_y) * 0.3),
            ),
            2,
            (0, 255, 0),
            -1,
        )

        left_eye_ratio = get_blinking_ratio((36, 37, 38, 39, 40, 41), landmarks)
        right_eye_ratio = get_blinking_ratio((42, 43, 44, 45, 46, 47), landmarks)
        blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2

        if blinking_ratio > 5.7:
            cv2.putText(
                frame, "BLINKING", (50, 150), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 1
            )

        if gaze_ratio_left_eye <= 1:
            cv2.putText(
                frame, "RIGHT", (50, 100), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 3
            )
        elif 1.2 < gaze_ratio_left_eye < 3:
            cv2.putText(
                frame, "CENTER", (50, 100), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 3
            )
        else:
            cv2.putText(
                frame, "LEFT", (50, 100), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 3
            )

    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

print("DataFrame:")
print(df)

output_file_path = "E:/Desktopp/FYP Stuff/SDS/impSDS/backend/eye_coordinates.xlsx"
df.to_excel(output_file_path, index=False)

print(f"Eye coordinates saved to {output_file_path}")

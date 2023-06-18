from typing import Any
import insightface
import roop.globals
import cv2

FACE_ANALYSER = None


def get_face_analyser() -> Any:
    global FACE_ANALYSER

    if FACE_ANALYSER is None:
        FACE_ANALYSER = insightface.app.FaceAnalysis(name='buffalo_l', providers=roop.globals.execution_providers)
        FACE_ANALYSER.prepare(ctx_id=0, det_size=(640, 640))
    return FACE_ANALYSER


def get_one_face(frame: Any) -> Any:
    face = get_face_analyser().get(frame)
    try:
        return min(face, key=lambda x: x.bbox[0])
    except ValueError:
        return None


def get_many_faces(frame: Any) -> Any:
    try:
        faces = get_face_analyser().get(frame)
        return sorted(faces, key = lambda x : x.bbox[0])
    except IndexError:
        return None

def extract_face_images(source_filename):
    face_data = []
    source_image = cv2.imread(source_filename)
    faces = get_many_faces(source_image)

    i = 0
    for face in faces:
        (startX, startY, endX, endY) = face['bbox'].astype("int")
        face_temp = source_image[startY:endY, startX:endX]
        cv2.imwrite(f'{i}.png', face_temp)
        i += 1
        face_data.append([face, face_temp])
    return face_data
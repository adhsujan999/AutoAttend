import dlib
import numpy as np
import face_recognition_models
from sklearn.svm import SVC
import streamlit as st

from database.db import get_all_students

@st.cache_resource
def load_dlib_models():
    # Load dlib face detector
    detector = dlib.get_frontal_face_detector()

    # Load facial landmark predictor
    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    # Load face recognition model
    facerec = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )


    return detector, sp, facerec


def get_face_embeddings(image_np):
    detector, sp, facerec = load_dlib_models()

    # Detect faces from image
    faces = detector(image_np, 1)

    encodings = []

    for face in faces:
        # Detect facial landmarks
        shape = sp(image_np, face)

        # Generate 128-dimensional face embedding
        face_descriptor = facerec.compute_face_descriptor(image_np, shape, 1) #128 embeddings

        encodings.append(np.array(face_descriptor))

    return encodings

@st.cache_resource
def get_trained_model():
    x = []
    y = []

    # Get all registered students
    students_db = get_all_students()

    if not students_db:
        return None

    for student in students_db:
        # Get stored face embedding
        embedding = student.get('face_embedding')

        if embedding:import dlib

@st.cache_resource
def load_dlib_models():
    detector = dlib.get_frontal_face_detector()

    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    facerec = dlib.face_recognition_model_v1(
    face_recognition_models.face_recognition_model_location()
)


    return detector, sp, facerec


def get_face_embeddings(image_np):
    detector, sp, facerec = load_dlib_models()
    faces = detector(image_np, 1)

    encodings = []

    for face in faces:
        shape = sp(image_np, face)
        face_descriptor = facerec.compute_face_descriptor(image_np, shape, 1) #128 embeddings

        encodings.append(np.array(face_descriptor))

    return encodings

@st.cache_resource
def get_trained_model():
    x = []
    y = []

    students_db = get_all_students()

    if not students_db:
        return None

    for student in students_db:
        embedding = student.get('face_embedding')

        if embedding:
            x.append(np.array(embedding))
            y.append(student.get('student_id'))

    if len(x) == 0:
        return 0

    clf = SVC(kernel='linear', probability=True, class_weight='balanced')

    try:
        clf.fit(x, y)
    except ValueError:
        pass

    return {'clf':clf, 'x':x, "y":y}


def train_classifier():
    st.cache_resource.clear()
    model_data = get_trained_model()

    return model_data


def predict_attendance(class_image_np):
    encodings = get_face_embeddings(class_image_np)

    detected_student = {}


    model_data = get_trained_model()

    if not model_data:
        return detected_student, [], len(encodings)
    
    clf = model_data['clf']
    X_train = model_data['x']
    y_train = model_data['y']

    all_students = sorted(list(set(y_train)))

    for encoding in encodings:
        if len(all_students)>= 2:
            predicted_id= int(clf.predict([encoding])[0])
        else:
            predicted_id = int(all_students[0])

        student_embedding = X_train[y_train.index(predicted_id)]

        best_match_score = np.linalg.norm(student_embedding - encoding)

        resemblance_threshold = 0.6

        if best_match_score <= resemblance_threshold:
            detected_student[predicted_id] = True
    return detected_student, all_students, len(encodings)
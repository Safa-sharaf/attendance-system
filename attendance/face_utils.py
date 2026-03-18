import cv2
import numpy as np
import os


def load_image_from_path(image_path):
    """Load image from file path and convert to RGB."""
    img = cv2.imread(image_path)
    if img is None:
        return None
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def load_image_from_bytes(image_bytes):
    """Load image from bytes (uploaded file)."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img   = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return None
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def detect_face(image_rgb):
    """Detect face in image using OpenCV Haar Cascade."""
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    gray  = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60)
    )
    return faces


def extract_face_region(image_rgb, face_coords):
    """Extract and resize face region from image."""
    x, y, w, h = face_coords
    face = image_rgb[y:y+h, x:x+w]
    face = cv2.resize(face, (100, 100))
    return face


def compare_faces(registered_image_path, selfie_bytes, threshold=0.4):
    """
    Compare registered face photo with selfie.
    Returns (match: bool, confidence: float, message: str)
    """
    try:
        # Load registered image
        registered_img = load_image_from_path(registered_image_path)
        if registered_img is None:
            return False, 0.0, "Could not load registered photo."

        # Load selfie image
        selfie_img = load_image_from_bytes(selfie_bytes)
        if selfie_img is None:
            return False, 0.0, "Could not load selfie."

        # Detect faces
        registered_faces = detect_face(registered_img)
        selfie_faces      = detect_face(selfie_img)

        if len(registered_faces) == 0:
            return False, 0.0, "No face detected in registered photo."

        if len(selfie_faces) == 0:
            return False, 0.0, "No face detected in selfie. Please look directly at camera."

        # Extract face regions
        reg_face   = extract_face_region(registered_img, registered_faces[0])
        self_face  = extract_face_region(selfie_img, selfie_faces[0])

        # Convert to grayscale for comparison
        reg_gray  = cv2.cvtColor(reg_face,  cv2.COLOR_RGB2GRAY).astype(np.float32)
        self_gray = cv2.cvtColor(self_face, cv2.COLOR_RGB2GRAY).astype(np.float32)

        # Normalize
        reg_gray  = reg_gray  / 255.0
        self_gray = self_gray / 255.0

        # Calculate similarity using normalized cross-correlation
        result = cv2.matchTemplate(
            reg_gray, self_gray, cv2.TM_CCOEFF_NORMED
        )
        confidence = float(result[0][0])

        # Also check using histogram comparison
        reg_hist  = cv2.calcHist([reg_gray],  [0], None, [256], [0, 1])
        self_hist = cv2.calcHist([self_gray], [0], None, [256], [0, 1])
        cv2.normalize(reg_hist,  reg_hist)
        cv2.normalize(self_hist, self_hist)
        hist_score = cv2.compareHist(reg_hist, self_hist, cv2.HISTCMP_CORREL)

        # Combined score
        combined = (confidence * 0.6) + (hist_score * 0.4)

        if combined >= threshold:
            return True, round(combined * 100, 1), f"Face matched! Confidence: {round(combined * 100, 1)}%"
        else:
            return False, round(combined * 100, 1), f"Face did not match. Please try again."

    except Exception as e:
        return False, 0.0, f"Face verification error: {str(e)}"
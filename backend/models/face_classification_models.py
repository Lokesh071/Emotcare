# face_classification_models.py
# Based on oarriaga/face_classification repository
# https://github.com/oarriaga/face_classification

import tensorflow as tf
from tensorflow.keras.layers import (
    Activation, Conv2D, BatchNormalization, GlobalAveragePooling2D,
    MaxPooling2D, SeparableConv2D, Input, add
)
from tensorflow.keras.models import Model
from tensorflow.keras.regularizers import l2
import numpy as np
import cv2

def mini_XCEPTION(input_shape, num_classes, l2_regularization=0.01):
    """
    Mini XCEPTION model for emotion classification
    Based on the face_classification repository by oarriaga
    """
    regularization = l2(l2_regularization)

    # Base
    img_input = Input(input_shape)
    x = Conv2D(8, (3, 3), strides=(1, 1), kernel_regularizer=regularization, use_bias=False)(img_input)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = Conv2D(8, (3, 3), strides=(1, 1), kernel_regularizer=regularization, use_bias=False)(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)

    # Module 1
    residual = Conv2D(16, (1, 1), strides=(2, 2), padding='same', use_bias=False)(x)
    residual = BatchNormalization()(residual)

    x = SeparableConv2D(16, (3, 3), padding='same', kernel_regularizer=regularization, use_bias=False)(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = SeparableConv2D(16, (3, 3), padding='same', kernel_regularizer=regularization, use_bias=False)(x)
    x = BatchNormalization()(x)
    x = MaxPooling2D((3, 3), strides=(2, 2), padding='same')(x)
    x = add([x, residual])

    # Module 2
    residual = Conv2D(32, (1, 1), strides=(2, 2), padding='same', use_bias=False)(x)
    residual = BatchNormalization()(residual)

    x = SeparableConv2D(32, (3, 3), padding='same', kernel_regularizer=regularization, use_bias=False)(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = SeparableConv2D(32, (3, 3), padding='same', kernel_regularizer=regularization, use_bias=False)(x)
    x = BatchNormalization()(x)
    x = MaxPooling2D((3, 3), strides=(2, 2), padding='same')(x)
    x = add([x, residual])

    # Module 3
    residual = Conv2D(64, (1, 1), strides=(2, 2), padding='same', use_bias=False)(x)
    residual = BatchNormalization()(residual)

    x = SeparableConv2D(64, (3, 3), padding='same', kernel_regularizer=regularization, use_bias=False)(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = SeparableConv2D(64, (3, 3), padding='same', kernel_regularizer=regularization, use_bias=False)(x)
    x = BatchNormalization()(x)
    x = MaxPooling2D((3, 3), strides=(2, 2), padding='same')(x)
    x = add([x, residual])

    # Module 4
    residual = Conv2D(128, (1, 1), strides=(2, 2), padding='same', use_bias=False)(x)
    residual = BatchNormalization()(residual)

    x = SeparableConv2D(128, (3, 3), padding='same', kernel_regularizer=regularization, use_bias=False)(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = SeparableConv2D(128, (3, 3), padding='same', kernel_regularizer=regularization, use_bias=False)(x)
    x = BatchNormalization()(x)
    x = MaxPooling2D((3, 3), strides=(2, 2), padding='same')(x)
    x = add([x, residual])

    x = Conv2D(num_classes, (3, 3), padding='same')(x)
    x = GlobalAveragePooling2D()(x)
    output = Activation('softmax', name='predictions')(x)

    model = Model(img_input, output)
    return model

def preprocess_input(x, v2=True):
    """
    Preprocess input for face_classification model
    """
    x = x.astype('float32')
    x = x / 255.0
    if v2:
        x = x - 0.5
        x = x * 2.0
    return x

def detect_faces_opencv(image, face_cascade=None):
    """
    Detect faces using OpenCV Haar Cascade
    """
    if face_cascade is None:
        # Load the default face cascade
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    return faces

def apply_offsets(face_coordinates, offsets):
    """
    Apply offsets to face coordinates
    """
    x, y, width, height = face_coordinates
    x_off, y_off = offsets
    return (x - x_off, x + width + x_off, y - y_off, y + height + y_off)

class FaceClassificationEmotionDetector:
    """
    Emotion detector using the face_classification model
    """

    def __init__(self, model_path, input_shape=(64, 64, 1)):
        self.model_path = model_path
        self.input_shape = input_shape
        self.model = None
        self.face_cascade = None
        self.actual_input_shape = None

        # Emotion labels from FER2013 dataset
        self.emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

        # EmotiCare emotion mapping
        self.emoticare_mapping = {
            'angry': 'stressed',
            'disgust': 'stressed',
            'fear': 'stressed',
            'happy': 'happy',
            'sad': 'sad',
            'surprise': 'happy',
            'neutral': 'peaceful'
        }

        self.load_model()
        self.load_face_detector()

    def load_model(self):
        """Load the pre-trained emotion detection model"""
        try:
            # Load model without optimizer state to suppress warnings (inference only)
            self.model = tf.keras.models.load_model(self.model_path, compile=False)
            # Store the actual input shape from the loaded model
            self.actual_input_shape = self.model.input_shape
            print(f"✅ Face classification model loaded from {self.model_path}")
            print(f"📐 Model input shape: {self.actual_input_shape}")
        except Exception as e:
            print(f"❌ Error loading face classification model: {e}")
            # Create a new model if loading fails
            self.model = mini_XCEPTION(self.input_shape, len(self.emotion_labels))
            self.actual_input_shape = self.input_shape
            print("⚠️ Created new mini_XCEPTION model (not pre-trained)")

    def load_face_detector(self):
        """Load OpenCV face detector"""
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            print("✅ OpenCV face detector loaded")
        except Exception as e:
            print(f"❌ Error loading face detector: {e}")

    def detect_emotion(self, image):
        """
        Detect emotions in the given image
        Returns: list of detected emotions with confidence scores
        """
        try:
            # Detect faces
            faces = detect_faces_opencv(image, self.face_cascade)

            if len(faces) == 0:
                return []

            results = []

            for (x, y, w, h) in faces:
                # Extract face region
                face_roi = image[y:y+h, x:x+w]

                # Convert to grayscale if needed
                if len(face_roi.shape) == 3:
                    face_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)

                # Resize to model input size (use stored actual input shape)
                if self.actual_input_shape is not None:
                    target_height = self.actual_input_shape[1]
                    target_width = self.actual_input_shape[2]
                else:
                    # Fallback to default
                    target_height = self.input_shape[0]
                    target_width = self.input_shape[1]

                face_roi = cv2.resize(face_roi, (target_width, target_height))

                # Normalize and reshape
                face_roi = face_roi.astype('float32')
                face_roi = np.expand_dims(face_roi, axis=0)
                face_roi = np.expand_dims(face_roi, axis=-1)

                # Preprocess
                face_roi = preprocess_input(face_roi)

                # Predict emotion
                if self.model is None:
                    continue  # Skip if model is not loaded

                emotion_prediction = self.model.predict(face_roi, verbose=0)
                emotion_probability = np.max(emotion_prediction)
                emotion_label_arg = np.argmax(emotion_prediction)
                emotion_label = self.emotion_labels[emotion_label_arg]

                # Map to EmotiCare emotions
                emoticare_emotion = self.emoticare_mapping.get(emotion_label, 'peaceful')

                results.append({
                    'emotion': emoticare_emotion,
                    'confidence': float(emotion_probability),
                    'original_emotion': emotion_label,
                    'face_coordinates': (x, y, w, h)
                })

            return results

        except Exception as e:
            print(f"❌ Error in emotion detection: {e}")
            return []

    def get_dominant_emotion(self, image):
        """
        Get the dominant emotion from the image
        Returns: emotion string and confidence score
        """
        emotions = self.detect_emotion(image)

        if not emotions:
            return 'peaceful', 0.5

        # Get the emotion with highest confidence
        dominant = max(emotions, key=lambda x: x['confidence'])
        return dominant['emotion'], dominant['confidence']

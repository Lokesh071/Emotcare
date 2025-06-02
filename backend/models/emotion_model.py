# Optimize TensorFlow memory usage
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tensorflow as tf
# Configure TensorFlow for memory efficiency
tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.threading.set_inter_op_parallelism_threads(1)

import numpy as np
import cv2
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Dropout, Flatten
from tensorflow.keras.optimizers import Adam
import pickle
from .face_classification_models import FaceClassificationEmotionDetector

class EmotionModel:
    def __init__(self):
        self.model = None
        self.emotion_labels = ['angry', 'anxious', 'happy', 'neutral', 'sad', 'stressed', 'surprised']
        self.img_size = 48
        self._model_loaded = False

        self.face_classifier = None
        self.use_face_classification = True
        self._init_face_classification_model()

    def _init_face_classification_model(self):
        try:
            model_path = os.path.join(
                os.path.dirname(__file__),
                '../../models/fer2013_mini_XCEPTION.h5'
            )

            if os.path.exists(model_path):
                self.face_classifier = FaceClassificationEmotionDetector(model_path)
                print("✅ Face classification model initialized successfully")
            else:
                print(f"⚠️ Face classification model not found at {model_path}")
                print("📥 Please ensure the model is downloaded")
                self.use_face_classification = False

        except Exception as e:
            print(f"❌ Error initializing face classification model: {e}")
            self.use_face_classification = False

    def create_model(self):
        model = Sequential([
            Conv2D(32, (3, 3), activation='relu', input_shape=(self.img_size, self.img_size, 1)),
            Conv2D(64, (3, 3), activation='relu'),
            MaxPooling2D(2, 2),
            Dropout(0.25),

            Conv2D(128, (3, 3), activation='relu'),
            Conv2D(128, (3, 3), activation='relu'),
            MaxPooling2D(2, 2),
            Dropout(0.25),

            Conv2D(256, (3, 3), activation='relu'),
            MaxPooling2D(2, 2),
            Dropout(0.25),

            Flatten(),
            Dense(512, activation='relu'),
            Dropout(0.5),
            Dense(256, activation='relu'),
            Dropout(0.5),
            Dense(len(self.emotion_labels), activation='softmax')
        ])

        model.compile(
            optimizer=Adam(learning_rate=0.0001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        return model

    def load_pretrained_model(self, model_path=None):
        if self._model_loaded and self.model is not None:
            print("✅ Model already loaded, skipping reload")
            return

        if model_path is None:
            model_path = os.path.join(
                os.path.dirname(__file__),
                '../../models/emotion_detection_model.h5'
            )

        try:
            if os.path.exists(model_path):
                print(f"Loading pre-trained model from {model_path}")
                try:
                    self.model = tf.keras.models.load_model(model_path, compile=False)
                    self.model.compile(
                        optimizer=Adam(learning_rate=0.0001),
                        loss='categorical_crossentropy',
                        metrics=['accuracy']
                    )
                    print("✅ Pre-trained model loaded successfully")
                    self._model_loaded = True
                    return
                except Exception as load_error:
                    print(f"⚠️ Failed to load pre-trained model: {load_error}")
                    print("🔄 Creating new model with same architecture...")
                    try:
                        os.remove(model_path)
                        print(f"🗑️ Removed incompatible model file: {model_path}")
                    except:
                        pass

            print("Creating new model with predefined architecture")
            self.model = self.create_model()
            self._model_loaded = True

            try:
                os.makedirs(os.path.dirname(model_path), exist_ok=True)
                self.model.save(model_path, save_format='h5')
                print(f"✅ New compatible model saved to {model_path}")
            except Exception as save_error:
                print(f"⚠️ Could not save model: {save_error}")

        except Exception as e:
            print(f"❌ Error in model initialization: {e}")
            self.model = self.create_model()
            self._model_loaded = True
            print("⚠️ Using fallback model")

    def preprocess_face(self, face_image):
        try:
            if len(face_image.shape) == 3:
                face_image = cv2.cvtColor(face_image, cv2.COLOR_RGB2GRAY)

            face_image = cv2.resize(face_image, (self.img_size, self.img_size))

            face_image = face_image.astype('float32') / 255.0

            face_image = np.expand_dims(face_image, axis=0)
            face_image = np.expand_dims(face_image, axis=-1)

            return face_image
        except Exception as e:
            print(f"Error preprocessing face: {e}")
            return None

    def detect_emotion(self, face_image):
        try:
            if self.model is None:
                return None, 0.0

            processed_face = self.preprocess_face(face_image)
            if processed_face is None:
                return None, 0.0

            predictions = self.model.predict(processed_face, verbose=0)

            emotion_index = np.argmax(predictions[0])
            confidence = float(predictions[0][emotion_index])
            emotion = self.emotion_labels[emotion_index]

            if confidence > 0.5:
                return emotion, confidence
            else:
                return 'neutral', confidence

        except Exception as e:
            print(f"Error detecting emotion: {e}")
            return None, 0.0

    def detect_faces(self, image):
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image

            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            detected_faces = []
            for (x, y, w, h) in faces:
                face_roi = gray[y:y+h, x:x+w]
                detected_faces.append({
                    'face': face_roi,
                    'bbox': (x, y, w, h)
                })

            return detected_faces
        except Exception as e:
            print(f"Error detecting faces: {e}")
            return []

    def analyze_image(self, image_data):
        try:
            if isinstance(image_data, str):
                import base64
                from io import BytesIO
                from PIL import Image

                image_data = base64.b64decode(image_data.split(',')[1])
                image = Image.open(BytesIO(image_data))
                image = np.array(image)
            elif isinstance(image_data, bytes):
                from PIL import Image
                from io import BytesIO

                image = Image.open(BytesIO(image_data))
                image = np.array(image)
            else:
                image = image_data

            if self.use_face_classification and self.face_classifier:
                try:
                    emotions = self.face_classifier.detect_emotion(image)

                    if not emotions:
                        return {
                            'success': False,
                            'message': 'No faces detected in the image',
                            'emotions': []
                        }

                    results = []
                    for i, emotion_data in enumerate(emotions):
                        results.append({
                            'face_id': i,
                            'emotion': emotion_data['emotion'],
                            'confidence': emotion_data['confidence'],
                            'bbox': emotion_data['face_coordinates']
                        })

                    return {
                        'success': True,
                        'message': f'Detected {len(results)} face(s) with emotions (face_classification)',
                        'emotions': results
                    }

                except Exception as e:
                    print(f"⚠️ Face classification failed, falling back to original model: {e}")

            faces = self.detect_faces(image)

            if not faces:
                return {
                    'success': False,
                    'message': 'No faces detected in the image',
                    'emotions': []
                }

            results = []
            for i, face_data in enumerate(faces):
                emotion, confidence = self.detect_emotion(face_data['face'])

                if emotion:
                    results.append({
                        'face_id': i,
                        'emotion': emotion,
                        'confidence': confidence,
                        'bbox': face_data['bbox']
                    })

            return {
                'success': True,
                'message': f'Detected {len(results)} face(s) with emotions',
                'emotions': results
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error analyzing image: {str(e)}',
                'emotions': []
            }

    def save_model(self, filepath='models/emotion_detection_model.h5'):
        try:
            if self.model:
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                self.model.save(filepath)
                print(f"Model saved to {filepath}")
                return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False

    def train_model(self, train_data, train_labels, validation_data, validation_labels, epochs=50):
        try:
            if self.model is None:
                self.model = self.create_model()

            from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

            early_stopping = EarlyStopping(
                monitor='val_accuracy',
                patience=10,
                restore_best_weights=True
            )

            reduce_lr = ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.2,
                patience=5,
                min_lr=0.00001
            )

            history = self.model.fit(
                train_data, train_labels,
                epochs=epochs,
                validation_data=(validation_data, validation_labels),
                batch_size=32,
                callbacks=[early_stopping, reduce_lr],
                verbose=1
            )

            return history
        except Exception as e:
            print(f"Error training model: {e}")
            return None

def prepare_emotion_data(data_directory):
    emotions = ['angry', 'anxious', 'happy', 'neutral', 'sad', 'stressed', 'surprised']
    data = []
    labels = []

    for emotion_idx, emotion in enumerate(emotions):
        emotion_path = os.path.join(data_directory, emotion)
        if os.path.exists(emotion_path):
            for image_file in os.listdir(emotion_path):
                if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(emotion_path, image_file)
                    try:
                        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                        image = cv2.resize(image, (48, 48))
                        image = image.astype('float32') / 255.0

                        data.append(image)
                        labels.append(emotion_idx)
                    except Exception as e:
                        print(f"Error processing {image_path}: {e}")

    return np.array(data), np.array(labels)

def create_model_for_web():
    model = EmotionModel()

    model.model = model.create_model()

    model.save_model('static/models/emotion_model.h5')

    try:
        import tensorflowjs as tfjs
        tfjs.converters.save_keras_model(model.model, 'static/models/emotion_model_js')
        print("Model saved in TensorFlow.js format")
    except ImportError:
        print("TensorFlow.js converter not installed. Install with: pip install tensorflowjs")

    return model

if __name__ == "__main__":
    emotion_model = create_model_for_web()
    print("Emotion detection model created and saved!")

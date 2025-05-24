# models/emotion_model.py
import tensorflow as tf
import numpy as np
import cv2
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Dropout, Flatten
from tensorflow.keras.optimizers import Adam
import os
import pickle

class EmotionModel:
    def __init__(self):
        self.model = None
        self.emotion_labels = ['angry', 'anxious', 'happy', 'neutral', 'sad', 'stressed', 'surprised']
        self.img_size = 48
        
    def create_model(self):
        """Create a CNN model for emotion detection"""
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
    
    def load_pretrained_model(self, model_path='models/emotion_detection_model.h5'):
        """Load a pre-trained emotion detection model"""
        try:
            if os.path.exists(model_path):
                self.model = tf.keras.models.load_model(model_path)
                print("Pre-trained model loaded successfully")
                return True
            else:
                print("Pre-trained model not found, creating new model")
                self.model = self.create_model()
                return False
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = self.create_model()
            return False
    
    def preprocess_face(self, face_image):
        """Preprocess face image for emotion detection"""
        try:
            # Convert to grayscale if needed
            if len(face_image.shape) == 3:
                face_image = cv2.cvtColor(face_image, cv2.COLOR_RGB2GRAY)
            
            # Resize to model input size
            face_image = cv2.resize(face_image, (self.img_size, self.img_size))
            
            # Normalize pixel values
            face_image = face_image.astype('float32') / 255.0
            
            # Reshape for model input
            face_image = np.expand_dims(face_image, axis=0)
            face_image = np.expand_dims(face_image, axis=-1)
            
            return face_image
        except Exception as e:
            print(f"Error preprocessing face: {e}")
            return None
    
    def detect_emotion(self, face_image):
        """Detect emotion from face image"""
        try:
            if self.model is None:
                return None, 0.0
            
            # Preprocess the face image
            processed_face = self.preprocess_face(face_image)
            if processed_face is None:
                return None, 0.0
            
            # Make prediction
            predictions = self.model.predict(processed_face, verbose=0)
            
            # Get the emotion with highest probability
            emotion_index = np.argmax(predictions[0])
            confidence = float(predictions[0][emotion_index])
            emotion = self.emotion_labels[emotion_index]
            
            # Only return if confidence is above threshold
            if confidence > 0.6:
                return emotion, confidence
            else:
                return 'neutral', confidence
                
        except Exception as e:
            print(f"Error detecting emotion: {e}")
            return None, 0.0
    
    def detect_faces(self, image):
        """Detect faces in image using OpenCV"""
        try:
            # Load face cascade classifier
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Convert to grayscale for face detection
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            # Detect faces
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
        """Analyze image for emotions (main function to call)"""
        try:
            # Convert base64 or bytes to numpy array if needed
            if isinstance(image_data, str):
                # Handle base64 encoded image
                import base64
                from io import BytesIO
                from PIL import Image
                
                image_data = base64.b64decode(image_data.split(',')[1])
                image = Image.open(BytesIO(image_data))
                image = np.array(image)
            elif isinstance(image_data, bytes):
                # Handle raw bytes
                from PIL import Image
                from io import BytesIO
                
                image = Image.open(BytesIO(image_data))
                image = np.array(image)
            else:
                image = image_data
            
            # Detect faces in the image
            faces = self.detect_faces(image)
            
            if not faces:
                return {
                    'success': False,
                    'message': 'No faces detected in the image',
                    'emotions': []
                }
            
            # Analyze emotion for each detected face
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
        """Save the trained model"""
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
        """Train the emotion detection model"""
        try:
            if self.model is None:
                self.model = self.create_model()
            
            # Setup callbacks
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
            
            # Train the model
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

# Utility functions for data preparation
def prepare_emotion_data(data_directory):
    """Prepare emotion data for training"""
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
    """Create and save a model optimized for web deployment"""
    model = EmotionModel()
    
    # Create the model
    model.model = model.create_model()
    
    # Save for web deployment (you can train this with your data)
    model.save_model('static/models/emotion_model.h5')
    
    # Also save as TensorFlow.js format for client-side usage
    try:
        import tensorflowjs as tfjs
        tfjs.converters.save_keras_model(model.model, 'static/models/emotion_model_js')
        print("Model saved in TensorFlow.js format")
    except ImportError:
        print("TensorFlow.js converter not installed. Install with: pip install tensorflowjs")
    
    return model

if __name__ == "__main__":
    # Create and save a basic model for the web application
    emotion_model = create_model_for_web()
    print("Emotion detection model created and saved!")

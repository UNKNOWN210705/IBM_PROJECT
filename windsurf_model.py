import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
import joblib
import matplotlib.pyplot as plt

class WindsurfPredictor:
    def __init__(self):
        self.model = None
        self.label_encoder = LabelEncoder()
        self.feature_names = ['wind_speed', 'temperature', 'humidity', 'uv_index', 
                              'cloud_cover', 'pressure', 'visibility']
        
    def load_data(self, csv_path='weather_data.csv', encoding='utf-8'):
        try:
            self.data = pd.read_csv(csv_path, encoding=encoding)
            required_cols = self.feature_names + ['safety_status']
            if not all(col in self.data.columns for col in required_cols):
                raise ValueError("Missing required columns in CSV")
            self.data = self.data.dropna()
            return self.data
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def prepare_data(self):
        X = self.data[self.feature_names]
        y = self.label_encoder.fit_transform(self.data['safety_status'])
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        return X, y
    
    def train_model(self, model_type='random_forest'):
        if model_type == 'decision_tree':
            self.model = DecisionTreeClassifier(random_state=42, max_depth=10)
        else:
            self.model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        self.model.fit(self.X_train, self.y_train)
        y_pred = self.model.predict(self.X_test)
        accuracy = accuracy_score(self.y_test, y_pred)
        print(f"Model trained. Accuracy: {accuracy:.2%}")
        print(classification_report(self.y_test, y_pred, target_names=self.label_encoder.classes_))
        return accuracy
    
    def predict_safety(self, wind_speed, temperature, humidity, uv_index, 
                      cloud_cover, pressure, visibility):
        if self.model is None:
            return "Model not trained yet!", 0.0
        inputs = [wind_speed, temperature, humidity, uv_index, cloud_cover, pressure, visibility]
        input_data = np.array([inputs])
        prediction = self.model.predict(input_data)[0]
        probability = self.model.predict_proba(input_data)[0]
        safety_status = self.label_encoder.inverse_transform([prediction])[0]
        confidence = max(probability) * 100
        return safety_status, confidence
    
    def get_safety_tips(self, safety_status, wind_speed, uv_index):
        tips = []
        if safety_status == "Safe":
            tips += [
                "Great conditions for windsurfing!",
                "Use reef-safe sunscreen to protect marine life",
                "Bring a reusable water bottle to reduce plastic waste"
            ]
        elif safety_status == "Caution":
            tips += [
                "Proceed with caution - conditions are challenging",
                "Wear proper safety gear including life jacket and helmet",
                "Stay close to shore and inform someone of your plans"
            ]
        else:
            tips += [
                "Not recommended for windsurfing today",
                "Consider indoor activities or wait for better conditions",
                "Use this time to learn about climate change impacts on weather"
            ]
        if wind_speed < 10:
            tips.append("Low wind conditions - consider a larger sail")
        elif wind_speed > 40:
            tips.append("Very strong winds - only for experienced windsurfers")
        if uv_index > 8:
            tips.append("High UV levels - protect yourself from sun exposure")
        tips.append("Climate Tip: Report unusual weather patterns to help climate research")
        return tips
    
    def plot_feature_importance(self):
        if self.model is None:
            print("Model not trained yet!")
            return
        importance = self.model.feature_importances_
        plt.figure(figsize=(10, 6))
        plt.barh(self.feature_names, importance)
        plt.xlabel('Feature Importance')
        plt.title('AquaSafe AI: Feature Importance')
        plt.tight_layout()
        plt.savefig('feature_importance.png', dpi=300, bbox_inches='tight')
        plt.show()
        return importance
    
    def save_model(self, filename='windsurf_model.pkl'):
        if self.model is None:
            print("No model to save!")
            return
        model_data = {
            'model': self.model,
            'label_encoder': self.label_encoder,
            'feature_names': self.feature_names
        }
        joblib.dump(model_data, filename)
        print(f"Model saved to {filename}")
    
    def load_model(self, filename='windsurf_model.pkl'):
        try:
            model_data = joblib.load(filename)
            if set(model_data['feature_names']) != set(self.feature_names):
                raise ValueError("Loaded model feature names mismatch")
            self.model = model_data['model']
            self.label_encoder = model_data['label_encoder']
            self.feature_names = model_data['feature_names']
            print(f"Model loaded from {filename}")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

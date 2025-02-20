### Line 149, change the model name


import sys
import numpy as np
import pickle
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QComboBox, QMessageBox)
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect
from PyQt5.QtGui import QPalette, QColor, QFont

class LiverDiseasePredictor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Liver Disease Predictor')
        
        
        # Set the background color
        self.setStyleSheet("background-color: #f0f8ff;")  # Light blue background
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setAlignment(Qt.AlignCenter)
        
        # Title
        title = QLabel('Liver Disease Prediction System')
        title.setFont(QFont('Arial', 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Create form layout
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        
        # Input fields with ranges
        self.inputs = {}
        
        # Define input fields and their ranges
        fields = {
            'Age': ('Age (18-100)', 18, 100),
            'Gender': ('Gender', None, None),  # Handled separately
            'Total_Bilirubin': ('Total Bilirubin (0.1-10.0)', 0.1, 10.0),
            'Alkaline_Phosphotase': ('Alkaline Phosphotase (20-500)', 20, 500),
            'Alamine_Aminotransferase': ('Alamine Aminotransferase (10-200)', 10, 200),
            'Aspartate_Aminotransferase': ('Aspartate Aminotransferase (10-200)', 10, 200),
            'Total_Protiens': ('Total Proteins (1.0-10.0)', 1.0, 10.0),
            'Albumin': ('Albumin (1.0-8.0)', 1.0, 8.0),
            'Albumin_and_Globulin_Ratio': ('Albumin and Globulin Ratio (0.3-3.0)', 0.3, 3.0)
        }
        
        for field, (label_text, min_val, max_val) in fields.items():
            h_layout = QHBoxLayout()
            
            label = QLabel(label_text)
            label.setFont(QFont('Arial', 12))
            label.setStyleSheet("color: #34495e;")
            h_layout.addWidget(label)
            
            if field == 'Gender':
                input_field = QComboBox()
                input_field.addItems(['Male', 'Female'])
                input_field.setStyleSheet("""
                    QComboBox {
                        padding: 5px;
                        border: 2px solid #bdc3c7;
                        border-radius: 5px;
                        background-color: white;
                    }
                """)
            else:
                input_field = QLineEdit()
                input_field.setPlaceholderText(f"Range: {min_val}-{max_val}")
                input_field.setStyleSheet("""
                    QLineEdit {
                        padding: 5px;
                        border: 2px solid #bdc3c7;
                        border-radius: 5px;
                        background-color: white;
                    }
                """)
            
            input_field.setFixedWidth(300)
            h_layout.addWidget(input_field)
            form_layout.addLayout(h_layout)
            self.inputs[field] = (input_field, min_val, max_val)
        
        layout.addLayout(form_layout)
        
        # Submit button
        self.submit_btn = QPushButton('Predict')
        self.submit_btn.setFont(QFont('Arial', 14, QFont.Bold))
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.submit_btn.clicked.connect(self.predict_disease)
        layout.addWidget(self.submit_btn, alignment=Qt.AlignCenter)
        
        # Result label
        self.result_label = QLabel('')
        self.result_label.setFont(QFont('Arial', 16, QFont.Bold))
        self.result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_label)
        
    def validate_inputs(self):
        values = {}
        for field, (input_field, min_val, max_val) in self.inputs.items():
            if field == 'Gender':
                values[field] = 1 if input_field.currentText() == 'Male' else 0
                continue
                
            try:
                value = float(input_field.text())
                if min_val is not None and max_val is not None:
                    if not (min_val <= value <= max_val):
                        QMessageBox.warning(self, 'Invalid Input',
                            f'{field.replace("_", " ")} must be between {min_val} and {max_val}')
                        return None
                values[field] = value
            except ValueError:
                QMessageBox.warning(self, 'Invalid Input',
                    f'Please enter a valid number for {field.replace("_", " ")}')
                return None
        return values
        
    def predict_disease(self):
        values = self.validate_inputs()
        if values is None:
            return
            
        # Load the model
        try:
            model = pickle.load(open('model.pkl', 'rb')) ##load the model here
        except FileNotFoundError:
            QMessageBox.critical(self, 'Error', 'Model file not found!')
            return
            
        # Prepare input array
        input_array = np.array([[
            values['Age'], values['Gender'], values['Total_Bilirubin'],
            values['Alkaline_Phosphotase'], values['Alamine_Aminotransferase'],
            values['Aspartate_Aminotransferase'], values['Total_Protiens'],
            values['Albumin'], values['Albumin_and_Globulin_Ratio']
        ]])
        
        # Suppress the feature names warning by setting feature_names_in_
        if hasattr(model, 'feature_names_in_'):
            feature_names = ['Age', 'Gender', 'Total_Bilirubin', 'Alkaline_Phosphotase',
                           'Alamine_Aminotransferase', 'Aspartate_Aminotransferase',
                           'Total_Protiens', 'Albumin', 'Albumin_and_Globulin_Ratio']
            model.feature_names_in_ = np.array(feature_names)
        
        # Make prediction
        prediction = model.predict(input_array)
        
        # Animate result
        self.animate_result(prediction[0])
        
    def animate_result(self, prediction):
        # Set result text and color
        if prediction == 2:
            result_text = "You have LIVER DISEASE"
            color = "#e74c3c"  # Red
        else:
            result_text = "You are HEALTHY"
            color = "#2ecc71"  # Green
            
        self.result_label.setText(result_text)
        self.result_label.setStyleSheet(f"color: {color};")
        
        # Create animation
        self.anim = QPropertyAnimation(self.result_label, b"geometry")
        self.anim.setDuration(1000)
        current_geometry = self.result_label.geometry()
        
        # Convert float values to integers for QRect
        center_x = int(current_geometry.x() + current_geometry.width() // 2)
        center_y = int(current_geometry.y() + current_geometry.height() // 2)
        
        # Start from small/invisible (using integers)
        start_geometry = QRect(
            center_x,
            center_y,
            0,
            0
        )
        
        self.anim.setStartValue(start_geometry)
        self.anim.setEndValue(current_geometry)
        self.anim.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LiverDiseasePredictor()
    ex.show()
    sys.exit(app.exec_())
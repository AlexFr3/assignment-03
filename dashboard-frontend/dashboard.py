"""
PyQt5 JSON Data Viewer
Prerequisiti:
 pip install pyqt5 requests matplotlib
Gestione del JSON di risposta anche se è un dict singolo (p.es. {"stato": "ok"}).
Calcolo della media se presenti i campi "sum" e "count" in ogni entry.
"""
import sys
import json
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QSlider, QSpinBox
from PyQt5.QtCore import QTimer, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Configurazione URL e payload per le richieste POST
url = "http://localhost:5006/temperature"

class JsonTableView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JSON Data Viewer")
        self.resize(800, 600)
        
        # Create main central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main vertical layout
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Widget for info section
        self.info_widget = QWidget()
        self.layout_info = QGridLayout(self.info_widget)
        
        # Create labels
        self.label_max = QLabel("Max: ")
        self.label_min = QLabel("Min: ")
        self.label_avg = QLabel("Avg: ")
        self.label_status = QLabel("Status: ")
        self.label_opening = QLabel("Opening: ")

        self.alarm_button = QPushButton("Deactivate Alarm")
        self.alarm_button.clicked.connect(self.onalarm_button_clicked)
        
        self.value_max = QLabel("None")
        self.value_min = QLabel("None")
        self.value_avg = QLabel("None")
        self.value_status = QLabel("None")
        self.value_opening = QLabel("None")

        # Add labels to info layout
        self.layout_info.addWidget(self.label_max, 0, 0)
        self.layout_info.addWidget(self.value_max, 0, 1)
        self.layout_info.addWidget(self.label_min, 1, 0)
        self.layout_info.addWidget(self.value_min, 1, 1)
        self.layout_info.addWidget(self.label_avg, 2, 0)
        self.layout_info.addWidget(self.value_avg, 2, 1)
        self.layout_info.addWidget(self.label_status, 3, 0)
        self.layout_info.addWidget(self.value_status, 3, 1)
        self.layout_info.addWidget(self.label_opening, 4, 0)
        self.layout_info.addWidget(self.value_opening, 4, 1)
        self.layout_info.addWidget(self.alarm_button, 5, 0, 1, 2)
        # Add info widget to main layout
        self.main_layout.addWidget(self.info_widget)
        
        opening_control_widget = QWidget()
        opening_layout = QHBoxLayout(opening_control_widget)
        
        self.opening_label = QLabel("Set Opening %:")
        opening_layout.addWidget(self.opening_label)
        
        # Create slider for opening percentage
        self.opening_slider = QSlider(Qt.Horizontal)
        self.opening_slider.setMinimum(0)
        self.opening_slider.setMaximum(100)
        self.opening_slider.setValue(0)
        self.opening_slider.setTickPosition(QSlider.TicksBelow)
        self.opening_slider.setTickInterval(10)
        self.opening_slider.valueChanged.connect(self.slider_value_changed)
        opening_layout.addWidget(self.opening_slider)
        
        # Create spin box for precise percentage input
        self.opening_spinbox = QSpinBox()
        self.opening_spinbox.setMinimum(0)
        self.opening_spinbox.setMaximum(100)
        self.opening_spinbox.setSuffix("%")
        self.opening_spinbox.valueChanged.connect(self.spinbox_value_changed)
        opening_layout.addWidget(self.opening_spinbox)
        
        self.send_opening_button = QPushButton("Set Opening")
        self.send_opening_button.clicked.connect(self.send_opening)
        opening_layout.addWidget(self.send_opening_button)
        
        # Add opening controls to main layout
        self.layout_info.addWidget(opening_control_widget, 6, 0, 1, 2)
        
       
        
        # Create matplotlib figure and add to main layout
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        self.main_layout.addWidget(self.canvas)
        
        # Initialize empty plot
        self.plot([])
        
        # Timer for periodic updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetch_and_update)
        self.timer.start(5000)
        
        # First immediate fetch
        QTimer.singleShot(0, self.fetch_and_update)
    
    def plot(self, dati):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(dati, label="Temperatura", color='blue')
        ax.set_title("Temperatura nel tempo")
        ax.set_xlabel("Indice")
        ax.set_ylabel("Temperatura")
        ax.grid(True)
        if dati:
            ax.set_ylim(min(dati) - 1, max(dati) + 1)
        self.canvas.draw()
    def onalarm_button_clicked(self):
        payload= {"reset": True}
        try:
            response = requests.post(url, json=payload, timeout=2)
            response.raise_for_status()
            data = response.json()
            
        except Exception as e:
            print(f"Errore fetch: {e}")

    def fetch_and_update(self):
        payload= {"reset": False}
        try:
            response = requests.post(url, json=payload, timeout=2)
            response.raise_for_status()
            data = response.json()
            print("Dati ricevuti:", data)
            
            # Update statistics labels
            if "max" in data and data["max"] != -272.15:
                self.value_max.setText(f"{data['max']:.2f}")
            
            if "min" in data and data["min"] != float('inf'):
                self.value_min.setText(f"{data['min']:.2f}")
            
            if "sum" in data and "count" in data and data["count"] > 0:
                avg = data["sum"] / data["count"]
                self.value_avg.setText(f"{avg:.4f}")
            if "status" in data:
                self.value_status.setText(data["status"])
            if "opening" in data:
                self.value_opening.setText(f'{data["opening"]}')
            # Update plot with temperature list
            if "list" in data and data["list"]:
                self.plot(data["list"])
                
        except Exception as e:
            print(f"Errore fetch: {e}")
            
    def slider_value_changed(self, value):
    # Update spin box when slider changes
        self.opening_spinbox.setValue(value)

    def spinbox_value_changed(self, value):
        # Update slider when spin box changes
        self.opening_slider.setValue(value)

    def send_opening(self):
        # Get opening percentage value
        opening_value = self.opening_spinbox.value() / 100.0  # Convert to decimal (0-1)
        payload = {"reset": False, "set_opening": opening_value}
        
        try:
            response = requests.post(url, json=payload, timeout=2)
            response.raise_for_status()
            print(f"Opening value sent: {opening_value}")
        except Exception as e:
            print(f"Error sending opening value: {e}")
        

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
    except ImportError:
        print("Errore: PyQt5 non installato. Esegui 'pip install pyqt5 requests matplotlib'")
        sys.exit(1)
    
    window = JsonTableView()
    window.show()
    sys.exit(app.exec_())
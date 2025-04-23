"""
PyQt5 JSON Data Viewer
Prerequisiti:
    pip install pyqt5 requests

Gestione del JSON di risposta anche se è un dict singolo (p.es. {"stato": "ok"}).
Calcolo della media se presenti i campi "sum" e "count" in ogni entry.
"""
import sys
import json
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QWidget, QGridLayout, QLabel, QVBoxLayout
from PyQt5.QtGui import QStandardItemModel, QStandardItem  # type: ignore
from PyQt5.QtCore import QTimer  # type: ignore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Configurazione URL e payload per le richieste POST
url = "http://localhost:5001/temperature"
payload = {"dummy": "data"}

class JsonTableView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JSON Data Viewer")
        self.resize(600, 400)

        layout = QVBoxLayout()
        layout_info = QGridLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        info_widget = QWidget()
        info_widget.setLayout(layout_info)
        self.setCentralWidget(central_widget)

        self.label_max = QLabel("Max: ")
        self.label_min = QLabel("Min: ")
        self.label_avg = QLabel("Avg: ")
        
        self.value_max = QLabel("None")
        self.value_min = QLabel("None")
        self.value_avg = QLabel("None")
        
        layout_info.addWidget(self.label_max, 0, 0)
        layout_info.addWidget(self.value_max, 0, 1)
        layout_info.addWidget(self.label_min, 1, 0)
        layout_info.addWidget(self.value_min, 1, 1)
        layout_info.addWidget(self.label_avg, 2, 0)
        layout_info.addWidget(self.value_avg, 2, 1)
        
        layout.addLayout(layout_info)
        
        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(self.canvas)
        
        
        self.plot([])
        
        

        # Timer per aggiornare periodicamente
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetch_and_update)
        self.timer.start(5000)

        # Primo fetch immediato
        QTimer.singleShot(0, self.fetch_and_update)

    def plot(self, dati):
        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)
        ax.plot(dati, label="Temperatura", color='blue')
        ax.set_title("Temperatura nel tempo")
        ax.set_xlabel("Indice")
        ax.set_ylabel("Temperatura")
        self.canvas.draw()
        
    def fetch_and_update(self):
        try:
            response = requests.post(url, json=payload, timeout=2)
            response.raise_for_status()
            data = response.json()
            print("Dati ricevuti:", data)
            
            max = data.get("max")
            min = data.get("min")
            avg = data.get("sum") / data.get("count")
            
            self.value_avg.setText(f"{avg:.4f}")
            self.value_max.setText(f"{max:.2f}")
            self.value_min.setText(f"{min:.2f}")
            
            lastTemperatures = data.get("list")
            self.plot(lastTemperatures)



        except Exception as e:
            print(f"Errore fetch: {e}")

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
    except ImportError:
        print("Errore: PyQt5 non installato. Esegui 'pip install pyqt5 requests matplotlib'")
        sys.exit(1)
    window = JsonTableView()
    window.show()
    sys.exit(app.exec_())

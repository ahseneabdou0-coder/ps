from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QPushButton, QScrollArea, QMessageBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt
import folium
import sys
import os
from extract_metadata import extract_metadata


class MapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Se Project")
        self.resize(1300, 800)

        self.map_path = os.path.abspath("map.html")
        self.m = folium.Map(location=[20, 0], zoom_start=2)
        self.m.save(self.map_path)

        self.web_view = QWebEngineView()
        self.web_view.load(QUrl.fromLocalFile(self.map_path))

        self.photo_panel = self.create_photo_panel()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.photo_panel, stretch=1)
        main_layout.addWidget(self.web_view, stretch=3)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def create_photo_panel(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)

        folder = "photos"
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.lower().endswith((".jpg", ".jpeg", ".png")):
                    path = os.path.join(folder, file)
                    data = extract_metadata(path)
                    coords = data["coordinates"]
                    time = data["time"]

                    img_label = QLabel()
                    pixmap = QPixmap(path).scaledToWidth(160, Qt.SmoothTransformation)
                    img_label.setPixmap(pixmap)

                    name_label = QLabel(f"<b>{file}</b>")
                    coords_label = QLabel(f"📍 {coords if coords else 'Not available'}")
                    time_label = QLabel(f"⏰ {time if time else 'Not available'}")

                    img_box = QVBoxLayout()
                    img_box.addWidget(img_label)
                    img_box.addWidget(name_label)
                    img_box.addWidget(coords_label)
                    img_box.addWidget(time_label)

                    item_widget = QWidget()
                    item_widget.setLayout(img_box)
                    item_widget.setStyleSheet(
                        "border: 1px solid #aaa; border-radius: 10px; padding: 8px; margin: 5px;"
                    )
                    layout.addWidget(item_widget)

        draw_button = QPushButton("Draw Path 🗺️")
        draw_button.setStyleSheet("padding: 8px; font-size: 14px;")
        draw_button.clicked.connect(self.draw_path)
        layout.addWidget(draw_button)

        scroll.setWidget(content)
        return scroll

    def draw_path(self):
        folder = "photos"
        points = []

        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.lower().endswith((".jpg", ".jpeg", ".png")):
                    path = os.path.join(folder, file)
                    data = extract_metadata(path)
                    coords = data["coordinates"]
                    time = data["time"]
                    if coords and time:
                        lat, lon = map(float, coords)
                        points.append((time, lat, lon, file))

        if len(points) < 3:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Error")
            msg.setText("Cannot draw the path. At least 3 photos must contain both GPS and time data.")
            msg.exec_()
            return

        points.sort(key=lambda x: x[0])

        start_point = [points[0][1], points[0][2]]
        m = folium.Map(location=start_point, zoom_start=10)

        for _, lat, lon, name in points:
            folium.Marker([lat, lon], popup=name).add_to(m)

        coords_list = [[p[1], p[2]] for p in points]
        folium.PolyLine(coords_list, color="blue", weight=3, opacity=0.8).add_to(m)

        m.save(self.map_path)
        self.web_view.load(QUrl.fromLocalFile(self.map_path))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapApp()
    window.show()
    sys.exit(app.exec_())

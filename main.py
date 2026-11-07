import sys
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QPainter, QPen, QAction
from PySide6.QtWidgets import (QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QPushButton, QColorDialog, QCheckBox, QComboBox, QSystemTrayIcon,
    QMenu, QGroupBox, QFormLayout)

class CrosshairOverlay(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.s = settings
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint |
                            Qt.Tool | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(QApplication.primaryScreen().geometry())
        self.show()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        c = QColor(self.s["color"])
        c.setAlpha(self.s["opacity"])
        cx, cy = self.width() // 2, self.height() // 2
        size, thick, gap = self.s["size"], self.s["thickness"], self.s["gap"]
        if self.s["outline"]:
            p.setPen(QPen(QColor(0, 0, 0, self.s["opacity"]), thick + 2, Qt.SolidLine, Qt.SquareCap))
            self.draw_shape(p, cx, cy, size, gap, thick + 2)
        p.setPen(QPen(c, thick, Qt.SolidLine, Qt.SquareCap))
        self.draw_shape(p, cx, cy, size, gap, thick)
        if self.s["dot"]:
            p.setPen(Qt.NoPen); p.setBrush(c)
            r = max(1, thick / 2)
            p.drawEllipse(QPoint(cx, cy), int(r), int(r))
        p.end()

    def draw_shape(self, p, x, y, size, gap, width):
        shape = self.s["shape"]
        if shape in ("Classic", "T-style", "Compact"):
            if shape == "T-style":
                p.drawLine(x-size, y, x-gap, y); p.drawLine(x+gap, y, x+size, y)
                p.drawLine(x, y+gap, x, y+size)
            else:
                p.drawLine(x-size, y, x-gap, y); p.drawLine(x+gap, y, x+size, y)
                p.drawLine(x, y-size, x, y-gap); p.drawLine(x, y+gap, x, y+size)
        elif shape == "Plus":
            p.drawLine(x-size, y, x+size, y); p.drawLine(x, y-size, x, y+size)
        elif shape == "Circle":
            p.setBrush(Qt.NoBrush); p.drawEllipse(QPoint(x, y), size, size)
        elif shape == "X":
            p.drawLine(x-size, y-size, x+size, y+size)
            p.drawLine(x-size, y+size, x+size, y-size)

    def refresh(self):
        self.update()

class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CrosshairX Pro")
        self.resize(440, 570)
        self.s = {"color":"#00ff66","opacity":255,"size":12,"thickness":2,"gap":5,
                  "shape":"Classic","dot":False,"outline":True}
        self.overlay = CrosshairOverlay(self.s)
        root = QWidget(); layout = QVBoxLayout(root)
        title = QLabel("CROSSHAIRX PRO"); title.setStyleSheet("font-size:24px;font-weight:800;color:#8b5cf6")
        subtitle = QLabel("Your screen. Your aim. Your style.")
        layout.addWidget(title); layout.addWidget(subtitle)
        group = QGroupBox("Crosshair settings"); form = QFormLayout(group)
        self.shape = QComboBox(); self.shape.addItems(["Classic","Compact","T-style","Plus","Circle","X"])
        self.shape.currentTextChanged.connect(self.change_shape); form.addRow("Style", self.shape)
        self.sliders = {}
        for key, label, lo, hi in [("size","Size",3,40),("thickness","Thickness",1,8),("gap","Center gap",0,20),("opacity","Opacity",40,255)]:
            row = QHBoxLayout(); slider = QSlider(Qt.Horizontal); slider.setRange(lo,hi); slider.setValue(self.s[key])
            value = QLabel(str(self.s[key])); slider.valueChanged.connect(lambda v,k=key,l=value: self.change_value(k,v,l))
            row.addWidget(slider); row.addWidget(value); form.addRow(label,row); self.sliders[key]=slider
        layout.addWidget(group)
        self.dot = QCheckBox("Center dot"); self.dot.setChecked(False); self.dot.toggled.connect(lambda v:self.set_value("dot",v))
        self.outline = QCheckBox("Black outline"); self.outline.setChecked(True); self.outline.toggled.connect(lambda v:self.set_value("outline",v))
        layout.addWidget(self.dot); layout.addWidget(self.outline)
        color = QPushButton("Choose crosshair color"); color.clicked.connect(self.choose_color); layout.addWidget(color)
        presets = QHBoxLayout()
        for name, col in [("Green","#00ff66"),("Cyan","#00e5ff"),("Red","#ff3333"),("White","#ffffff"),("Yellow","#ffe600")]:
            b=QPushButton(name); b.clicked.connect(lambda checked=False,c=col:self.set_color(c)); presets.addWidget(b)
        layout.addLayout(presets)
        toggle = QPushButton("Hide / show overlay"); toggle.clicked.connect(self.toggle_overlay); layout.addWidget(toggle)
        note = QLabel("Tip: Use the Hide / show button or the tray icon to control the overlay.\nDesigned as a visual overlay; it does not interact with games.")
        note.setWordWrap(True); note.setStyleSheet("color:#888;padding:8px"); layout.addWidget(note)
        layout.addStretch(); self.setCentralWidget(root)
        self.setStyleSheet("QMainWindow,QWidget{background:#171923;color:#f4f4f5} QGroupBox{border:1px solid #444;padding:10px;margin-top:8px} QPushButton{background:#292d3e;border:1px solid #555;padding:8px;border-radius:6px} QPushButton:hover{background:#45405f}")
        self.tray = QSystemTrayIcon(self)
        self.tray.setToolTip("CrosshairX Pro")
        menu=QMenu(); show=QAction("Show settings",self); show.triggered.connect(self.show)
        toggle_action=QAction("Hide / show overlay",self); toggle_action.triggered.connect(self.toggle_overlay)
        quit_action=QAction("Quit",self); quit_action.triggered.connect(QApplication.quit)
        menu.addAction(show); menu.addAction(toggle_action); menu.addSeparator(); menu.addAction(quit_action)
        self.tray.setContextMenu(menu); self.tray.show()

    def set_value(self,k,v): self.s[k]=v; self.overlay.refresh()
    def change_value(self,k,v,label): label.setText(str(v)); self.set_value(k,v)
    def change_shape(self,v): self.set_value("shape",v)
    def set_color(self,c): self.s["color"]=c; self.overlay.refresh()
    def choose_color(self):
        c=QColorDialog.getColor(QColor(self.s["color"]),self,"Crosshair color")
        if c.isValid(): self.set_color(c.name())
    def toggle_overlay(self):
        if self.overlay.isVisible(): self.overlay.hide()
        else: self.overlay.show()

    def closeEvent(self,event):
        self.overlay.hide(); self.tray.hide(); event.accept()

if __name__ == "__main__":
    app=QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    w=SettingsWindow(); w.show()
    sys.exit(app.exec())

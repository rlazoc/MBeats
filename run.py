import sys
from main import MBeats
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)
app.setStyle('Fusion')
window = MBeats()
sys.exit(app.exec_())
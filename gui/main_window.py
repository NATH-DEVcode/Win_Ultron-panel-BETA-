import sys
import psutil

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QProgressBar,
    QFrame,
)


RED = "#ff2020"
DARK_RED = "#8b0000"
CYAN = "#00e5ff"
GREEN = "#00ff66"
YELLOW = "#ffd000"
WHITE = "#eeeeee"
GRAY = "#777777"
BLACK = "#050505"
PANEL = "#0b0b0b"


class Panel(QFrame):

    def __init__(self, title):

        super().__init__()

        self.setObjectName("panel")

        layout = QVBoxLayout(self)

        title_label = QLabel(title)

        title_label.setObjectName("panelTitle")

        layout.addWidget(title_label)


class ULTRONWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "ULTRON PANEL"
        )

        self.resize(
            1400,
            850
        )

        self.build_ui()

        self.start_monitor()


    def build_ui(self):

        central = QWidget()

        self.setCentralWidget(
            central
        )

        main = QVBoxLayout(
            central
        )

        main.setSpacing(10)

        # =========================
        # HEADER
        # =========================

        header = QFrame()

        header.setObjectName(
            "header"
        )

        header_layout = QHBoxLayout(
            header
        )

        title = QLabel(
            "SYSTEM LOCKDOWN"
        )

        title.setObjectName(
            "headerTitle"
        )

        ready = QLabel(
            "🛡 JARVIS READY"
        )

        ready.setObjectName(
            "ready"
        )

        header_layout.addWidget(
            title
        )

        header_layout.addStretch()

        header_layout.addWidget(
            ready
        )

        main.addWidget(
            header
        )


        # =========================
        # LOCKDOWN
        # =========================

        lockdown = QLabel(
            "⚠  LOCKDOWN ACTIVE  ⚠"
        )

        lockdown.setAlignment(
            Qt.AlignCenter
        )

        lockdown.setObjectName(
            "lockdown"
        )

        main.addWidget(
            lockdown
        )


        subtitle = QLabel(
            "TODOS LOS SISTEMAS PROTEGIDOS  •  "
            "AMENAZAS NEUTRALIZADAS  •  "
            "ACCESO DENEGADO"
        )

        subtitle.setAlignment(
            Qt.AlignCenter
        )

        subtitle.setObjectName(
            "subtitle"
        )

        main.addWidget(
            subtitle
        )


        # =========================
        # TOP PANELS
        # =========================

        top = QHBoxLayout()

        # SECURITY

        security = Panel(
            "SECURITY STATUS"
        )

        security_layout = security.layout()

        self.security_items = []

        items = [
            ("SECURITY LEVEL", "HIGH"),
            ("EXTERNAL ACCESS", "MONITORED"),
            ("NETWORK", "RESTRICTED"),
            ("USER PRIVILEGES", "STANDARD"),
            ("SYSTEM PROTECTION", "ACTIVE"),
        ]

        for name, value in items:

            label = QLabel(
                f"{name}:  {value}"
            )

            label.setObjectName(
                "status"
            )

            security_layout.addWidget(
                label
            )

            self.security_items.append(
                label
            )

        top.addWidget(
            security
        )


        # CENTER

        center = Panel(
            "SYSTEM CORE"
        )

        center_layout = center.layout()

        core = QLabel(
            "◉\n"
            "◉ 🔒 ◉\n"
            "◉"
        )

        core.setAlignment(
            Qt.AlignCenter
        )

        core.setObjectName(
            "core"
        )

        center_layout.addWidget(
            core
        )

        top.addWidget(
            center
        )


        # THREAT

        threat = Panel(
            "THREAT LEVEL"
        )

        threat_layout = threat.layout()

        threat_label = QLabel(
            "CONTROLLED"
        )

        threat_label.setAlignment(
            Qt.AlignCenter
        )

        threat_label.setObjectName(
            "threat"
        )

        threat_layout.addWidget(
            threat_label
        )

        world = QLabel(
            "       🌎\n"
            "   •        •\n"
            "       •"
        )

        world.setAlignment(
            Qt.AlignCenter
        )

        world.setObjectName(
            "world"
        )

        threat_layout.addWidget(
            world
        )

        live = QLabel(
            "● LIVE MONITORING"
        )

        live.setAlignment(
            Qt.AlignCenter
        )

        live.setObjectName(
            "live"
        )

        threat_layout.addWidget(
            live
        )

        top.addWidget(
            threat
        )

        main.addLayout(
            top
        )


        # =========================
        # PROTOCOL
        # =========================

        protocol = Panel(
            "LOCKDOWN PROTOCOL"
        )

        protocol_layout = protocol.layout()

        self.progress = QProgressBar()

        self.progress.setValue(
            20
        )

        self.progress.setTextVisible(
            True
        )

        self.progress.setFormat(
            "%p%"
        )

        protocol_layout.addWidget(
            self.progress
        )

        self.protocol_status = QLabel(
            "9s elapsed  •  35s estimated  •  RUNNING"
        )

        protocol_layout.addWidget(
            self.protocol_status
        )

        main.addWidget(
            protocol
        )


        # =========================
        # BOTTOM
        # =========================

        bottom = QHBoxLayout()


        # LOGS

        logs = Panel(
            "SYSTEM LOGS  •  LIVE"
        )

        logs_layout = logs.layout()

        self.logs = QLabel(
            "12:01  FIREWALL INITIALIZED\n"
            "12:02  SECURITY PROTOCOL OK\n"
            "12:03  COLLECTORS INITIALIZED\n"
            "12:04  NETWORK MONITOR OK\n"
            "12:05  ⚠ ATTENTION REQUIRED"
        )

        self.logs.setObjectName(
            "logs"
        )

        logs_layout.addWidget(
            self.logs
        )

        bottom.addWidget(
            logs
        )


        # METRICS

        metrics = Panel(
            "SYSTEM METRICS"
        )

        metrics_layout = metrics.layout()

        self.cpu = QLabel()
        self.memory = QLabel()
        self.disk = QLabel()

        metrics_layout.addWidget(
            self.cpu
        )

        metrics_layout.addWidget(
            self.memory
        )

        metrics_layout.addWidget(
            self.disk
        )

        network = QLabel(
            "NETWORK      ACTIVE"
        )

        metrics_layout.addWidget(
            network
        )

        bottom.addWidget(
            metrics
        )

        main.addLayout(
            bottom
        )


    def start_monitor(self):

        self.timer = QTimer()

        self.timer.timeout.connect(
            self.update_metrics
        )

        self.timer.start(
            1000
        )

        self.update_metrics()


    def update_metrics(self):

        cpu = psutil.cpu_percent()

        memory = psutil.virtual_memory().percent

        disk = psutil.disk_usage(
            "/"
        ).percent

        self.cpu.setText(
            f"CPU          {cpu:.0f}%"
        )

        self.memory.setText(
            f"MEMORY       {memory:.0f}%"
        )

        self.disk.setText(
            f"DISK         {disk:.0f}%"
        )


def main():

    app = QApplication(
        sys.argv
    )

    app.setStyleSheet("""

        QWidget {
            background: #050505;
            color: #eeeeee;
            font-family: monospace;
        }

        #header {
            background: #120000;
            border: 1px solid #ff2020;
        }

        #headerTitle {
            color: #00e5ff;
            font-size: 25px;
            font-weight: bold;
        }

        #ready {
            color: #00ff66;
            font-size: 18px;
            font-weight: bold;
        }

        #lockdown {
            color: #ff2020;
            font-size: 38px;
            font-weight: bold;
            padding: 15px;
        }

        #subtitle {
            color: #777777;
            font-size: 12px;
        }

        #panel {
            background: #0b0b0b;
            border: 1px solid #8b0000;
            padding: 8px;
        }

        #panelTitle {
            color: #00e5ff;
            font-size: 15px;
            font-weight: bold;
        }

        #status {
            color: #eeeeee;
            padding: 5px;
        }

        #core {
            color: #ff2020;
            font-size: 45px;
        }

        #threat {
            color: #00ff66;
            font-size: 25px;
            font-weight: bold;
        }

        #world {
            color: #00ff66;
            font-size: 25px;
        }

        #live {
            color: #00ff66;
            font-weight: bold;
        }

        #logs {
            color: #00e5ff;
            font-size: 13px;
        }

        QProgressBar {
            border: 1px solid #8b0000;
            background: #050505;
            height: 20px;
        }

        QProgressBar::chunk {
            background: #ff2020;
        }

    """)

    window = ULTRONWindow()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()

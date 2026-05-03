"""
GUI Application Module
PyQt5-based desktop application for the XONOMO Anti-Detect Browser.

Features:
- Profile management with 1.5x row/text size
- No timezone text in profile rows
- Search profiles by name or number
- Android screen mode with proper mouse scroll support
- Full Screen / Android Screen feature swap (corrected)
- License enforcement on profile create/run
"""

import sys
import os
import json
import time
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QDialog, QFormLayout, QMessageBox, QSplitter, QFrame,
    QScrollArea, QGroupBox, QCheckBox, QTabWidget, QStatusBar,
    QAction, QMenu, QToolBar, QSizePolicy, QSpacerItem,
    QInputDialog, QFileDialog, QProgressBar,
)
from PyQt5.QtCore import (
    Qt, QTimer, QSize, QThread, pyqtSignal, QUrl, QEvent,
)
from PyQt5.QtGui import (
    QFont, QColor, QPalette, QIcon, QPixmap, QPainter,
    QLinearGradient, QBrush, QCursor, QWheelEvent,
)

from profile_manager import ProfileManager
from license_manager import LicenseManager
from fingerprint_generator import FingerprintGenerator
from browser_core import BrowserLauncher, BinaryPatcher, JSProtection


# ══════════════════════════════════════════════════════════════
#  Color Theme
# ══════════════════════════════════════════════════════════════

DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #0a0e1a;
    color: #e2e8f0;
    font-family: 'Segoe UI', 'Arial', sans-serif;
}

QLabel {
    color: #e2e8f0;
}

QPushButton {
    background-color: #1e293b;
    color: #e2e8f0;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 14px;
}
QPushButton:hover {
    background-color: #334155;
    border-color: #6366f1;
}
QPushButton:pressed {
    background-color: #4338ca;
}
QPushButton:disabled {
    background-color: #1e293b;
    color: #475569;
    border-color: #1e293b;
}

QPushButton#btnCreate {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #4338ca, stop:1 #6366f1);
    color: white;
    border: none;
    font-size: 15px;
    padding: 12px 24px;
}
QPushButton#btnCreate:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #4f46e5, stop:1 #818cf8);
}

QPushButton#btnRun {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #065f46, stop:1 #10b981);
    color: white;
    border: none;
}
QPushButton#btnRun:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #047857, stop:1 #34d399);
}

QPushButton#btnStop {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #9f1239, stop:1 #f43f5e);
    color: white;
    border: none;
}

QPushButton#btnDelete {
    background: #1e293b;
    color: #f43f5e;
    border: 1px solid #f43f5e;
}

QPushButton#btnPatch {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #78350f, stop:1 #f59e0b);
    color: white;
    border: none;
}

QLineEdit {
    background-color: #0f172a;
    color: #e2e8f0;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 14px;
    selection-background-color: #6366f1;
}
QLineEdit:focus {
    border-color: #6366f1;
}
QLineEdit::placeholder {
    color: #475569;
}

QComboBox {
    background-color: #0f172a;
    color: #e2e8f0;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 14px;
}
QComboBox:focus {
    border-color: #6366f1;
}
QComboBox QAbstractItemView {
    background-color: #0f172a;
    color: #e2e8f0;
    border: 1px solid #334155;
    selection-background-color: #4338ca;
}

QTableWidget {
    background-color: #0a0e1a;
    color: #e2e8f0;
    border: 1px solid #1e293b;
    border-radius: 10px;
    gridline-color: #1e293b;
    selection-background-color: rgba(99, 102, 241, 0.2);
    selection-color: #e2e8f0;
}
QTableWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid #1e293b;
}
QTableWidget::item:selected {
    background-color: rgba(99, 102, 241, 0.15);
}

QHeaderView::section {
    background-color: #111827;
    color: #94a3b8;
    border: none;
    border-bottom: 2px solid #6366f1;
    padding: 10px 12px;
    font-weight: 700;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

QScrollBar:vertical {
    background: #0a0e1a;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #334155;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #6366f1;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: #0a0e1a;
    height: 10px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal {
    background: #334155;
    border-radius: 5px;
    min-width: 30px;
}

QTabWidget::pane {
    border: 1px solid #1e293b;
    border-radius: 10px;
    background: #0a0e1a;
}
QTabBar::tab {
    background: #111827;
    color: #94a3b8;
    border: 1px solid #1e293b;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 10px 24px;
    font-weight: 600;
    font-size: 13px;
}
QTabBar::tab:selected {
    background: #0a0e1a;
    color: #6366f1;
    border-color: #6366f1;
}

QGroupBox {
    border: 1px solid #1e293b;
    border-radius: 10px;
    margin-top: 12px;
    padding-top: 18px;
    font-weight: 700;
    color: #94a3b8;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
}

QStatusBar {
    background: #111827;
    color: #94a3b8;
    border-top: 1px solid #1e293b;
    font-size: 12px;
}

QTextEdit {
    background-color: #0f172a;
    color: #e2e8f0;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}

QProgressBar {
    background: #1e293b;
    border: none;
    border-radius: 6px;
    height: 8px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4338ca, stop:1 #6366f1);
    border-radius: 6px;
}

QMessageBox {
    background-color: #0a0e1a;
}
QMessageBox QLabel {
    color: #e2e8f0;
    font-size: 14px;
}
"""


# ══════════════════════════════════════════════════════════════
#  Browser Launch Thread
# ══════════════════════════════════════════════════════════════

class BrowserThread(QThread):
    """Thread for launching browser without blocking GUI."""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, profile_dir, fingerprint, proxy=None):
        super().__init__()
        self.profile_dir = profile_dir
        self.fingerprint = fingerprint
        self.proxy = proxy
        self.launcher = None

    def run(self):
        try:
            self.launcher = BrowserLauncher(
                self.profile_dir, self.fingerprint, self.proxy
            )
            result = self.launcher.launch()
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


# ══════════════════════════════════════════════════════════════
#  Create Profile Dialog
# ══════════════════════════════════════════════════════════════

class CreateProfileDialog(QDialog):
    """Dialog for creating a new browser profile."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Profile")
        self.setMinimumWidth(450)
        self.setStyleSheet(DARK_STYLE)

        layout = QFormLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Create New Profile")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #a5b4fc; margin-bottom: 8px;")
        layout.addRow(title)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter profile name...")
        layout.addRow("Profile Name:", self.name_input)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["desktop", "android"])
        layout.addRow("Mode:", self.mode_combo)

        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("socks5://user:pass@host:port (optional)")
        layout.addRow("Proxy:", self.proxy_input)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Notes (optional)...")
        self.notes_input.setMaximumHeight(80)
        layout.addRow("Notes:", self.notes_input)

        btn_layout = QHBoxLayout()
        self.btn_create = QPushButton("Create Profile")
        self.btn_create.setObjectName("btnCreate")
        self.btn_create.clicked.connect(self.accept)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_create)
        layout.addRow(btn_layout)

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "mode": self.mode_combo.currentText(),
            "proxy": self.proxy_input.text().strip(),
            "notes": self.notes_input.toPlainText().strip(),
        }


# ══════════════════════════════════════════════════════════════
#  License Dialog
# ══════════════════════════════════════════════════════════════

class LicenseDialog(QDialog):
    """Dialog for license activation."""

    def __init__(self, license_mgr: LicenseManager, parent=None):
        super().__init__(parent)
        self.license_mgr = license_mgr
        self.setWindowTitle("License Activation")
        self.setMinimumWidth(500)
        self.setStyleSheet(DARK_STYLE)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("License Activation")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #a5b4fc;")
        layout.addWidget(title)

        # Current status
        info = self.license_mgr.get_license_info()
        status_label = QLabel(f"Status: {info['status'].upper()}")
        if info["status"] == "valid":
            status_label.setStyleSheet("color: #10b981; font-weight: bold; font-size: 14px;")
        else:
            status_label.setStyleSheet("color: #f43f5e; font-weight: bold; font-size: 14px;")
        layout.addWidget(status_label)

        hw_label = QLabel(f"Hardware ID: {info['hardware_id'][:16]}...")
        hw_label.setStyleSheet("color: #94a3b8; font-family: monospace;")
        layout.addWidget(hw_label)

        if info.get("expiry_date"):
            exp_label = QLabel(f"Expiry: {info['expiry_date']}")
            exp_label.setStyleSheet("color: #f59e0b;")
            layout.addWidget(exp_label)

        if info.get("reason"):
            reason_label = QLabel(info["reason"])
            reason_label.setStyleSheet("color: #94a3b8;")
            reason_label.setWordWrap(True)
            layout.addWidget(reason_label)

        layout.addSpacing(12)

        # Key input
        key_label = QLabel("License Key:")
        key_label.setStyleSheet("font-weight: 600; font-size: 13px;")
        layout.addWidget(key_label)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("XONOMO-XXXXX-XXXXX-XXXXX")
        layout.addWidget(self.key_input)

        btn_layout = QHBoxLayout()
        self.btn_activate = QPushButton("Activate")
        self.btn_activate.setObjectName("btnCreate")
        self.btn_activate.clicked.connect(self._activate)

        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_close)
        btn_layout.addWidget(self.btn_activate)
        layout.addLayout(btn_layout)

        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)

    def _activate(self):
        key = self.key_input.text().strip()
        if not key:
            self.result_label.setText("Please enter a license key.")
            self.result_label.setStyleSheet("color: #f43f5e;")
            return

        result = self.license_mgr.activate_license(key)
        if result.get("success"):
            self.result_label.setText("License activated successfully!")
            self.result_label.setStyleSheet("color: #10b981; font-weight: bold;")
        else:
            self.result_label.setText(f"Error: {result.get('error', 'Unknown error')}")
            self.result_label.setStyleSheet("color: #f43f5e;")


# ══════════════════════════════════════════════════════════════
#  Android Screen Widget (with proper scroll support)
# ══════════════════════════════════════════════════════════════

class AndroidScreenWidget(QFrame):
    """
    Android-style screen frame with proper mouse wheel scrolling.
    Shows browser in a mobile-sized viewport.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            AndroidScreenWidget {
                background: #000000;
                border: 3px solid #333333;
                border-radius: 28px;
            }
        """)
        self.setMinimumSize(430, 880)
        self.setMaximumSize(430, 880)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 40, 8, 40)

        # Status bar area
        status_bar = QHBoxLayout()
        time_label = QLabel(datetime.now().strftime("%H:%M"))
        time_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
        status_bar.addWidget(time_label)
        status_bar.addStretch()
        battery_label = QLabel("100%")
        battery_label.setStyleSheet("color: white; font-size: 12px;")
        status_bar.addWidget(battery_label)
        layout.addLayout(status_bar)

        # Scroll area for content — this enables mouse wheel scrolling
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: #111111;
                border: none;
                border-radius: 12px;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 6px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255,255,255,0.3);
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(12, 12, 12, 12)
        self.content_layout.setSpacing(8)

        self.info_label = QLabel("Android Browser Ready\nProfile will render here")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("""
            color: #94a3b8;
            font-size: 14px;
            padding: 40px;
        """)
        self.content_layout.addWidget(self.info_label)

        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)

        # Navigation bar
        nav_bar = QHBoxLayout()
        nav_bar.setSpacing(30)
        for icon_text in ["◁", "○", "□"]:
            btn = QPushButton(icon_text)
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #666;
                    border: none;
                    font-size: 20px;
                }
                QPushButton:hover { color: white; }
            """)
            nav_bar.addWidget(btn, alignment=Qt.AlignCenter)
        layout.addLayout(nav_bar)

    def wheelEvent(self, event: QWheelEvent):
        """Forward mouse wheel events to the scroll area for proper scrolling."""
        if self.scroll_area:
            scroll_bar = self.scroll_area.verticalScrollBar()
            delta = event.angleDelta().y()
            scroll_bar.setValue(scroll_bar.value() - delta)
            event.accept()
        else:
            super().wheelEvent(event)

    def set_profile_info(self, profile_data: dict):
        """Display profile info in the Android screen."""
        # Clear existing content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        fp = profile_data.get("fingerprint_data", {})
        nav = fp.get("navigator", {})
        screen = fp.get("screen", {})
        webgl = fp.get("webgl", {})

        # Header
        header = QLabel(f"Profile #{profile_data.get('profile_number', '?')}")
        header.setStyleSheet("color: #a5b4fc; font-size: 18px; font-weight: bold; padding: 8px;")
        header.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(header)

        name_label = QLabel(profile_data.get("name", ""))
        name_label.setStyleSheet("color: #e2e8f0; font-size: 16px; padding: 4px;")
        name_label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(name_label)

        # Info cards
        info_items = [
            ("Device", nav.get("user_agent", "")[:50] + "..."),
            ("Screen", f"{screen.get('width', 0)}x{screen.get('height', 0)}"),
            ("DPR", str(screen.get("device_pixel_ratio", 1))),
            ("GPU", webgl.get("gpu_renderer", "")[:40]),
            ("Language", nav.get("language", "")),
            ("Touch Points", str(nav.get("max_touch_points", 0))),
            ("Proxy", profile_data.get("proxy", "None") or "None"),
        ]

        for label_text, value_text in info_items:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background: #1a1a2e;
                    border: 1px solid #2a2a4a;
                    border-radius: 8px;
                    padding: 8px;
                }
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 6, 10, 6)
            card_layout.setSpacing(2)

            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #6366f1; font-size: 11px; font-weight: bold;")
            card_layout.addWidget(lbl)

            val = QLabel(value_text)
            val.setStyleSheet("color: #e2e8f0; font-size: 13px;")
            val.setWordWrap(True)
            card_layout.addWidget(val)

            self.content_layout.addWidget(card)

        self.content_layout.addStretch()


# ══════════════════════════════════════════════════════════════
#  Main Application Window
# ══════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    """Main application window for XONOMO Anti-Detect Browser."""

    # Base row height (will be multiplied by 1.5x)
    BASE_ROW_HEIGHT = 36
    ROW_SCALE = 1.5
    SCALED_ROW_HEIGHT = int(BASE_ROW_HEIGHT * ROW_SCALE)

    # Base font size (will be multiplied by 1.5x)
    BASE_FONT_SIZE = 10
    SCALED_FONT_SIZE = int(BASE_FONT_SIZE * ROW_SCALE)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("XONOMO Anti-Detect Browser")
        self.setMinimumSize(1200, 750)
        self.setStyleSheet(DARK_STYLE)

        self.profile_mgr = ProfileManager()
        self.license_mgr = LicenseManager()
        self.running_browsers = {}  # profile_id -> BrowserThread

        self._build_ui()
        self._refresh_profiles()
        self._update_license_status()

        # Periodic license check
        self.license_timer = QTimer()
        self.license_timer.timeout.connect(self._update_license_status)
        self.license_timer.start(60000)

    def _build_ui(self):
        """Build the main UI layout."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(12)

        # ── Top Bar ──
        top_bar = QHBoxLayout()

        logo_label = QLabel("XONOMO")
        logo_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        logo_label.setStyleSheet("""
            color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #a5b4fc, stop:1 #c084fc);
        """)
        top_bar.addWidget(logo_label)

        subtitle = QLabel("Anti-Detect Browser")
        subtitle.setStyleSheet("color: #64748b; font-size: 14px; margin-left: 8px;")
        top_bar.addWidget(subtitle)

        top_bar.addStretch()

        # License status
        self.license_indicator = QLabel("● Licensed")
        self.license_indicator.setStyleSheet("color: #10b981; font-weight: bold; font-size: 13px;")
        top_bar.addWidget(self.license_indicator)

        btn_license = QPushButton("License")
        btn_license.setFixedWidth(100)
        btn_license.clicked.connect(self._show_license_dialog)
        top_bar.addWidget(btn_license)

        btn_patch = QPushButton("Binary Patch")
        btn_patch.setObjectName("btnPatch")
        btn_patch.setFixedWidth(120)
        btn_patch.clicked.connect(self._run_binary_patch)
        top_bar.addWidget(btn_patch)

        main_layout.addLayout(top_bar)

        # ── Action Bar ──
        action_bar = QHBoxLayout()

        self.btn_create = QPushButton("+ Create Profile")
        self.btn_create.setObjectName("btnCreate")
        self.btn_create.setFixedHeight(44)
        self.btn_create.clicked.connect(self._create_profile)
        action_bar.addWidget(self.btn_create)

        # Saved Profiles label
        saved_label = QLabel("Saved Profiles")
        saved_label.setStyleSheet("color: #94a3b8; font-weight: 700; font-size: 14px; margin-left: 12px;")
        action_bar.addWidget(saved_label)

        action_bar.addStretch()

        # Search Profile — positioned on the right side of saved profiles
        search_label = QLabel("Search Profile:")
        search_label.setStyleSheet("color: #94a3b8; font-size: 13px;")
        action_bar.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Name or Number...")
        self.search_input.setFixedWidth(220)
        self.search_input.setFixedHeight(38)
        self.search_input.textChanged.connect(self._on_search_changed)
        action_bar.addWidget(self.search_input)

        main_layout.addLayout(action_bar)

        # ── Profile Table ──
        # Columns: #, Name, Mode, Status, Proxy, Actions
        # NO timezone column as requested
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "#", "Profile Name", "Mode", "Status", "Proxy", "Actions"
        ])

        # Apply 1.5x font size to table
        table_font = QFont("Segoe UI", self.SCALED_FONT_SIZE)
        self.table.setFont(table_font)

        header = self.table.horizontalHeader()
        header.setFont(QFont("Segoe UI", int(12 * self.ROW_SCALE), QFont.Bold))
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Fixed)

        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(2, 110)
        self.table.setColumnWidth(3, 110)
        self.table.setColumnWidth(5, 280)

        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
        self.table.setShowGrid(False)

        # Row height 1.5x
        self.table.verticalHeader().setDefaultSectionSize(self.SCALED_ROW_HEIGHT)

        main_layout.addWidget(self.table)

        # ── Bottom Bar with screen mode buttons ──
        bottom_bar = QHBoxLayout()

        # Full Screen button — launches in full desktop mode
        self.btn_fullscreen = QPushButton("Full Screen")
        self.btn_fullscreen.setFixedHeight(40)
        self.btn_fullscreen.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e1b4b, stop:1 #4f46e5);
                color: white; border: none; border-radius: 8px;
                font-weight: bold; font-size: 14px; padding: 0 24px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #312e81, stop:1 #6366f1);
            }
        """)
        self.btn_fullscreen.clicked.connect(self._launch_fullscreen)
        bottom_bar.addWidget(self.btn_fullscreen)

        # Android Screen button — launches in android emulated mode
        self.btn_android = QPushButton("Android Screen")
        self.btn_android.setFixedHeight(40)
        self.btn_android.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #065f46, stop:1 #10b981);
                color: white; border: none; border-radius: 8px;
                font-weight: bold; font-size: 14px; padding: 0 24px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #047857, stop:1 #34d399);
            }
        """)
        self.btn_android.clicked.connect(self._launch_android_screen)
        bottom_bar.addWidget(self.btn_android)

        bottom_bar.addStretch()

        # Profile count
        self.count_label = QLabel("0 profiles")
        self.count_label.setStyleSheet("color: #64748b; font-size: 13px;")
        bottom_bar.addWidget(self.count_label)

        main_layout.addLayout(bottom_bar)

        # ── Status Bar ──
        self.statusBar().showMessage("Ready")

    # ── Profile Table Management ──────────────────────────

    def _refresh_profiles(self, profiles=None):
        """Refresh the profile table."""
        if profiles is None:
            profiles = self.profile_mgr.get_all_profiles()

        self.table.setRowCount(len(profiles))

        row_font = QFont("Segoe UI", self.SCALED_FONT_SIZE)

        for row, p in enumerate(profiles):
            self.table.setRowHeight(row, self.SCALED_ROW_HEIGHT)

            # Column 0: Profile Number
            num_item = QTableWidgetItem(str(p["profile_number"]))
            num_item.setFont(QFont("Space Mono", self.SCALED_FONT_SIZE, QFont.Bold))
            num_item.setForeground(QColor("#a5b4fc"))
            num_item.setTextAlignment(Qt.AlignCenter)
            num_item.setData(Qt.UserRole, p["id"])
            self.table.setItem(row, 0, num_item)

            # Column 1: Name (NO timezone text)
            name_item = QTableWidgetItem(p["name"])
            name_item.setFont(row_font)
            self.table.setItem(row, 1, name_item)

            # Column 2: Mode
            mode_text = p["mode"].capitalize()
            mode_item = QTableWidgetItem(mode_text)
            mode_item.setFont(row_font)
            mode_item.setTextAlignment(Qt.AlignCenter)
            if p["mode"] == "android":
                mode_item.setForeground(QColor("#22d3ee"))
            else:
                mode_item.setForeground(QColor("#818cf8"))
            self.table.setItem(row, 2, mode_item)

            # Column 3: Status
            status = p.get("status", "stopped")
            status_item = QTableWidgetItem(status.capitalize())
            status_item.setFont(row_font)
            status_item.setTextAlignment(Qt.AlignCenter)
            if status == "running":
                status_item.setForeground(QColor("#10b981"))
            else:
                status_item.setForeground(QColor("#64748b"))
            self.table.setItem(row, 3, status_item)

            # Column 4: Proxy
            proxy_text = p.get("proxy", "") or "Direct"
            proxy_item = QTableWidgetItem(proxy_text)
            proxy_item.setFont(QFont("Segoe UI", self.SCALED_FONT_SIZE - 1))
            proxy_item.setForeground(QColor("#94a3b8"))
            self.table.setItem(row, 4, proxy_item)

            # Column 5: Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 2, 4, 2)
            action_layout.setSpacing(6)

            btn_run = QPushButton("Run")
            btn_run.setObjectName("btnRun")
            btn_run.setFixedSize(int(70 * self.ROW_SCALE), int(28 * self.ROW_SCALE))
            btn_run.setFont(QFont("Segoe UI", int(10 * self.ROW_SCALE), QFont.Bold))
            btn_run.setProperty("profile_id", p["id"])
            btn_run.clicked.connect(lambda checked, pid=p["id"]: self._run_profile(pid))

            btn_stop = QPushButton("Stop")
            btn_stop.setObjectName("btnStop")
            btn_stop.setFixedSize(int(70 * self.ROW_SCALE), int(28 * self.ROW_SCALE))
            btn_stop.setFont(QFont("Segoe UI", int(10 * self.ROW_SCALE), QFont.Bold))
            btn_stop.setEnabled(status == "running")
            btn_stop.clicked.connect(lambda checked, pid=p["id"]: self._stop_profile(pid))

            btn_del = QPushButton("Delete")
            btn_del.setObjectName("btnDelete")
            btn_del.setFixedSize(int(70 * self.ROW_SCALE), int(28 * self.ROW_SCALE))
            btn_del.setFont(QFont("Segoe UI", int(10 * self.ROW_SCALE), QFont.Bold))
            btn_del.clicked.connect(lambda checked, pid=p["id"]: self._delete_profile(pid))

            action_layout.addWidget(btn_run)
            action_layout.addWidget(btn_stop)
            action_layout.addWidget(btn_del)

            self.table.setCellWidget(row, 5, action_widget)

        self.count_label.setText(f"{len(profiles)} profiles")

    def _on_search_changed(self, text):
        """Handle search input changes."""
        if text.strip():
            results = self.profile_mgr.search_profiles(text.strip())
            self._refresh_profiles(results)
        else:
            self._refresh_profiles()

    # ── Profile CRUD ──────────────────────────────────────

    def _create_profile(self):
        """Create a new profile with license check."""
        can_create, reason = self.license_mgr.can_create_profile()
        if not can_create:
            QMessageBox.warning(
                self, "License Required",
                f"Cannot create profile:\n{reason}"
            )
            return

        dialog = CreateProfileDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["name"]:
                QMessageBox.warning(self, "Error", "Profile name is required.")
                return

            profile = self.profile_mgr.create_profile(
                name=data["name"],
                mode=data["mode"],
                proxy=data["proxy"],
                notes=data["notes"],
            )
            self._refresh_profiles()
            self.statusBar().showMessage(
                f"Profile #{profile['profile_number']} '{data['name']}' created", 5000
            )

    def _run_profile(self, profile_id: int):
        """Launch a browser profile with license check."""
        can_run, reason = self.license_mgr.can_run_profile()
        if not can_run:
            QMessageBox.warning(
                self, "License Required",
                f"Cannot run profile:\n{reason}"
            )
            return

        profile = self.profile_mgr.get_profile(profile_id)
        if not profile:
            return

        fp = profile.get("fingerprint_data", {})
        profile_dir = self.profile_mgr.get_profile_dir(profile["profile_number"])

        thread = BrowserThread(profile_dir, fp, profile.get("proxy"))
        thread.finished.connect(
            lambda result, pid=profile_id: self._on_browser_launched(pid, result)
        )
        thread.error.connect(
            lambda err, pid=profile_id: self._on_browser_error(pid, err)
        )

        self.running_browsers[profile_id] = thread
        self.profile_mgr.set_profile_status(profile_id, "running")
        thread.start()

        self._refresh_profiles()
        self.statusBar().showMessage(
            f"Launching profile #{profile['profile_number']}...", 5000
        )

    def _on_browser_launched(self, profile_id, result):
        """Handle browser launch completion."""
        if result.get("success"):
            self.statusBar().showMessage(
                f"Profile launched (PID: {result.get('pid', '?')})", 5000
            )
        else:
            self.profile_mgr.set_profile_status(profile_id, "stopped")
            self._refresh_profiles()
            QMessageBox.warning(
                self, "Launch Error",
                f"Failed to launch: {result.get('error', 'Unknown error')}"
            )

    def _on_browser_error(self, profile_id, error):
        """Handle browser launch error."""
        self.profile_mgr.set_profile_status(profile_id, "stopped")
        self._refresh_profiles()
        QMessageBox.critical(self, "Error", f"Browser error: {error}")

    def _stop_profile(self, profile_id: int):
        """Stop a running browser profile."""
        thread = self.running_browsers.get(profile_id)
        if thread and thread.launcher:
            thread.launcher.stop()

        self.profile_mgr.set_profile_status(profile_id, "stopped")
        self.running_browsers.pop(profile_id, None)
        self._refresh_profiles()
        self.statusBar().showMessage("Profile stopped", 3000)

    def _delete_profile(self, profile_id: int):
        """Delete a profile."""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this profile?\nThis will also remove browser data.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if profile_id in self.running_browsers:
                self._stop_profile(profile_id)
            self.profile_mgr.delete_profile(profile_id)
            self._refresh_profiles()
            self.statusBar().showMessage("Profile deleted", 3000)

    # ── Screen Mode Launchers ─────────────────────────────

    def _launch_fullscreen(self):
        """
        Full Screen mode — launches selected profile in desktop full-screen mode.
        (Previously this was incorrectly assigned to Android screen)
        """
        selected = self._get_selected_profile_id()
        if selected is None:
            QMessageBox.information(self, "Select Profile", "Please select a profile first.")
            return

        can_run, reason = self.license_mgr.can_run_profile()
        if not can_run:
            QMessageBox.warning(self, "License Required", f"Cannot run:\n{reason}")
            return

        profile = self.profile_mgr.get_profile(selected)
        if not profile:
            return

        # Regenerate fingerprint in desktop mode for full screen
        fp = profile.get("fingerprint_data", {})
        fp["mode"] = "desktop"
        screen = fp.get("screen", {})
        screen["width"] = 1920
        screen["height"] = 1080
        screen["avail_width"] = 1920
        screen["avail_height"] = 1040
        fp["screen"] = screen

        profile_dir = self.profile_mgr.get_profile_dir(profile["profile_number"])
        thread = BrowserThread(profile_dir, fp, profile.get("proxy"))
        thread.finished.connect(
            lambda result, pid=selected: self._on_browser_launched(pid, result)
        )
        thread.error.connect(
            lambda err, pid=selected: self._on_browser_error(pid, err)
        )

        self.running_browsers[selected] = thread
        self.profile_mgr.set_profile_status(selected, "running")
        thread.start()
        self._refresh_profiles()
        self.statusBar().showMessage("Launching in Full Screen mode...", 5000)

    def _launch_android_screen(self):
        """
        Android Screen mode — launches selected profile in Android emulated mode.
        (Previously this was incorrectly assigned to Full Screen)
        Opens an Android screen widget showing the profile info with proper scroll.
        """
        selected = self._get_selected_profile_id()
        if selected is None:
            QMessageBox.information(self, "Select Profile", "Please select a profile first.")
            return

        can_run, reason = self.license_mgr.can_run_profile()
        if not can_run:
            QMessageBox.warning(self, "License Required", f"Cannot run:\n{reason}")
            return

        profile = self.profile_mgr.get_profile(selected)
        if not profile:
            return

        # Regenerate fingerprint in android mode
        fp = profile.get("fingerprint_data", {})
        fp["mode"] = "android"

        # Launch browser with android emulation
        profile_dir = self.profile_mgr.get_profile_dir(profile["profile_number"])
        thread = BrowserThread(profile_dir, fp, profile.get("proxy"))
        thread.finished.connect(
            lambda result, pid=selected: self._on_browser_launched(pid, result)
        )
        thread.error.connect(
            lambda err, pid=selected: self._on_browser_error(pid, err)
        )

        self.running_browsers[selected] = thread
        self.profile_mgr.set_profile_status(selected, "running")
        thread.start()

        # Show Android Screen widget
        self._show_android_screen(profile)
        self._refresh_profiles()
        self.statusBar().showMessage("Launching in Android Screen mode...", 5000)

    def _show_android_screen(self, profile: dict):
        """Show the Android screen widget in a separate window."""
        self.android_window = QMainWindow()
        self.android_window.setWindowTitle(
            f"Android Screen — {profile.get('name', 'Profile')}"
        )
        self.android_window.setFixedSize(460, 920)
        self.android_window.setStyleSheet("background: #1a1a2e;")

        android_widget = AndroidScreenWidget()
        android_widget.set_profile_info(profile)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(android_widget)

        self.android_window.setCentralWidget(container)
        self.android_window.show()

    def _get_selected_profile_id(self) -> int:
        """Get the profile ID of the selected table row."""
        selected = self.table.selectedItems()
        if not selected:
            return None
        row = selected[0].row()
        id_item = self.table.item(row, 0)
        if id_item:
            return id_item.data(Qt.UserRole)
        return None

    # ── License ───────────────────────────────────────────

    def _show_license_dialog(self):
        """Show the license activation dialog."""
        dialog = LicenseDialog(self.license_mgr, self)
        dialog.exec_()
        self._update_license_status()

    def _update_license_status(self):
        """Update the license status indicator."""
        valid, reason = self.license_mgr.is_licensed()
        if valid:
            self.license_indicator.setText("● Licensed")
            self.license_indicator.setStyleSheet(
                "color: #10b981; font-weight: bold; font-size: 13px;"
            )
        else:
            self.license_indicator.setText("● Unlicensed")
            self.license_indicator.setStyleSheet(
                "color: #f43f5e; font-weight: bold; font-size: 13px;"
            )

    # ── Binary Patch ──────────────────────────────────────

    def _run_binary_patch(self):
        """Run binary patcher on chromedriver and chrome."""
        reply = QMessageBox.question(
            self, "Binary Patch",
            "This will patch chromedriver and Chrome to remove\n"
            "automation detection strings (cdc_, webdriver, etc.).\n\n"
            "A backup will be created. Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        results = BinaryPatcher.patch_all()

        msg_parts = []
        for target, result in results.items():
            if result.get("success"):
                patches = result.get("total_patches", 0)
                msg_parts.append(f"{target}: {patches} patches applied")
            else:
                msg_parts.append(f"{target}: {result.get('error', 'Error')}")

        QMessageBox.information(
            self, "Binary Patch Results",
            "\n".join(msg_parts)
        )

    # ── Close Event ───────────────────────────────────────

    def closeEvent(self, event):
        """Clean up on window close."""
        for pid, thread in list(self.running_browsers.items()):
            if thread.launcher:
                thread.launcher.stop()
        event.accept()


def run_app():
    """Launch the application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_app()

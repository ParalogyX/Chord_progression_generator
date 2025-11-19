#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple Windows GUI (PySide6) for the chord progression generator.

- Mode dropdown: major / minor / any
- Mood dropdown: Any + moods from AVAILABLE_MOODS
- Chord count dropdown: Any / 3–8
- Song section: dropdown + free text field (you can type your own)
- Generate button: calls filter_progressions(...) from progressions_logic
- Copy button: copies current result to Windows clipboard

Design: dark, simple, but clean and “professional enough”.
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QComboBox, QLineEdit, QSpinBox,
    QTextEdit, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout,
    QGroupBox
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

# Import your logic module
from generator_script import filter_progressions, AVAILABLE_MOODS


class ProgressionGeneratorUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chord Progression Generator")
        self.resize(800, 600)
        self.available_count = 0
        self._init_ui()
        self._apply_styles()
        self.update_available_count()  # initial calculation

    def _init_ui(self):
        # === Controls ===

        # Mode (major / minor / any)
        self.mode_label = QLabel("Mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Any", "Major", "Minor"])

        # Mood (Any + moods from logic)
        self.mood_label = QLabel("Mood:")
        self.mood_combo = QComboBox()
        self.mood_combo.addItem("Any")
        for m in sorted(AVAILABLE_MOODS):
            self.mood_combo.addItem(m)

        # Chord count (bars approximation)
        self.bars_label = QLabel("Chord count:")
        self.bars_combo = QComboBox()
        self.bars_combo.addItem("Any")
        for n in range(3, 9):  # 3–8 chords
            self.bars_combo.addItem(str(n))

        # Number of progressions to generate
        self.count_label = QLabel("How many progressions (Max avail. 0):")
        self.count_spin = QSpinBox()
        self.count_spin.setRange(0, 50)
        self.count_spin.setValue(0)

        # Song section (dropdown + free text)
        self.section_label = QLabel("Song section:")
        self.section_combo = QComboBox()
        self.section_combo.addItems([
            "Riff",
            "Intro",
            "Verse",
            "Pre-chorus",
            "Chorus",
            "Bridge",
            "Breakdown",
            "Outro",
            "Custom..."
        ])
        self.section_edit = QLineEdit()
        self.section_edit.setPlaceholderText("Custom section (or auto-filled from dropdown)")
        self.section_edit.setText("Riff")

        self.section_combo.currentTextChanged.connect(self._on_section_changed)

        # Buttons
        self.generate_button = QPushButton("Generate")
        self.copy_button = QPushButton("Copy to clipboard")

        self.generate_button.clicked.connect(self.on_generate_clicked)
        self.copy_button.clicked.connect(self.on_copy_clicked)

        # Result display
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # === Layouts ===

        # Top filter panel
        filter_group = QGroupBox("Filters")
        filter_layout = QGridLayout()
        filter_layout.setColumnStretch(0, 0)
        filter_layout.setColumnStretch(1, 1)
        filter_layout.setColumnStretch(2, 0)
        filter_layout.setColumnStretch(3, 1)

        filter_layout.addWidget(self.mode_label, 0, 0)
        filter_layout.addWidget(self.mode_combo, 0, 1)
        filter_layout.addWidget(self.mood_label, 0, 2)
        filter_layout.addWidget(self.mood_combo, 0, 3)

        filter_layout.addWidget(self.bars_label, 1, 0)
        filter_layout.addWidget(self.bars_combo, 1, 1)
        filter_layout.addWidget(self.count_label, 1, 2)
        filter_layout.addWidget(self.count_spin, 1, 3)

        filter_layout.addWidget(self.section_label, 2, 0)
        filter_layout.addWidget(self.section_combo, 2, 1)
        filter_layout.addWidget(self.section_edit, 2, 2, 1, 2)

        filter_group.setLayout(filter_layout)

        # Buttons row
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.generate_button)
        buttons_layout.addWidget(self.copy_button)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(filter_group)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.result_text, stretch=1)
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

        # Connect filter change signals → update_available_count
        self.mode_combo.currentTextChanged.connect(self.update_available_count)
        self.mood_combo.currentTextChanged.connect(self.update_available_count)
        self.bars_combo.currentTextChanged.connect(self.update_available_count)

    def _apply_styles(self):
        # Dark-ish theme with a primary accent
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-family: Segoe UI, Arial, sans-serif;
                font-size: 10pt;
            }
            QGroupBox {
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                margin-top: 8px;
                padding: 8px;
                font-weight: bold;
                color: #f0f0f0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }
            QLabel {
                color: #c0c0c0;
            }
            QLineEdit, QComboBox, QSpinBox, QTextEdit {
                background-color: #252526;
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                padding: 3px;
                selection-background-color: #007acc;
                selection-color: #ffffff;
            }
            QPushButton {
                background-color: #007acc;
                border: none;
                border-radius: 4px;
                padding: 6px 14px;
                color: #ffffff;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1493ff;
            }
            QPushButton:pressed {
                background-color: #005c99;
            }
            QTextEdit {
                border: 1px solid #3a3a3a;
                border-radius: 4px;
            }
        """)

        title_font = QFont("Segoe UI", 10)
        self.setFont(title_font)

    def _on_section_changed(self, text: str):
        """Update the text field when the section combo changes."""
        if text == "Custom...":
            if not self.section_edit.text():
                self.section_edit.setText("")
        else:
            self.section_edit.setText(text)

    def _current_filters(self):
        """Read current filter values from UI and return (mode_filter, mood_filter, bars)."""
        # Mode
        mode_text = self.mode_combo.currentText().lower()
        if mode_text == "any":
            mode_filter = "any"
        elif mode_text == "major":
            mode_filter = "major"
        elif mode_text == "minor":
            mode_filter = "minor"
        else:
            mode_filter = "any"

        # Mood
        mood_text = self.mood_combo.currentText()
        if mood_text == "Any":
            mood_filter = []
        else:
            mood_filter = [mood_text.lower()]

        # Chord count
        bars_text = self.bars_combo.currentText()
        if bars_text == "Any":
            bars = 0
        else:
            try:
                bars = int(bars_text)
            except ValueError:
                bars = 0

        return mode_filter, mood_filter, bars

    def update_available_count(self):
        """Recalculate how many progressions are available for current filters."""
        mode_filter, mood_filter, bars = self._current_filters()

        # Use a big max_results to effectively get full count
        res = filter_progressions(
            mode_filter=mode_filter,
            mood_filter=mood_filter,
            bars=bars,
            max_results=9999
        )
        self.available_count = len(res)

        # Update label
        self.count_label.setText(f"How many progressions (Max avail. {self.available_count}):")

        # Update spinbox range
        if self.available_count == 0:
            self.count_spin.setRange(0, 0)
            self.count_spin.setValue(0)
        else:
            current_value = self.count_spin.value()
            self.count_spin.setRange(1, self.available_count)
            if current_value < 1 or current_value > self.available_count:
                self.count_spin.setValue(min(max(current_value, 1), self.available_count))

        # Optional: also update status hint (not required but informative)
        if self.available_count == 0:
            self.status_label.setText("No progressions available with current filters.")
        else:
            self.status_label.setText(f"{self.available_count} progression(s) available with current filters.")

    def on_generate_clicked(self):
        mode_filter, mood_filter, bars = self._current_filters()

        # Count to generate (could be 0 if no available)
        count = self.count_spin.value()

        # Section label
        section_label = self.section_edit.text().strip()
        if not section_label:
            section_label = "riff"

        # Call logic
        res = filter_progressions(
            mode_filter=mode_filter,
            mood_filter=mood_filter,
            bars=bars,
            max_results=count
        )

        # Build output
        if not res:
            self.result_text.setPlainText("No progressions found with these filters.")
            self.status_label.setText("No results. Try loosening the filters.")
            return

        lines = []
        for pr in res:
            header = f"#{pr['id']} | {pr['roman']} | mode={pr['base_mode']} | moods={','.join(pr['moods'])}"
            lines.append(header)
            lines.append(f"  → suggested section: {section_label}")
            lines.append(f"  {pr['description']}")
            lines.append("")

        output = "\n".join(lines)
        self.result_text.setPlainText(output)
        self.status_label.setText(f"Generated {len(res)} progression(s).")

    def on_copy_clicked(self):
        text = self.result_text.toPlainText()
        if not text.strip():
            self.status_label.setText("Nothing to copy.")
            return
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.status_label.setText("Progressions copied to clipboard.")


def main():
    app = QApplication(sys.argv)
    win = ProgressionGeneratorUI()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

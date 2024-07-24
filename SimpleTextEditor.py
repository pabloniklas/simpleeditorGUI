import sys
import os
import configparser
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QLabel, QMenuBar,
                             QMenu, QAction, QFileDialog, QMessageBox, QFontDialog, QVBoxLayout, QWidget)
from PyQt5.QtGui import QFont, QIcon, QPainter, QFontMetrics
from PyQt5.QtCore import Qt

# Path to the configuration file
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".simple_text_editor_config.ini")


class Ruler(QWidget):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit
        self.setFixedHeight(30)  # Increased height to accommodate larger font sizes
        self.setFont(QFont("Monospaced", 10))  # Set monospaced font for the ruler
        self.text_edit.cursorPositionChanged.connect(self.update_ruler)

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        painter.fillRect(rect, Qt.lightGray)

        font_metrics = QFontMetrics(self.font())
        font_height = font_metrics.height()
        font_width = font_metrics.horizontalAdvance('0')

        # Number of columns to be displayed
        columns = rect.width() // font_width

        # Draw ruler numbers and dots
        for col in range(columns):
            x = col * font_width
            if col % 5 == 0:
                number = str(col // 5 * 5)
                if not number.endswith('5'):  # Skip numbers ending in '5'
                    painter.drawText(x, font_height, number)
                    # Draw a vertical line under the number
                    painter.drawLine(x, font_height, x, font_height + 10)
            else:
                # Draw a dot for intervals between numbers
                painter.drawText(x, font_height, '.')

    def update_ruler(self):
        self.update()


class SimpleTextEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.filename = "Untitled"
        self.config = configparser.ConfigParser()
        self.load_config()  # Load configuration from file
        self.init_ui()  # Initialize the UI components

    def load_config(self):
        """
        Load configuration settings from the config file if it exists.
        """
        if os.path.exists(CONFIG_FILE):
            self.config.read(CONFIG_FILE)
            self.font_family = self.config.get('Settings', 'FontFamily', fallback="Monospaced")
            self.font_size = self.config.getint('Settings', 'FontSize', fallback=12)
            self.window_width = self.config.getint('Settings', 'WindowWidth', fallback=800)
            self.window_height = self.config.getint('Settings', 'WindowHeight', fallback=600)
        else:
            # Default values if no config file exists
            self.font_family = "Monospaced"
            self.font_size = 12
            self.window_width = 800
            self.window_height = 600

    def save_config(self):
        """
        Save the current configuration settings to the config file.
        """
        self.config['Settings'] = {
            'FontFamily': self.font_family,
            'FontSize': self.font_size,
            'WindowWidth': self.width(),
            'WindowHeight': self.height()
        }
        with open(CONFIG_FILE, 'w') as configfile:
            self.config.write(configfile)

    def init_ui(self):
        """
        Initialize the user interface components of the text editor.
        """
        self.setWindowTitle(self.filename)
        self.setGeometry(100, 100, self.window_width, self.window_height)

        # Create a central widget to hold both the text area and the ruler
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)

        # Create the text area
        self.text_area = QTextEdit(self)
        self.text_area.setFont(QFont(self.font_family, self.font_size))
        self.text_area.textChanged.connect(self.update_status)

        # Create the ruler
        self.ruler = Ruler(self.text_area)

        # Add the ruler and text area to the central layout
        central_layout.addWidget(self.ruler)
        central_layout.addWidget(self.text_area)

        self.setCentralWidget(central_widget)

        self.status_bar = QLabel(self)
        self.statusBar().addWidget(self.status_bar)

        self.create_menu_bar()

        self.update_status()
        self.show()

    def create_menu_bar(self):
        """
        Create and set up the menu bar with actions for file operations, editing, settings, and help.
        """
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu('File')

        save_action = QAction(QIcon.fromTheme("document-save"), 'Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        exit_action = QAction(QIcon.fromTheme("application-exit"), 'Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.exit_program)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menu_bar.addMenu('Edit')

        cut_action = QAction(QIcon.fromTheme("edit-cut"), 'Cut', self)
        cut_action.setShortcut('Ctrl+X')
        cut_action.triggered.connect(self.text_area.cut)
        edit_menu.addAction(cut_action)

        copy_action = QAction(QIcon.fromTheme("edit-copy"), 'Copy', self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(self.text_area.copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction(QIcon.fromTheme("edit-paste"), 'Paste', self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(self.text_area.paste)
        edit_menu.addAction(paste_action)

        # Settings menu
        settings_menu = menu_bar.addMenu('Settings')

        font_action = QAction(QIcon.fromTheme("preferences-desktop-font"), 'Font', self)
        font_action.setShortcut('Ctrl+F')
        font_action.triggered.connect(self.select_font)
        settings_menu.addAction(font_action)

        # Help menu
        help_menu = menu_bar.addMenu('Help')

        about_action = QAction(QIcon.fromTheme("help-about"), 'About', self)
        about_action.setShortcut('Ctrl+A')
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        # Move the 'Help' menu to the right side of the menu bar
        help_menu.setStyleSheet("margin-left: auto;")

    def update_status(self):
        """
        Update the status bar with the current line and column number of the cursor.
        """
        cursor = self.text_area.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        self.status_bar.setText(f"Ln {line}, Col {column}   |   {self.filename}")

    def save_file(self):
        """
        Open a file dialog to save the content of the text area to a file.
        """
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            self.filename = os.path.basename(file_path)
            self.setWindowTitle(self.filename)
            with open(file_path, 'w') as file:
                file.write(self.text_area.toPlainText())
            self.update_status()

    def exit_program(self):
        """
        Prompt the user to confirm exit. Save configuration before quitting if confirmed.
        """
        reply = QMessageBox.question(self, 'Confirm Exit', 'Exit without saving?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.save_config()  # Save the configuration before exiting
            QApplication.instance().quit()

    def show_about_dialog(self):
        """
        Show an 'About' dialog with information about the program creator.
        """
        QMessageBox.about(self, "About", "This program was created by Pablo Niklas.")

    def select_font(self):
        """
        Open a font dialog to select a new font for the text editor.
        """
        font, ok = QFontDialog.getFont(QFont(self.font_family, self.font_size), self)
        if ok:
            self.font_family = font.family()
            self.font_size = font.pointSize()
            self.text_area.setFont(font)
            self.ruler.setFont(font)  # Update the ruler font
            self.save_config()  # Save the updated font settings


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = SimpleTextEditor()
    sys.exit(app.exec_())

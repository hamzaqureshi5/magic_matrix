import json
import os
import random
import shutil
import subprocess
import sys
import time
from urllib import request, parse, error
import certifi
import ssl
import cryptocode

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices, QFontDatabase, QIcon, QPixmap
from PyQt5.QtGui import QColor

from PyQt5.QtWidgets import QMessageBox, QFileDialog, QApplication

from generate_image import generate_solution_img, generate_puzzle_img
from generate_square import choose_square, add_subtract_from_square, multiply_square
from generate_svg import generate_solution_svg, generate_puzzle_svg
from solve_puzzle import get_unsolved_puzzle

class MathSquareGeneratorApp(QtWidgets.QWidget):

    def get_datafile_path(self):
        app_data = os.getenv("APPDATA")
        program_data_dir = os.path.join(app_data, "MagicMatrix")
        if not os.path.exists(program_data_dir):
            os.makedirs(program_data_dir)
        return os.path.join(program_data_dir, "data.json")

    def get_database_path(self):
        app_data = os.getenv("APPDATA")
        program_data_dir = os.path.join(app_data, "MagicMatrix")
        database_file = os.path.join(program_data_dir, "squares.json")

        if not os.path.exists(database_file):
            # Copy the squares.json file from the script's directory to the AppData folder.
            script_dir = os.path.abspath(os.path.dirname(__file__))
            source_database = os.path.join(script_dir, 'squares.json')
            if os.path.exists(source_database):
                os.makedirs(program_data_dir, exist_ok=True)
                shutil.copy(source_database, database_file)

        return database_file

    def get_icon_path(self):
        bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        return os.path.join(bundle_dir, 'data', 'icon.ico')

    def get_path(self):
        try:
            data_file = self.get_datafile_path()
            with open(data_file, 'r') as jsonfile:
                loaded_data = json.load(jsonfile)
                p_path = loaded_data.get("puzzle_path")
                s_path = loaded_data.get("solution_path")
                return {"puzzle_path": p_path if p_path else "", "solution_path": s_path if s_path else ""}
        except:
            return {"puzzle_path": "", "solution_path": ""}

    def get_min_max(self):
        if self.n1_99:
            min_ = 1
            max_ = 99
        else:
            min_ = 100
            max_ = 999
        return min_, max_

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MAGIC MATRIX")
        screen = QApplication.desktop().screenGeometry()
        self.setGeometry(100, 100, 1200, 600)
        self.setStyleSheet("background-color: #222; color: #fff;")
        self.setWindowIcon(QtGui.QIcon('icon.ico'))

        self.square_size = 3

        self.puzzle_path = self.get_path().get("puzzle_path")
        self.solution_path = self.get_path().get("solution_path")

        self.easy_box = True
        self.medium_box = False        
        self.hard_box = False

        self.selected_font = "Arial"
        self.font_size = 50

        self.grid_thickness = 4

        self.how_many_puzzles = 1

        self.png_box = False
        self.svg_box = True
        self.vertical_alignment = 2.1
        
        self.positive = True
        self.positive_negative = False

        self.n1_99 = True
        self.n100_999 = False

        self.shutdown_box = False

        style_sheet = """
                    QMessageBox { background-color: lightblue; }
                    QLabel { width: 800px; }
                """
        self.message_box = QMessageBox()
        self.message_box.setIcon(QMessageBox.Information)
        self.message_box.setStyleSheet(style_sheet)

        self.init_ui()

    def show_progress_dialog(self):
        self.abort_operation = False

        self.progress_dialog = QtWidgets.QProgressDialog(self)
        self.progress_dialog.setWindowTitle("Generating Puzzles")
        # self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setAutoReset(False)
        self.progress_dialog.setAutoClose(False)

        self.abort_button = QtWidgets.QPushButton("Abort", self.progress_dialog)
        self.abort_button.clicked.connect(self.handle_abort)
        self.progress_dialog.setCancelButton(self.abort_button)

        self.progress_bar = QtWidgets.QProgressBar(self.progress_dialog)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setMinimum(0)
        self.progress_dialog.setBar(self.progress_bar)
        self.progress_dialog.forceShow()

    def handle_abort(self):
        self.abort_operation = True

    def positive_box_change(self, state):
        self.positive = state == QtCore.Qt.Checked
        if self.positive:
            self.positive_negative_box.setCheckState(QtCore.Qt.Unchecked)

    def positive_negative_box_change(self, state):
        self.positive_negative = state == QtCore.Qt.Checked
        if self.positive_negative:
            self.positive_box.setCheckState(QtCore.Qt.Unchecked)

    def on_1_to_99_change(self, state):
        self.n1_99 = state == QtCore.Qt.Checked

    def on_100_to_999_change(self, state):
        self.n100_999 = state == QtCore.Qt.Checked

    def on_png_checkbox_change(self, state):
        self.png_box = state == QtCore.Qt.Checked

    def on_svg_checkbox_change(self, state):
        self.svg_box = state == QtCore.Qt.Checked
        
    def on_easy_checkbox_change(self, state):
        self.easy_box = state == QtCore.Qt.Checked
        if self.easy_box:
            self.medium_box_check.setCheckState(QtCore.Qt.Unchecked)
            self.hard_box_check.setCheckState(QtCore.Qt.Unchecked)

    def on_medium_checkbox_change(self, state):
        self.medium_box = state == QtCore.Qt.Checked
        if self.medium_box:
            self.easy_box_check.setCheckState(QtCore.Qt.Unchecked)
            self.hard_box_check.setCheckState(QtCore.Qt.Unchecked)

    def on_hard_checkbox_change(self, state):
        self.hard_box = state == QtCore.Qt.Checked
        if self.hard_box:
            self.easy_box_check.setCheckState(QtCore.Qt.Unchecked)
            self.medium_box_check.setCheckState(QtCore.Qt.Unchecked)

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()
        top_spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        bottom_spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

        layout.addSpacing(10)
        self.header_widgets(layout)
        layout.addSpacing(10)
        self.dimensions_widget(layout)
        layout.addSpacing(10)
        self.difficulty_settings_widget(layout)
        layout.addSpacing(10)                                                           
        self.font_selection_widget(layout)
        layout.addSpacing(10)
        self.grid_line_widget(layout)
        layout.addSpacing(10)
        self.how_many_puzzle_widget(layout)
        layout.addSpacing(10)
        self.paths_widget(layout)
        layout.addSpacing(10)
        self.bottom_buttons_widget(layout)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.addSpacerItem(bottom_spacer)

        self.setLayout(layout)

    def set_label_style(self, label):
        label.setStyleSheet("font-family: Arial;font-size: 20px; font-weight: bold; color: #fff; padding: 10px")

    def set_input_style(self, input):
        input.setStyleSheet("font-family: Arial;font-size: 20px; color: #000; background-color: #fff; padding: 5px; "
                            "border-radius: 5px; width: 40px; font-weight: bold")

    def set_checkbox_style(self, checkbox):
        checkbox.setStyleSheet(f"""
        QCheckBox {{
            color: #fff;
            padding: 2px;
        }}

        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border-radius: 3px;
            background-color: #fff;
        }}

        QCheckBox::indicator:checked {{
            background-color: #34e807
        }}

        QCheckBox::indicator:unchecked {{
            background-color: #fff; /* White background for unchecked */
        }}

        """
                               )

    def get_font_for_header_buttons(self):
        font = QtGui.QFont()
        font.setFamily("ARIAL")
        font.setPointSize(10)
        return font

    def header_widgets(self, layout):
        header_layout = QtWidgets.QHBoxLayout()

        about = QtWidgets.QPushButton("ABOUT")
        about.setStyleSheet(
            "color: #000; background-color: #fff; padding: 10px; border-radius: 15px; width: 200%; font-weight: bold"
        )
        about.clicked.connect(self.about)
        about.setFont(self.get_font_for_header_buttons())
        email = QtWidgets.QPushButton("EMAIL SUPPORT")
        email.clicked.connect(self.email_support)
        email.setStyleSheet(
            "color: #fff; background-color: #aaa; padding: 10px; border-radius: 15px; width: 200%; font-weight: bold"
        )
        email.setFont(self.get_font_for_header_buttons())
        youtube = QtWidgets.QPushButton("YOUTUBE")
        youtube.clicked.connect(self.open_youtube)
        youtube.setStyleSheet(
            "color: #fff; background-color: red; padding: 10px; border-radius: 15px; width: 200%; font-weight: bold"
        )
        youtube.setFont(self.get_font_for_header_buttons())
        fb = QtWidgets.QPushButton("FACEBOOK")
        fb.clicked.connect(self.open_facebook_group)
        fb.setStyleSheet(
            "color: #fff; background-color: #0af; padding: 10px; border-radius: 15px; width: 200%; font-weight: bold"
        )
        fb.setFont(self.get_font_for_header_buttons())

        header_layout.addStretch(10)
        header_layout.addWidget(about)
        header_layout.addWidget(email)
        header_layout.addWidget(youtube)
        header_layout.addWidget(fb)
        header_layout.addStretch(10)  # Add a stretchable space to balance the layout

        layout.addLayout(header_layout)

    def dimensions_widget(self, layout):
        dimensions_layout = QtWidgets.QHBoxLayout()

        dimensions_txt = QtWidgets.QLabel("Select Grid Size 3-12")
        self.set_label_style(dimensions_txt)
        size_lbl = QtWidgets.QLabel("Size")
        self.set_label_style(size_lbl)
        self.size_entry = QtWidgets.QLineEdit(str(self.square_size))
        self.size_entry.textChanged.connect(
            lambda text: setattr(self, 'square_size', int(text) if text.isdigit() and 0 < int(text) < 13 else self.size_entry.setText("")))
        self.set_input_style(self.size_entry)
        self.size_entry.setFixedWidth(50)

        spacer1 = QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        spacer2 = QtWidgets.QWidget()
        spacer2.setFixedWidth(50)

        num_range_layout = QtWidgets.QHBoxLayout()
        numbers_range_layout = QtWidgets.QHBoxLayout()

        spacer = QtWidgets.QWidget()
        spacer.setFixedWidth(30)

        spacer3 = QtWidgets.QWidget()
        spacer3.setFixedWidth(30)

        puzzle_include_lbl = QtWidgets.QLabel("Puzzle Grid to include")
        self.set_label_style(puzzle_include_lbl)
        n1_99_lbl = QtWidgets.QLabel("     1-99")
        n1_99_lbl.setStyleSheet("font-family: Arial;font-size: 20px; font-weight: bold; color: #fff; padding: 0px")
        n100_999_lbl = QtWidgets.QLabel("100-999")
        n100_999_lbl.setStyleSheet("font-family: Arial;font-size: 20px; font-weight: bold; color: #fff; padding: 0px")
        self.n1_99_box = QtWidgets.QCheckBox(checked=self.n1_99)
        self.n1_99_box.stateChanged.connect(self.on_1_to_99_change)
        self.set_checkbox_style(self.n1_99_box)
        self.n100_999_box = QtWidgets.QCheckBox()
        self.n100_999_box.stateChanged.connect(self.on_100_to_999_change)
        self.set_checkbox_style(self.n100_999_box)

        positive_num_lbl = QtWidgets.QLabel("Positive Numbers Only")
        self.set_label_style(positive_num_lbl)
        positive_num_and_negative_lbl = QtWidgets.QLabel("Positive And Negative Numbers")
        self.set_label_style(positive_num_and_negative_lbl)
        self.positive_box = QtWidgets.QCheckBox(checked=self.positive)
        self.positive_box.stateChanged.connect(self.positive_box_change)
        self.set_checkbox_style(self.positive_box)
        self.positive_negative_box = QtWidgets.QCheckBox()
        self.positive_negative_box.stateChanged.connect(self.positive_negative_box_change)
        self.set_checkbox_style(self.positive_negative_box)
        num_range_pad = QtWidgets.QWidget()
        num_range_pad.setFixedWidth(308)

        dimensions_layout.addWidget(dimensions_txt)
        dimensions_layout.addWidget(spacer2)
        dimensions_layout.addWidget(size_lbl, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        dimensions_layout.addWidget(self.size_entry, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        dimensions_layout.addSpacerItem(spacer1)

        num_range_layout.addWidget(puzzle_include_lbl)
        num_range_layout.addWidget(spacer)
        num_range_layout.addWidget(spacer3)
        num_range_layout.addWidget(positive_num_lbl)
        num_range_layout.addWidget(self.positive_box)
        num_range_layout.addWidget(positive_num_and_negative_lbl)
        num_range_layout.addWidget(self.positive_negative_box)
        num_range_layout.addSpacerItem(spacer1)
        numbers_range_layout.addWidget(num_range_pad)
        numbers_range_layout.addWidget(n1_99_lbl)
        numbers_range_layout.addWidget(self.n1_99_box)
        numbers_range_layout.addWidget(n100_999_lbl)
        numbers_range_layout.addWidget(self.n100_999_box)
        numbers_range_layout.addSpacerItem(spacer1)

        layout.addLayout(dimensions_layout)
        layout.addLayout(num_range_layout)
        layout.addLayout(numbers_range_layout)

    def difficulty_settings_widget(self, layout):
        difficulty_layout = QtWidgets.QHBoxLayout()
        
        difficulty_label = QtWidgets.QLabel("Select Difficulty Settings")
        self.set_label_style(difficulty_label)

        easy_lbl = QtWidgets.QLabel("EASY")
        medium_lbl = QtWidgets.QLabel("MEDIUM")
        hard_lbl = QtWidgets.QLabel("HARD")

        self.easy_box_check = QtWidgets.QCheckBox(checked=True)  # Easy is the default
        self.medium_box_check = QtWidgets.QCheckBox()
        self.hard_box_check = QtWidgets.QCheckBox()

        self.easy_box_check.stateChanged.connect(self.on_easy_checkbox_change)
        self.medium_box_check.stateChanged.connect(self.on_medium_checkbox_change)
        self.hard_box_check.stateChanged.connect(self.on_hard_checkbox_change)

        self.set_label_style(easy_lbl)
        self.set_label_style(medium_lbl)
        self.set_label_style(hard_lbl)

        self.set_checkbox_style(self.easy_box_check)
        self.set_checkbox_style(self.medium_box_check)
        self.set_checkbox_style(self.hard_box_check)

        spacer1 = QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        difficulty_layout.addWidget(difficulty_label)
        difficulty_layout.addWidget(easy_lbl)
        difficulty_layout.addWidget(self.easy_box_check)
        difficulty_layout.addWidget(medium_lbl)
        difficulty_layout.addWidget(self.medium_box_check)
        difficulty_layout.addWidget(hard_lbl)
        difficulty_layout.addWidget(self.hard_box_check)
        difficulty_layout.addWidget(difficulty_label) 
        difficulty_layout.addSpacerItem(spacer1)

        layout.addLayout(difficulty_layout)

    def on_difficulty_checkbox_change(self, state):
        if state == QtCore.Qt.Checked:
            sender = self.sender()
            checkboxes = [self.easy_box, self.medium_box, self.hard_box]
            for checkbox in checkboxes:
                if checkbox is not sender:
                    checkbox.setChecked(False)
    def populate_font_combobox(self):
        font_db = QFontDatabase()
        font_families = font_db.families(QFontDatabase.Any)
        self.font_selection_combo.addItems(["Arial"] + font_families)

    def on_font_selection_change(self, index):
        selected_font = self.font_selection_combo.itemText(index)
        self.selected_font = selected_font

    def font_selection_widget(self, layout):
        font_selection_layout = QtWidgets.QHBoxLayout()

        font_selection = QtWidgets.QLabel("Font Selection")
        self.set_label_style(font_selection)
        font_size = QtWidgets.QLabel("Font Size in %")
        self.set_label_style(font_size)
        self.font_selection_combo = QtWidgets.QComboBox()
        self.populate_font_combobox()
        self.font_selection_combo.currentIndexChanged.connect(self.on_font_selection_change)

        # Create a QScrollBar style
        scroll_bar_style = "QScrollBar:vertical { width: 10px; }"

        # Apply the style to the combo box
        self.font_selection_combo.setStyleSheet(
            "font-family: Arial; font-size: 20px; color: #000; background-color: #fff; "
            "padding: 5px; border-radius: 5px; width: 200px; font-weight: bold;"
        )

        # Apply the scroll bar style to the QAbstractItemView of the combo box
        self.font_selection_combo.view().setStyleSheet(scroll_bar_style)
        self.font_size_entry = QtWidgets.QLineEdit(str(self.font_size))
        self.font_size_entry.textChanged.connect(
            lambda text: setattr(self, 'font_size',
                                 int(text) if text.isdigit() and int(text) <= 80 else self.font_size_entry.setText("")))
        self.set_input_style(self.font_size_entry)

        font_selection_layout.addWidget(font_selection)
        font_selection_layout.addSpacing(20)  # Add spacing between elements
        font_selection_layout.addWidget(self.font_selection_combo)
        font_selection_layout.addSpacing(20)  # Add spacing between elements
        font_selection_layout.addWidget(font_size)
        font_selection_layout.addWidget(self.font_size_entry, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        font_selection_layout.addStretch(1)  # Add stretchable space to align right

        layout.addLayout(font_selection_layout)

    def grid_line_widget(self, layout):
        grid_line_layout = QtWidgets.QHBoxLayout()

        grid_line = QtWidgets.QLabel("Gridline thickness (1-12)")
        self.set_label_style(grid_line)

        self.grid_line_entry = QtWidgets.QLineEdit(str(self.grid_thickness))
        self.grid_line_entry.textChanged.connect(
            lambda text: setattr(self, 'grid_thickness',
                                 int(text) if text.isdigit() and 0 < int(text) < 12 else self.grid_line_entry.setText(
                                     "")))
        self.grid_line_entry.setStyleSheet("font-family: Arial; font-size: 20px; color: #000; background-color: #fff; "
                                           "padding: 5px; border-radius: 5px; width: 40px; font-weight: bold")

        spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        space_width = QtWidgets.QWidget()
        space_width.setFixedWidth(40)

        grid_line_layout.addWidget(grid_line)
        grid_line_layout.addWidget(self.grid_line_entry, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        grid_line_layout.addSpacerItem(spacer)

        layout.addLayout(grid_line_layout)

    def how_many_puzzle_widget(self, layout):
        how_many_layout = QtWidgets.QHBoxLayout()

        how_many_lbl = QtWidgets.QLabel("How many puzzles do you want?")
        self.set_label_style(how_many_lbl)
        self.how_many_entry = QtWidgets.QLineEdit(str(self.how_many_puzzles))
        self.how_many_entry.textChanged.connect(
            lambda text: setattr(self, 'how_many_puzzles',
                                 int(text) if text.isdigit() and int(text) < 5001 else self.how_many_entry.setText("")))
        self.set_input_style(self.how_many_entry)
        png_lbl = QtWidgets.QLabel("PNG")
        png_lbl.setStyleSheet("font-family: Arial;font-size: 20px; font-weight: bold; color: #fff")
        svg_lbl = QtWidgets.QLabel("SVG")
        svg_lbl.setStyleSheet("font-family: Arial;font-size: 20px; font-weight: bold; color: #fff")
        self.select_png_box = QtWidgets.QCheckBox()
        self.select_png_box.stateChanged.connect(self.on_png_checkbox_change)
        self.set_checkbox_style(self.select_png_box)
        self.select_svg_box = QtWidgets.QCheckBox(checked=self.svg_box)
        self.select_svg_box.stateChanged.connect(self.on_svg_checkbox_change)
        self.set_checkbox_style(self.select_svg_box)

        # Add widgets for vertical alignment
        vertical_alignment_lbl = QtWidgets.QLabel("  Vertical Alignment  ")
        vertical_alignment_lbl.setStyleSheet("font-family: Arial; font-size: 20px; font-weight: bold; color: #fff")
        self.vertical_alignment_entry = QtWidgets.QLineEdit(str(self.vertical_alignment))
        self.vertical_alignment_entry.textChanged.connect(
            lambda text: setattr(self, 'vertical_alignment', text) if text.replace(".", "").isdigit() else self.vertical_alignment_entry.setText(text))
        self.set_input_style(self.vertical_alignment_entry)

        spacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        spacer2 = QtWidgets.QWidget()
        spacer2.setFixedWidth(50)

        how_many_layout.addWidget(how_many_lbl)
        how_many_layout.addWidget(self.how_many_entry, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        how_many_layout.addWidget(spacer2)
        how_many_layout.addWidget(png_lbl)
        how_many_layout.addWidget(self.select_png_box)
        how_many_layout.addWidget(svg_lbl)
        how_many_layout.addWidget(self.select_svg_box)
        
        # Add widgets for vertical alignment
        how_many_layout.addWidget(vertical_alignment_lbl)
        how_many_layout.addWidget(self.vertical_alignment_entry, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
            
        how_many_layout.addItem(spacer)

        layout.addLayout(how_many_layout)

    def bottom_buttons_widget(self, layout):
        bottom_layout = QtWidgets.QHBoxLayout()

        generate = QtWidgets.QPushButton("GENERATE")
        generate.setStyleSheet("background-color: green; color: white; font-size: 24px; border: none; width: 200%; "
                               "font-family: Arial; padding: 10px; border-radius: 15px; font-weight: bold")

        reset = QtWidgets.QPushButton("RESET TO DEFAULT")
        reset.setStyleSheet("background-color: yellow; color: black; font-size: 20px; border: none; width: 200%; "
                            "font-family: Arial; padding: 10px; border-radius: 15px; font-weight: bold")
        generate.clicked.connect(self.generate_puzzles)
        reset.clicked.connect(self.reset_default_selection)

        spacer = QtWidgets.QWidget()
        spacer.setFixedWidth(50)

        left_stretch = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        right_stretch = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        bottom_layout.addSpacerItem(left_stretch)
        bottom_layout.addWidget(generate)
        bottom_layout.addWidget(spacer)
        bottom_layout.addWidget(reset)
        bottom_layout.addSpacerItem(right_stretch)

        layout.addLayout(bottom_layout)

    def browse_puzzle(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Puzzles Export Folder ")
        if folder_path:
            self.puzzle_path = folder_path
            self.puzzle_entry.setText(self.puzzle_path)

    def browse_solution(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Solutions Export Folder")
        if folder_path:
            self.solution_path = folder_path
            self.solution_entry.setText(self.solution_path)

    def paths_widget(self, layout):
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        path_layout = QtWidgets.QVBoxLayout()

        spacer1 = QtWidgets.QWidget()
        spacer1.setFixedWidth(5)

        spacer2 = QtWidgets.QWidget()
        spacer2.setFixedWidth(40)

        spacer3 = QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        puzzle_row_layout = QtWidgets.QHBoxLayout()
        puzzle_lbl = QtWidgets.QLabel("Puzzles Export Folder")
        self.set_label_style(puzzle_lbl)
        self.puzzle_entry = QtWidgets.QLineEdit(self.puzzle_path)
        self.puzzle_entry.setStyleSheet("background-color: #fff; color: #000; padding: 10px; border-radius: 15px; "
                                        "width: 400px; font-size: 20px")
        self.puzzle_entry.textChanged.connect(lambda text: setattr(self, 'puzzle_path', text))
        puzzle_browse_button = QtWidgets.QPushButton("BROWSE")
        puzzle_browse_button.setStyleSheet("background-color: #aaa; color: white; font-size: 20px; border: none; "
                                           "font-family: Arial; padding: 10px; border-radius: 15px; font-weight: bold")
        puzzle_browse_button.clicked.connect(self.browse_puzzle)
        puzzle_row_layout.addWidget(puzzle_lbl)
        puzzle_row_layout.addWidget(spacer1)
        puzzle_row_layout.addWidget(self.puzzle_entry, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        puzzle_row_layout.addWidget(puzzle_browse_button, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        solution_row_layout = QtWidgets.QHBoxLayout()
        solution_lbl = QtWidgets.QLabel("Solutions Export Folder")
        self.set_label_style(solution_lbl)
        self.solution_entry = QtWidgets.QLineEdit(self.solution_path)
        self.solution_entry.setStyleSheet("color: #000; background-color: #fff; font-size: 20px; padding: 10px; "
                                          "border-radius: 15px; width: 400px;")
        self.solution_entry.textChanged.connect(lambda text: setattr(self, 'solution_path', text))
        solution_browse_button = QtWidgets.QPushButton("BROWSE")
        solution_browse_button.clicked.connect(self.browse_solution)
        solution_browse_button.setStyleSheet("background-color: #aaa; color: white; font-size: 20px; border: none; "
                                             "font-family: Arial; padding: 10px; border-radius: 15px;  font-weight: bold")
        solution_row_layout.addWidget(solution_lbl)
        puzzle_row_layout.addWidget(spacer1)
        solution_row_layout.addWidget(self.solution_entry)
        solution_row_layout.addWidget(solution_browse_button)
        solution_row_layout.addSpacerItem(spacer3)

        path_layout.addLayout(puzzle_row_layout)
        path_layout.addLayout(solution_row_layout)

        main_layout.addLayout(path_layout)

        restart_layout = QtWidgets.QHBoxLayout()
        restart_computer_lbl = QtWidgets.QLabel("Shutdown computer after generation is completed?")
        restart_computer_lbl.setStyleSheet("font-family: Arial; font-size: 20px; font-weight: bold; color: #fff;")
        restart_computer_lbl.setWordWrap(True)

        self.restart_computer_box = QtWidgets.QCheckBox()
        self.restart_computer_box.stateChanged.connect(
            lambda state: setattr(self, 'shutdown_box', state == QtCore.Qt.Checked))
        self.set_checkbox_style(self.restart_computer_box)

        restart_layout.addWidget(spacer2)
        restart_layout.addWidget(restart_computer_lbl)
        restart_layout.addWidget(self.restart_computer_box)
        restart_layout.addStretch()

        main_layout.addLayout(restart_layout)

        layout.addLayout(main_layout)

    def reset_default_selection(self):
        self.square_size = 3

        self.how_many_puzzles = 1
        self.how_many_entry.setText("1")

        self.size_entry.setText("3")

        self.n1_99_box.setCheckState(QtCore.Qt.Checked)
        self.n100_999_box.setCheckState(QtCore.Qt.Unchecked)

        self.positive_box.setCheckState(QtCore.Qt.Checked)
        self.positive_negative_box.setCheckState(QtCore.Qt.Unchecked)

        self.positive = True
        self.positive_negative = False

        self.easy_box = True
        self.medium_box = False       
        self.hard_box = False

        self.restart_computer_box.setCheckState(QtCore.Qt.Unchecked)
        self.shutdown_box = False

        self.selected_font = "Arial"
        self.font_size = 50
        self.grid_thickness = 4
        self.font_selection_combo.setCurrentIndex(0)

        self.font_size_entry.setText("50")
        self.grid_line_entry.setText("4")

        self.png_box = False
        self.svg_box = True
        self.vertical_alignment = 2.1

        self.vertical_alignment_entry.setText("2.1")
        
        self.select_png_box.setCheckState(QtCore.Qt.Unchecked)
        self.select_svg_box.setCheckState(QtCore.Qt.Checked)

    def get_file_index(self):
        path = self.solution_path
        file_list = [int(f.split(".")[0].split("_")[-1]) for f in os.listdir(path) if
                     os.path.isfile(os.path.join(path, f))]
        return sorted(file_list)[-1] if file_list else 0

    def generate_puzzles(self):
        if self.puzzle_path and not os.path.exists(self.puzzle_path):
            self.message_box.setWindowTitle("Validation Error")
            self.message_box.setText("Puzzle Path does not exist")
            self.message_box.exec_()
        elif self.solution_path and not os.path.exists(self.solution_path):
            self.message_box.setWindowTitle("Validation Error")
            self.message_box.setText("Solution Path does not exist")
            self.message_box.exec_()
        elif not (self.positive or self.positive_negative):
            self.message_box.setWindowTitle("Validation Error")
            self.message_box.setText("Please select positive or negative numbers")
            self.message_box.exec_()
        elif not (self.easy_box or self.medium_box or self.hard_box):
            self.message_box.setWindowTitle("Validation Error")
            self.message_box.setText("Please select difficuly level")
            self.message_box.exec_()            
        elif not self.grid_thickness or int(self.grid_thickness) < 1:
            self.message_box.setWindowTitle("Validation Error")
            self.message_box.setText("Grid Thickness may not be null")
            self.message_box.exec_()
        elif not self.how_many_puzzles or int(self.how_many_puzzles) < 1:
            self.message_box.setWindowTitle("Validation Error")
            self.message_box.setText("Number of Puzzles may not be null")
            self.message_box.exec_()
        elif not (self.solution_path and self.puzzle_path):
            self.message_box.setWindowTitle("Validation Error")
            self.message_box.setText("Please Select Puzzle and Solution Path")
            self.message_box.exec_()
        elif not (self.square_size and 13 > self.square_size >= 3):
            self.message_box.setWindowTitle("Validation Error")
            self.message_box.setText("Size must be in 3 - 12 and may not be Null")
            self.message_box.exec_()
        elif not (self.n1_99 or self.n100_999):
            self.message_box.setWindowTitle("Validation Error")
            self.message_box.setText("Please select puzzle include numbers")
            self.message_box.exec_()
        elif not (self.png_box or self.svg_box):
            self.message_box.setWindowTitle("Validation Error")
            self.message_box.setText("Please Select the OutPut format of the Puzzle (PNG, SVG) or both")
            self.message_box.exec_()
        else:
            data = {"puzzle_path": self.puzzle_path, "solution_path": self.solution_path}
            data_file = self.get_datafile_path()
            with open(data_file, 'w') as jsonfile:
                json.dump(data, jsonfile)
            try:
                self.show_progress_dialog()
            except Exception as e:
                print(e)
            already = []
            for i in range(int(self.how_many_puzzles)):
                try:
                    self.progress_bar.setValue(int((i + 1) * 100 / int(self.how_many_puzzles)))
                    QtWidgets.QApplication.processEvents()
                except Exception as e:
                    print(e)
                if self.abort_operation:
                    QMessageBox.information(self, "Info", "Operation aborted by user!")
                    return
                file_index = self.get_file_index()
                rand = int(file_index) + 1
                print("generating . . .")
                while True:
                    if self.n100_999 and not self.n1_99:
                        square = choose_square(self.square_size, self.get_database_path())
                        if not self.positive:
                            square = add_subtract_from_square(self.square_size, square, self.positive)
                        solved_square = multiply_square(self.square_size, square)
                    else:
                        square = choose_square(self.square_size, self.get_database_path())
                        if not self.positive:
                            square = add_subtract_from_square(self.square_size, square, self.positive)
                        solved_square = square
                    if solved_square not in already:
                        already.append(solved_square)
                        break
                    else:
                        if self.n1_99 and self.n100_999:
                            solved_square1 = add_subtract_from_square(self.square_size, already[0], self.positive)
                            solved_square2 = multiply_square(self.square_size, already[0])
                            solved_square = random.choice([solved_square1, solved_square2])
                            if solved_square not in already:
                                already.append(solved_square)
                                break
                        elif self.n1_99:
                            solved_square = add_subtract_from_square(self.square_size, already[0], self.positive)
                            if solved_square not in already:
                                already.append(solved_square)
                                break
                        else:
                            if self.square_size < 10:
                                square = choose_square(self.square_size, self.get_database_path())
                                solved_square = multiply_square(self.square_size, square)
                                if solved_square not in already:
                                    already.append(solved_square)
                                    break
                difficulty_level = "easy"
                if self.medium_box:
                    difficulty_level = "medium"
                elif self.hard_box:
                    difficulty_level = "hard"
                unsolved = get_unsolved_puzzle(solved_square, difficulty_level)
                if self.png_box:
                    generate_solution_img(unsolved, self.solution_path, self.selected_font, self.font_size, self.grid_thickness, rand)
                if self.svg_box:
                    generate_solution_svg(unsolved, self.solution_path, self.selected_font, self.font_size, self.grid_thickness, rand, vertical_alignment=self.vertical_alignment)
                if self.png_box:
                    generate_puzzle_img(unsolved, self.puzzle_path, self.selected_font, self.font_size, self.grid_thickness, rand)
                if self.svg_box:
                    generate_puzzle_svg(unsolved, self.puzzle_path, self.selected_font, self.font_size, self.grid_thickness, rand, vertical_alignment=self.vertical_alignment)
                time.sleep(1)
            if self.shutdown_box:
                subprocess.run(["shutdown", "/s", "/f", "/t", "0"], shell=True)
            else:
                self.progress_dialog.accept()
                QMessageBox.information(self, "Success",
                                        "Your Puzzles are Generated Successfully")

    def about(self):
        version_info = "Version 0.1\n"
        copyright_info = "Copyright (c) Marina Art Design 2023. All Rights Reserved.\n"
        third_party_info = "Magic Matrix Puzzle Generator also uses 3rd party libraries, software & APIs to assist in its functionality."

        message = version_info + copyright_info + third_party_info

        self.message_box.setWindowTitle("About")
        self.message_box.setText(message)
        self.message_box.setFixedWidth(800)  # Set the desired width
        self.message_box.exec_()

    def email_support(self):
        self.message_box.setWindowTitle("Email Support")
        self.message_box.setText(
            """If you have any questions or concerns regarding program please contact me at <a href="marinapomorac@gmail.com">marinapomorac@gmail.com</a>""")
        self.message_box.exec_()

    def open_youtube(self):
        youtube_url = "https://www.youtube.com/@MarinaArtDesign"
        QDesktopServices.openUrl(QUrl(youtube_url))

    def open_facebook_group(self):
        facebook = "https://www.facebook.com/MarinaArtDesignStudio"
        QDesktopServices.openUrl(QUrl(facebook))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MathSquareGeneratorApp()
    window.show()
    sys.exit(app.exec_())


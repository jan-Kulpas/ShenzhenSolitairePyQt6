import os
import random
import sys

import constants
from logic import *

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("ShenzhenSolitairePyQt - Kulpas\nOriginal by Zachtronics")
        layout.addWidget(self.label)
        self.setLayout(layout)

class RulesWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel()
        pixmap = QPixmap(os.path.join("images", "rules.png"))
        self.label.setPixmap(pixmap)

        layout.addWidget(self.label)
        self.setLayout(layout)
class BottomBar(QWidget):

    def __init__(self):
        super().__init__()
        self.setFixedHeight(30)
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor.fromRgb(0x888888))
        self.setPalette(palette)

        self.wins = QLabel("Wins: 0")
        self.timer = QLabel("Time: 0:00:00")
        self.best = QLabel("Best: 0:00:00")

        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.wins, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.timer, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.best, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.setLayout(layout)

    def setWins(self, c: int) -> None:
        self.wins.setText(f"Wins: {str(c)}")

    def setTime(self, t: QTime) -> None:
        self.timer.setText(f"Time: {t.toString()}")

    def setBest(self, t: QTime) -> None:
        self.best.setText(f"Time: {t.toString()}")


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.about = None
        self.rules = None

        self.setFixedSize(*constants.WINDOW_SIZE)
        self.setWindowTitle("Shenzhen Solitaire")

        self.view = QGraphicsView()
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene);

        scene_rect = QRectF(0, 0, constants.WINDOW_SIZE[0], constants.WINDOW_SIZE[1] - 90)
        self.scene.setSceneRect(scene_rect)

        about_menu = self.menuBar().addMenu("&Program")
        game_menu = self.menuBar().addMenu("&Gra")

        about_action = QAction("O programie", self)
        about_action.triggered.connect(self.show_about_menu)
        new_game_action = QAction("Nowa Gra", self)
        new_game_action.triggered.connect(self.new_game)
        show_rules_action = QAction("Jak grać", self)
        show_rules_action.triggered.connect(self.show_rules)
        about_menu.addAction(about_action)
        game_menu.addActions([new_game_action, show_rules_action])

        bg_img = QPixmap(os.path.join("images", "background.png"))
        bg_brush = QBrush(bg_img)
        self.scene.setBackgroundBrush(bg_brush)

        self.bar = BottomBar()

        self.load_save_data()

        self.bar.setWins(self.win_count)
        self.bar.setBest(self.best_time)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.bar)
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.new_game()
        self.show()

    def show_about_menu(self):
        if self.about is None:
            self.about = AboutWindow()
        self.about.show()

    def new_game(self):
        self.timer = QTimer()
        self.time = QTime(0,0,0)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

        self.scene.clear()
        self.board = Board(self.scene)
        self.board.generate_deck()
        self.board.deal()
        self.board.signals.win.connect(self.win)

    def show_rules(self):
        if self.rules is None:
            self.rules = RulesWindow()
        self.rules.show()


    def win(self):
        print("You won!")
        self.win_count += 1
        self.best_time = self.time if self.time < self.best_time else self.best_time
        self.timer.stop()

        self.bar.setWins(self.win_count)
        self.bar.setBest(self.best_time)
        self.update_save_data()

    def load_save_data(self) -> None:
        print(QTime(0,2,2) > QTime(1,1,1))
        self.win_count = 0
        self.best_time = QTime(0,0,0)
        try:
            with open("save.txt", "r") as f:
                self.win_count = int(next(f).split()[0])
                self.best_time = QTime.fromString(next(f).split()[0], "hh:mm:ss")
                print(self.best_time.toString())
        except IOError:
            self.win_count = 0
            self.best_time = QTime(0,0,0)

    def update_save_data(self) -> None:
        try:
            with open("save.txt", "w+") as f:
                f.write(f"{str(self.win_count)}\n")
                f.write(f"{self.best_time.toString()}\n")
        except IOError:
            pass
    
    def update_timer(self):
        self.time = self.time.addSecs(1)
        self.bar.setTime(self.time)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec()

import os
import random
import sys

import constants
from logic import *

from PyQt6.QtCore import (
    QPoint,
    QPointF,
    QRectF,
    Qt,
    QTimer,
)
from PyQt6.QtGui import (
    QAction,
    QActionGroup,
    QBrush,
    QIcon,
    QPixmap,
)
from PyQt6.QtWidgets import (
    QApplication,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QMainWindow,
    QMessageBox,
    QWidget,
)

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setFixedSize(*constants.WINDOW_SIZE)
        self.setWindowTitle("Shenzhen Solitaire")

        view = QGraphicsView()
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scene = QGraphicsScene()
        view.setScene(self.scene);
        self.setCentralWidget(view)

        scene_rect = QRectF(0, 0, constants.WINDOW_SIZE[0], constants.WINDOW_SIZE[1] - 50)
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

        self.new_game()

        self.show()

    def show_about_menu(self):
        print("About")

    def new_game(self):
        self.scene.clear()
        self.board = Board(self.scene)
        self.board.generate_deck()
        self.board.deal()

    def show_rules(self):
        print("Show rules")

    def win(self):
        print("You won!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec()

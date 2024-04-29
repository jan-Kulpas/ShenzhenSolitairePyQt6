from enum import Enum
import os
import random
from typing import List

import constants
from PyQt6.QtCore import QObject, QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QPen, QPixmap
from PyQt6.QtWidgets import (
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSceneMouseEvent,
)


class Suit(Enum):
    NONE = 0
    BLACK = 1
    RED = 2
    GREEN = 3

class Rank(Enum):
    NONE = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9

class Card(QGraphicsPixmapItem):
    class Signals(QObject):
        dropped = pyqtSignal()
        doubleclicked = pyqtSignal()

    def __init__(self, rank: Rank, suit: Suit) -> None:
        super().__init__()
        self.rank = rank
        self.suit = suit

        self.stack: Stack | Cell = None
        self.child: Card = None
        
        self.signals = Card.Signals()

        self.setShapeMode(QGraphicsPixmapItem.ShapeMode.BoundingRectShape)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        pixmap = QPixmap(os.path.join("images","cards",f"{self.name}.png"))
        pixmap = pixmap.scaled(constants.CARD_DIMENSIONS.width(), constants.CARD_DIMENSIONS.height())
        self.setPixmap(pixmap)

    @property
    def is_special_card(self) -> bool:
        return self.rank == Rank.NONE or self.suit == Suit.NONE
    
    @property
    def is_free(self) -> bool:
        return self.child == None or self.can_receive_card(self.child)
    
    @property
    def can_be_picked_up(self) -> bool:
        return self.is_free and not isinstance(self.stack, (FoundationStack, FlowerCell))
    
    def is_dragon(self, suit: Suit) -> bool:
        return self.suit == suit and self.rank == Rank.NONE

    def can_receive_card(self, other: "Card") -> bool:
        if(self.is_special_card or other.is_special_card):
            return False
        return other.suit != self.suit and other.rank == Rank(self.rank.value - 1)

    def resetPosition(self) -> None:
        if isinstance(self.parentItem(), Card) and not isinstance(self.stack, FoundationStack):
            self.setPos(0, constants.WORK_OFFSET_Y)
        else:
            self.setPos(0, 0)

    def mousePressEvent(self, e) -> None:
        if not self.can_be_picked_up:
            e.ignore()
            return
        self.stack.setZValue(1000) #todo: check
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e) -> None:
        super().mouseReleaseEvent(e)

        self.stack.setZValue(0)
        items = self.collidingItems()
        if items:
            for item in items:
                selected_stack = None
                if isinstance(item, Card):
                    selected_stack = item.stack
                elif isinstance(item, Stack) or isinstance(item, Cell):
                    selected_stack = item

                if selected_stack and selected_stack.can_accept(self):
                    self.stack.remove_card(self)
                    selected_stack.add_card(self)

        self.signals.dropped.emit()
        self.resetPosition()

    def mouseDoubleClickEvent(self, e) -> None:
        super().mouseDoubleClickEvent(e)
        self.signals.doubleclicked.emit()
        self.stack.setZValue(0)

    def __str__(self) -> str:
        s = self.suit.name.title() if self.suit != Suit.NONE else "Flower"
        return f"{self.rank.value} of {s}"
    
    def __repr__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        s = self.suit.name[0] if self.suit != Suit.NONE else "F"
        return f"{self.rank.value}{s}"

class Cell(QGraphicsRectItem):
    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        self.card = None

        self.setPos(x, y)
        self.setRect(QRectF(constants.CARD_RECT))
        self.setPen(QPen(Qt.PenStyle.NoPen))

    def can_accept(self, card: Card) -> bool:
        raise NotImplementedError()
    
    def add_card(self, card: Card) -> None:
        card.setParentItem(self)

        card.stack = self
        card.resetPosition()
        card.setZValue(1)

        self.card = card

    def remove_card(self, card: Card) -> None:
        self.card.stack = None
        self.card.child = None
        self.card.setParentItem(None)
        self.card = None

class TempCell(Cell):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        self.collapsed = False

        color = QColor(Qt.GlobalColor.black)
        color.setAlpha(75)
        pen = QPen(color)
        pen.setWidth(5)
        self.setPen(pen)

    @property
    def empty(self) -> bool:
        return not self.card and not self.collapsed
    
    def has_dragon(self, suit: Suit) -> bool:
        return self.card and self.card.is_dragon(suit)

    def can_accept(self, card: Card) -> bool:
        return not self.collapsed and not self.card and not card.child
    
    def collapse(self):
        self.collapsed = True

        color = QColor(Qt.GlobalColor.darkGreen)
        brush = QBrush(color)
        self.setBrush(brush)

    
class FlowerCell(Cell):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)

        color = QColor(Qt.GlobalColor.darkMagenta)
        color.setAlpha(90)
        pen = QPen(color)
        pen.setWidth(5)
        self.setPen(pen)

    def can_accept(self, card: Card) -> bool:
        return card.suit == Suit.NONE and card.rank == Rank.NONE and not self.card and not card.child

class Stack(QGraphicsRectItem):
    def __init__(self, x: int, y: int) -> None:
        super().__init__()

        self.cards: List[Card] = []

        self.setPos(x, y)
        self.setRect(QRectF(constants.CARD_RECT))
        self.setPen(QPen(Qt.PenStyle.NoPen))

    @property
    def size(self) -> int:
        return len(self.cards)
    
    def can_accept(self, card: Card) -> bool:
        raise NotImplementedError()

    def add_card(self, card: Card) -> None:
        if(self.size > 0):
            card.setParentItem(self.cards[-1])
            self.cards[-1].child = card
        else:
            card.setParentItem(self)

        card.stack = self
        card.resetPosition()
        card.setZValue(self.size)

        self.cards.append(card)

        if(card.child):
            self.add_card(card.child)

    def remove_card(self, card: Card) -> None:
        idx = self.cards.index(card)
        self.cards[idx-1].child = None
        card.setParentItem(None)

        for c in self.cards[idx:]:
            c.stack = None
            self.cards.remove(c)

    def __str__(self) -> str:
        return str(self.cards)
    
    def __repr__(self) -> str:
        return self.__str__()

class WorkStack(Stack):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)

        color = QColor(Qt.GlobalColor.black)
        color.setAlpha(75)
        brush = QBrush(color)
        self.setBrush(brush)
    
    def can_accept(self, card: Card) -> bool:
        return self.size == 0 or (self.cards[-1].can_receive_card(card))

class FoundationStack(Stack):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)

        color = QColor(Qt.GlobalColor.blue)
        color.setAlpha(75)
        pen = QPen(color)
        pen.setWidth(5)
        self.setPen(pen)

    def can_accept(self, card: Card) -> bool:
        if card.is_special_card:
            return False
        if self.size == 0:
            return card.rank == Rank.ONE
        return self.cards[-1].rank == Rank(card.rank.value - 1) and self.cards[-1].suit == card.suit

class Button(QGraphicsPixmapItem):
    def __init__(self, x: int, y: int, suit: Suit) -> None:
        super().__init__()

        self.suit = suit

        self.board: Board = None

        self.setPos(x, y)
        self.setShapeMode(QGraphicsPixmapItem.ShapeMode.BoundingRectShape)

        w = constants.BUTTON_DIMENSIONS.width()
        h = constants.BUTTON_DIMENSIONS.height()
        self.pixmap_off = QPixmap(os.path.join("images","buttons",f"B0{suit.name[0]}.png")).scaled(w,h)
        self.pixmap_on = QPixmap(os.path.join("images","buttons",f"B1{suit.name[0]}.png")).scaled(w,h)

        self.disable()
        
    def enable(self) -> None:
        self.setEnabled(True)
        self.setPixmap(self.pixmap_on)

    def disable(self) -> None:
        self.setEnabled(False)
        self.setPixmap(self.pixmap_off)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent | None) -> None:
        super().mousePressEvent(event)
        self.board.collapse_dragon(self.suit)


class Board(QObject):
    class Signals(QObject):
        win = pyqtSignal()

    def __init__(self, scene: QGraphicsScene) -> None:
        super().__init__()
        self.signals = Board.Signals()

        self.scene = scene

        self.temp_cells: List[TempCell] = []
        self.foundation: List[FoundationStack] = []
        self.work_stacks: List[WorkStack] = []
        self.buttons: List[Button] = []
        self.deck: List[Card] = []

        self.flower_cell = FlowerCell(constants.MARGIN_LEFT + 4*constants.CARD_SPACING_X, constants.MARGIN_TOP)
        scene.addItem(self.flower_cell)

        for i in range(3):
            cell = TempCell(constants.MARGIN_LEFT + i*constants.CARD_SPACING_X, constants.MARGIN_TOP)
            scene.addItem(cell)
            self.temp_cells.append(cell)

            foun = FoundationStack(constants.MARGIN_LEFT + (i+5)*constants.CARD_SPACING_X, constants.MARGIN_TOP)
            scene.addItem(foun)
            self.foundation.append(foun)

            button = Button(constants.BUTTON_MARGIN_X, constants.BUTTON_MARGIN_Y+i*constants.BUTTON_SPACING_Y, Suit(i+1))
            button.board = self
            scene.addItem(button)
            self.buttons.append(button)
        
        for i in range(8):
            stack = WorkStack(constants.MARGIN_LEFT + constants.CARD_SPACING_X * i, constants.WORK_PILE_Y)
            scene.addItem(stack)
            self.work_stacks.append(stack)


    def generate_deck(self) -> None:
        for suit in [Suit.BLACK, Suit.GREEN, Suit.RED]:
            for rank in range(1,10):
                self.deck.append(Card(Rank(rank), suit))
                pass
            for _ in range(4):
                self.deck.append(Card(Rank.NONE, suit))
        self.deck.append(Card(Rank.NONE, Suit.NONE))

        for card in self.deck:
            self.scene.addItem(card)
            card.signals.dropped.connect(self.check_buttons)
            card.signals.dropped.connect(self.check_win)
            card.signals.doubleclicked.connect(
                lambda card=card: self.auto_drop(card)
            )

    def deal(self) -> None:
        random.shuffle(self.deck)
        #deal what you can evenly
        n = len(self.deck)//len(self.work_stacks)
        for i, stack in enumerate(self.work_stacks):
            for j in range(n):
                stack.add_card(self.deck[i*n+j])

        #deal extra cards to leftmost stacks
        for i in range(len(self.deck)%len(self.work_stacks)):
            self.work_stacks[i].add_card(self.deck[-(i+1)])
    
    def auto_drop(self, card: Card):
        for stack in [*self.foundation, self.flower_cell]:
            if stack.can_accept(card):
                card.stack.setZValue(0)
                card.stack.remove_card(card)
                stack.add_card(card)
                card.resetPosition()


    def check_buttons(self) -> None:
        for button in self.buttons:
            suit = button.suit
            count = 0
            free_cell = False

            for cell in self.temp_cells:
                if cell.empty or cell.has_dragon(suit):
                    free_cell = True
        
            #todo: could just loop through deck probably
            for stack in self.work_stacks:
                if stack.size > 0:
                    if stack.cards[-1].is_dragon(suit):
                        count +=1
            for cell in self.temp_cells:
                if cell.has_dragon(suit):
                    count +=1
            if(count == 4 and free_cell):
                button.enable()
            else:
                button.disable()

    def collapse_dragon(self, suit: Suit):
        for stack in self.work_stacks:
            if stack.size > 0:
                if stack.cards[-1].is_dragon(suit):
                    self.scene.removeItem(stack.cards[-1])
                    stack.remove_card(stack.cards[-1])
        for cell in self.temp_cells:
            if cell.card:
                if cell.card.is_dragon(suit):
                    self.scene.removeItem(cell.card)
                    cell.remove_card(cell.card)
        for cell in self.temp_cells:
            if cell.empty:
                cell.collapse()
                break

        self.check_buttons()

    def check_win(self) -> None:
        for stack in self.foundation:
            if stack.size < 9:
                return
        if not self.flower_cell.card:
            return
        self.signals.win.emit()
        
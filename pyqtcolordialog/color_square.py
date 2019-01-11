import enum

from PyQt5 import QtCore, QtGui, QtWidgets

from .color_model import ColorModel, black_or_white
from .util import is_imprecise_click, is_precise_click


class ColorSquareStyle(enum.IntEnum):
    Hue = 1
    Saturation = 2
    Value = 3
    Red = 4
    Green = 5
    Blue = 6


class ColorSquare(QtWidgets.QFrame):
    def __init__(
        self,
        parent: QtWidgets.QWidget,
        model: ColorModel,
        square_style: ColorSquareStyle = ColorSquareStyle.Hue,
    ) -> None:
        super().__init__(parent)

        self._square_style = square_style
        self._model = model
        self._pressed = False

        self._model.changed.connect(self.update)

        self.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken)
        self.setFixedSize(300, 300)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum
        )

    @property
    def square_style(self) -> ColorSquareStyle:
        return self._square_style

    def set_square_style(self, square_style: ColorSquareStyle) -> None:
        self._square_style = square_style
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        rect = self.rect()
        rect -= QtCore.QMargins(*[self.lineWidth()] * 4)

        painter = QtGui.QPainter(self)
        painter.setRenderHint(painter.Antialiasing)

        for y in range(rect.top(), rect.top() + rect.height()):
            x1 = 0
            x2 = self.width()
            gradient = QtGui.QLinearGradient(x1, y, x2, y)
            self._decorate_gradient(gradient, y / rect.height())

            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(gradient)
            painter.drawRect(QtCore.QRect(rect.left(), y, rect.width(), 1))

        pos = self._get_color_pos()
        pos.setX(pos.x() * rect.width())
        pos.setY(pos.y() * rect.height())

        cx = pos.x()
        cy = pos.y()

        painter.setPen(QtGui.QPen(black_or_white(self._model.color), 1.5))
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawEllipse(QtCore.QRect(cx - 5, cy - 5, 10, 10))

        super().paintEvent(event)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        is_precise = is_precise_click(event.button(), self.style())
        is_imprecise = is_imprecise_click(event.button(), self.style())

        if is_precise or is_imprecise:
            event.accept()
            self._sync(event.pos())
            if is_imprecise:
                self._pressed = True
            return

        event.ignore()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self._pressed:
            event.accept()
            self._sync(event.pos())
        else:
            event.ignore()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self._pressed = None

    def _get_color_pos(self) -> QtCore.QPointF:
        if self._square_style == ColorSquareStyle.Hue:
            return QtCore.QPointF(self._model.s, 1 - self._model.v)
        elif self._square_style == ColorSquareStyle.Saturation:
            return QtCore.QPointF(self._model.h, 1 - self._model.v)
        elif self._square_style == ColorSquareStyle.Value:
            return QtCore.QPointF(self._model.h, 1 - self._model.s)
        elif self._square_style == ColorSquareStyle.Red:
            return QtCore.QPointF(self._model.b, 1 - self._model.g)
        elif self._square_style == ColorSquareStyle.Green:
            return QtCore.QPointF(self._model.b, 1 - self._model.r)
        elif self._square_style == ColorSquareStyle.Blue:
            return QtCore.QPointF(self._model.r, 1 - self._model.g)
        else:
            assert False

    def _decorate_gradient(self, gradient: QtGui.QGradient, y: float) -> None:
        if self._square_style == ColorSquareStyle.Hue:
            for i in [0, 1]:
                gradient.setColorAt(
                    i, QtGui.QColor.fromHsvF(self._model.h, i, 1 - y)
                )

        elif self._square_style == ColorSquareStyle.Saturation:
            for i in range(6):
                gradient.setColorAt(
                    i / 6, QtGui.QColor.fromHsvF(i / 6, self._model.s, 1 - y)
                )

        elif self._square_style == ColorSquareStyle.Value:
            for i in range(6):
                gradient.setColorAt(
                    i / 6, QtGui.QColor.fromHsvF(i / 6, 1 - y, self._model.v)
                )

        elif self._square_style == ColorSquareStyle.Red:
            for i in [0, 1]:
                gradient.setColorAt(
                    i, QtGui.QColor.fromRgbF(self._model.r, 1 - y, i)
                )

        elif self._square_style == ColorSquareStyle.Green:
            for i in [0, 1]:
                gradient.setColorAt(
                    i, QtGui.QColor.fromRgbF(1 - y, self._model.g, i)
                )

        elif self._square_style == ColorSquareStyle.Blue:
            for i in [0, 1]:
                gradient.setColorAt(
                    i, QtGui.QColor.fromRgbF(i, 1 - y, self._model.b)
                )

        else:
            assert False

    def _sync(self, pos: QtCore.QPoint) -> None:
        x = pos.x() / self.rect().width()
        y = pos.y() / self.rect().height()
        if self._square_style == ColorSquareStyle.Hue:
            self._model.s = x
            self._model.v = 1 - y
        elif self._square_style == ColorSquareStyle.Saturation:
            self._model.h = x
            self._model.v = 1 - y
        elif self._square_style == ColorSquareStyle.Value:
            self._model.h = x
            self._model.s = 1 - y
        elif self._square_style == ColorSquareStyle.Red:
            self._model.b = x
            self._model.g = 1 - y
        elif self._square_style == ColorSquareStyle.Green:
            self._model.b = x
            self._model.r = 1 - y
        elif self._square_style == ColorSquareStyle.Blue:
            self._model.r = x
            self._model.g = 1 - y
        else:
            assert False

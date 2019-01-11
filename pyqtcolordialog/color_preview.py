import typing as T

from PyQt5 import QtCore, QtGui, QtWidgets

from .color_model import ColorModel, black_or_white


class ColorPreview(QtWidgets.QFrame):
    def __init__(
        self,
        parent: QtWidgets.QWidget,
        orig_color: QtGui.QColor,
        model: ColorModel,
        alpha_grid: QtGui.QPixmap,
    ) -> None:
        super().__init__(parent)
        self._orig_color = orig_color
        self._model = model
        self._alpha_grid = alpha_grid

        self._model.changed.connect(self.update)

        self.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken)

    def sizeHint(self) -> T.Tuple[int, int]:
        return QtCore.QSize(300, 50)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        rect = self.rect()
        rect -= QtCore.QMargins(*[self.lineWidth()] * 4)

        left = QtCore.QRect(rect)
        left.setWidth(left.width() // 2)
        right = QtCore.QRect(rect)
        right.setLeft(left.width())

        painter = QtGui.QPainter()
        painter.begin(self)
        painter.drawTiledPixmap(rect, self._alpha_grid)
        self._draw_color(painter, left, self._orig_color)
        self._draw_color(painter, right, self._model.color)
        painter.end()

        super().paintEvent(event)

    def _draw_color(
        self, painter: QtGui.QPainter, rect: QtCore.QRect, color: QtGui.QColor
    ) -> None:
        text = f"#{color.red():02X}{color.green():02X}{color.blue():02X}"
        painter.fillRect(rect, color)

        painter.setPen(black_or_white(color))
        painter.drawText(rect, QtCore.Qt.AlignCenter, text)

    def set_color(self, color: QtGui.QColor) -> None:
        self._color = color
        self.update()

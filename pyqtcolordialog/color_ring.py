import math
import sys
import typing as T

from PyQt5 import QtCore, QtGui, QtWidgets

from .color_model import ColorModel, black_or_white
from .geometry import point_in_ring, point_in_triangle
from .util import blend, clamp, is_imprecise_click, is_precise_click


class ColorRing(QtWidgets.QWidget):
    _ring_outer_radius = 150
    _ring_width = 35

    def __init__(self, parent: QtWidgets.QWidget, model: ColorModel) -> None:
        super().__init__(parent)
        self._model = model
        self._model.changed.connect(self.update)

        self._pressed_control: T.Optional[str] = None
        self._ring_gradient = QtGui.QConicalGradient(
            QtCore.QPoint(self._ring_outer_radius, self._ring_outer_radius),
            0.0,
        )
        self._ring_gradient.setColorAt(0 / 6, QtGui.QColor(255, 0, 0, 255))
        self._ring_gradient.setColorAt(1 / 6, QtGui.QColor(255, 0, 255, 255))
        self._ring_gradient.setColorAt(2 / 6, QtGui.QColor(0, 0, 255, 255))
        self._ring_gradient.setColorAt(3 / 6, QtGui.QColor(0, 255, 255, 255))
        self._ring_gradient.setColorAt(4 / 6, QtGui.QColor(0, 255, 0, 255))
        self._ring_gradient.setColorAt(5 / 6, QtGui.QColor(255, 255, 0, 255))
        self._ring_gradient.setColorAt(6 / 6, QtGui.QColor(255, 0, 0, 255))

        self.setFixedSize(self._ring_outer_diameter, self._ring_outer_diameter)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum
        )

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, self._draw_ring())
        painter.drawImage(0, 0, self._draw_triangle())

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        is_precise = is_precise_click(event.button(), self.style())
        is_imprecise = is_imprecise_click(event.button(), self.style())

        if is_precise or is_imprecise:
            if point_in_ring(
                event.pos() - self.rect().center(),
                self._ring_inner_radius,
                self._ring_outer_radius,
            ):
                event.accept()
                self._sync_hue_from_ring(event.pos())
                if is_imprecise:
                    self._pressed_control = "ring"
                return

            if point_in_triangle(event.pos(), self._get_triangle_points()):
                event.accept()
                self._sync_value_and_saturation_from_triangle(event.pos())
                if is_imprecise:
                    self._pressed_control = "triangle"
                return

        event.ignore()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self._pressed_control == "ring":
            event.accept()
            self._sync_hue_from_ring(event.pos())
        elif self._pressed_control == "triangle":
            event.accept()
            self._sync_value_and_saturation_from_triangle(event.pos())
        else:
            event.ignore()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self._pressed_control = None

    def _sync_value_and_saturation_from_triangle(
        self, pos: QtCore.QPoint
    ) -> None:
        transform, _ = self._get_triangle_transform().inverted()
        pos = transform.map(pos)

        height = self._triangle_height
        side = self._triangle_side

        p1c, p2c, p3c = self._get_triangle_colors()
        y_ratio = pos.y() / height
        y_ratio = clamp(y_ratio, 0, 1)
        x1 = (1 - y_ratio) / 2
        x2 = 1 - x1
        x_ratio = ((pos.x() / side) - x1) / max(sys.float_info.min, x2 - x1)
        x_ratio = clamp(x_ratio, 0, 1)

        y_c1 = blend(p1c, p2c, y_ratio)
        y_c2 = blend(p1c, p3c, y_ratio)
        x_c = blend(y_c1, y_c2, x_ratio)

        self._model.s = x_c.saturationF()
        self._model.v = x_c.valueF()

    def _sync_hue_from_ring(self, pos: QtCore.QPoint) -> None:
        pos -= self.rect().center()
        x = pos.x()
        y = pos.y()
        theta = (math.atan2(y, x) / (2 * math.pi)) % 1.0
        self._model.h = theta

    @property
    def _ring_inner_radius(self) -> int:
        return self._ring_outer_radius - self._ring_width

    @property
    def _ring_inner_diameter(self) -> int:
        return self._ring_inner_radius * 2

    @property
    def _ring_outer_diameter(self) -> int:
        return self._ring_outer_radius * 2

    @property
    def _triangle_side(self) -> int:
        return int(self._ring_inner_radius * 3 / math.sqrt(3))

    @property
    def _triangle_height(self) -> int:
        return int(self._ring_inner_radius * 3 / 2)

    def _get_triangle_transform(self) -> QtGui.QTransform:
        transform = QtGui.QTransform()
        transform.translate(self._ring_outer_radius, self._ring_outer_radius)
        transform.rotate(self._model.h * 360.0)
        transform.rotate(90.0)
        transform.translate(
            -self._triangle_side / 2, -self._triangle_height * 2 / 3
        )
        return transform

    def _get_triangle_points(
        self, use_transform: bool = True
    ) -> T.Tuple[QtCore.QPoint, QtCore.QPoint, QtCore.QPoint]:
        p1 = QtCore.QPoint(self._triangle_side / 2, 0)
        p2 = QtCore.QPoint(0, self._triangle_height)
        p3 = QtCore.QPoint(self._triangle_side, self._triangle_height)
        if use_transform:
            transform = self._get_triangle_transform()
            p1 = transform.map(p1)
            p2 = transform.map(p2)
            p3 = transform.map(p3)
        return (p1, p2, p3)

    def _get_triangle_colors(
        self
    ) -> T.Tuple[QtGui.QColor, QtGui.QColor, QtGui.QColor]:
        p1c = QtGui.QColor.fromHsvF(self._model.h, 1, 1)
        p2c = QtGui.QColor.fromHsvF(self._model.h, 1, 0)
        p3c = QtGui.QColor.fromHsvF(self._model.h, 0, 1)
        return (p1c, p2c, p3c)

    def _draw_ring(self) -> QtGui.QImage:
        image = QtGui.QImage(
            self._ring_outer_diameter,
            self._ring_outer_diameter,
            QtGui.QImage.Format_ARGB32,
        )
        image.fill(0)

        painter = QtGui.QPainter(image)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.white)
        painter.drawEllipse(
            0, 0, self._ring_outer_diameter, self._ring_outer_diameter
        )

        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
        painter.setBrush(QtCore.Qt.transparent)
        painter.drawEllipse(
            self._ring_width,
            self._ring_width,
            self._ring_inner_diameter,
            self._ring_inner_diameter,
        )

        painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceAtop)
        painter.setBrush(QtGui.QBrush(self._ring_gradient))
        painter.drawRect(image.rect())

        theta = self._model.h
        painter.setPen(
            QtGui.QPen(
                black_or_white(QtGui.QColor.fromHsvF(self._model.h, 1, 1)), 1.5
            )
        )
        painter.translate(self._ring_outer_radius, self._ring_outer_radius)
        painter.rotate(self._model.h * 360.0)
        painter.drawLine(0, 0, self._ring_outer_diameter, 0)

        return image

    def _draw_triangle(self) -> QtGui.QImage:
        height = self._triangle_height
        side = self._triangle_side

        image = QtGui.QImage(
            self._ring_outer_diameter,
            self._ring_outer_diameter,
            QtGui.QImage.Format_ARGB32,
        )
        image.fill(0)

        painter = QtGui.QPainter(image)
        painter.setRenderHint(painter.Antialiasing)

        p1, p2, p3 = self._get_triangle_points(use_transform=False)
        p1c, p2c, p3c = self._get_triangle_colors()

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.black)
        painter.setTransform(self._get_triangle_transform())
        painter.drawPolygon(p1, p2, p3)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceAtop)

        for y in range(0, height):
            ratio = y / height
            x1 = (1 - ratio) / 2
            x2 = 1 - x1
            c1 = blend(p1c, p2c, ratio)
            c2 = blend(p1c, p3c, ratio)

            gradient = QtGui.QLinearGradient(x1 * side, y, x2 * side, y)
            gradient.setColorAt(0, c1)
            gradient.setColorAt(1, c2)
            painter.setBrush(gradient)
            painter.drawRect(0, y, side, 2)

        v = self._model.v
        s = self._model.s
        cx = math.floor(
            p2.x() + (p3.x() - p2.x()) * v + (p1.x() - p3.x()) * s * v + 0.5
        )
        cy = math.floor(
            p2.y() + (p3.y() - p2.y()) * v + (p1.y() - p3.y()) * s * v + 0.5
        )

        painter.setPen(QtGui.QPen(black_or_white(self._model.color), 1.5))
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
        painter.drawEllipse(QtCore.QRect(cx - 5, cy - 5, 10, 10))

        return image

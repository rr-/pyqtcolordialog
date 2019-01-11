import math
import typing as T

from PyQt5 import QtCore, QtGui


class ColorModel(QtCore.QObject):
    changed = QtCore.pyqtSignal()

    def __init__(self, color: QtGui.QColor) -> None:
        super().__init__()
        self._h: float = color.hueF()
        self._s: float = color.saturationF()
        self._v: float = color.valueF()
        self._r: float = color.redF()
        self._g: float = color.greenF()
        self._b: float = color.blueF()
        self._a: float = color.alphaF()
        self._syncing = False
        self._color = QtGui.QColor(color)

    @property
    def color(self) -> QtGui.QColor:
        return self._color

    @color.setter
    def color(self, color: QtGui.QColor) -> None:
        self._r = color.redF()
        self._g = color.greenF()
        self._b = color.blueF()
        self._sync_to_hsv()
        self.a = color.alphaF()

    def _sync_to_rgb(self) -> None:
        if self._syncing:
            return
        self._syncing = True
        self._color = QtGui.QColor.fromHsvF(self.h, self.s, self.v, self.a)
        self.r = self._color.redF()
        self.g = self._color.greenF()
        self.b = self._color.blueF()
        self._syncing = False

    def _sync_to_hsv(self) -> None:
        if self._syncing:
            return
        self._syncing = True
        self._color = QtGui.QColor.fromRgbF(self.r, self.g, self.b, self.a)
        self.h = self._color.hueF()
        self.s = self._color.saturationF()
        self.v = self._color.valueF()
        self._syncing = False

    @property
    def a(self) -> float:
        return self._a

    @a.setter
    def a(self, a: float) -> None:
        a = max(0.0, min(1.0, a))
        if a != self._a:
            self._a = a
            self.changed.emit()
            self._color.setAlphaF(a)

    @property
    def h(self) -> float:
        return self._h

    @h.setter
    def h(self, h: float) -> None:
        h = max(0.0, min(1.0, h))
        if h != self._h:
            self._h = h
            self._sync_to_rgb()
            self.changed.emit()

    @property
    def s(self) -> float:
        return self._s

    @s.setter
    def s(self, s: float) -> None:
        s = max(0.0, min(1.0, s))
        if s != self._s:
            self._s = s
            self._sync_to_rgb()
            self.changed.emit()

    @property
    def v(self) -> float:
        return self._v

    @v.setter
    def v(self, v: float) -> None:
        v = max(0.0, min(1.0, v))
        if v != self._v:
            self._v = v
            self._sync_to_rgb()
            self.changed.emit()

    @property
    def r(self) -> float:
        return self._r

    @r.setter
    def r(self, r: float) -> None:
        r = max(0.0, min(1.0, r))
        if r != self._r:
            self._r = r
            self._sync_to_hsv()
            self.changed.emit()

    @property
    def g(self) -> float:
        return self._g

    @g.setter
    def g(self, g: float) -> None:
        g = max(0.0, min(1.0, g))
        if g != self._g:
            self._g = g
            self._sync_to_hsv()
            self.changed.emit()

    @property
    def b(self) -> float:
        return self._b

    @b.setter
    def b(self, b: float) -> None:
        b = max(0.0, min(1.0, b))
        if b != self._b:
            self._b = b
            self._sync_to_hsv()
            self.changed.emit()


def black_or_white(color: QtGui.QColor) -> int:
    rgb: T.List[float] = []
    for c in [color.redF(), color.greenF(), color.blueF()]:
        if c <= 0.03928:
            c = c / 12.92
        else:
            c = ((c + 0.055) / 1.055) ** 2.4
        rgb.append(c)
    r, g, b = rgb
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    if luminance > math.sqrt(1.05 * 0.05) - 0.05:
        return QtCore.Qt.black
    return QtCore.Qt.white

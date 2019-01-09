import functools
import math
import typing as T
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets

from .color_model import ColorModel, black_or_white
from .color_preview import ColorPreview
from .color_ring import ColorRing
from .color_sliders import (
    AlphaColorControl,
    BlueColorControl,
    GreenColorControl,
    HueColorControl,
    RedColorControl,
    SaturationColorControl,
    ValueColorControl,
)
from .util import is_imprecise_click, is_precise_click


class QColorDialog(QtWidgets.QDialog):
    def __init__(
        self,
        color: T.Optional[QtGui.QColor] = None,
        parent: QtWidgets.QWidget = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Select color...")

        self._alpha_grid = QtGui.QPixmap(
            str(Path(__file__).parent / "grid.png")
        )

        self._orig_color = color
        self._model = ColorModel(
            color if color is not None else QtGui.QColor(0, 0, 0)
        )

        strip = QtWidgets.QDialogButtonBox(self)
        strip.addButton(strip.Reset)
        strip.addButton(strip.Ok)
        strip.addButton(strip.Cancel)
        strip.accepted.connect(self.accept)
        strip.rejected.connect(self.reject)
        strip.button(strip.Reset).clicked.connect(self.reset)

        self._color_ring = ColorRing(self, self._model)
        self._color_preview = ColorPreview(
            self, color, self._model, self._alpha_grid
        )
        self._hue_slider = HueColorControl(self, self._model, self._alpha_grid)
        self._saturation_slider = SaturationColorControl(
            self, self._model, self._alpha_grid
        )
        self._value_slider = ValueColorControl(
            self, self._model, self._alpha_grid
        )
        self._red_slider = RedColorControl(self, self._model, self._alpha_grid)
        self._green_slider = GreenColorControl(
            self, self._model, self._alpha_grid
        )
        self._blue_slider = BlueColorControl(
            self, self._model, self._alpha_grid
        )
        self._alpha_slider = AlphaColorControl(
            self, self._model, self._alpha_grid
        )

        circle_layout = QtWidgets.QVBoxLayout()
        circle_layout.setSpacing(16)
        circle_layout.setContentsMargins(0, 0, 16, 0)
        circle_layout.addWidget(self._color_ring)
        circle_layout.addWidget(self._color_preview)

        layout = QtWidgets.QGridLayout(self)

        layout.addLayout(circle_layout, 0, 0, 11, 1)
        layout.addWidget(QtWidgets.QLabel("Hue:", self), 0, 1)
        layout.addWidget(QtWidgets.QLabel("Saturation:", self), 1, 1)
        layout.addWidget(QtWidgets.QLabel("Value:", self), 2, 1)
        layout.addWidget(self._hue_slider, 0, 2)
        layout.addWidget(self._saturation_slider, 1, 2)
        layout.addWidget(self._value_slider, 2, 2)

        layout.addWidget(QtWidgets.QFrame(self), 3, 1, 1, 2)

        layout.addWidget(QtWidgets.QLabel("Red:", self), 4, 1)
        layout.addWidget(QtWidgets.QLabel("Green:", self), 5, 1)
        layout.addWidget(QtWidgets.QLabel("Blue:", self), 6, 1)
        layout.addWidget(self._red_slider, 4, 2)
        layout.addWidget(self._green_slider, 5, 2)
        layout.addWidget(self._blue_slider, 6, 2)

        layout.addWidget(QtWidgets.QFrame(self), 7, 1, 1, 2)

        layout.addWidget(QtWidgets.QLabel("Transparency:", self), 8, 1)
        layout.addWidget(self._alpha_slider, 8, 2)

        layout.addWidget(QtWidgets.QFrame(self), 9, 1, 1, 2)

        layout.addWidget(strip, 10, 1, 1, 2)

        self.show()

    def reset(self) -> None:
        self._model.color = self._orig_color

    def value(self) -> QtGui.QColor:
        return self._model.color

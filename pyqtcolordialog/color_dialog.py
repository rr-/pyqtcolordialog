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
    ColorDialogOption = QtWidgets.QColorDialog.ColorDialogOption
    ColorDialogOptions = QtWidgets.QColorDialog.ColorDialogOptions
    ShowAlphaChannel = QtWidgets.QColorDialog.ShowAlphaChannel
    NoButtons = QtWidgets.QColorDialog.NoButtons
    DontUseNativeDialog = QtWidgets.QColorDialog.DontUseNativeDialog

    colorSelected = QtCore.pyqtSignal(QtGui.QColor)
    currentColorChanged = QtCore.pyqtSignal(QtGui.QColor)

    def __init__(
        self,
        initial: T.Optional[QtGui.QColor] = None,
        parent: QtWidgets.QWidget = None,
    ) -> None:
        super().__init__(parent)
        initial = (
            initial if initial is not None else QtGui.QColor(255, 255, 255)
        )

        self.setWindowTitle("Select color")

        self._alpha_grid = QtGui.QPixmap(
            str(Path(__file__).parent / "grid.png")
        )

        self._options = (
            QtWidgets.QColorDialog.ColorDialogOptions() | self.ShowAlphaChannel
        )

        self._initial = initial
        self._model = ColorModel(initial)

        self._strip = QtWidgets.QDialogButtonBox(self)
        self._strip.addButton(self._strip.Reset)
        self._strip.addButton(self._strip.Ok)
        self._strip.addButton(self._strip.Cancel)
        self._strip.accepted.connect(self.accept)
        self._strip.rejected.connect(self.reject)
        self._strip.button(self._strip.Reset).clicked.connect(self.reset)

        self._color_ring = ColorRing(self, self._model)
        self._color_preview = ColorPreview(
            self, initial, self._model, self._alpha_grid
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

        sliders_layout = QtWidgets.QGridLayout()
        sliders_layout.setContentsMargins(0, 0, 0, 0)
        sliders_layout.addWidget(QtWidgets.QLabel("Hue:", self), 0, 1)
        sliders_layout.addWidget(QtWidgets.QLabel("Saturation:", self), 1, 1)
        sliders_layout.addWidget(QtWidgets.QLabel("Value:", self), 2, 1)
        sliders_layout.addWidget(self._hue_slider, 0, 2)
        sliders_layout.addWidget(self._saturation_slider, 1, 2)
        sliders_layout.addWidget(self._value_slider, 2, 2)

        sliders_layout.addWidget(QtWidgets.QFrame(self), 3, 1, 1, 2)
        sliders_layout.addWidget(QtWidgets.QLabel("Red:", self), 4, 1)
        sliders_layout.addWidget(QtWidgets.QLabel("Green:", self), 5, 1)
        sliders_layout.addWidget(QtWidgets.QLabel("Blue:", self), 6, 1)
        sliders_layout.addWidget(self._red_slider, 4, 2)
        sliders_layout.addWidget(self._green_slider, 5, 2)
        sliders_layout.addWidget(self._blue_slider, 6, 2)

        self._alpha_widgets = [
            QtWidgets.QFrame(self),
            QtWidgets.QLabel("Transparency:", self),
            self._alpha_slider,
        ]
        sliders_layout.addWidget(self._alpha_widgets[0], 7, 1, 1, 2)
        sliders_layout.addWidget(self._alpha_widgets[1], 8, 1)
        sliders_layout.addWidget(self._alpha_widgets[2], 8, 2)

        self._strip_widgets = [QtWidgets.QFrame(self), self._strip]
        sliders_layout.addWidget(self._strip_widgets[0], 9, 1, 1, 2)
        sliders_layout.addWidget(self._strip_widgets[1], 10, 1, 1, 2)

        root_layout = QtWidgets.QHBoxLayout(self)
        root_layout.addLayout(circle_layout)
        root_layout.addLayout(sliders_layout)

        self._model.changed.connect(self._emit_signal)

        self.show()

    def options(self) -> QtWidgets.QColorDialog.ColorDialogOptions:
        return self._options

    def testOption(
        self, option: QtWidgets.QColorDialog.ColorDialogOption
    ) -> bool:
        return self._options & option

    def setOption(
        self, option: QtWidgets.QColorDialog.ColorDialogOption, on: bool = True
    ) -> None:
        if on:
            self._options |= option
        else:
            self._options &= ~option
        self._update_options()

    def setOptions(
        self, options: QtWidgets.QColorDialog.ColorDialogOptions
    ) -> None:
        self._options = options
        self._update_options()

    def setCurrentColor(self, color: QtGui.QColor) -> None:
        self._model.color = color

    def reset(self) -> None:
        self._model.color = self._initial

    def currentColor(self) -> QtGui.QColor:
        return self._model.color

    def selectedColor(self) -> QtGui.QColor:
        return self._model.color

    def alphaGrid(self) -> QtGui.QPixmap:
        return self._alpha_grid

    def setAlphaGrid(self, alpha_grid: QtGui.QPixmap) -> None:
        self._alpha_grid.convertFromImage(alpha_grid.toImage())
        self.update()

    @staticmethod
    def getColor(
        initial: T.Optional[QtGui.QColor] = None,
        parent: T.Optional[QtWidgets.QWidget] = None,
        title: T.Optional[str] = None,
        options: T.Optional[QtWidgets.QColorDialog.ColorDialogOptions] = None,
        alpha_grid: T.Optional[QtGui.QPixmap] = None,
    ) -> QtGui.QColor:
        dialog = QColorDialog(initial, parent)
        if title is not None:
            dialog.setWindowTitle(title)
        if options is not None:
            dialog.setOptions(options)
        if alpha_grid is not None:
            dialog.setAlphaGrid(alpha_grid)
        ret = dialog.exec_()
        if ret == QtWidgets.QDialog.Accepted:
            return dialog.selectedColor()
        return QtGui.QColor()

    def _update_options(self) -> None:
        for widget in self._alpha_widgets:
            widget.setVisible(self._options & self.ShowAlphaChannel)
        for widget in self._strip_widgets:
            widget.setVisible(not self._options & self.NoButtons)

    def _emit_signal(self) -> None:
        self.colorSelected.emit(self.selectedColor())
        self.currentColorChanged.emit(self.currentColor())

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


class ButtonStrip(QtWidgets.QDialogButtonBox):
    reset = QtCore.pyqtSignal()

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        self.addButton(self.Reset)
        self.addButton(self.Ok)
        self.addButton(self.Cancel)
        self.button(self.Reset).clicked.connect(self.reset.emit)


class SlidersControl(QtWidgets.QWidget):
    def __init__(
        self,
        parent: QtWidgets.QWidget,
        model: ColorModel,
        alpha_grid: QtGui.QPixmap,
    ) -> None:
        super().__init__(parent)
        layout = QtWidgets.QGridLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QtWidgets.QLabel("Hue:", self), 0, 1)
        layout.addWidget(QtWidgets.QLabel("Saturation:", self), 1, 1)
        layout.addWidget(QtWidgets.QLabel("Value:", self), 2, 1)
        layout.addWidget(HueColorControl(self, model, alpha_grid), 0, 2)
        layout.addWidget(SaturationColorControl(self, model, alpha_grid), 1, 2)
        layout.addWidget(ValueColorControl(self, model, alpha_grid), 2, 2)

        layout.addWidget(QtWidgets.QFrame(self), 3, 1, 1, 2)
        layout.addWidget(QtWidgets.QLabel("Red:", self), 4, 1)
        layout.addWidget(QtWidgets.QLabel("Green:", self), 5, 1)
        layout.addWidget(QtWidgets.QLabel("Blue:", self), 6, 1)
        layout.addWidget(RedColorControl(self, model, alpha_grid), 4, 2)
        layout.addWidget(GreenColorControl(self, model, alpha_grid), 5, 2)
        layout.addWidget(BlueColorControl(self, model, alpha_grid), 6, 2)

        self.alpha_widgets = [
            QtWidgets.QFrame(self),
            QtWidgets.QLabel("Transparency:", self),
            AlphaColorControl(self, model, alpha_grid),
        ]
        layout.addWidget(self.alpha_widgets[0], 7, 1, 1, 2)
        layout.addWidget(self.alpha_widgets[1], 8, 1)
        layout.addWidget(self.alpha_widgets[2], 8, 2)


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

        self._initial = initial
        self._model = ColorModel(initial)
        self._options = (
            QtWidgets.QColorDialog.ColorDialogOptions() | self.ShowAlphaChannel
        )
        self._alpha_grid = QtGui.QPixmap(
            str(Path(__file__).parent / "grid.png")
        )

        self._color_ring = ColorRing(self, self._model)
        self._color_preview = ColorPreview(
            self, initial, self._model, self._alpha_grid
        )
        self._sliders = SlidersControl(self, self._model, self._alpha_grid)
        self._strip = ButtonStrip(self)

        left_layout = QtWidgets.QVBoxLayout()
        left_layout.setSpacing(16)
        left_layout.setContentsMargins(0, 0, 16, 0)
        left_layout.addWidget(self._color_ring)
        left_layout.addWidget(self._color_preview)

        right_layout = QtWidgets.QVBoxLayout()
        right_layout.setSpacing(32)
        right_layout.addWidget(self._sliders)
        right_layout.addWidget(self._strip)

        root_layout = QtWidgets.QHBoxLayout(self)
        root_layout.addLayout(left_layout)
        root_layout.addLayout(right_layout)

        self._strip.accepted.connect(self.accept)
        self._strip.rejected.connect(self.reject)
        self._strip.reset.connect(self.reset)
        self._model.changed.connect(self._emit_signal)

        self.setWindowTitle("Select color")
        self.layout().setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
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
        for widget in self._sliders.alpha_widgets:
            widget.setVisible(self._options & self.ShowAlphaChannel)
        self._strip.setVisible(not self._options & self.NoButtons)

    def _emit_signal(self) -> None:
        self.colorSelected.emit(self.selectedColor())
        self.currentColorChanged.emit(self.currentColor())

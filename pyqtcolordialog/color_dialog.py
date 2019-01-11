import functools
import typing as T
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets

from .color_model import ColorModel
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
from .color_square import ColorSquare, ColorSquareStyle
from .screen_color_picker import ScreenColorPicker


class ButtonStrip(QtWidgets.QDialogButtonBox):
    reset = QtCore.pyqtSignal()
    pick = QtCore.pyqtSignal()

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        pick_button = QtWidgets.QPushButton("Pick screen color")
        self.addButton(self.Reset)
        self.addButton(pick_button, self.ActionRole)
        self.addButton(self.Ok)
        self.addButton(self.Cancel)
        self.button(self.Reset).clicked.connect(self.reset.emit)
        pick_button.clicked.connect(self.pick.emit)


class ClickableLabel(QtWidgets.QLabel):
    pressed = QtCore.pyqtSignal()
    released = QtCore.pyqtSignal()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() != QtCore.Qt.LeftButton:
            event.ignore()
        event.accept()
        self.pressed.emit()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() != QtCore.Qt.LeftButton:
            event.ignore()
        event.accept()
        self.released.emit()


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

        def mouse_down(radio_button: QtWidgets.QRadioButton) -> None:
            radio_button.setDown(True)

        def mouse_up(radio_button: QtWidgets.QRadioButton) -> None:
            radio_button.setDown(False)
            radio_button.setChecked(True)
            radio_button.clicked.emit()

        self.radio_buttons = {
            square_style: QtWidgets.QRadioButton(self)
            for square_style in ColorSquareStyle
        }
        self.labels = {
            square_style: ClickableLabel(square_style.name.title() + ":", self)
            for square_style in ColorSquareStyle
        }

        for label, radio_button in zip(
            self.labels.values(), self.radio_buttons.values()
        ):
            label.pressed.connect(functools.partial(mouse_down, radio_button))
            label.released.connect(functools.partial(mouse_up, radio_button))

        layout.addWidget(self.radio_buttons[ColorSquareStyle.Hue], 0, 0)
        layout.addWidget(self.radio_buttons[ColorSquareStyle.Saturation], 1, 0)
        layout.addWidget(self.radio_buttons[ColorSquareStyle.Value], 2, 0)
        layout.addWidget(self.labels[ColorSquareStyle.Hue], 0, 1)
        layout.addWidget(self.labels[ColorSquareStyle.Saturation], 1, 1)
        layout.addWidget(self.labels[ColorSquareStyle.Value], 2, 1)
        layout.addWidget(HueColorControl(self, model, alpha_grid), 0, 2)
        layout.addWidget(SaturationColorControl(self, model, alpha_grid), 1, 2)
        layout.addWidget(ValueColorControl(self, model, alpha_grid), 2, 2)

        layout.addWidget(QtWidgets.QFrame(self), 3, 1, 1, 2)

        layout.addWidget(self.radio_buttons[ColorSquareStyle.Red], 4, 0)
        layout.addWidget(self.radio_buttons[ColorSquareStyle.Green], 5, 0)
        layout.addWidget(self.radio_buttons[ColorSquareStyle.Blue], 6, 0)
        layout.addWidget(self.labels[ColorSquareStyle.Red], 4, 1)
        layout.addWidget(self.labels[ColorSquareStyle.Green], 5, 1)
        layout.addWidget(self.labels[ColorSquareStyle.Blue], 6, 1)
        layout.addWidget(RedColorControl(self, model, alpha_grid), 4, 2)
        layout.addWidget(GreenColorControl(self, model, alpha_grid), 5, 2)
        layout.addWidget(BlueColorControl(self, model, alpha_grid), 6, 2)

        self.alpha_widgets = [
            QtWidgets.QFrame(self),
            QtWidgets.QLabel("Opacity:", self),
            AlphaColorControl(self, model, alpha_grid),
        ]
        layout.addWidget(self.alpha_widgets[0], 7, 0, 1, 2)
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

        self._use_square_view = False
        self._initial = initial
        self._model = ColorModel(initial)
        self._screen_color_picker = ScreenColorPicker(self._model, self)
        self._options = (
            QtWidgets.QColorDialog.ColorDialogOptions() | self.ShowAlphaChannel
        )
        self._alpha_grid = QtGui.QPixmap(
            str(Path(__file__).parent / "grid.png")
        )

        self._color_square = ColorSquare(self, self._model)
        self._color_ring = ColorRing(self, self._model)
        self._color_preview = ColorPreview(
            self, initial, self._model, self._alpha_grid
        )
        self._sliders = SlidersControl(self, self._model, self._alpha_grid)
        self._strip = ButtonStrip(self)

        left_layout = QtWidgets.QVBoxLayout()
        left_layout.setSpacing(16)
        left_layout.setContentsMargins(0, 0, 16, 0)
        left_layout.addWidget(self._color_square)
        left_layout.addWidget(self._color_ring)
        left_layout.addWidget(self._color_preview)

        right_layout = QtWidgets.QVBoxLayout()
        right_layout.setSpacing(32)
        right_layout.addWidget(self._sliders)
        right_layout.addWidget(self._strip)

        root_layout = QtWidgets.QHBoxLayout(self)
        root_layout.addLayout(left_layout)
        root_layout.addLayout(right_layout)

        self._sliders.radio_buttons[
            self._color_square.square_style
        ].setChecked(True)

        for square_style, radio_button in self._sliders.radio_buttons.items():
            radio_button.clicked.connect(
                functools.partial(
                    self._color_square.set_square_style, square_style
                )
            )
        self._strip.accepted.connect(self.accept)
        self._strip.rejected.connect(self.reject)
        self._strip.reset.connect(self.reset)
        self._strip.pick.connect(self._screen_color_picker.pick_screen_color)
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

    def useSquareView(self) -> bool:
        return self._use_square_view

    def setUseSquareView(self, use_square_view: bool) -> None:
        self._use_square_view = use_square_view
        self._update_options()

    @staticmethod
    def getColor(
        initial: T.Optional[QtGui.QColor] = None,
        parent: T.Optional[QtWidgets.QWidget] = None,
        title: T.Optional[str] = None,
        options: T.Optional[QtWidgets.QColorDialog.ColorDialogOptions] = None,
        use_square_view: T.Optional[bool] = False,
        alpha_grid: T.Optional[QtGui.QPixmap] = None,
    ) -> QtGui.QColor:
        dialog = QColorDialog(initial, parent)
        if title is not None:
            dialog.setWindowTitle(title)
        if options is not None:
            dialog.setOptions(options)
        if alpha_grid is not None:
            dialog.setAlphaGrid(alpha_grid)
        if use_square_view is not None:
            dialog.setUseSquareView(use_square_view)
        ret = dialog.exec_()
        if ret == QtWidgets.QDialog.Accepted:
            return dialog.selectedColor()
        return QtGui.QColor()

    def _update_options(self) -> None:
        for widget in self._sliders.alpha_widgets:
            widget.setVisible(self._options & self.ShowAlphaChannel)
        self._color_square.setVisible(self._use_square_view)
        self._color_ring.setVisible(not self._use_square_view)
        for widget in self._sliders.radio_buttons.values():
            widget.setVisible(self._use_square_view)
        self._strip.setVisible(not self._options & self.NoButtons)

    def _emit_signal(self) -> None:
        self.colorSelected.emit(self.selectedColor())
        self.currentColorChanged.emit(self.currentColor())

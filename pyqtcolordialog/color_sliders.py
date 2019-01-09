import typing as T

from PyQt5 import QtCore, QtGui, QtWidgets

from .color_model import ColorModel
from .util import is_imprecise_click, is_precise_click


class ColorSlider(QtWidgets.QAbstractSlider):
    _thumb_size = 8

    def __init__(
        self,
        parent: QtWidgets.QWidget,
        gradient_decorator: T.Callable[[QtGui.QLinearGradient], None],
        alpha_grid: QtGui.QPixmap,
        value: int,
    ) -> None:
        super().__init__(
            parent,
            minimum=0,
            maximum=255,
            orientation=QtCore.Qt.Horizontal,
            value=value,
        )
        self._gradient_decorator = gradient_decorator
        self._alpha_grid = alpha_grid
        self._pressed_control = QtWidgets.QStyle.SC_None

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum
        )

    def setValue(self, value: float) -> None:
        super().setValue(value)
        self.update()

    def sizeHint(self) -> T.Tuple[int, int]:
        return QtCore.QSize(300, 25)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        groove_rect = self._groove_rect
        handle_rect = self._handle_rect

        gradient = QtGui.QLinearGradient(
            groove_rect.topLeft(), groove_rect.topRight()
        )
        self._gradient_decorator(gradient)

        painter = QtGui.QPainter(self)
        painter.drawTiledPixmap(groove_rect, self._alpha_grid)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(gradient)
        painter.drawRect(groove_rect)

        opt = QtWidgets.QStyleOptionFrame()
        opt.rect = groove_rect
        opt.state = QtWidgets.QStyle.State_Sunken
        opt.lineWidth = 1
        opt.frameShape = QtWidgets.QFrame.Panel
        self.style().drawControl(
            QtWidgets.QStyle.CE_ShapedFrame, opt, painter, self
        )

        opt = QtWidgets.QStyleOptionButton()
        opt.state = (
            QtWidgets.QStyle.State_Active | QtWidgets.QStyle.State_Enabled
        )
        if self.isSliderDown():
            opt.state |= QtWidgets.QStyle.State_Sunken
        opt.rect = handle_rect
        self.style().drawControl(
            QtWidgets.QStyle.CE_PushButton, opt, painter, self
        )

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if is_precise_click(event.button(), self.style()):
            event.accept()
            self.setSliderPosition(self._val_from_point(event.pos()))
            self.triggerAction(QtWidgets.QSlider.SliderMove)
            self._pressed_control = QtWidgets.QStyle.SC_SliderHandle
            self.update()

        elif is_imprecise_click(event.button(), self.style()):
            event.accept()

            self._pressed_control = (
                QtWidgets.QStyle.SC_SliderHandle
                if event.pos() in self._handle_rect
                else QtWidgets.QStyle.SC_SliderGroove
            )

            action = self.SliderNoAction
            if self._pressed_control == QtWidgets.QStyle.SC_SliderGroove:
                press_value = self._val_from_point(event.pos())
                if press_value > self.value():
                    action = self.SliderPageStepAdd
                elif press_value < self.value():
                    action = self.SliderPageStepSub
                if action:
                    self.triggerAction(action)
                    self.setRepeatAction(action)

        else:
            event.ignore()
            return

        if self._pressed_control == QtWidgets.QStyle.SC_SliderHandle:
            self.setRepeatAction(self.SliderNoAction)
            self.update()
            self.setSliderDown(True)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self._pressed_control != QtWidgets.QStyle.SC_SliderHandle:
            event.ignore()
            return
        event.accept()
        self.setSliderPosition(self._val_from_point(event.pos()))

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if (
            self._pressed_control == QtWidgets.QStyle.SC_None
            or event.buttons()
        ):
            event.ignore()
            return
        event.accept()
        old_pressed = QtWidgets.QStyle.SubControl(self._pressed_control)
        self._pressed_control = QtWidgets.QStyle.SC_None
        self.setRepeatAction(self.SliderNoAction)
        if old_pressed == QtWidgets.QStyle.SC_SliderHandle:
            self.setSliderDown(False)
        self.update()

    @property
    def _groove_rect(self) -> QtCore.QRect:
        return QtCore.QRect(
            self._thumb_size,
            3,
            self.width() - self._thumb_size * 2,
            self.height() - 6,
        )

    @property
    def _handle_rect(self) -> QtCore.QRect:
        x = (self.value() - self.minimum()) / (self.maximum() - self.minimum())
        x = x * (self.width() - self._thumb_size * 2)
        return QtCore.QRect(x, 0, self._thumb_size * 2, self.height())

    def _val_from_point(self, pos: QtCore.QPoint) -> int:
        center = self._handle_rect.center() - self._handle_rect.topLeft()
        x = (pos - center).x()
        return int(
            self.minimum()
            + x * (self.maximum() - self.minimum()) / self._groove_rect.width()
        )


class BaseColorControl(QtWidgets.QWidget):
    def __init__(
        self,
        parent: QtWidgets.QWidget,
        model: ColorModel,
        alpha_grid: QtGui.QPixmap,
    ) -> None:
        super().__init__(parent)
        self._model = model

        self._slider = ColorSlider(
            self,
            lambda gradient: self._decorate_gradient(
                gradient, self._model.color
            ),
            alpha_grid,
            value=int(self._get_value(self._model) * 255),
        )
        self._up_down = QtWidgets.QSpinBox(
            self,
            minimum=0,
            maximum=255,
            value=int(self._get_value(self._model) * 255),
        )

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._slider)
        layout.addWidget(self._up_down)

        self._slider.valueChanged.connect(self._slider_changed)
        self._up_down.valueChanged.connect(self._up_down_changed)
        self._model.changed.connect(self._model_changed)

    def _get_value(self, model: ColorModel) -> float:
        raise NotImplementedError("not implemented")

    def _set_value(self, model: ColorModel, value: float) -> None:
        raise NotImplementedError("not implemented")

    def _decorate_gradient(
        self, gradient: QtGui.QLinearGradient, color: QtGui.QColor
    ) -> None:
        tmp_model = ColorModel(self._model.color)
        tmp_model.a = 1.0
        self._set_value(tmp_model, 0.0)
        gradient.setColorAt(0, tmp_model.color)
        self._set_value(tmp_model, 1.0)
        gradient.setColorAt(1, tmp_model.color)

    def _model_changed(self) -> None:
        self._slider.setValue(self._get_value(self._model) * 255)
        self._up_down.setValue(self._get_value(self._model) * 255)

    def _slider_changed(self) -> None:
        self._set_value(self._model, self._slider.value() / 255.0)

    def _up_down_changed(self) -> None:
        self._set_value(self._model, self._up_down.value() / 255.0)


class HueColorControl(BaseColorControl):
    def _get_value(self, model: ColorModel) -> float:
        return model.h

    def _set_value(self, model: ColorModel, value: float) -> None:
        model.h = value

    def _decorate_gradient(
        self, gradient: QtGui.QLinearGradient, color: QtGui.QColor
    ) -> None:
        gradient.setColorAt(0 / 6, QtGui.QColor(255, 0, 0, 255))
        gradient.setColorAt(1 / 6, QtGui.QColor(255, 255, 0, 255))
        gradient.setColorAt(2 / 6, QtGui.QColor(0, 255, 0, 255))
        gradient.setColorAt(3 / 6, QtGui.QColor(0, 255, 255, 255))
        gradient.setColorAt(4 / 6, QtGui.QColor(0, 0, 255, 255))
        gradient.setColorAt(5 / 6, QtGui.QColor(255, 0, 255, 255))
        gradient.setColorAt(6 / 6, QtGui.QColor(255, 0, 0, 255))


class SaturationColorControl(BaseColorControl):
    def _get_value(self, model: ColorModel) -> float:
        return model.s

    def _set_value(self, model: ColorModel, value: float) -> None:
        model.s = value


class ValueColorControl(BaseColorControl):
    def _get_value(self, model: ColorModel) -> float:
        return model.v

    def _set_value(self, model: ColorModel, value: float) -> None:
        model.v = value


class RedColorControl(BaseColorControl):
    def _get_value(self, model: ColorModel) -> float:
        return model.r

    def _set_value(self, model: ColorModel, value: float) -> None:
        model.r = value


class GreenColorControl(BaseColorControl):
    def _get_value(self, model: ColorModel) -> float:
        return model.g

    def _set_value(self, model: ColorModel, value: float) -> None:
        model.g = value


class BlueColorControl(BaseColorControl):
    def _get_value(self, model: ColorModel) -> float:
        return model.b

    def _set_value(self, model: ColorModel, value: float) -> None:
        model.b = value


class AlphaColorControl(BaseColorControl):
    def _get_value(self, model: ColorModel) -> float:
        return model.a

    def _set_value(self, model: ColorModel, value: float) -> None:
        model.a = value

    def _decorate_gradient(
        self, gradient: QtGui.QLinearGradient, color: QtGui.QColor
    ) -> None:
        gradient.setColorAt(
            0, QtGui.QColor(color.red(), color.green(), color.blue(), 0)
        )
        gradient.setColorAt(
            1, QtGui.QColor(color.red(), color.green(), color.blue(), 255)
        )

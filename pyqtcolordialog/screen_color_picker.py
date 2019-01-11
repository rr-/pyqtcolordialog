from PyQt5 import QtCore, QtGui, QtWidgets

from .color_model import ColorModel


class ColorPickingEventFilter(QtCore.QObject):
    def __init__(self, parent: QtCore.QObject) -> None:
        super().__init__(parent)
        self._parent = parent

    def eventFilter(
        self, _object: QtCore.QObject, event: QtCore.QEvent
    ) -> bool:
        if event.type() == QtCore.QEvent.MouseMove:
            return self._parent.handle_mouse_move(event)
        elif event.type() == QtCore.QEvent.MouseButtonRelease:
            return self._parent.handle_mouse_button_release(event)
        elif event.type() == QtCore.QEvent.KeyPress:
            return self._parent.handle_key_press(event)
        return False


class ScreenColorPicker(QtCore.QObject):
    def __init__(self, model: ColorModel, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        self._model = model
        self._parent = parent
        self._dummy_transparent_window = QtGui.QWindow()
        self._dummy_transparent_window.resize(1, 1)
        self._dummy_transparent_window.setFlags(
            QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint
        )
        self._color_picking_event_filter = ColorPickingEventFilter(self)
        self._old_color = QtGui.QColor()

    def pick_screen_color(self) -> None:
        self._old_color = self._model.color
        self._dummy_transparent_window.show()
        self._parent.installEventFilter(self._color_picking_event_filter)
        self._parent.grabMouse(QtCore.Qt.CrossCursor)
        self._parent.grabKeyboard()
        self._parent.setMouseTracking(True)

    def _release(self) -> None:
        self._dummy_transparent_window.setVisible(False)
        self._parent.removeEventFilter(self._color_picking_event_filter)
        self._parent.releaseMouse()
        self._parent.releaseKeyboard()
        self._parent.setMouseTracking(False)

    def handle_mouse_move(self, event: QtGui.QMouseEvent) -> bool:
        self._model.color = self._grab_screen_color(event.globalPos())
        return True

    def handle_mouse_button_release(self, event: QtGui.QMouseEvent) -> bool:
        self._model.color = self._grab_screen_color(event.globalPos())
        self._release()
        return True

    def handle_key_press(self, event: QtGui.QKeyEvent) -> bool:
        if event.matches(QtGui.QKeySequence.Cancel):
            self._release()
            self._model.color = self._old_color
        elif event.key() in {QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter}:
            self._model.color = self._grab_screen_color(QtGui.QCursor.pos())
            self._release()
        event.accept()
        return True

    def _grab_screen_color(self, point: QtCore.QPoint) -> QtGui.QColor:
        desktop = QtWidgets.QApplication.desktop()
        pixmap = QtWidgets.QApplication.primaryScreen().grabWindow(
            desktop.winId(), point.x(), point.y(), 1, 1
        )
        return pixmap.toImage().pixelColor(0, 0)

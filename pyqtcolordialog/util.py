from PyQt5 import QtCore, QtGui, QtWidgets


def is_precise_click(
    button: QtCore.Qt.MouseButton, style: QtWidgets.QStyle
) -> bool:
    return (
        button & style.styleHint(QtWidgets.QStyle.SH_Slider_AbsoluteSetButtons)
    ) == button


def is_imprecise_click(
    button: QtCore.Qt.MouseButton, style: QtWidgets.QStyle
) -> bool:
    return (
        button & style.styleHint(QtWidgets.QStyle.SH_Slider_PageSetButtons)
    ) == button


def blend(c1: QtGui.QColor, c2: QtGui.QColor, ratio: float) -> QtGui.QColor:
    return QtGui.QColor.fromRgbF(
        c1.redF() * (1 - ratio) + c2.redF() * ratio,
        c1.greenF() * (1 - ratio) + c2.greenF() * ratio,
        c1.blueF() * (1 - ratio) + c2.blueF() * ratio,
    )


def clamp(val: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, val))

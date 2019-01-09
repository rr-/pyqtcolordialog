from PyQt5 import QtCore, QtWidgets


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

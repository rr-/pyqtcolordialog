#!/usr/bin/env python3
import sys
import typing as T

from PyQt5 import QtCore, QtGui, QtWidgets

# from PyQt5.QtWidgets import QColorDialog
from pyqtcolordialog import QColorDialog


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)

    color = QColorDialog.getColor(
        initial=QtGui.QColor(202, 224, 250),
        title="Fancy title...",
        options=QColorDialog.ColorDialogOptions()
        & ~QColorDialog.ShowAlphaChannel,
    )

    print(color.isValid())
    print(f"{color.red():02x}{color.green():02x}{color.blue():02x}")


if __name__ == "__main__":
    main()

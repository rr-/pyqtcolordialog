#!/usr/bin/env python3
import argparse
import sys
import typing as T

from PyQt5 import QtCore, QtGui, QtWidgets

# from PyQt5.QtWidgets import QColorDialog
from pyqtcolordialog import QColorDialog


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha", action="store_true")
    parser.add_argument("--no-alpha", action="store_false", dest="alpha")
    parser.add_argument("--buttons", action="store_true")
    parser.add_argument("--no-buttons", action="store_false", dest="buttons")
    parser.add_argument("--square", action="store_true")
    parser.add_argument("--no-square", action="store_false", dest="square")
    parser.set_defaults(alpha=True, buttons=True, square=False)
    return parser.parse_args()


def set_bit(
    options: QColorDialog.ColorDialogOptions,
    option: QColorDialog.ColorDialogOption,
    value: bool,
) -> None:
    if value:
        options |= option
    else:
        options &= ~option
    return options


def main() -> None:
    args = parse_args()
    app = QtWidgets.QApplication(sys.argv)

    options = QColorDialog.ColorDialogOptions()
    options = set_bit(options, QColorDialog.ShowAlphaChannel, args.alpha)
    options = set_bit(options, QColorDialog.NoButtons, not args.buttons)
    color = QColorDialog.getColor(
        initial=QtGui.QColor(202, 224, 250),
        title="Fancy title...",
        options=options,
        use_square_view=args.square,
    )

    print(color.isValid())
    print(f"{color.red():02x}{color.green():02x}{color.blue():02x}")


if __name__ == "__main__":
    main()

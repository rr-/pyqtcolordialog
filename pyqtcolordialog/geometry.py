import typing as T

from PyQt5 import QtCore


def point_in_triangle(
    point: QtCore.QPoint,
    triangle_points: T.Tuple[QtCore.QPoint, QtCore.QPoint, QtCore.QPoint],
) -> bool:
    p = point
    p1, p2, p3 = triangle_points
    area = 0.5 * (
        -p2.y() * p3.x()
        + p1.y() * (-p2.x() + p3.x())
        + p1.x() * (p2.y() - p3.y())
        + p2.x() * p3.y()
    )
    s = (
        1
        / (2 * area)
        * (
            p1.y() * p3.x()
            - p1.x() * p3.y()
            + (p3.y() - p1.y()) * p.x()
            + (p1.x() - p3.x()) * p.y()
        )
    )
    t = (
        1
        / (2 * area)
        * (
            p1.x() * p2.y()
            - p1.y() * p2.x()
            + (p1.y() - p2.y()) * p.x()
            + (p2.x() - p1.x()) * p.y()
        )
    )
    return s > 0 and t > 0 and 1 - s - t > 0


def point_in_ring(
    point: QtCore.QPoint, inner_radius: float, outer_radius: float
) -> bool:
    dist = (point.y() * point.y() + point.x() * point.x()) ** 0.5
    return inner_radius <= dist <= outer_radius

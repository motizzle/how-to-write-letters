#!/usr/bin/env python3

from __future__ import annotations

import ast
import hashlib
import json
import math
import os
import sys

from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONT = os.path.join(HERE, "fonts", "Roboto-Bold.ttf")
FONT_HEBREW = os.path.join(HERE, "fonts", "Heebo-Bold.ttf")
OUT_DIR = os.path.join(ROOT, "docs", "data")

MANIFEST = {
    "A": [
        {"pts": [[0.50, 0.04], [0.10, 0.95]]},
        {"pts": [[0.50, 0.04], [0.90, 0.95]]},
        {"pts": [[0.27, 0.66], [0.73, 0.66]]},
    ],
    "B": [
        {"pts": [[0.14, 0.05], [0.14, 0.95]]},
        {"pts": [[0.14, 0.07], [0.50, 0.06], [0.76, 0.15], [0.78, 0.30],
                 [0.70, 0.45], [0.45, 0.49], [0.14, 0.49]]},
        {"pts": [[0.14, 0.49], [0.45, 0.49], [0.75, 0.53], [0.85, 0.65],
                 [0.84, 0.78], [0.65, 0.90], [0.40, 0.93], [0.14, 0.92]]},
    ],
    "C": [
        {"pts": [[0.85, 0.16], [0.50, 0.04], [0.14, 0.18], [0.05, 0.50],
                 [0.14, 0.82], [0.50, 0.96], [0.85, 0.84]]},
    ],
    "D": [
        {"pts": [[0.13, 0.05], [0.13, 0.95]]},
        {"pts": [[0.13, 0.07], [0.50, 0.05], [0.80, 0.20], [0.88, 0.50],
                 [0.80, 0.80], [0.50, 0.95], [0.13, 0.93]]},
    ],
    "E": [
        {"pts": [[0.15, 0.05], [0.15, 0.95]]},
        {"pts": [[0.30, 0.08], [0.90, 0.08]]},
        {"pts": [[0.30, 0.49], [0.80, 0.49]]},
        {"pts": [[0.30, 0.92], [0.90, 0.92]]},
    ],
    "F": [
        {"pts": [[0.15, 0.05], [0.15, 0.95]]},
        {"pts": [[0.30, 0.08], [0.90, 0.08]]},
        {"pts": [[0.30, 0.51], [0.82, 0.51]]},
    ],
    "G": [
        {"pts": [[0.86, 0.14], [0.50, 0.04], [0.13, 0.18], [0.05, 0.50],
                 [0.13, 0.82], [0.50, 0.96], [0.86, 0.84], [0.90, 0.62]]},
        {"pts": [[0.55, 0.58], [0.90, 0.58]]},
    ],
    "H": [
        {"pts": [[0.12, 0.05], [0.12, 0.95]]},
        {"pts": [[0.88, 0.05], [0.88, 0.95]]},
        {"pts": [[0.20, 0.52], [0.80, 0.52]]},
    ],
    "I": [
        {"pts": [[0.50, 0.06], [0.50, 0.94]]},
        {"pts": [[0.10, 0.06], [0.90, 0.06]]},
        {"pts": [[0.10, 0.94], [0.90, 0.94]]},
    ],
    "J": [
        {"pts": [[0.85, 0.05], [0.85, 0.70], [0.70, 0.92], [0.40, 0.96],
                 [0.15, 0.82]]},
    ],
    "K": [
        {"pts": [[0.13, 0.05], [0.13, 0.95]]},
        {"pts": [[0.88, 0.05], [0.28, 0.55]]},
        {"pts": [[0.42, 0.44], [0.92, 0.95]]},
    ],
    "L": [
        {"pts": [[0.15, 0.05], [0.15, 0.95]]},
        {"pts": [[0.28, 0.92], [0.90, 0.92]]},
    ],
    "M": [
        {"pts": [[0.08, 0.05], [0.08, 0.95]]},
        {"pts": [[0.10, 0.06], [0.50, 0.80]]},
        {"pts": [[0.50, 0.80], [0.90, 0.06]]},
        {"pts": [[0.92, 0.05], [0.92, 0.95]]},
    ],
    "N": [
        {"pts": [[0.10, 0.05], [0.10, 0.95]]},
        {"pts": [[0.12, 0.06], [0.88, 0.94]]},
        {"pts": [[0.90, 0.05], [0.90, 0.95]]},
    ],
    "O": [
        {"pts": [[0.50, 0.03], [0.13, 0.18], [0.04, 0.50], [0.13, 0.82],
                 [0.50, 0.97], [0.87, 0.82], [0.96, 0.50], [0.87, 0.18],
                 [0.54, 0.04]]},
    ],
    "P": [
        {"pts": [[0.13, 0.05], [0.13, 0.95]]},
        {"pts": [[0.13, 0.07], [0.50, 0.06], [0.82, 0.15], [0.87, 0.30],
                 [0.80, 0.45], [0.50, 0.55], [0.13, 0.56]]},
    ],
    "Q": [
        {"pts": [[0.50, 0.03], [0.13, 0.16], [0.04, 0.45], [0.13, 0.74],
                 [0.50, 0.88], [0.84, 0.76], [0.95, 0.45], [0.86, 0.16],
                 [0.54, 0.04]]},
        {"pts": [[0.62, 0.68], [0.93, 0.97]]},
    ],
    "R": [
        {"pts": [[0.13, 0.05], [0.13, 0.95]]},
        {"pts": [[0.13, 0.07], [0.50, 0.06], [0.80, 0.14], [0.86, 0.28],
                 [0.80, 0.43], [0.50, 0.52], [0.13, 0.53]]},
        {"pts": [[0.48, 0.55], [0.90, 0.95]]},
    ],
    "S": [
        {"pts": [[0.85, 0.16], [0.50, 0.04], [0.15, 0.16], [0.13, 0.36],
                 [0.50, 0.50], [0.86, 0.64], [0.86, 0.84], [0.50, 0.96],
                 [0.13, 0.84]]},
    ],
    "T": [
        {"pts": [[0.50, 0.07], [0.50, 0.95]]},
        {"pts": [[0.05, 0.07], [0.95, 0.07]]},
    ],
    "U": [
        {"pts": [[0.10, 0.05], [0.10, 0.70], [0.28, 0.94], [0.72, 0.94],
                 [0.90, 0.70], [0.90, 0.05]]},
    ],
    "V": [
        {"pts": [[0.07, 0.05], [0.50, 0.99]]},
        {"pts": [[0.50, 0.99], [0.93, 0.05]]},
    ],
    "W": [
        {"pts": [[0.04, 0.05], [0.27, 0.94]]},
        {"pts": [[0.27, 0.94], [0.50, 0.06]]},
        {"pts": [[0.50, 0.06], [0.73, 0.94]]},
        {"pts": [[0.73, 0.94], [0.96, 0.05]]},
    ],
    "X": [
        {"pts": [[0.08, 0.05], [0.92, 0.95]]},
        {"pts": [[0.92, 0.05], [0.08, 0.95]]},
    ],
    "Y": [
        {"pts": [[0.07, 0.05], [0.50, 0.52]]},
        {"pts": [[0.93, 0.05], [0.50, 0.52]]},
        {"pts": [[0.50, 0.52], [0.50, 0.95]]},
    ],
    "Z": [
        {"pts": [[0.08, 0.07], [0.92, 0.07], [0.08, 0.93], [0.92, 0.93]]},
    ],
    "a": [
        {"pts": [[0.72, 0.10], [0.34, 0.20], [0.14, 0.50],
                 [0.34, 0.86], [0.70, 0.95]]},
        {"pts": [[0.86, 0.03], [0.86, 0.96]]},
    ],
    "t": [
        {"pts": [[0.48, 0.03], [0.48, 0.97]]},
        {"pts": [[0.06, 0.274], [0.94, 0.274]]},
    ],
    "b": [
        {"pts": [[0.15, 0.03], [0.15, 0.96]]},
        {"pts": [[0.17, 0.42], [0.45, 0.37], [0.573, 0.333], [0.80, 0.40],
                 [0.86, 0.60], [0.76, 0.85], [0.45, 0.94], [0.17, 0.92]]},
    ],
    "c": [
        {"pts": [[0.85, 0.16], [0.50, 0.04], [0.14, 0.18], [0.05, 0.50],
                 [0.14, 0.82], [0.50, 0.96], [0.85, 0.84]]},
    ],
    "d": [
        {"pts": [[0.65, 0.335], [0.42, 0.30], [0.20, 0.45], [0.15, 0.63],
                 [0.22, 0.85], [0.48, 0.94], [0.62, 0.92]]},
        {"pts": [[0.85, 0.03], [0.85, 0.96]]},
    ],
    "e": [
        {"pts": [[0.10, 0.47], [0.55, 0.45], [0.95, 0.43], [0.90, 0.20],
                 [0.52, 0.04], [0.14, 0.20], [0.05, 0.52], [0.16, 0.84],
                 [0.52, 0.96], [0.88, 0.82]]},
    ],
    "f": [
        {"pts": [[0.85, 0.06], [0.62, 0.05], [0.46, 0.12], [0.42, 0.22],
                 [0.43, 0.98]]},
        {"pts": [[0.03, 0.375], [0.92, 0.375]]},
    ],
    "g": [
        {"pts": [[0.82, 0.10], [0.50, 0.03], [0.20, 0.16], [0.14, 0.35],
                 [0.20, 0.58], [0.50, 0.68], [0.82, 0.62]]},
        {"pts": [[0.85, 0.05], [0.85, 0.62], [0.75, 0.85], [0.45, 0.95],
                 [0.18, 0.88]]},
    ],
    "h": [
        {"pts": [[0.155, 0.03], [0.155, 0.97]]},
        {"pts": [[0.17, 0.42], [0.45, 0.36], [0.60, 0.325], [0.79, 0.42],
                 [0.846, 0.60], [0.846, 0.97]]},
    ],
    "i": [
        {"pts": [[0.50, 0.32], [0.50, 0.97]]},
        {"pts": [[0.36, 0.099], [0.64, 0.099]], "press": True},
    ],
    "j": [
        {"pts": [[0.70, 0.25], [0.70, 0.66], [0.60, 0.85], [0.36, 0.93],
                 [0.13, 0.86]]},
        {"pts": [[0.57, 0.077], [0.81, 0.077]], "press": True},
    ],
    "k": [
        {"pts": [[0.145, 0.03], [0.145, 0.97]]},
        {"pts": [[0.92, 0.32], [0.30, 0.66]]},
        {"pts": [[0.45, 0.57], [0.95, 0.97]]},
    ],
    "l": [
        {"pts": [[0.50, 0.03], [0.50, 0.97]]},
    ],
    "m": [
        {"pts": [[0.093, 0.05], [0.093, 0.96]]},
        {"pts": [[0.10, 0.30], [0.28, 0.10], [0.45, 0.28], [0.499, 0.55],
                 [0.499, 0.96]]},
        {"pts": [[0.51, 0.30], [0.69, 0.10], [0.86, 0.28], [0.907, 0.55],
                 [0.907, 0.96]]},
    ],
    "n": [
        {"pts": [[0.155, 0.05], [0.155, 0.96]]},
        {"pts": [[0.17, 0.30], [0.45, 0.10], [0.75, 0.25], [0.845, 0.52],
                 [0.845, 0.96]]},
    ],
    "o": [
        {"pts": [[0.50, 0.03], [0.13, 0.18], [0.04, 0.50], [0.13, 0.82],
                 [0.50, 0.97], [0.87, 0.82], [0.96, 0.50], [0.87, 0.18],
                 [0.54, 0.04]]},
    ],
    "p": [
        {"pts": [[0.15, 0.05], [0.15, 0.97]]},
        {"pts": [[0.16, 0.10], [0.45, 0.04], [0.76, 0.16], [0.85, 0.37],
                 [0.76, 0.60], [0.45, 0.69], [0.16, 0.66]]},
    ],
    "q": [
        {"pts": [[0.82, 0.10], [0.50, 0.04], [0.20, 0.16], [0.14, 0.37],
                 [0.20, 0.60], [0.50, 0.69], [0.82, 0.63]]},
        {"pts": [[0.85, 0.05], [0.85, 0.97]]},
    ],
    "r": [
        {"pts": [[0.24, 0.05], [0.24, 0.96]]},
        {"pts": [[0.42, 0.30], [0.52, 0.22], [0.62, 0.15], [0.72, 0.09],
                 [0.84, 0.04]], "curve": True},
    ],
    "s": [
        {"pts": [[0.85, 0.16], [0.50, 0.04], [0.15, 0.16], [0.13, 0.36],
                 [0.50, 0.50], [0.86, 0.64], [0.86, 0.84], [0.50, 0.96],
                 [0.13, 0.84]]},
    ],
    "u": [
        {"pts": [[0.155, 0.05], [0.155, 0.60], [0.19, 0.76], [0.33, 0.85],
                 [0.55, 0.85], [0.72, 0.75], [0.845, 0.50], [0.845, 0.06]]},
        {"pts": [[0.845, 0.10], [0.845, 0.95]]},
    ],
    "v": [
        {"pts": [[0.10, 0.05], [0.50, 0.98]]},
        {"pts": [[0.50, 0.98], [0.90, 0.05]]},
    ],
    "w": [
        {"pts": [[0.08, 0.04], [0.26, 0.95]]},
        {"pts": [[0.26, 0.95], [0.50, 0.35]]},
        {"pts": [[0.50, 0.35], [0.74, 0.95]]},
        {"pts": [[0.74, 0.95], [0.92, 0.04]]},
    ],
    "x": [
        {"pts": [[0.08, 0.04], [0.92, 0.96]]},
        {"pts": [[0.92, 0.04], [0.08, 0.96]]},
    ],
    "y": [
        {"pts": [[0.10, 0.04], [0.52, 0.68]]},
        {"pts": [[0.95, 0.05], [0.62, 0.55], [0.45, 0.82], [0.33, 0.92],
                 [0.20, 0.95]]},
    ],
    "z": [
        {"pts": [[0.08, 0.07], [0.92, 0.07], [0.08, 0.93], [0.92, 0.93]]},
    ],
    "Ñ": [
        {"pts": [[0.10, 0.25], [0.10, 0.96]]},
        {"pts": [[0.12, 0.257], [0.88, 0.953]]},
        {"pts": [[0.90, 0.25], [0.90, 0.96]]},
        {"pts": [[0.25, 0.150], [0.31, 0.090], [0.38, 0.045], [0.48, 0.055],
                 [0.56, 0.100], [0.63, 0.145], [0.70, 0.090], [0.75, 0.045]]},
    ],
    "ñ": [
        {"pts": [[0.155, 0.318], [0.155, 0.971]]},
        {"pts": [[0.17, 0.497], [0.45, 0.354], [0.75, 0.462], [0.845, 0.655],
                 [0.845, 0.971]]},
        {"pts": [[0.19, 0.160], [0.26, 0.090], [0.35, 0.045], [0.47, 0.060],
                 [0.57, 0.110], [0.66, 0.155], [0.74, 0.100], [0.81, 0.045]]},
    ],
    "א": [
        {"pts": [[0.18, 0.07], [0.36, 0.30], [0.57, 0.60], [0.82, 0.94]]},
        {"pts": [[0.845, 0.05], [0.79, 0.16], [0.73, 0.27], [0.66, 0.36],
                 [0.56, 0.40], [0.46, 0.42]]},
        {"pts": [[0.46, 0.45], [0.34, 0.45], [0.24, 0.47], [0.19, 0.54],
                 [0.166, 0.75], [0.165, 0.94]]},
    ],
    "ב": [
        {"pts": [[0.10, 0.09], [0.55, 0.08], [0.72, 0.26], [0.72, 0.84]]},
        {"pts": [[0.92, 0.90], [0.06, 0.90]]},
    ],
    "ג": [
        {"pts": [[0.22, 0.10], [0.42, 0.10], [0.58, 0.13], [0.67, 0.22],
                 [0.69, 0.40], [0.70, 0.58], [0.74, 0.76], [0.79, 0.92]]},
        {"pts": [[0.50, 0.71], [0.42, 0.77], [0.33, 0.83], [0.24, 0.89],
                 [0.16, 0.94], [0.10, 0.98]]},
    ],
    "ד": [
        {"pts": [[0.06, 0.10], [0.35, 0.09], [0.60, 0.09], [0.80, 0.10]]},
        {"pts": [[0.65, 0.20], [0.65, 0.55], [0.65, 0.92]]},
    ],
    "ה": [
        {"pts": [[0.06, 0.09], [0.30, 0.08], [0.52, 0.08], [0.70, 0.13],
                 [0.81, 0.24], [0.84, 0.42], [0.84, 0.70], [0.84, 0.95]]},
        {"pts": [[0.14, 0.50], [0.14, 0.72], [0.14, 0.95]]},
    ],
    "ו": [
        {"pts": [[0.63, 0.07], [0.63, 0.94]]},
    ],
    "ז": [
        {"pts": [[0.08, 0.10], [0.40, 0.09], [0.70, 0.09], [0.92, 0.10]]},
        {"pts": [[0.32, 0.22], [0.36, 0.40], [0.42, 0.60], [0.48, 0.80],
                 [0.55, 0.97]]},
    ],
    "ח": [
        {"pts": [[0.06, 0.09], [0.30, 0.08], [0.52, 0.08], [0.70, 0.13],
                 [0.81, 0.23], [0.84, 0.40], [0.84, 0.70], [0.84, 0.95]]},
        {"pts": [[0.15, 0.22], [0.15, 0.50], [0.15, 0.75], [0.15, 0.95]]},
    ],
    "ט": [
        {"pts": [[0.50, 0.22], [0.52, 0.14], [0.62, 0.08], [0.75, 0.07],
                 [0.85, 0.12], [0.85, 0.35], [0.85, 0.60], [0.78, 0.78],
                 [0.60, 0.88], [0.40, 0.87], [0.22, 0.76], [0.15, 0.55],
                 [0.15, 0.25], [0.15, 0.08]]},
    ],
    "י": [
        {"pts": [[0.06, 0.15], [0.18, 0.15], [0.32, 0.15], [0.46, 0.15],
                 [0.58, 0.17], [0.66, 0.26], [0.69, 0.45], [0.69, 0.70],
                 [0.69, 0.92]]},
    ],
    "כ": [
        {"pts": [[0.12, 0.10], [0.35, 0.09], [0.55, 0.09], [0.70, 0.11],
                 [0.79, 0.15], [0.83, 0.24], [0.83, 0.40], [0.83, 0.58],
                 [0.79, 0.70], [0.70, 0.79], [0.55, 0.85], [0.35, 0.89],
                 [0.18, 0.91], [0.08, 0.92]]},
    ],
    "ך": [
        {"pts": [[0.08, 0.07], [0.30, 0.06], [0.50, 0.06], [0.66, 0.08],
                 [0.77, 0.11], [0.82, 0.17], [0.82, 0.35], [0.82, 0.60],
                 [0.82, 0.80], [0.82, 0.96]]},
    ],
    "ל": [
        {"pts": [[0.15, 0.06], [0.15, 0.20], [0.22, 0.29], [0.45, 0.30],
                 [0.70, 0.31], [0.84, 0.38], [0.76, 0.55], [0.63, 0.72],
                 [0.52, 0.88], [0.44, 0.97]]},
    ],
    "מ": [
        {"pts": [[0.77, 0.95], [0.83, 0.72], [0.86, 0.50], [0.86, 0.34],
                 [0.78, 0.24], [0.60, 0.16], [0.42, 0.12], [0.30, 0.16],
                 [0.24, 0.32], [0.20, 0.55], [0.17, 0.78], [0.15, 0.95]]},
        {"pts": [[0.22, 0.075], [0.16, 0.12], [0.115, 0.17], [0.085, 0.21],
                 [0.066, 0.25]]},
    ],
    "ם": [
        {"pts": [[0.93, 0.07], [0.08, 0.08], [0.08, 0.92], [0.93, 0.92],
                 [0.93, 0.20]]},
    ],
    "נ": [
        {"pts": [[0.20, 0.07], [0.75, 0.07], [0.75, 0.30], [0.75, 0.60],
                 [0.70, 0.80], [0.35, 0.92], [0.12, 0.94]]},
    ],
    "ן": [
        {"pts": [[0.12, 0.09], [0.35, 0.08], [0.55, 0.09], [0.65, 0.14],
                 [0.66, 0.35], [0.66, 0.60], [0.66, 0.80], [0.66, 0.96]]},
    ],
    "ס": [
        {"pts": [[0.05, 0.135], [0.14, 0.11], [0.28, 0.085], [0.44, 0.075],
                 [0.60, 0.085], [0.74, 0.12], [0.83, 0.21], [0.87, 0.38],
                 [0.86, 0.55], [0.81, 0.71], [0.70, 0.83], [0.55, 0.88],
                 [0.40, 0.86], [0.27, 0.77], [0.21, 0.62], [0.20, 0.45],
                 [0.215, 0.30], [0.215, 0.24], [0.20, 0.19], [0.17, 0.15],
                 [0.14, 0.13]]},
    ],
    "ע": [
        {"pts": [[0.20, 0.07], [0.26, 0.25], [0.32, 0.45], [0.39, 0.65]]},
        {"pts": [[0.85, 0.07], [0.85, 0.35], [0.84, 0.58], [0.79, 0.73],
                 [0.66, 0.83], [0.45, 0.88], [0.25, 0.88], [0.10, 0.87],
                 [0.04, 0.86]]},
    ],
    "פ": [
        {"pts": [[0.31, 0.60], [0.20, 0.55], [0.11, 0.47], [0.11, 0.35],
                 [0.17, 0.25], [0.22, 0.17], [0.30, 0.10], [0.50, 0.09],
                 [0.70, 0.09], [0.83, 0.14], [0.86, 0.30], [0.86, 0.50],
                 [0.83, 0.66], [0.74, 0.77], [0.55, 0.85], [0.32, 0.88],
                 [0.14, 0.87], [0.08, 0.86]]},
    ],
    "ף": [
        {"pts": [[0.35, 0.49], [0.24, 0.45], [0.12, 0.38], [0.12, 0.28],
                 [0.19, 0.19], [0.26, 0.13], [0.40, 0.08], [0.60, 0.07],
                 [0.78, 0.08], [0.85, 0.13], [0.85, 0.30], [0.85, 0.55],
                 [0.85, 0.75], [0.85, 0.96]]},
    ],
    "צ": [
        {"pts": [[0.82, 0.07], [0.74, 0.17], [0.66, 0.28], [0.58, 0.42],
                 [0.54, 0.53]]},
        {"pts": [[0.19, 0.07], [0.28, 0.18], [0.37, 0.30], [0.46, 0.44],
                 [0.55, 0.58], [0.63, 0.72], [0.72, 0.83], [0.50, 0.89],
                 [0.25, 0.90], [0.14, 0.89]]},
    ],
    "ץ": [
        {"pts": [[0.80, 0.07], [0.72, 0.15], [0.64, 0.24], [0.56, 0.34]]},
        {"pts": [[0.20, 0.07], [0.29, 0.16], [0.38, 0.26], [0.48, 0.38],
                 [0.56, 0.50], [0.61, 0.65], [0.61, 0.82], [0.61, 0.96]]},
    ],
    "ק": [
        {"pts": [[0.15, 0.38], [0.15, 0.60], [0.15, 0.80], [0.15, 0.97]]},
        {"pts": [[0.10, 0.07], [0.35, 0.06], [0.58, 0.06], [0.76, 0.09],
                 [0.85, 0.17], [0.85, 0.35], [0.83, 0.50], [0.75, 0.62],
                 [0.60, 0.69]]},
    ],
    "ר": [
        {"pts": [[0.08, 0.09], [0.30, 0.08], [0.55, 0.09], [0.72, 0.14],
                 [0.81, 0.25], [0.82, 0.45], [0.82, 0.70], [0.82, 0.94]]},
    ],
    "ש": [
        {"pts": [[0.90, 0.07], [0.90, 0.30], [0.89, 0.50], [0.86, 0.63],
                 [0.80, 0.74], [0.68, 0.82], [0.50, 0.87], [0.30, 0.88],
                 [0.14, 0.85], [0.10, 0.70], [0.10, 0.45], [0.10, 0.20],
                 [0.10, 0.07]]},
        {"pts": [[0.50, 0.07], [0.49, 0.30], [0.49, 0.50], [0.48, 0.63],
                 [0.47, 0.74], [0.46, 0.82]]},
    ],
    "ת": [
        {"pts": [[0.12, 0.10], [0.35, 0.08], [0.58, 0.08], [0.75, 0.12],
                 [0.85, 0.22], [0.87, 0.40], [0.87, 0.65], [0.87, 0.92]]},
        {"pts": [[0.31, 0.20], [0.30, 0.45], [0.30, 0.65], [0.29, 0.75],
                 [0.26, 0.83], [0.21, 0.89], [0.17, 0.95]]},
    ],
}

RULES_LATIN = [
    {"kind": "mid", "y": 0.42},
    {"kind": "base", "y": 0.72},
]

RULES_HEBREW = [
    {"kind": "top", "y": 0.39},
    {"kind": "base", "y": 0.72},
]

DECKS = {
    "print": {
        "font": FONT,
        "letters": {c: c for c in
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    "abcdefghijklmnopqrstuvwxyz" "Ññ"},
        "cap_ref": "H",
        "x_ref": "x",
        "rules": RULES_LATIN,
        "synth": {
            "I": "synth_capital_I",
            "a": "synth_single_storey_a",
            "t": "synth_straight_t",
        },
    },
    "hebrew": {
        "font": FONT_HEBREW,
        "letters": {c: c for c in "אבגדהוזחטיכךלמםנןסעפףצץקרשת"},
        "x_ref": "א",
        "rules": RULES_HEBREW,
        "synth": {"ש": "synth_shin"},
    },
}


CACHE_DIR = os.path.join(ROOT, ".cache", "print")

_ALGO_SHA = None
_FONT_SHA = {}


def _algorithm_sha():
    global _ALGO_SHA
    if _ALGO_SHA is None:
        with open(os.path.abspath(__file__), "r", encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        tree.body = [
            n for n in tree.body
            if not (isinstance(n, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id in ("MANIFEST", "DECKS")
                for t in n.targets))
        ]
        _ALGO_SHA = hashlib.sha256(
            ast.dump(tree).encode("utf-8")).hexdigest()[:16]
    return _ALGO_SHA


def _font_sha(path):
    if path not in _FONT_SHA:
        with open(path, "rb") as fh:
            _FONT_SHA[path] = hashlib.sha256(fh.read()).hexdigest()[:16]
    return _FONT_SHA[path]


def manifest_for(deck_name, fk, char):
    try:
        return MANIFEST[char]
    except KeyError:
        raise SystemExit(
            f"{deck_name}/{fk}: no MANIFEST entry for {char!r} — sketch the "
            "strokes a teacher would draw, then rerun") from None


def form_fingerprint(deck_name, deck, fk):
    char = deck["letters"][fk]
    payload = {
        "algorithm": _algorithm_sha(),
        "font": _font_sha(deck["font"]),
        "deck": deck_name,
        "form": fk,
        "char": char,
        "manifest": manifest_for(deck_name, fk, char),
        "rules": deck["rules"],
        "x_ref": deck["x_ref"],
        "cap_ref": deck.get("cap_ref"),
        "synth": deck.get("synth", {}).get(fk),
    }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def _cache_read(fp):
    path = os.path.join(CACHE_DIR, fp + ".json")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            entry = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(entry, dict) or "letter" not in entry \
            or "min_half" not in entry:
        return None
    return entry


def _cache_write(fp, entry):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, fp + ".json")
    tmp = "%s.%d.tmp" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(entry, fh)
    os.replace(tmp, path)


MARGIN = 0.046

ARROW_BASIS_MAX = 0.029

FLATTEN_STEPS = 16
RAY_STEP = 2.0

ARROW_SIZE = 0.85
ARROW_MAX = 0.95
ARROW_SPACING = 2.0
ARROW_BACK = 0.55
ARROW_WING = 0.62
PULSE = 1.25

WALK_SPEED = 0.45
WALK_MIN_MS = 700
WALK_MAX_MS = 4000
WALK_HOLD_MS = 1000

CORNER_DEG = 35.0

STRAIGHT_SAGITTA = 0.08

CURVE_MIN_WIDTHS = 0.32

CURVE_ALWAYS_SAGITTA = 0.25

MIN_SECTION = 60.0


def glyph_segments(font: TTFont, ch: str):
    from fontTools.pens.recordingPen import DecomposingRecordingPen

    glyph_name = font.getBestCmap()[ord(ch)]
    pen = DecomposingRecordingPen(font.getGlyphSet())
    font.getGlyphSet()[glyph_name].draw(pen)

    contours = []
    cur = start = None
    segs = []
    for op, pts in pen.value:
        if op == "moveTo":
            if segs:
                contours.append(segs)
            segs = []
            cur = start = pts[0]
        elif op == "lineTo":
            segs.append((cur, None, pts[0]))
            cur = pts[0]
        elif op == "qCurveTo":
            assert pts[-1] is not None, "TrueType all-offcurve contour"
            ctrls, end = list(pts[:-1]), pts[-1]
            for i, c in enumerate(ctrls):
                if i < len(ctrls) - 1:
                    nxt = ctrls[i + 1]
                    mid = ((c[0] + nxt[0]) / 2, (c[1] + nxt[1]) / 2)
                    segs.append((cur, c, mid))
                    cur = mid
                else:
                    segs.append((cur, c, end))
                    cur = end
            if not ctrls:
                segs.append((cur, None, end))
                cur = end
        elif op == "closePath":
            if cur != start:
                segs.append((cur, None, start))
            contours.append(segs)
            segs = []
            cur = start
        elif op == "curveTo":
            raise SystemExit("cubic curve in a TrueType glyph — unexpected")
    if segs:
        contours.append(segs)
    return contours


def flatten(contours):
    polys = []
    for segs in contours:
        poly = []
        for p0, c, p1 in segs:
            if c is None:
                poly.append(p0)
            else:
                for i in range(FLATTEN_STEPS):
                    t = i / FLATTEN_STEPS
                    u = 1 - t
                    poly.append((
                        u * u * p0[0] + 2 * u * t * c[0] + t * t * p1[0],
                        u * u * p0[1] + 2 * u * t * c[1] + t * t * p1[1],
                    ))
        polys.append(poly)
    return polys


def in_ink(pt, polys):
    x, y = pt
    wn = 0
    for poly in polys:
        n = len(poly)
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % n]
            if y1 <= y:
                if y2 > y and (x2 - x1) * (y - y1) - (x - x1) * (y2 - y1) > 0:
                    wn += 1
            elif y2 <= y and (x2 - x1) * (y - y1) - (x - x1) * (y2 - y1) < 0:
                wn -= 1
    return wn != 0


def spans_at_y(y, polys):
    hits = []
    for poly in polys:
        n = len(poly)
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % n]
            if (y1 <= y < y2) or (y2 <= y < y1):
                t = (y - y1) / (y2 - y1)
                hits.append((x1 + t * (x2 - x1), 1 if y2 > y1 else -1))
    hits.sort()
    spans, wn, start = [], 0, None
    for x, d in hits:
        prev, wn = wn, wn + d
        if prev == 0 and wn != 0:
            start = x
        elif prev != 0 and wn == 0:
            spans.append((start, x))
    return spans


def bbox(polys):
    xs = [p[0] for poly in polys for p in poly]
    ys = [p[1] for poly in polys for p in poly]
    return min(xs), min(ys), max(xs), max(ys)


def march_out(p, d, polys, max_r):
    r = RAY_STEP
    while r < max_r:
        if not in_ink((p[0] + d[0] * r, p[1] + d[1] * r), polys):
            return r - RAY_STEP / 2
        r += RAY_STEP
    return max_r


DIRS_16 = [(math.cos(a * math.pi / 8), math.sin(a * math.pi / 8))
           for a in range(16)]


def clearance(p, polys, max_r):
    return min(march_out(p, d, polys, max_r) for d in DIRS_16)


def snap_to_ink(p, polys, max_r):
    if in_ink(p, polys):
        return p
    r = RAY_STEP
    while r < max_r:
        for d in DIRS_16:
            q = (p[0] + d[0] * r, p[1] + d[1] * r)
            if in_ink(q, polys):
                return q
        r += RAY_STEP * 2
    raise SystemExit(f"sketch point {p} is nowhere near ink")


def medial_push(points, polys, target):
    out = []
    for p in points:
        q = p
        for _ in range(14):
            probes = [(march_out(q, d, polys, target * 3), d) for d in DIRS_16]
            c_min, d_min = min(probes, key=lambda x: x[0])
            if c_min >= target:
                break
            step = min(target - c_min, 6)
            cand = (q[0] - d_min[0] * step, q[1] - d_min[1] * step)
            if not in_ink(cand, polys):
                break
            q = cand
        out.append(q)
    return out


def resample(points, n):
    lens = [0.0]
    for i in range(1, len(points)):
        lens.append(lens[-1] + math.dist(points[i - 1], points[i]))
    total = lens[-1]
    out = []
    for k in range(n):
        target = total * k / (n - 1)
        for i in range(1, len(points)):
            if target <= lens[i] or i == len(points) - 1:
                span = lens[i] - lens[i - 1]
                u = 0.0 if span == 0 else (target - lens[i - 1]) / span
                out.append((
                    points[i - 1][0] + (points[i][0] - points[i - 1][0]) * u,
                    points[i - 1][1] + (points[i][1] - points[i - 1][1]) * u,
                ))
                break
    return out


def simplify(points, tol):
    keep = {0, len(points) - 1}

    def rec(i, j):
        if j <= i + 1:
            return
        a, b = points[i], points[j]
        ab = (b[0] - a[0], b[1] - a[1])
        l2 = ab[0] * ab[0] + ab[1] * ab[1]
        best, bd = -1, -1.0
        for k in range(i + 1, j):
            p = points[k]
            if l2 == 0:
                d = math.dist(p, a)
            else:
                t = max(0.0, min(1.0, ((p[0] - a[0]) * ab[0]
                                       + (p[1] - a[1]) * ab[1]) / l2))
                d = math.dist(p, (a[0] + ab[0] * t, a[1] + ab[1] * t))
            if d > bd:
                bd, best = d, k
        if bd > tol:
            keep.add(best)
            rec(i, best)
            rec(best, j)

    rec(0, len(points) - 1)
    return [points[k] for k in sorted(keep)]


def smooth(points):
    if len(points) < 3:
        return list(points)
    mid = [
        ((points[i - 1][0] + points[i][0] + points[i + 1][0]) / 3,
         (points[i - 1][1] + points[i][1] + points[i + 1][1]) / 3)
        for i in range(1, len(points) - 1)
    ]
    return [points[0]] + mid + [points[-1]]


def _tls_dir(points):
    n = len(points)
    mx = sum(p[0] for p in points) / n
    my = sum(p[1] for p in points) / n
    sxx = sum((p[0] - mx) ** 2 for p in points)
    syy = sum((p[1] - my) ** 2 for p in points)
    sxy = sum((p[0] - mx) * (p[1] - my) for p in points)
    th = 0.5 * math.atan2(2 * sxy, sxx - syy)
    ux, uy = math.cos(th), math.sin(th)
    d = (points[-1][0] - points[0][0], points[-1][1] - points[0][1])
    if d[0] * ux + d[1] * uy < 0:
        ux, uy = -ux, -uy
    return mx, my, ux, uy


def _perp_span(p, nx, ny, polys, step=2.0, lim=600.0):
    d1 = 0.0
    while d1 < lim and in_ink((p[0] + nx * (d1 + step),
                               p[1] + ny * (d1 + step)), polys):
        d1 += step
    d2 = 0.0
    while d2 < lim and in_ink((p[0] - nx * (d2 + step),
                               p[1] - ny * (d2 + step)), polys):
        d2 += step
    return d1, d2


def _fit_line(sec, polys, max_r, min_clear):
    arc = sum(math.dist(sec[i - 1], sec[i]) for i in range(1, len(sec)))
    chord = math.dist(sec[0], sec[-1])
    if chord < 1e-9 or arc > 1.25 * chord:
        return None
    _, _, ux, uy = _tls_dir(sec)
    nx, ny = -uy, ux
    centers, widths = [], []
    for p in sec:
        d1, d2 = _perp_span(p, nx, ny, polys)
        centers.append((p[0] + nx * (d1 - d2) / 2,
                        p[1] + ny * (d1 - d2) / 2))
        widths.append(d1 + d2)
    sw = sorted(widths)
    ref_w = sw[len(sw) // 4]
    good = [c for c, w in zip(centers, widths) if w <= 1.4 * ref_w]
    ux0, uy0 = (sec[-1][0] - sec[0][0]) / chord, (sec[-1][1] - sec[0][1]) / chord
    dev = max(abs((p[0] - sec[0][0]) * uy0 - (p[1] - sec[0][1]) * ux0) for p in sec)
    curved = dev > CURVE_ALWAYS_SAGITTA * chord or (
        dev > STRAIGHT_SAGITTA * chord and dev > CURVE_MIN_WIDTHS * ref_w)
    if curved:
        return None
    mx, my, ux, uy = _tls_dir(good if len(good) >= 3 else sec)

    def proj(p):
        t = (p[0] - mx) * ux + (p[1] - my) * uy
        return (mx + t * ux, my + t * uy)

    a, b = proj(sec[0]), proj(sec[-1])
    ex, ey = b[0] - a[0], b[1] - a[1]
    en = math.hypot(ex, ey)
    if en > 1e-9:
        ex, ey = ex / en, ey / en

        def reach(p, dx, dy):
            far, r = p, 0.0
            while r < max_r:
                r += RAY_STEP
                q = (p[0] + dx * r, p[1] + dy * r)
                if not in_ink(q, polys):
                    break
                if clearance(q, polys, max_r) < min_clear:
                    break
                d1, d2 = _perp_span(q, -ey, ex, polys)
                if d1 + d2 > 1.4 * ref_w:
                    break
                far = q
            return far

        a = reach(a, -ex, -ey)
        b = reach(b, ex, ey)
    orig_min = min(clearance(p, polys, max_r) for p in sec)
    floor = min(min_clear, orig_min * 0.9)
    for j in range(41):
        q = (a[0] + (b[0] - a[0]) * j / 40, a[1] + (b[1] - a[1]) * j / 40)
        if not in_ink(q, polys) or clearance(q, polys, max_r) < floor:
            return None
    return (a, b)


def _corner_point(fa, fb, polys, min_clear, max_r):
    ua = (fa[1][0] - fa[0][0], fa[1][1] - fa[0][1])
    ub = (fb[1][0] - fb[0][0], fb[1][1] - fb[0][1])
    na, nb = math.hypot(*ua), math.hypot(*ub)
    if na < 1e-9 or nb < 1e-9:
        return None
    ua = (ua[0] / na, ua[1] / na)
    ub = (ub[0] / nb, ub[1] / nb)
    dx, dy = ua[0] - ub[0], ua[1] - ub[1]
    n = math.hypot(dx, dy)
    if n < 0.5:
        return None
    dx, dy = dx / n, dy / n
    start = ((fa[1][0] + fb[0][0]) / 2, (fa[1][1] + fb[0][1]) / 2)
    best, r = None, 0.0
    while r < max_r:
        q = (start[0] + dx * r, start[1] + dy * r)
        if not in_ink(q, polys) or clearance(q, polys, max_r) < min_clear:
            break
        best = q
        r += RAY_STEP
    return best


def _isect(a1, a2, b1, b2):
    d1 = (a2[0] - a1[0], a2[1] - a1[1])
    d2 = (b2[0] - b1[0], b2[1] - b1[1])
    den = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(den) < 1e-9:
        return None
    t = ((b1[0] - a1[0]) * d2[1] - (b1[1] - a1[1]) * d2[0]) / den
    return (a1[0] + d1[0] * t, a1[1] + d1[1] * t)


def straighten(pts, polys, max_r, min_clear):
    simp = simplify(pts, 3.0)
    corners = []
    for i in range(1, len(simp) - 1):
        a = (simp[i][0] - simp[i - 1][0], simp[i][1] - simp[i - 1][1])
        b = (simp[i + 1][0] - simp[i][0], simp[i + 1][1] - simp[i][1])
        na, nb = math.hypot(*a), math.hypot(*b)
        if not na or not nb:
            continue
        dot = max(-1.0, min(1.0, (a[0] * b[0] + a[1] * b[1]) / (na * nb)))
        if math.degrees(math.acos(dot)) > CORNER_DEG:
            corners.append(simp[i])
    cut = [0]
    for c in corners:
        j = min(range(len(pts)), key=lambda k: math.dist(pts[k], c))
        if cut[-1] < j < len(pts) - 1:
            cut.append(j)
    if len(cut) > 1:
        cumr = [0.0]
        for i in range(1, len(pts)):
            cumr.append(cumr[-1] + math.dist(pts[i - 1], pts[i]))
        keep = [0]
        for j in cut[1:]:
            if cumr[j] - cumr[keep[-1]] >= MIN_SECTION:
                keep.append(j)
        while len(keep) > 1 and cumr[-1] - cumr[keep[-1]] < MIN_SECTION:
            keep.pop()
        cut = keep
    cut.append(len(pts) - 1)
    secs = [pts[cut[k]:cut[k + 1] + 1] for k in range(len(cut) - 1)]
    fits = [_fit_line(s, polys, max_r, min_clear) for s in secs]

    starts = [None] * len(secs)
    ends = [None] * len(secs)
    starts[0] = fits[0][0] if fits[0] else secs[0][0]
    ends[-1] = fits[-1][1] if fits[-1] else secs[-1][-1]
    via = {}
    for k in range(1, len(secs)):
        fa, fb = fits[k - 1], fits[k]
        ref = secs[k][0]
        joint = ref
        if fa and fb:
            pt = _isect(fa[0], fa[1], fb[0], fb[1])
            near = 0.25 * min(math.dist(*fa), math.dist(*fb))
            if pt and in_ink(pt, polys) and math.dist(pt, ref) < near:
                joint = pt
            elif pt is not None and not in_ink(pt, polys):
                tip = _corner_point(fa, fb, polys, min_clear, max_r)
                if tip is not None:
                    ends[k - 1] = fa[1]
                    starts[k] = fb[0]
                    via[k] = tip
                    continue
        ends[k - 1] = joint
        starts[k] = joint
    out = []
    for k, (s, f) in enumerate(zip(secs, fits)):
        if f is None:
            seg = list(s)
            seg[0] = starts[k]
            seg[-1] = ends[k]
        else:
            seg = resample([starts[k], ends[k]], 8)
        if out and math.dist(out[-1], seg[0]) < 1e-9:
            seg = seg[1:]
        out.extend(seg)
        if (k + 1) in via:
            out.append(via[k + 1])
    return out


def derive_stroke(polys, pts_frac, push_target):
    x0, y0, x1, y1 = bbox(polys)
    raw = [(x0 + fx * (x1 - x0), y1 - fy * (y1 - y0)) for fx, fy in pts_frac]
    raw = resample(raw, 60)
    raw = [snap_to_ink(p, polys, y1 - y0) for p in raw]
    pts = medial_push(raw, polys, push_target)
    return smooth(smooth(pts))


def _rect(x0, y0, x1, y1, clockwise=True):
    c = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    if clockwise:
        c.reverse()
    return [(c[i], None, c[(i + 1) % 4]) for i in range(4)]


def _area(poly):
    return sum(poly[i][0] * poly[(i + 1) % len(poly)][1]
               - poly[(i + 1) % len(poly)][0] * poly[i][1]
               for i in range(len(poly))) / 2


def _counter(polys):
    return min(polys, key=lambda c: abs(_area(c)))


def synth_single_storey_a(font, m):
    segs = glyph_segments(font, "o")
    polys = flatten(segs)
    x1 = bbox(polys)[2]
    y_top = max(p[1] for p in polys[0])
    stem_l = max(p[0] for p in _counter(polys))
    cw = _area(polys[0]) < 0
    return segs + [_rect(stem_l, 0.0, x1, y_top, clockwise=cw)]


def synth_shin(font, m):
    segs = glyph_segments(font, "ש")
    polys = flatten(segs)
    small = min(range(len(polys)), key=lambda i: abs(_area(polys[i])))
    branch = polys[small]
    bx0 = min(p[0] for p in branch)
    bx1 = max(p[0] for p in branch)
    by0 = min(p[1] for p in branch)
    cup = [p for i, p in enumerate(polys) if i != small]
    cx = (bx0 + bx1) / 2
    y, step, limit = by0, 4.0, by0 - 4000.0
    while y > limit:
        y -= step
        if any(sp[0] <= cx <= sp[1] for sp in spans_at_y(y, cup)):
            break
    else:
        raise SystemExit("synth_shin: no cup found below the middle branch")
    inset = (bx1 - bx0) * 0.14
    cw = _area(polys[0]) < 0
    return segs + [_rect(bx0 + inset, y - 3 * step, bx1 - inset, by0 + 3 * step,
                         clockwise=cw)]


def synth_straight_t(font, m):
    polys = flatten(glyph_segments(font, "t"))
    x0, y0, x1, y1 = bbox(polys)
    stem = spans_at_y(y1 * 0.95, polys)[0]
    stem_w = stem[1] - stem[0]

    rows = []
    for i in range(401):
        y = y1 * 0.45 + (y1 - y1 * 0.45) * i / 400.0
        sp = spans_at_y(y, polys)
        if sp and (sp[0][1] - sp[0][0]) > stem_w * 1.5:
            rows.append((y, sp[0]))
    if not rows:
        raise SystemExit("synth t: no crossbar found in the font's own t")
    bar_x0 = min(sp[0] for _, sp in rows)
    bar_x1 = max(sp[1] for _, sp in rows)
    return [_rect(stem[0], 0.0, stem[1], y1),
            _rect(bar_x0, rows[0][0], bar_x1, rows[-1][0])]


def synth_capital_I(font, m):
    cap_h, stem_w = m["cap_h"], m["stem_w"]
    bar = 2.4 * stem_w
    cx = bar / 2
    rects = [
        (cx - stem_w / 2, 0.0, cx + stem_w / 2, cap_h),
        (0.0, cap_h - stem_w, bar, cap_h),
        (0.0, 0.0, bar, stem_w),
    ]
    segs = []
    for x0, y0, x1, y1 in rects:
        c = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        segs.append([(c[i], None, c[(i + 1) % 4]) for i in range(4)])
    return segs


def seg_cum(m):
    cum = [0.0]
    for i in range(1, len(m)):
        cum.append(cum[-1] + math.dist(m[i - 1], m[i]))
    return cum


def seg_along(m, cum, t):
    target = min(max(t, 0.0), 1.0) * cum[-1]
    for i in range(1, len(cum)):
        if target <= cum[i] or i == len(cum) - 1:
            span = cum[i] - cum[i - 1]
            u = 0.0 if span == 0 else (target - cum[i - 1]) / span
            return (m[i - 1][0] + (m[i][0] - m[i - 1][0]) * u,
                    m[i - 1][1] + (m[i][1] - m[i - 1][1]) * u), i
    return m[-1], len(m) - 1


def corner_positions(m, cum):
    out = []
    for i in range(1, len(m) - 1):
        a = (m[i][0] - m[i - 1][0], m[i][1] - m[i - 1][1])
        b = (m[i + 1][0] - m[i][0], m[i + 1][1] - m[i][1])
        na, nb = math.hypot(*a), math.hypot(*b)
        if na == 0 or nb == 0:
            continue
        dot = max(-1.0, min(1.0, (a[0] * b[0] + a[1] * b[1]) / (na * nb)))
        if math.degrees(math.acos(dot)) > CORNER_DEG:
            out.append(cum[i])
    return out


def stroke_sections(m, cum, min_len=0.0):
    cs = [0.0]
    for pos in corner_positions(m, cum):
        if pos - cs[-1] < min_len:
            if len(cs) > 1:
                cs[-1] = (cs[-1] + pos) / 2
            continue
        cs.append(pos)
    if len(cs) > 1 and cum[-1] - cs[-1] < min_len:
        cs.pop()
    cs.append(cum[-1])
    out = []
    for a, b in zip(cs, cs[1:]):
        pa, _ = seg_along(m, cum, a / cum[-1])
        pb, _ = seg_along(m, cum, b / cum[-1])
        chord = math.dist(pa, pb)
        d = None
        if chord > 1e-9:
            ux, uy = (pb[0] - pa[0]) / chord, (pb[1] - pa[1]) / chord
            dev = 0.0
            for k in range(1, 20):
                p, _ = seg_along(m, cum, (a + (b - a) * k / 20) / cum[-1])
                dev = max(dev, abs((p[0] - pa[0]) * uy - (p[1] - pa[1]) * ux))
            if dev <= STRAIGHT_SAGITTA * chord:
                d = (ux, uy)
        out.append((a, b, d))
    return out


def tangent_at(m, cum, t, w, sections):
    target = min(max(t, 0.0), 1.0) * cum[-1]
    lo, hi, straight = sections[-1]
    for s in sections:
        if s[0] <= target <= s[1]:
            lo, hi, straight = s
            break
    if straight is not None:
        return straight
    a, _ = seg_along(m, cum, max(lo, target - w) / cum[-1])
    b, _ = seg_along(m, cum, min(hi, target + w) / cum[-1])
    d = (b[0] - a[0], b[1] - a[1])
    n = math.hypot(*d)
    if n < 1e-9:
        _, idx = seg_along(m, cum, t)
        d = (m[idx][0] - m[idx - 1][0], m[idx][1] - m[idx - 1][1])
        n = math.hypot(*d) or 1.0
    return d[0] / n, d[1] / n


def _tris_overlap(a, b):
    for t in (a, b):
        for i in range(3):
            p, q = t[i], t[(i + 1) % 3]
            ax, ay = -(q[1] - p[1]), q[0] - p[0]
            pa = [v[0] * ax + v[1] * ay for v in a]
            pb = [v[0] * ax + v[1] * ay for v in b]
            if max(pa) <= min(pb) or max(pb) <= min(pa):
                return False
    return True


def arrow_triangle(a, scale):
    s = min(a["s"] * scale, a["smax"])
    tip = (a["x"] + a["dx"] * s, a["y"] + a["dy"] * s)
    bx, by = a["x"] - a["dx"] * s * ARROW_BACK, a["y"] - a["dy"] * s * ARROW_BACK
    nx, ny = -a["dy"], a["dx"]
    return [
        tip,
        (bx + nx * s * ARROW_WING, by + ny * s * ARROW_WING),
        (bx - nx * s * ARROW_WING, by - ny * s * ARROW_WING),
    ]


def build_deck(deck_name, deck):
    forms = deck["letters"]
    only = os.environ.get("TRACE_ONLY")
    if only:
        want = {k.strip() for k in only.split(",") if k.strip()}
        sel = want & set(forms)
        if not sel:
            return None
        keep = sel | ({deck["cap_ref"]} if deck.get("cap_ref") else set())
        forms = {k: v for k, v in forms.items() if k in keep}
    for fk in forms:
        manifest_for(deck_name, fk, forms[fk])

    use_cache = not only and os.environ.get("STROKES_NO_CACHE") != "1"
    fps = ({fk: form_fingerprint(deck_name, deck, fk) for fk in forms}
           if use_cache else {})
    cached = {}
    if use_cache:
        for fk, fp in fps.items():
            entry = _cache_read(fp)
            if entry is not None:
                cached[fk] = entry
    todo = [fk for fk in forms if fk not in cached]
    if os.environ.get("TRACE_PROGRESS") or use_cache:
        print(f"{deck_name}: {len(cached)} cached, {len(todo)} to draw",
              file=sys.stderr, flush=True)

    font = TTFont(deck["font"])
    synth = {k: v for k, v in deck.get("synth", {}).items() if k in forms}
    glyphs = {}
    cap_ref = deck.get("cap_ref")
    need = set(todo) | ({cap_ref} if cap_ref else set())
    for fk in forms:
        if fk in synth or fk not in need:
            continue
        segs = glyph_segments(font, forms[fk])
        polys = flatten(segs)
        glyphs[fk] = (segs, polys, bbox(polys))

    y_band = [r["y"] for r in deck["rules"]]
    y_top, y_base = min(y_band), max(y_band)
    x_h = bbox(flatten(glyph_segments(font, deck["x_ref"])))[3]
    cell_h = x_h / (y_base - y_top)

    if cap_ref:
        cap_h = glyphs[cap_ref][2][3]
        h_span = spans_at_y(cap_h * 0.25, glyphs[cap_ref][1])[0]
        stem_w = h_span[1] - h_span[0]
    else:
        cap_h, stem_w = x_h, None
    metrics = {"cap_h": cap_h, "x_h": x_h, "stem_w": stem_w}
    for fk, builder in synth.items():
        if fk not in need:
            continue
        segs_s = globals()[builder](font, metrics)
        polys_s = flatten(segs_s)
        glyphs[fk] = (segs_s, polys_s, bbox(polys_s))

    margin = MARGIN * cell_h
    push_target = 0.07 * cap_h

    def cell_aspect(fk):
        x0, _, x1, _ = glyphs[fk][2]
        return ((x1 - x0) + 2 * margin) / cell_h

    def to_cell(fk, p):
        x0, _, x1, _ = glyphs[fk][2]
        return (
            (p[0] - x0 + margin) / cell_h,
            y_base - p[1] / cell_h,
        )

    derived = {}
    half_of = {}
    for fk in todo:
        if os.environ.get("TRACE_PROGRESS"):
            print("derive", fk, file=sys.stderr, flush=True)
        min_half = math.inf
        _, polys, bb = glyphs[fk]
        strokes = []
        for si, spec in enumerate(manifest_for(deck_name, fk, forms[fk])):
            fracs = spec["pts"]
            if spec.get("reverse"):
                fracs = list(reversed(fracs))
            pts = derive_stroke(polys, fracs, push_target)
            if not spec.get("curve"):
                pts = straighten(pts, polys, cell_h, 25)
            pts = simplify(pts, 3.0)
            local = [clearance(p, polys, cell_h) for p in pts]
            for p, c in zip(pts, local):
                if not in_ink(p, polys):
                    raise SystemExit(
                        f"{fk} stroke {si}: median point {p} off the glyph")
                if c < 25:
                    raise SystemExit(
                        f"{fk} stroke {si}: only {c:.0f} units of ink "
                        f"around {p}")
            for i in range(1, len(pts)):
                for k in range(1, 5):
                    q = (pts[i - 1][0]
                         + (pts[i][0] - pts[i - 1][0]) * k / 5,
                         pts[i - 1][1]
                         + (pts[i][1] - pts[i - 1][1]) * k / 5)
                    if not in_ink(q, polys) or clearance(
                            q, polys, cell_h) < 8:
                        raise SystemExit(
                            f"{fk} stroke {si}: segment {i} leaves the "
                            f"ink near {q}")
            min_half = min(min_half, min(local) / cell_h)
            cumf = seg_cum(pts)
            dense = [clearance(seg_along(pts, cumf, j / 11)[0],
                               polys, cell_h) for j in range(1, 11)]
            strokes.append((pts, local, dense))
        derived[fk] = strokes
        half_of[fk] = min_half

    fresh = {}
    for fk in todo:
        if os.environ.get("TRACE_PROGRESS"):
            print("arrows", fk, file=sys.stderr, flush=True)
        segs, polys, bb = glyphs[fk]
        all_cl = sorted(
            c for _, _, dense in derived[fk] for c in dense)
        basis = min(ARROW_BASIS_MAX, 0.9 * all_cl[len(all_cl) // 2] / cell_h)
        medians = []
        cands = []
        specs = manifest_for(deck_name, fk, forms[fk])
        press = [bool(sp.get("press")) for sp in specs]
        for si, (pts, local, _) in enumerate(derived[fk]):
            m_cell = [to_cell(fk, p) for p in pts]
            if press[si]:
                cands.append([])
                medians.append([[round(x, 4), round(y, 4)] for x, y in m_cell])
                continue
            cum = seg_cum(m_cell)
            sections = stroke_sections(m_cell, cum, basis)
            tan_w = basis * ARROW_SPACING / 2
            stroke_cands, kept = [], []
            def tri_fit(p, dx, dy):
                probe = {"x": p[0], "y": p[1], "dx": dx, "dy": dy}
                s_lo, s_hi = 0.0, basis * 1.6
                for _ in range(12):
                    mid = (s_lo + s_hi) / 2
                    probe["s"] = probe["smax"] = mid
                    ok = True
                    for vx, vy in arrow_triangle(probe, 1.0):
                        fq = (vx * cell_h + bb[0] - margin,
                              (y_base - vy) * cell_h)
                        if not in_ink(fq, polys):
                            ok = False
                            break
                    if ok:
                        s_lo = mid
                    else:
                        s_hi = mid
                return s_lo * 0.98

            fit_floor = basis * 0.55 * PULSE
            want = basis * ARROW_SPACING
            tri_len = basis * ARROW_SIZE * (1.0 + ARROW_BACK)
            corner_off = []
            for s_prev, s_next in zip(sections, sections[1:]):
                c = s_prev[1]
                lim = 0.45 * min(s_prev[1] - s_prev[0], s_next[1] - s_next[0])
                d = 0.0
                while d < lim:
                    pa, _ = seg_along(m_cell, cum, (c - d) / cum[-1])
                    pb, _ = seg_along(m_cell, cum, (c + d) / cum[-1])
                    if math.dist(pa, pb) >= want:
                        break
                    d += basis * 0.05
                corner_off.append(min(d, lim))
            for k, (lo, hi, straight) in enumerate(sections):
                span_len = hi - lo
                pad = min(basis * 0.9, span_len * 0.25)
                pad_lo = max(pad, corner_off[k - 1]) if k > 0 else pad
                pad_hi = max(pad, corner_off[k]) if k < len(sections) - 1 else pad
                inner = max(0.0, span_len - pad_lo - pad_hi)
                m = 1 if inner < basis * 0.5 else max(
                    2, min(12, round(inner / want) + 1))
                radius = tri_len
                for j in range(m):
                    base = lo + pad_lo + inner * (j / (m - 1) if m > 1 else 0.5)
                    for off in (0.0, -0.35 * basis, 0.35 * basis,
                                -0.7 * basis, 0.7 * basis):
                        arc = min(max(base + off, lo + pad_lo),
                                  hi - pad_hi)
                        u = arc / cum[-1]
                        p, _ = seg_along(m_cell, cum, u)
                        if any(math.dist(p, q) < radius for q in kept):
                            continue
                        dx, dy = tangent_at(m_cell, cum, u, tan_w, sections)
                        s_fit = tri_fit(p, dx, dy)
                        if s_fit < fit_floor:
                            continue
                        kept.append(p)
                        stroke_cands.append(
                            {"u": u, "p": p, "d": (dx, dy), "fit": s_fit})
                        break
            stroke_cands.sort(key=lambda c: c["u"])
            cands.append(stroke_cands)
            medians.append([[round(x, 4), round(y, 4)] for x, y in m_cell])

        min_fit = min((c["fit"] for row in cands for c in row),
                      default=basis)
        s_letter = min(basis * ARROW_SIZE, min_fit / PULSE)
        arrows = []
        for si, stroke_cands in enumerate(cands):
            row, fix_row = [], []
            for c in stroke_cands:
                a = {
                    "u": round(c["u"], 4),
                    "x": round(c["p"][0], 4), "y": round(c["p"][1], 4),
                    "dx": round(c["d"][0], 4), "dy": round(c["d"][1], 4),
                    "s": round(s_letter, 4),
                    "smax": round(c["fit"], 4),
                }
                row.append(a)
                fix_row.append([[round(v, 4) for v in vert]
                                for vert in arrow_triangle(a, 1.0)])
                for scale in (1.0, PULSE):
                    for vx, vy in arrow_triangle(a, scale):
                        fp = (
                            vx * cell_h + bb[0] - margin,
                            (y_base - vy) * cell_h,
                        )
                        if not in_ink(fp, polys):
                            raise SystemExit(
                                f"{fk} stroke {si} arrow u={a['u']:.2f} "
                                f"scale={scale}: vertex off the glyph")
            drop = set()
            for i in range(len(fix_row)):
                if i in drop:
                    continue
                for j in range(i + 1, len(fix_row)):
                    if j in drop:
                        continue
                    if _tris_overlap(fix_row[i], fix_row[j]):
                        loser = j if row[j]["smax"] <= row[i]["smax"] else i
                        keeper = i if loser == j else j
                        print(f"{fk} stroke {si}: arrow at u={row[loser]['u']} "
                              f"dropped, it overlaps the one at "
                              f"u={row[keeper]['u']}", file=sys.stderr)
                        drop.add(loser)
                        if loser == i:
                            break
            row = [a for k, a in enumerate(row) if k not in drop]
            fix_row = [f for k, f in enumerate(fix_row) if k not in drop]
            for i in range(len(fix_row)):
                for j in range(i + 1, len(fix_row)):
                    assert not _tris_overlap(fix_row[i], fix_row[j]), \
                        f"{fk} stroke {si}: overlap survived the drop"
            arrows.append(row)

        fresh[fk] = {
            "aspect": round(cell_aspect(fk), 4),
            "medians": medians, "arrows": arrows, "press": press,
            "outline": _svg_path(segs, lambda p: to_cell(fk, p)),
        }

    if use_cache:
        for fk in todo:
            _cache_write(fps[fk], {"letter": fresh[fk], "min_half": half_of[fk]})

    letters = {}
    for fk in forms:
        if only and fk not in sel:
            continue
        letters[fk] = fresh[fk] if fk in fresh else cached[fk]["letter"]
    stroke_half = min(half_of[fk] if fk in half_of else cached[fk]["min_half"]
                      for fk in forms)

    meta = {
        "rules": [dict(r) for r in deck["rules"]],
        "strokeHalf": round(stroke_half, 4),
        "arrow": {"back": ARROW_BACK, "wing": ARROW_WING, "pulse": PULSE},
        "walk": {"speed": WALK_SPEED, "minMs": WALK_MIN_MS,
                 "maxMs": WALK_MAX_MS, "holdMs": WALK_HOLD_MS},
    }
    return letters, meta


def _svg_path(segs, to_cell):
    parts = []
    f = lambda p: f"{round(p[0], 4)} {round(p[1], 4)}"
    for contour in segs:
        parts.append("M" + f(to_cell(contour[0][0])))
        for p0, c, p1 in contour:
            if c is None:
                parts.append("L" + f(to_cell(p1)))
            else:
                parts.append("Q" + f(to_cell(c)) + " " + f(to_cell(p1)))
        parts.append("Z")
    return " ".join(parts)


def document(name, letters, meta, lift=None):
    out = {}
    for ch, d in letters.items():
        strokes = []
        for i, pts in enumerate(d["medians"]):
            strokes.append({
                "points": pts,
                "press": d["press"][i],
                "lift": True if lift is None else lift[ch][i],
                "arrows": d["arrows"][i],
            })
        out[ch] = {"aspect": d["aspect"], "outline": d["outline"],
                   "strokes": strokes}
    return {"format": "how-to-write-letters/1", "alphabet": name, **meta,
            "letters": out}


def write_document(doc, out_dir=OUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, doc["alphabet"] + ".json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write("\n")
    os.replace(tmp, path)
    return path


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    unknown = [a for a in args if a not in DECKS]
    if unknown:
        raise SystemExit(f"unknown alphabet {unknown[0]!r}; "
                         f"choose from {', '.join(DECKS)}")
    names = args or list(DECKS)
    if "--fingerprint" in sys.argv:
        json.dump({
            "algorithm": _algorithm_sha(),
            "decks": {name: {fk: form_fingerprint(name, DECKS[name], fk)
                             for fk in DECKS[name]["letters"]}
                      for name in names},
        }, sys.stdout, sort_keys=True, ensure_ascii=False)
        return 0
    built = {}
    for name in names:
        got = build_deck(name, DECKS[name])
        if got is not None:
            built[name] = got
    if not built:
        raise SystemExit(
            f"TRACE_ONLY={os.environ.get('TRACE_ONLY')!r} matched no letter")
    for name, (letters, meta) in built.items():
        doc = document(name, letters, meta)
        if os.environ.get("TRACE_ONLY"):
            json.dump(doc, sys.stdout, ensure_ascii=False)
            continue
        n_arrows = sum(len(s["arrows"]) for L in doc["letters"].values()
                       for s in L["strokes"])
        print(f"wrote {os.path.relpath(write_document(doc))}  "
              f"letters={len(letters)}  arrows={n_arrows}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

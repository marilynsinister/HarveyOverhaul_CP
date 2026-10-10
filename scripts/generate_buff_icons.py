"""Генерирует уникальные иконки для всех баффов мода: assets/Tilesheets/harveyBuffIcons.png.

Каждая иконка = базовый символ (что болит / чем лечат) + значки (фаза, лечение, запрет).
Контур и объём добавляются автоматически, в стиле иконок мода (тёплый тёмный контур).

    python scripts/generate_buff_icons.py            # лист + assets/Tilesheets/harveyBuffIcons.json (id → индекс)
    python scripts/generate_buff_icons.py --preview  # + scripts/_preview_buff_icons.png с подписями
    python scripts/generate_buff_icons.py --apply    # прописать IconTexture/IconSpriteIndex в assets/Code/*.json
"""
import glob
import json
import re
import sys

from PIL import Image, ImageDraw

S = 16
COLUMNS = 16
TEXTURE = "Mods/{{ModId}}/HarveyBuffIcons"

# --- палитра ---------------------------------------------------------------
SKIN, SKIN_D = (244, 196, 150), (206, 146, 102)
BONE = (240, 232, 210)
WHITE, CREAM = (252, 250, 242), (226, 216, 196)
RED, DRED, PINK = (220, 56, 60), (150, 30, 44), (246, 136, 136)
BLUE, LBLUE, DBLUE = (100, 164, 236), (196, 228, 255), (56, 88, 168)
GREEN, LGREEN, DGREEN = (104, 182, 78), (170, 220, 120), (56, 120, 50)
YELLOW, GOLD, ORANGE = (255, 216, 84), (236, 176, 52), (240, 140, 48)
PURPLE, DPURP, LPURP = (146, 98, 200), (74, 48, 118), (196, 166, 236)
BROWN, LBROWN = (140, 94, 54), (196, 146, 96)
GREY, LGREY, DGREY = (150, 150, 162), (204, 206, 214), (88, 88, 100)
INK = (44, 36, 44)
TEAL = (76, 186, 176)
NIGHT = (52, 48, 92)


def rgba(c, a=255):
    return tuple(c) if len(c) == 4 else (c[0], c[1], c[2], a)


class Icon:
    def __init__(self):
        self.img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.badges = []

    # примитивы (без сглаживания)
    def rect(self, x0, y0, x1, y1, c):
        self.d.rectangle([x0, y0, x1, y1], fill=rgba(c))

    def oval(self, x0, y0, x1, y1, c):
        self.d.ellipse([x0, y0, x1, y1], fill=rgba(c))

    def line(self, pts, c, w=1):
        self.d.line(pts, fill=rgba(c), width=w)

    def poly(self, pts, c):
        self.d.polygon(pts, fill=rgba(c))

    def px(self, x, y, c):
        if 0 <= x < S and 0 <= y < S:
            self.img.putpixel((x, y), rgba(c))

    def grid(self, x0, y0, rows, colors):
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch != ".":
                    self.px(x0 + x, y0 + y, colors[ch])

    def badge(self, fn, *args):
        self.badges.append((fn, args))


# --- постобработка ---------------------------------------------------------
def shade_and_outline(img):
    src = img.copy()
    px = src.load()
    out = img.load()

    def opaque(x, y):
        return 0 <= x < S and 0 <= y < S and px[x, y][3] > 0

    for y in range(S):
        for x in range(S):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            if not opaque(x + 1, y) or not opaque(x, y + 1):
                f = 0.78
            elif not opaque(x - 1, y) or not opaque(x, y - 1):
                f = 1.12
            else:
                continue
            out[x, y] = (min(255, int(r * f)), min(255, int(g * f)), min(255, int(b * f)), a)

    shaded = img.copy()
    sp = shaded.load()
    for y in range(S):
        for x in range(S):
            if sp[x, y][3] > 0:
                continue
            neigh = [sp[nx, ny] for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
                     if 0 <= nx < S and 0 <= ny < S and sp[nx, ny][3] == 255]
            if neigh:
                r = sum(n[0] for n in neigh) // len(neigh)
                g = sum(n[1] for n in neigh) // len(neigh)
                b = sum(n[2] for n in neigh) // len(neigh)
                out[x, y] = (int(r * 0.32) + 18, int(g * 0.28) + 10, int(b * 0.30) + 14, 255)


def outlined_badge(icon, draw_fn):
    layer = Icon()
    draw_fn(layer)
    shade_and_outline(layer.img)
    icon.img.alpha_composite(layer.img)


# --- значки ----------------------------------------------------------------
def b_plus(c, color=GREEN):
    c.rect(11, 9, 12, 14, color)
    c.rect(9, 11, 14, 12, color)


def b_cross(c):
    c.line([(9, 9), (14, 14)], RED, 2)
    c.line([(14, 9), (9, 14)], RED, 2)


def b_bang(c, color=YELLOW):
    c.rect(12, 8, 13, 11, color)
    c.rect(12, 13, 13, 14, color)


def b_drop(c, color=BLUE):
    c.poly([(12, 8), (14, 12), (12, 14), (10, 12)], color)


def b_z(c):
    c.grid(10, 9, ["####", "..#.", ".#..", "####"], {"#": LBLUE})


def b_heart(c, color=PINK):
    c.grid(9, 9, [".##.##", "######", "######", ".####.", "..##.."], {"#": color})


def b_up(c, color=GREEN):
    c.poly([(12, 8), (15, 11), (13, 11), (13, 14), (11, 14), (11, 11), (9, 11)], color)


def b_down(c, color=RED):
    c.poly([(12, 15), (15, 12), (13, 12), (13, 9), (11, 9), (11, 12), (9, 12)], color)


def b_level(c, n, total=3):
    """Уровень/фаза: точки в правом нижнем углу, цвет от красного к зелёному."""
    colors = {1: RED, 2: ORANGE, 3: GREEN}
    col = colors[min(3, n)] if total > 1 else GREEN
    for i in range(total):
        x = 14 - (total - 1 - i) * 3
        c.rect(x - 1, 13, x, 14, col if i < n else GREY)


def b_star(c, color=GOLD):
    c.grid(9, 8, ["..#..", "..#..", "#####", ".###.", ".#.#."], {"#": color})


def b_clock(c):
    c.oval(9, 9, 14, 14, WHITE)
    c.line([(11, 11), (11, 12), (13, 12)], INK)


# --- базовые символы -------------------------------------------------------
def bone(c, col=BONE):
    c.line([(4, 11), (11, 4)], col, 3)
    for cx, cy in ((3, 10), (5, 12), (10, 3), (12, 5)):
        c.oval(cx - 2, cy - 2, cx + 1, cy + 1, col)


def crack(c, col=DRED):
    c.line([(5, 6), (7, 8), (6, 9), (8, 11)], col)


def cast(c):
    """Рука в гипсе: кисть сверху, гипс по диагонали."""
    c.oval(9, 1, 14, 6, SKIN)
    c.line([(3, 13), (10, 5)], WHITE, 5)
    c.line([(4, 10), (7, 13)], CREAM)
    c.line([(7, 7), (10, 10)], CREAM)


def head(c, col=SKIN):
    c.oval(3, 3, 12, 12, col)
    c.rect(5, 12, 10, 14, col)
    c.px(6, 7, INK)
    c.px(9, 7, INK)


def stars_over(c):
    for x, y in ((2, 2), (12, 1), (13, 6)):
        c.px(x, y, YELLOW)
        c.px(x + 1, y, YELLOW)
        c.px(x, y + 1, YELLOW)


def pillow(c):
    c.oval(1, 9, 14, 14, WHITE)


def headband(c):
    c.rect(3, 4, 12, 5, WHITE)


def shards(c, col=LGREY):
    c.poly([(2, 4), (6, 2), (5, 7)], col)
    c.poly([(9, 3), (13, 5), (10, 8)], col)
    c.poly([(4, 10), (8, 9), (6, 14)], col)
    c.px(7, 6, RED)
    c.px(11, 11, RED)


def scalpel(c):
    c.line([(3, 12), (9, 6)], GREY, 2)
    c.poly([(9, 6), (13, 2), (12, 5), (10, 7)], LGREY)


def wound_line(c, col=RED):
    c.oval(2, 5, 13, 10, SKIN)
    c.line([(4, 8), (11, 7)], col)


def stitches(c):
    for x in range(5, 12, 2):
        c.line([(x, 6), (x, 9)], INK)


def arm(c, col=SKIN):
    c.line([(2, 13), (6, 9)], col, 4)
    c.line([(6, 9), (5, 3)], col, 4)
    c.oval(6, 5, 11, 10, col)


def tear(c):
    c.line([(7, 6), (9, 8), (8, 9)], RED)


def tape(c):
    c.line([(4, 9), (9, 6)], WHITE, 2)


def dumbbell(c):
    c.rect(2, 6, 4, 11, DGREY)
    c.rect(11, 6, 13, 11, DGREY)
    c.rect(4, 8, 11, 9, GREY)


def foot(c, col=SKIN):
    c.rect(4, 2, 8, 10, col)
    c.oval(3, 8, 13, 13, col)


def swelling(c):
    c.oval(5, 7, 9, 11, PINK)


def brace(c):
    c.rect(3, 6, 9, 9, BLUE)


def ribs(c):
    c.rect(7, 2, 8, 13, BONE)
    for y in (3, 6, 9):
        c.line([(7, y), (3, y + 2), (3, y + 3)], BONE)
        c.line([(8, y), (12, y + 2), (12, y + 3)], BONE)


def bruise(c):
    c.oval(9, 5, 13, 9, LPURP)


def band(c):
    c.rect(2, 7, 13, 9, WHITE)


def blade(c):
    c.poly([(2, 13), (10, 4), (12, 6), (4, 14)], LGREY)
    c.rect(11, 2, 13, 4, BROWN)


def blood(c):
    c.poly([(6, 7), (8, 11), (6, 13), (4, 11)], RED)


def plaster(c, col=CREAM):
    c.poly([(2, 9), (9, 2), (13, 6), (6, 13)], col)
    c.rect(6, 6, 9, 9, (240, 210, 170))


def flame(c, col=ORANGE):
    c.poly([(8, 1), (13, 8), (12, 13), (4, 13), (3, 8), (6, 5), (7, 8)], col)
    c.poly([(8, 7), (10, 10), (9, 13), (6, 13), (6, 10)], YELLOW)


def skin_patch(c):
    c.oval(1, 6, 14, 14, SKIN)


def gel(c):
    c.oval(4, 8, 11, 13, LBLUE)


def germ(c, col=GREEN):
    c.oval(3, 3, 12, 12, col)
    for x, y in ((1, 7), (13, 7), (7, 1), (7, 13), (3, 3), (11, 11), (11, 3), (3, 11)):
        c.px(x, y, col)
    c.px(6, 6, DGREEN)
    c.px(9, 8, DGREEN)


def capsule(c, a=RED, b=WHITE):
    c.line([(4, 11), (7, 8)], a, 4)
    c.line([(8, 7), (11, 4)], b, 4)


def spine(c):
    for y in range(2, 14, 3):
        c.rect(6, y, 9, y + 1, BONE)
    c.line([(7, 2), (7, 14)], CREAM)


def bolt(c, col=YELLOW):
    c.poly([(9, 1), (4, 8), (7, 8), (5, 14), (11, 6), (8, 6), (11, 1)], col)


def heat_pad(c):
    c.rect(3, 7, 12, 10, ORANGE)


def heart(c, col=RED):
    c.grid(1, 2, [
        ".####..####.",
        "######.#####",
        "############",
        "############",
        ".##########.",
        "..########..",
        "...######...",
        "....####....",
        ".....##.....",
    ], {"#": col})


def battery(c, level, col=GREEN):
    c.rect(2, 4, 12, 11, DGREY)
    c.rect(13, 6, 14, 9, DGREY)
    c.rect(3, 5, 11, 10, (60, 60, 70))
    if level > 0:
        c.rect(3, 5, 3 + int(8 * level), 10, col)


def zzz(c, col=LBLUE):
    c.grid(2, 2, ["#####", "...#.", "..#..", ".#...", "#####"], {"#": col})
    c.grid(9, 8, ["####", "..#.", ".#..", "####"], {"#": col})


def bottle(c, col=GREEN):
    c.rect(6, 1, 9, 4, col)
    c.rect(4, 5, 11, 14, col)
    c.rect(5, 8, 10, 11, CREAM)


def droplet(c, col=BLUE):
    c.poly([(7, 1), (12, 8), (11, 12), (7, 14), (3, 12), (2, 8)], col)
    c.px(5, 8, WHITE)


def pickaxe(c):
    c.line([(3, 13), (10, 6)], BROWN, 2)
    c.poly([(5, 2), (10, 3), (13, 6), (12, 9), (10, 6), (7, 4)], GREY)


def crutch(c):
    c.line([(4, 3), (10, 14)], LBROWN, 2)
    c.line([(2, 3), (7, 2)], LBROWN, 2)
    c.line([(6, 8), (9, 7)], LBROWN)


def thin_arm(c):
    c.line([(3, 13), (6, 8)], SKIN, 2)
    c.line([(6, 8), (6, 2)], SKIN, 2)


def lungs(c, col=PINK):
    c.oval(2, 4, 7, 13, col)
    c.oval(8, 4, 13, 13, col)
    c.line([(7, 1), (7, 6)], CREAM, 2)


def thermometer(c, col=RED):
    c.rect(6, 1, 9, 11, WHITE)
    c.oval(4, 9, 11, 15, col)
    c.rect(7, 4, 8, 11, col)


def snowflake(c, col=LBLUE):
    c.line([(7, 1), (7, 14)], col)
    c.line([(1, 7), (14, 7)], col)
    c.line([(3, 3), (12, 12)], col)
    c.line([(12, 3), (3, 12)], col)
    c.rect(6, 6, 8, 8, WHITE)


def scarf(c):
    c.rect(2, 4, 13, 7, RED)
    c.rect(9, 7, 12, 14, RED)
    c.line([(2, 6), (13, 6)], WHITE)


def med_cross(c, col=GREEN):
    c.rect(6, 2, 9, 13, col)
    c.rect(2, 6, 13, 9, col)


def iv_bag(c):
    c.rect(4, 1, 11, 9, LBLUE)
    c.rect(5, 2, 10, 4, WHITE)
    c.line([(7, 9), (7, 14)], LGREY)


def clipboard(c):
    c.rect(3, 2, 12, 14, LBROWN)
    c.rect(4, 4, 11, 13, WHITE)
    c.rect(6, 1, 9, 3, GREY)
    for y in (6, 8, 10):
        c.line([(5, y), (10, y)], GREY)


def leaf(c, col=GREEN):
    c.poly([(2, 13), (3, 6), (8, 2), (13, 2), (12, 8), (7, 12)], col)
    c.line([(3, 12), (11, 4)], DGREEN)


def shield(c, col=BLUE):
    c.poly([(2, 2), (13, 2), (13, 8), (7, 14), (2, 8)], col)


def dropper(c):
    c.line([(3, 12), (9, 6)], LBLUE, 2)
    c.oval(9, 1, 14, 6, RED)
    c.px(2, 14, BLUE)


def vial(c, col=TEAL):
    c.rect(5, 1, 10, 3, GREY)
    c.rect(5, 4, 10, 14, WHITE)
    c.rect(5, 8, 10, 14, col)


def teacup(c, col=GREEN):
    c.rect(2, 6, 11, 13, WHITE)
    c.rect(3, 6, 10, 7, col)
    c.rect(12, 8, 13, 11, WHITE)
    c.px(5, 3, LGREY)
    c.px(6, 2, LGREY)
    c.px(8, 3, LGREY)
    c.px(9, 2, LGREY)


def eye(c, iris=BLUE):
    c.oval(1, 4, 14, 11, WHITE)
    c.oval(5, 5, 10, 10, iris)
    c.rect(7, 7, 8, 8, INK)


def droopy_eye(c):
    c.oval(1, 5, 14, 11, WHITE)
    c.oval(5, 6, 10, 11, BLUE)
    c.rect(1, 4, 14, 7, SKIN_D)
    c.px(7, 9, INK)


def siren(c):
    c.oval(3, 2, 12, 11, RED)
    c.rect(2, 11, 13, 13, DGREY)
    c.px(6, 5, WHITE)
    c.px(1, 3, YELLOW)
    c.px(14, 3, YELLOW)


def syringe(c):
    c.line([(3, 12), (11, 4)], WHITE, 3)
    c.line([(4, 11), (9, 6)], LBLUE)
    c.line([(11, 4), (14, 1)], GREY)
    c.line([(1, 14), (3, 12)], GREY)


def glasses(c):
    c.oval(1, 5, 6, 10, INK)
    c.oval(9, 5, 14, 10, INK)
    c.oval(2, 6, 5, 9, LBLUE)
    c.oval(10, 6, 13, 9, LBLUE)
    c.line([(6, 7), (9, 7)], INK)


def rx(c):
    c.rect(2, 1, 13, 14, WHITE)
    c.grid(3, 2, ["##.", "#.#", "##.", "#.#"], {"#": DBLUE})


def bed(c, small=False):
    y = 6 if small else 5
    c.rect(1, y + 3, 14, y + 6, LBROWN)
    c.rect(2, y + 1, 13, y + 3, WHITE)
    c.rect(2, y, 5, y + 2, CREAM)
    c.rect(1, y + 6, 2, y + 8, BROWN)
    c.rect(13, y + 6, 14, y + 8, BROWN)


def umbrella(c):
    c.poly([(1, 7), (4, 3), (8, 2), (11, 3), (14, 7)], BLUE)
    c.line([(8, 7), (8, 13), (6, 13)], BROWN)


def feather(c):
    c.poly([(3, 13), (6, 6), (11, 2), (12, 5), (8, 10)], WHITE)
    c.line([(3, 13), (11, 3)], LGREY)


def stethoscope(c):
    c.line([(4, 2), (4, 7), (7, 10), (10, 7), (10, 2)], DGREY, 1)
    c.line([(7, 10), (7, 12)], DGREY)
    c.oval(5, 11, 10, 15, LGREY)


def clinic(c):
    c.poly([(1, 7), (7, 1), (14, 7)], RED)
    c.rect(2, 7, 13, 14, CREAM)
    c.rect(6, 9, 9, 14, LBROWN)


def house(c):
    c.poly([(1, 7), (7, 1), (14, 7)], LBROWN)
    c.rect(2, 7, 13, 14, CREAM)
    c.rect(6, 10, 9, 14, BROWN)


def bandage_roll(c):
    c.oval(1, 3, 11, 13, WHITE)
    c.oval(4, 6, 8, 10, CREAM)
    c.rect(9, 9, 14, 12, WHITE)


def person(c, col=BLUE):
    c.oval(5, 1, 10, 6, SKIN)
    c.poly([(3, 14), (4, 8), (11, 8), (12, 14)], col)


def cloud(c, col=LGREY):
    c.oval(1, 5, 7, 11, col)
    c.oval(4, 2, 11, 9, col)
    c.oval(8, 5, 14, 11, col)
    c.rect(3, 8, 12, 11, col)


def plate(c):
    c.oval(1, 4, 14, 13, WHITE)
    c.oval(4, 6, 11, 11, CREAM)
    c.line([(0, 2), (0, 7)], GREY)
    c.line([(15, 2), (15, 7)], GREY)


def hoe(c):
    c.line([(3, 14), (11, 3)], BROWN, 2)
    c.poly([(9, 1), (14, 2), (13, 5), (10, 4)], GREY)


def moon(c, col=YELLOW):
    c.oval(2, 2, 13, 13, col)
    c.oval(6, 0, 15, 10, (0, 0, 0, 0))


def moon_crescent(c, col=YELLOW):
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([2, 2, 13, 13], fill=rgba(col))
    d.ellipse([6, 0, 16, 10], fill=(0, 0, 0, 0))
    c.img.alpha_composite(layer)


def dark_orb(c, eyes=1, col=NIGHT):
    c.oval(1, 1, 14, 14, col)
    spots = [(5, 6), (10, 6), (7, 10)][:eyes]
    for x, y in spots:
        c.rect(x - 1, y, x, y, YELLOW)


def candle(c, lit=0.5):
    c.rect(5, 7, 10, 14, CREAM)
    c.px(7, 6, INK)
    if lit:
        c.oval(6, 1 if lit > 0.6 else 3, 9, 6, ORANGE if lit < 0.6 else YELLOW)


def lantern(c):
    c.rect(5, 1, 10, 2, DGREY)
    c.rect(4, 3, 11, 12, DGREY)
    c.rect(5, 4, 10, 11, YELLOW)
    c.rect(6, 6, 9, 9, WHITE)
    c.rect(4, 13, 11, 14, DGREY)


def sunrise(c):
    c.oval(3, 6, 12, 15, YELLOW)
    c.rect(0, 11, 15, 15, (0, 0, 0, 0))
    c.rect(1, 11, 14, 12, ORANGE)
    for x, y in ((7, 2), (2, 6), (13, 6)):
        c.px(x, y, YELLOW)


def bubbles(c):
    c.oval(1, 1, 9, 7, WHITE)
    c.oval(6, 7, 14, 13, LGREY)
    c.px(3, 8, WHITE)


def wave(c, col=TEAL):
    for y in (4, 8, 12):
        c.line([(1, y), (4, y - 2), (7, y), (10, y - 2), (14, y)], col, 2)


def brain(c, col=PINK):
    c.oval(1, 3, 14, 13, col)
    c.line([(7, 3), (7, 13)], DRED)
    c.line([(3, 7), (5, 8), (4, 10)], DRED)
    c.line([(11, 6), (10, 8), (12, 10)], DRED)


def ghost(c, col=WHITE):
    c.oval(3, 1, 12, 10, col)
    c.poly([(3, 6), (12, 6), (12, 14), (10, 12), (8, 14), (6, 12), (3, 14)], col)
    c.rect(5, 5, 6, 6, INK)
    c.rect(9, 5, 10, 6, INK)


def match(c):
    c.line([(3, 13), (10, 6)], LBROWN, 2)
    c.oval(9, 2, 13, 6, INK)
    c.px(13, 1, GREY)


def hand(c, col=SKIN):
    c.grid(1, 1, [
        "..#.#.#.....",
        ".##.#.#.#...",
        ".##.#.#.#...",
        ".##.#.#.#...",
        ".########...",
        ".########.##",
        ".##########.",
        ".#########..",
        "..#######...",
        "..######....",
        "...#####....",
        "...#####....",
    ], {"#": col})


def ice_cube(c):
    c.rect(2, 3, 13, 14, LBLUE)
    c.rect(3, 4, 6, 6, WHITE)


def pointing(c):
    c.rect(2, 6, 9, 12, SKIN)
    c.rect(9, 6, 14, 7, SKIN)
    c.rect(4, 4, 7, 6, SKIN_D)


def rain_cloud(c):
    cloud(c, GREY)
    for x in (3, 7, 11):
        c.line([(x, 12), (x - 1, 14)], BLUE)


def warning(c, col=RED):
    c.poly([(7, 1), (14, 14), (1, 14)], col)
    c.rect(7, 5, 8, 10, WHITE)
    c.rect(7, 12, 8, 12, WHITE)


def arrow_up(c, col=GREEN, double=False):
    c.poly([(7, 1), (13, 7), (10, 7), (10, 14), (5, 14), (5, 7), (2, 7)], col)
    if double:
        c.line([(2, 10), (5, 7)], LGREEN)


def sparkle(c, col=GOLD):
    c.poly([(7, 0), (9, 6), (15, 7), (9, 9), (7, 15), (6, 9), (0, 7), (6, 6)], col)


def lightbulb(c):
    c.oval(3, 1, 12, 10, YELLOW)
    c.rect(5, 10, 10, 13, LGREY)
    c.px(5, 4, WHITE)


def skin_dots(c):
    c.oval(1, 2, 14, 13, SKIN)
    for x, y in ((4, 5), (8, 4), (10, 8), (5, 9), (8, 11)):
        c.rect(x, y, x + 1, y + 1, RED)


def lonely(c):
    person(c, GREY)


def pause_sign(c):
    c.oval(1, 1, 14, 14, WHITE)
    c.rect(5, 4, 6, 11, GREEN)
    c.rect(9, 4, 10, 11, GREEN)


def coffee(c):
    teacup(c, BROWN)


def figure_in_circle(c):
    c.oval(0, 0, 15, 15, GREY)
    c.oval(2, 2, 13, 13, (0, 0, 0, 0))
    person(c, LGREY)


def falling(c):
    c.oval(9, 9, 14, 14, SKIN)
    c.line([(3, 3), (9, 9)], BLUE, 3)
    c.line([(2, 8), (6, 6)], BLUE, 2)


def mud(c):
    for x, y in ((4, 9), (9, 5), (11, 10)):
        c.oval(x - 1, y - 1, x + 1, y + 1, BROWN)


def cobweb(c):
    c.line([(1, 1), (14, 14)], LGREY)
    c.line([(1, 1), (14, 6)], LGREY)
    c.line([(1, 1), (6, 14)], LGREY)
    c.line([(5, 3), (3, 5)], LGREY)
    c.line([(9, 4), (4, 9)], LGREY)


def tension_gauge(c):
    """Шкала напряжения: полукруг зелёный→красный, стрелка в красной зоне."""
    c.d.pieslice([1, 3, 14, 16], 180, 240, fill=rgba(GREEN))
    c.d.pieslice([1, 3, 14, 16], 240, 300, fill=rgba(YELLOW))
    c.d.pieslice([1, 3, 14, 16], 300, 360, fill=rgba(RED))
    c.oval(5, 7, 10, 12, CREAM)
    c.line([(7, 9), (12, 5)], INK, 1)
    c.rect(7, 9, 8, 10, INK)


def bed_cross(c):
    bed(c)
    c.rect(10, 1, 11, 5, RED)
    c.rect(9, 2, 12, 3, RED)


def mishap_sheet_icon(index):
    sheet = Image.open("assets/Items/mishapBuffIcons.png").convert("RGBA")
    return sheet.crop((index * 16, 0, index * 16 + 16, 16))


# --- рецепты: id баффа → функция рисования -------------------------------------
def R(*steps):
    """Собрать иконку: шаги — функции(c) для символа, значки задаются через ('badge', fn, args)."""
    def build():
        c = Icon()
        badges = []
        for step in steps:
            if isinstance(step, tuple) and step and step[0] == "badge":
                badges.append(step[1:])
            else:
                step(c)
        shade_and_outline(c.img)
        for fn, *args in badges:
            outlined_badge(c, lambda layer, fn=fn, args=args: fn(layer, *args))
        return c.img
    return build


def B(fn, *args):
    return ("badge", fn, *args)


def phase(n, total):
    return B(b_level, n, total)


def stress_cure(base):
    return R(*base, B(b_plus))


STRESS_BASE = {
    "Tired": (droopy_eye,),
    "Lonely": (lonely,),
    "Thunder": (cloud, lambda c: bolt(c)),
    "Hunger": (plate,),
    "Overwork": (hoe, lambda c: b_drop(c, LBLUE)),
    "NoSleep": (moon_crescent, lambda c: eye(c, PURPLE)),
    "TooCold": (snowflake,),
    "Darkness": (lambda c: dark_orb(c, 1),),
    "Social": (bubbles,),
    "BadDream": (lambda c: cloud(c, LPURP), lambda c: moon_crescent(c, GOLD)),
    "AnxietyWave": (wave,),
    "Breakdown": (lambda c: heart(c, DGREY), crack),
    "Collapse": (falling,),
    "Despair": (rain_cloud,),
    "Panic": (lambda c: heart(c, RED), lambda c: bolt(c, WHITE)),
    "Critical": (warning,),
    "Exhaustion": (lambda c: battery(c, 0.15, RED),),
    "PhysicalDepletion": (lambda c: battery(c, 0.35, ORANGE), crack),
    "NightTerror": (lambda c: ghost(c, LPURP),),
    "Burnout": (match,),
    "MentalBreakdown": (brain, crack),
    "PanicCollapse": (lambda c: heart(c, PINK), lambda c: wave(c, DRED)),
    "DespairCollapse": (lambda c: heart(c, GREY), crack),
    "PanicBreakdown": (lambda c: warning(c, ORANGE),),
    "ParanoidCollapse": (lambda c: dark_orb(c, 3, DPURP),),
    "CriticalExhaustion": (lambda c: battery(c, 0, RED),),
    "Numbness": (lambda c: hand(c, LGREY),),
    "ShadowParanoia": (lambda c: person(c, NIGHT),),
    "FreezeResponse": (ice_cube, lambda c: person(c, BLUE)),
    "Isolation": (figure_in_circle,),
    "Criticism": (pointing,),
    "MentalFatigue": (lambda c: brain(c, LPURP),),
}


def build_recipes():
    r = {}

    # --- стресс-дебаффы
    simple_stress = {
        "buffStressTired": "Tired", "buffStressLonely": "Lonely", "buffStressThunder": "Thunder",
        "buffStressHunger": "Hunger", "buffStressOverwork": "Overwork", "buffStressNoSleep": "NoSleep",
        "buffStressTooCold": "TooCold", "buffStressSocial": "Social", "buffStressBadDream": "BadDream",
        "buffStressAnxietyWave": "AnxietyWave", "buffStressBreakdown": "Breakdown",
        "buffStressCollapse": "Collapse", "buffStressDespair": "Despair", "buffStressPanic": "Panic",
        "buffStressCritical": "Critical", "buffStressExhaustion": "Exhaustion",
        "buffStressPhysicalDepletion": "PhysicalDepletion", "buffStressNightTerror": "NightTerror",
        "buffStressBurnout": "Burnout", "buffStressMentalBreakdown": "MentalBreakdown",
        "buffStressPanicCollapse": "PanicCollapse", "buffStressDespairCollapse": "DespairCollapse",
        "buffStressPanicBreakdown": "PanicBreakdown", "buffStressParanoidCollapse": "ParanoidCollapse",
        "buffStressCriticalExhaustion": "CriticalExhaustion", "buffStressNumbness": "Numbness",
        "buffStressShadowParanoia": "ShadowParanoia", "buffStressFreezeResponse": "FreezeResponse",
        "buffStressIsolation": "Isolation", "buffStressCriticism": "Criticism",
        "buffStressMentalFatigue": "MentalFatigue",
    }
    for buff_id, key in simple_stress.items():
        r[buff_id] = R(*STRESS_BASE[key])

    r["buffStressDarkness"] = R(lambda c: dark_orb(c, 1))
    r["buffDarknessLevel1"] = R(lambda c: dark_orb(c, 1), phase(1, 3))
    r["buffDarknessLevel2"] = R(lambda c: dark_orb(c, 2), phase(2, 3))
    r["buffDarknessLevel3"] = R(lambda c: dark_orb(c, 3, INK), B(b_bang, RED))
    r["buffSleepDeprivation"] = R(droopy_eye, B(b_clock))
    r["buffDimLight"] = R(lambda c: candle(c, 0.4))
    r["buffHarveyLantern"] = R(lantern)
    r["buffDarknessOvercome"] = R(sunrise)
    r["buffStressLoadTier"] = R(tension_gauge)

    # --- лечение стресса у Харви: символ проблемы + зелёный плюс
    cure_map = {
        "Breakdown": "Breakdown", "Collapse": "Collapse", "Numbness": "Numbness", "Despair": "Despair",
        "Critical": "Critical", "Tired": "Tired", "Lonely": "Lonely", "Thunder": "Thunder",
        "Hunger": "Hunger", "Overwork": "Overwork", "NoSleep": "NoSleep", "TooCold": "TooCold",
        "Social": "Social", "Darkness": "Darkness", "Criticism": "Criticism", "BadDream": "BadDream",
        "Panic": "Panic", "AnxietyWave": "AnxietyWave", "MentalFatigue": "MentalFatigue",
        "ShadowParanoia": "ShadowParanoia", "FreezeResponse": "FreezeResponse", "Isolation": "Isolation",
    }
    for suffix, key in cure_map.items():
        r[f"buffHarveyTreatment{suffix}"] = stress_cure(STRESS_BASE[key])

    r["buffStressImmunity"] = R(lambda c: shield(c, TEAL), B(b_plus))
    r["buffStressRecovery"] = R(arrow_up)
    r["buffStressRecoveryAdvanced"] = R(lambda c: arrow_up(c, GREEN, True), B(b_star))
    r["buffStressRecoveryGlow"] = R(sparkle)
    r["buffRestingAtHome"] = R(house, B(b_z))
    r["buffCalmingAtHospitalWithHarvey"] = R(clinic, B(b_heart))
    r["buffOverworkBreak"] = R(pause_sign)
    r["buffLightAndSafe"] = R(lightbulb)
    r["buffTraumaHealing"] = R(lambda c: heart(c, PINK), lambda c: band(c), B(b_star))

    # --- травмы (базовые дебаффы)
    r["buffHurt"] = R(plaster)
    r["buffBadlyHurt"] = R(lambda c: heart(c, RED), crack, B(b_bang, RED))
    r["buffPainFlare"] = R(lambda c: bolt(c, RED))
    r["buffFarmerExhausted"] = R(lambda c: battery(c, 0.1, RED), B(b_z))
    r["buffSleepy"] = R(zzz)
    r["buffBruisedRibs"] = R(ribs, bruise)
    r["buffSprainedAnkle"] = R(foot, swelling)
    r["buffBackStrain"] = R(spine, B(b_bang, RED))
    r["buffDeepCuts"] = R(blade, blood)
    r["buffBurnWounds"] = R(flame)
    r["buffTornMuscles"] = R(arm, tear)
    r["buffConcussion"] = R(head, stars_over)
    r["buffFracturedBone"] = R(bone, crack)
    r["buffShrapnelWounds"] = R(shards)
    r["buffInfectedWound"] = R(germ)
    r["buffAlcoholPoisoning"] = R(bottle, B(b_cross))
    r["buffSurgicalWound"] = R(wound_line, stitches)
    r["buffTooCold"] = R(lambda c: thermometer(c, BLUE))
    r["buffCold"] = R(scarf)

    # --- осложнения
    r["HarveyMod_WetBandage"] = R(bandage_roll, B(b_drop))
    r["HarveyMod_DirtyWound"] = R(plaster, mud)
    r["HarveyMod_Neglect"] = R(cobweb, lambda c: plaster(c, GREY))
    r["HarveyMod_MineForbidden"] = R(pickaxe, B(b_cross))
    r["HarveyMod_MineRestricted"] = R(pickaxe, B(b_bang))
    r["HarveyMod_PainFlare"] = R(cloud, lambda c: bolt(c, RED))
    r["HarveyMod_AllergicRash"] = R(skin_dots)
    r["HarveyMod_WetStitches"] = R(wound_line, stitches, B(b_drop))
    r["HarveyMod_ImpairedMobility"] = R(crutch)
    r["HarveyMod_MuscleAtrophy"] = R(thin_arm, B(b_down))
    r["HarveyMod_BreathingDifficulty"] = R(lungs)
    r["HarveyMod_Sepsis"] = R(lambda c: droplet(c, RED), B(b_bang, RED))

    # --- фазы лечения: символ травмы в состоянии лечения + точки фазы
    r["HarveyMod_FracturedBone_Acute"] = R(bone, crack, phase(1, 3))
    r["HarveyMod_FracturedBone_Cast"] = R(cast, phase(2, 3))
    r["HarveyMod_FracturedBone_Recovery"] = R(bone, lambda c: c.rect(6, 7, 9, 8, WHITE), phase(3, 3))
    r["HarveyMod_Concussion_Acute"] = R(head, stars_over, phase(1, 3))
    r["HarveyMod_Concussion_Rest"] = R(pillow, head, B(b_z), phase(2, 3))
    r["HarveyMod_Concussion_Limited"] = R(head, headband, phase(3, 3))
    r["HarveyMod_Shrapnel_Surgery"] = R(scalpel, phase(1, 3))
    r["HarveyMod_Shrapnel_Healing"] = R(wound_line, stitches, lambda c: c.px(3, 5, LGREY), phase(2, 3))
    r["HarveyMod_Shrapnel_Recovery"] = R(lambda c: wound_line(c, PINK), phase(3, 3))
    r["HarveyMod_TornMuscles_Acute"] = R(arm, tear, phase(1, 3))
    r["HarveyMod_TornMuscles_Healing"] = R(arm, tape, phase(2, 3))
    r["HarveyMod_TornMuscles_Rehab"] = R(dumbbell, phase(3, 3))
    r["HarveyMod_SprainedAnkle_Acute"] = R(foot, swelling, phase(1, 2))
    r["HarveyMod_SprainedAnkle_Recovery"] = R(foot, brace, phase(2, 2))
    r["HarveyMod_BruisedRibs_Acute"] = R(ribs, bruise, phase(1, 2))
    r["HarveyMod_BruisedRibs_Healing"] = R(ribs, band, phase(2, 2))
    r["HarveyMod_DeepCuts_Acute"] = R(wound_line, stitches, lambda c: c.px(12, 5, RED), phase(1, 3))
    r["HarveyMod_DeepCuts_Healing"] = R(plaster, phase(2, 3))
    r["HarveyMod_DeepCuts_Recovery"] = R(lambda c: wound_line(c, PINK), B(b_up), phase(3, 3))
    r["HarveyMod_BurnWounds_Acute"] = R(skin_patch, lambda c: flame(c, RED), phase(1, 2))
    r["HarveyMod_BurnWounds_Healing"] = R(skin_patch, gel, phase(2, 2))
    r["HarveyMod_InfectedWound_Acute"] = R(lambda c: germ(c, LGREEN), B(b_bang, RED), phase(1, 2))
    r["HarveyMod_InfectedWound_Treatment"] = R(lambda c: germ(c, LGREEN), lambda c: capsule(c), phase(2, 2))
    r["HarveyMod_BackStrain_Acute"] = R(spine, lambda c: c.rect(5, 7, 10, 8, RED), phase(1, 2))
    r["HarveyMod_BackStrain_Recovery"] = R(spine, heat_pad, phase(2, 2))
    r["HarveyMod_BadlyHurt_Acute"] = R(lambda c: heart(c, RED), crack, phase(1, 3))
    r["HarveyMod_BadlyHurt_Healing"] = R(lambda c: heart(c, RED), band, phase(2, 3))
    r["HarveyMod_BadlyHurt_Recovery"] = R(lambda c: heart(c, PINK), B(b_up), phase(3, 3))
    r["HarveyMod_Cold_Acute"] = R(lambda c: thermometer(c, RED), phase(1, 2))
    r["HarveyMod_Cold_Recovery"] = R(scarf, phase(2, 2))

    # --- лечебные баффы Харви
    r["buffHarveyTreatment"] = R(med_cross)
    r["buffHarveyIntensiveCare"] = R(iv_bag)
    r["HarveyMod_BadlyHurt_OutpatientCare"] = R(clipboard, B(b_heart))
    r["buffHarveyHealing"] = R(leaf, B(b_plus))
    r["buffHarveyRecovery"] = R(lambda c: heart(c, PINK), B(b_up))
    r["buffHarveyProtection"] = R(shield, B(b_plus, WHITE))
    r["buffAntibioticsTreatment"] = R(capsule)
    r["buffHarveyDropper"] = R(dropper)
    r["buffTeracitin"] = R(vial)
    r["buffCalmTeaEffect"] = R(teacup)
    r["buffStrictSupervision"] = R(eye)
    r["buffEmergencySupervision"] = R(siren)
    r["buffConstantSupervision"] = R(eye, B(b_clock))
    r["buffForcedSedation"] = R(syringe, B(b_z))
    r["buffPostSurgicalCare"] = R(wound_line, stitches, B(b_heart))
    r["buffHarveyCare"] = R(glasses, B(b_heart, RED))

    # --- назначения и статусы
    r["HarveyMod_Prescription_Rest"] = R(rx, B(b_z))
    r["HarveyMod_Prescription_NoMine"] = R(rx, B(b_cross))
    r["HarveyMod_Prescription_KeepDry"] = R(umbrella)
    r["HarveyMod_Prescription_LightWork"] = R(feather)
    r["HarveyMod_Prescription_Checkup"] = R(stethoscope)
    r["HarveyMod_Hospitalized"] = R(bed_cross)
    r["HarveyMod_DoctorVisitNeeded"] = R(clinic, B(b_bang))
    r["buffHarveyRehab"] = R(lambda c: person(c, GREEN), B(b_up))
    r["HarveyMod_SelfCare"] = R(house, B(b_heart))
    r["HarveyMod_CleanBandage"] = R(bandage_roll)
    r["HarveyMod_WarmTea"] = R(lambda c: teacup(c, ORANGE))

    # --- мелкие неприятности и закалка: нарисованы вручную
    for i, buff_id in enumerate(["HarveyMod_Resilience", "HarveyMod_Splinter", "HarveyMod_BeeSting",
                                 "HarveyMod_Sunstroke", "HarveyMod_Frostbite"]):
        r[buff_id] = (lambda i=i: mishap_sheet_icon(i))

    return {k: v for k, v in r.items()}


# --- сборка листа и обновление JSON --------------------------------------------
STRING = re.compile(r'"(?:[^"\\]|\\.)*"', re.S)


def all_buff_ids():
    ids = []
    for path in sorted(glob.glob("assets/Code/*.json")):
        s = open(path, encoding="utf-8-sig").read()
        s = re.sub(r"^\s*//.*$", "", s, flags=re.M)
        s = STRING.sub(lambda m: m.group(0).replace("\n", "\\n").replace("\r", ""), s)
        s = re.sub(r",(\s*[}\]])", r"\1", s)
        data = json.loads(s)
        for ch in data.get("Changes", []):
            if ch.get("Target") == "Data/Buffs":
                ids.extend((path, k) for k, v in ch["Entries"].items() if isinstance(v, dict))
    return ids


def main():
    recipes = build_recipes()
    buffs = all_buff_ids()
    missing = [b for _, b in buffs if b not in recipes]
    if missing:
        raise SystemExit(f"Нет иконки для: {missing}")

    order = [b for _, b in buffs]
    rows = (len(order) + COLUMNS - 1) // COLUMNS
    sheet = Image.new("RGBA", (COLUMNS * S, rows * S), (0, 0, 0, 0))
    index = {}
    seen = {}
    for i, buff_id in enumerate(order):
        icon = recipes[buff_id]()
        key = icon.tobytes()
        if key in seen:
            raise SystemExit(f"Иконки совпадают: {buff_id} и {seen[key]}")
        seen[key] = buff_id
        sheet.paste(icon, ((i % COLUMNS) * S, (i // COLUMNS) * S))
        index[buff_id] = i

    sheet.save("assets/Tilesheets/harveyBuffIcons.png")
    with open("assets/Tilesheets/harveyBuffIcons.json", "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=2)
    print(f"{len(order)} иконок -> assets/Tilesheets/harveyBuffIcons.png")

    if "--preview" in sys.argv:
        scale = 4
        cell_w, cell_h = 240, S * scale + 4
        prev = Image.new("RGBA", (cell_w * 6, cell_h * ((len(order) + 5) // 6)), (118, 118, 138, 255))
        draw = ImageDraw.Draw(prev)
        for i, buff_id in enumerate(order):
            x, y = (i % 6) * cell_w, (i // 6) * cell_h
            icon = sheet.crop(((i % COLUMNS) * S, (i // COLUMNS) * S, (i % COLUMNS) * S + S, (i // COLUMNS) * S + S))
            prev.alpha_composite(icon.resize((S * scale, S * scale), Image.NEAREST), (x + 2, y + 2))
            draw.text((x + S * scale + 6, y + 24), buff_id.replace("HarveyMod_", "HM_"), fill=(255, 255, 255, 255))
        prev.save("scripts/_preview_buff_icons.png")

    if "--apply" in sys.argv:
        apply_to_json(buffs, index)


def apply_to_json(buffs, index):
    by_file = {}
    for path, buff_id in buffs:
        by_file.setdefault(path, []).append(buff_id)

    for path, ids in by_file.items():
        text = open(path, encoding="utf-8-sig").read()
        for buff_id in ids:
            start = re.search(r'"' + re.escape(buff_id) + r'"\s*:\s*\{', text)
            if not start:
                raise SystemExit(f"{path}: не найден {buff_id}")
            tex = re.compile(r'("IconTexture"\s*:\s*)("[^"]*"|null)')
            idx = re.compile(r'("IconSpriteIndex"\s*:\s*)(-?\d+)')
            m_tex = tex.search(text, start.end())
            m_idx = idx.search(text, start.end())
            text = text[:m_idx.start()] + m_idx.group(1) + str(index[buff_id]) + text[m_idx.end():]
            m_tex = tex.search(text, start.end())
            text = text[:m_tex.start()] + m_tex.group(1) + f'"{TEXTURE}"' + text[m_tex.end():]
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"обновлён {path}: {len(ids)}")


if __name__ == "__main__":
    main()

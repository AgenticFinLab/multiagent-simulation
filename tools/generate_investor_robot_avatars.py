from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
IMAGE_ROOT = ROOT / "examples" / "AGENT_POOL" / "agent_images"
SOURCE_MAP_PATH = ROOT / "investor_agent_images" / "agent_avatar_map.csv"
PNG_DIR = IMAGE_ROOT / "png"
CATALOG_PATH = IMAGE_ROOT / "agent_avatar_map.json"
SIZE = 512
OUTLINE = "#17233b"
FACE = "#f7f8fb"
FACE_SHADE = "#dce5ef"
BLUE = "#2f8af5"
CYAN = "#5dd9ff"
GOLD = "#ffd24d"
ORANGE = "#ff8a2a"
RED = "#ef4444"
GREEN = "#20c997"
PURPLE = "#7654f5"


THEMES = {
    "AlgorithmicHighFrequencyTrader": ("#2f91ff", "#22d3ee", "terminal"),
    "AnchoringBiasInvestor": ("#3b82f6", "#d5aa48", "anchor"),
    "Arbitrageur": ("#d7b65b", "#38bdf8", "scales"),
    "BankingCreditAgent": ("#2f91ff", "#93c5fd", "bank"),
    "ContrarianReversalInvestor": ("#ff8a2a", "#ffd166", "reverse"),
    "CryptoDeFiAgent": ("#1e8fff", "#22c55e", "crypto"),
    "FramingEffectTrader": ("#d7b65b", "#60a5fa", "frame"),
    "HerdingCascadeAgent": ("#2f91ff", "#8b5cf6", "network"),
    "InformedOpportunisticTrader": ("#d7b65b", "#38bdf8", "eye"),
    "LeveragedFundInvestor": ("#ff8a2a", "#facc15", "lever"),
    "LossAversionDispositionInvestor": ("#fb7185", "#ffd166", "loss"),
    "MacroCurrencySovereignTrader": ("#2f91ff", "#22d3ee", "globe"),
    "MarketMakerLiquidityAgent": ("#d7b65b", "#34d399", "orderbook"),
    "MentalAccountingSunkCostTrader": ("#d7b65b", "#f59e0b", "ledger"),
    "MomentumTrendTrader": ("#2f91ff", "#facc15", "trend"),
    "NoiseTrader": ("#94a3b8", "#38bdf8", "noise"),
    "OverconfidenceAndRepresentativenessTrader": ("#ff8a2a", "#ef4444", "burst"),
    "PanicForcedSeller": ("#fb7185", "#ef4444", "panic"),
    "PassiveInstitutionalLongHorizonInvestor": ("#d7b65b", "#93c5fd", "institution"),
    "PolicyBackstopAgent": ("#2f91ff", "#facc15", "shield"),
    "RationalAnalystInvestor": ("#d7b65b", "#38bdf8", "magnifier"),
    "RebalancingStatusQuoInvestor": ("#2f91ff", "#8b5cf6", "rebalance"),
    "RetailCoordinatedTrader": ("#ff8a2a", "#ffd166", "crowd"),
    "RiskManagementInvestor": ("#2f91ff", "#22c55e", "risk"),
    "SentimentNarrativeTrader": ("#ff8a2a", "#ec4899", "speech"),
    "ShortSellerAndShortVolTrader": ("#fb7185", "#facc15", "short"),
    "SocialInformationAgents": ("#2f91ff", "#8b5cf6", "social"),
    "ValueFundamentalInvestor": ("#d7b65b", "#22c55e", "value"),
    "VolatilityProductTrader": ("#2f91ff", "#22d3ee", "volatility"),
}

LABELS = {
    "AlgorithmicHighFrequencyTrader": "量化型投资者",
    "AnchoringBiasInvestor": "固守型投资者",
    "Arbitrageur": "套利型投资者",
    "BankingCreditAgent": "信贷型投资者",
    "ContrarianReversalInvestor": "逆向型投资者",
    "CryptoDeFiAgent": "数字资产型投资者",
    "FramingEffectTrader": "主题型投资者",
    "HerdingCascadeAgent": "跟风型投资者",
    "InformedOpportunisticTrader": "信息型投资者",
    "LeveragedFundInvestor": "激进型投资者",
    "LossAversionDispositionInvestor": "保守型投资者",
    "MacroCurrencySovereignTrader": "宏观型投资者",
    "MarketMakerLiquidityAgent": "做市型投资者",
    "MentalAccountingSunkCostTrader": "谨慎型投资者",
    "MomentumTrendTrader": "趋势型投资者",
    "NoiseTrader": "随性型投资者",
    "OverconfidenceAndRepresentativenessTrader": "冒进型投资者",
    "PanicForcedSeller": "恐慌型投资者",
    "PassiveInstitutionalLongHorizonInvestor": "稳健型投资者",
    "PolicyBackstopAgent": "防御型投资者",
    "RationalAnalystInvestor": "研究型投资者",
    "RebalancingStatusQuoInvestor": "平衡型投资者",
    "RetailCoordinatedTrader": "抱团型投资者",
    "RiskManagementInvestor": "风控型投资者",
    "SentimentNarrativeTrader": "情绪型投资者",
    "ShortSellerAndShortVolTrader": "空头型投资者",
    "SocialInformationAgents": "社交型投资者",
    "ValueFundamentalInvestor": "价值型投资者",
    "VolatilityProductTrader": "波动型投资者",
}

FONT_CANDIDATES = [
    Path("C:/Windows/Fonts/NotoSansSC-VF.ttf"),
    Path("C:/Windows/Fonts/simhei.ttf"),
    Path("C:/Windows/Fonts/msyh.ttc"),
    Path("C:/Windows/Fonts/Dengb.ttf"),
]


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def lerp(a: int, b: int, t: float) -> int:
    return round(a + (b - a) * t)


def make_bg(primary: str, accent: str) -> Image.Image:
    scale = 2
    small_size = SIZE // scale
    img = Image.new("RGBA", (small_size, small_size), (255, 255, 255, 0))
    px = img.load()
    c1 = hex_to_rgb(primary)
    c2 = hex_to_rgb(accent)
    center_x = small_size / 2
    center_y = small_size * 0.43
    radius = small_size * 0.405
    for y in range(small_size):
        for x in range(small_size):
            dx = x - center_x
            dy = y - center_y
            dist = math.hypot(dx, dy)
            if dist <= radius:
                t = min(1, max(0, (x * 0.45 + y * 0.55) / small_size))
                rgb = tuple(lerp(c1[i], c2[i], t) for i in range(3))
                shade = 1 - min(0.18, dist / radius * 0.18)
                px[x, y] = tuple(int(v * shade) for v in rgb) + (255,)
    img = img.resize((SIZE, SIZE), Image.Resampling.BICUBIC)
    glow = Image.new("RGBA", (SIZE, SIZE), (255, 255, 255, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((100, 38, 412, 350), fill=(255, 255, 255, 30))
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(26)))
    return img


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in FONT_CANDIDATES:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def round_rect(d: ImageDraw.ImageDraw, box, radius, fill, outline=OUTLINE, width=7):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def line(d: ImageDraw.ImageDraw, pts, fill=OUTLINE, width=8, joint="curve"):
    d.line(pts, fill=fill, width=width, joint=joint)


def draw_robot(d: ImageDraw.ImageDraw):
    # Antennas and ears.
    line(d, [(164, 112), (164, 210)], width=7)
    line(d, [(348, 112), (348, 210)], width=7)
    d.ellipse((150, 95, 178, 123), fill=CYAN, outline=OUTLINE, width=6)
    d.ellipse((334, 95, 362, 123), fill=CYAN, outline=OUTLINE, width=6)
    round_rect(d, (102, 190, 146, 282), 18, "#5ca7ff")
    round_rect(d, (366, 190, 410, 282), 18, "#5ca7ff")

    # Body.
    round_rect(d, (169, 338, 343, 500), 40, "#eef3f8")
    d.pieslice((180, 356, 332, 508), 180, 360, fill="#d7e4ef")
    d.ellipse((216, 370, 296, 450), fill="#56c7f4", outline=OUTLINE, width=7)
    d.ellipse((236, 390, 276, 430), fill="#2f91ff", outline="#1773ba", width=4)

    # Head and visor.
    round_rect(d, (104, 132, 408, 340), 84, FACE)
    d.arc((160, 137, 352, 202), 35, 145, fill="#aeb9c6", width=5)
    round_rect(d, (152, 186, 360, 282), 36, "#1d2943")
    d.ellipse((199, 213, 226, 252), fill=CYAN)
    d.ellipse((286, 213, 313, 252), fill=CYAN)
    d.rounded_rectangle((230, 261, 282, 271), radius=5, fill=CYAN)
    d.arc((122, 139, 392, 330), 20, 160, fill=(255, 255, 255), width=5)


def draw_compact_robot(d: ImageDraw.ImageDraw):
    line(d, [(168, 70), (168, 138)], width=6)
    line(d, [(344, 70), (344, 138)], width=6)
    d.ellipse((156, 58, 180, 82), fill=CYAN, outline=OUTLINE, width=5)
    d.ellipse((332, 58, 356, 82), fill=CYAN, outline=OUTLINE, width=5)
    round_rect(d, (104, 139, 145, 222), 17, "#5ca7ff", width=6)
    round_rect(d, (367, 139, 408, 222), 17, "#5ca7ff", width=6)
    round_rect(d, (116, 82, 396, 266), 76, FACE)
    d.arc((177, 85, 335, 143), 35, 145, fill="#aeb9c6", width=5)
    round_rect(d, (161, 132, 351, 218), 33, "#1d2943", width=6)
    d.ellipse((207, 158, 232, 195), fill=CYAN)
    d.ellipse((280, 158, 305, 195), fill=CYAN)
    d.rounded_rectangle((232, 204, 280, 213), radius=5, fill=CYAN)
    round_rect(d, (197, 246, 315, 325), 28, "#eef3f8", width=6)
    d.ellipse((229, 260, 283, 314), fill="#56c7f4", outline=OUTLINE, width=6)


def paste_scaled_region(
    base: Image.Image,
    layer: Image.Image,
    crop_box: tuple[int, int, int, int],
    scale: float,
    top: int,
    opacity: float = 1.0,
    blur: float = 0.0,
) -> None:
    region = layer.crop(crop_box)
    width = int(region.width * scale)
    height = int(region.height * scale)
    region = region.resize((width, height), Image.Resampling.LANCZOS)
    if blur:
        region = region.filter(ImageFilter.GaussianBlur(blur))
    if opacity < 1.0:
        alpha = region.getchannel("A").point(lambda value: int(value * opacity))
        region.putalpha(alpha)
    left = (SIZE - width) // 2
    base.alpha_composite(region, (left, top))


def draw_label(d: ImageDraw.ImageDraw, agent_type: str):
    label = LABELS.get(agent_type, agent_type)
    kind = label.removesuffix("投资者")
    kind_font = font(34 if len(kind) <= 4 else 28)
    suffix_font = font(24)
    d.rounded_rectangle((92, 418, 420, 502), radius=24, fill=(255, 255, 255, 245), outline="#e5e7eb", width=3)
    for text, text_font, y in ((kind, kind_font, 427), ("投资者", suffix_font, 467)):
        box = d.textbbox((0, 0), text, font=text_font)
        text_w = box[2] - box[0]
        x = (SIZE - text_w) / 2
        d.text((x, y), text, fill="#0f172a", font=text_font)


def draw_panel(d, box, fill="#1d2943"):
    round_rect(d, box, 14, fill, width=6)
    x1, y1, x2, y2 = box
    d.rectangle((x1 + 14, y2 - 30, x2 - 14, y2 - 15), fill="#91a4bd")
    d.rectangle((x1 + 55, y2 - 16, x2 - 55, y2 + 3), fill="#d6e3ef", outline=OUTLINE, width=4)


def draw_lightning(d, cx=256, cy=250, scale=1.0, fill=GOLD):
    pts = [
        (cx + int(-16 * scale), cy + int(-74 * scale)),
        (cx + int(36 * scale), cy + int(-74 * scale)),
        (cx + int(12 * scale), cy + int(-12 * scale)),
        (cx + int(52 * scale), cy + int(-12 * scale)),
        (cx + int(-19 * scale), cy + int(83 * scale)),
        (cx + int(2 * scale), cy + int(12 * scale)),
        (cx + int(-42 * scale), cy + int(12 * scale)),
    ]
    d.polygon(pts, fill=fill, outline=OUTLINE)


def draw_icon(d: ImageDraw.ImageDraw, motif: str):
    if motif == "terminal":
        draw_panel(d, (96, 329, 416, 444))
        for i, y in enumerate([356, 382, 408]):
            d.text((126, y - 8), ">", fill=CYAN)
            line(d, [(158, y), (230 + i * 24, y)], fill=[GREEN, GOLD, "#ef4444"][i], width=5)
        line(d, [(334, 350), (374, 388), (334, 426)], fill=CYAN, width=6)
    elif motif == "anchor":
        line(d, [(256, 318), (256, 432)], width=8)
        d.ellipse((236, 298, 276, 338), outline=PURPLE, width=8)
        line(d, [(206, 385), (306, 385)], width=8)
        d.arc((174, 353, 338, 480), 15, 165, fill=PURPLE, width=9)
        line(d, [(187, 398), (165, 369)], fill=PURPLE, width=8)
        line(d, [(325, 398), (347, 369)], fill=PURPLE, width=8)
    elif motif == "scales":
        line(d, [(256, 292), (256, 432)], width=7)
        line(d, [(178, 330), (334, 330)], width=7)
        for cx in [190, 322]:
            line(d, [(cx, 330), (cx - 36, 391), (cx + 36, 391), (cx, 330)], fill="#67e8f9", width=5)
        d.rectangle((212, 430, 300, 444), fill=OUTLINE)
    elif motif == "bank" or motif == "institution":
        d.polygon([(146, 352), (256, 294), (366, 352)], fill="#dce8f5", outline=OUTLINE)
        d.rectangle((164, 352, 348, 374), fill="#f8fafc", outline=OUTLINE, width=5)
        for x in [184, 230, 276, 322]:
            d.rectangle((x, 374, x + 22, 438), fill="#eef3f8", outline=OUTLINE, width=5)
        d.rectangle((150, 438, 362, 458), fill="#dce8f5", outline=OUTLINE, width=5)
    elif motif == "reverse":
        line(d, [(174, 352), (320, 352), (287, 322)], fill=GOLD, width=10)
        line(d, [(338, 404), (192, 404), (225, 434)], fill=ORANGE, width=10)
    elif motif == "crypto":
        d.regular_polygon((256, 386, 76), n_sides=6, rotation=math.pi / 6, fill="#dffaf0", outline=OUTLINE)
        d.text((232, 356), "De", fill="#16a34a")
        d.text((228, 394), "Fi", fill="#2f8af5")
    elif motif == "frame":
        round_rect(d, (148, 326, 364, 450), 16, "#f8fafc")
        for y in [354, 384, 414]:
            line(d, [(180, y), (324, y)], fill="#b8860b", width=6)
    elif motif in {"network", "social"}:
        pts = [(172, 352), (252, 322), (340, 356), (220, 428), (332, 430)]
        for a, b in [(0, 1), (1, 2), (1, 3), (2, 4), (3, 4)]:
            line(d, [pts[a], pts[b]], fill="#9bbcf9", width=5)
        for i, p in enumerate(pts):
            d.ellipse((p[0] - 15, p[1] - 15, p[0] + 15, p[1] + 15), fill=[CYAN, GOLD, PURPLE, GREEN, ORANGE][i], outline=OUTLINE, width=5)
        if motif == "social":
            round_rect(d, (104, 316, 194, 372), 16, "#ffffff", width=5)
            round_rect(d, (318, 310, 414, 370), 16, "#ffffff", width=5)
    elif motif == "eye":
        d.ellipse((151, 333, 361, 439), outline=OUTLINE, width=8)
        d.ellipse((218, 337, 294, 413), fill=CYAN, outline=OUTLINE, width=7)
        d.ellipse((242, 361, 270, 389), fill="#1d2943")
    elif motif == "lever":
        line(d, [(146, 418), (366, 342)], fill=GOLD, width=12)
        d.ellipse((128, 398, 172, 442), fill=ORANGE, outline=OUTLINE, width=5)
        d.ellipse((340, 318, 384, 362), fill=ORANGE, outline=OUTLINE, width=5)
        line(d, [(256, 384), (256, 456)], width=8)
    elif motif == "loss":
        draw_panel(d, (104, 340, 408, 450))
        line(d, [(130, 380), (188, 380), (222, 420), (268, 392), (310, 431), (380, 431)], fill="#fb7185", width=7)
    elif motif == "globe":
        d.ellipse((165, 306, 347, 488), fill="#dff6ff", outline=OUTLINE, width=7)
        line(d, [(165, 397), (347, 397)], fill="#147aa1", width=5)
        d.arc((200, 306, 312, 488), 90, 270, fill="#147aa1", width=5)
        d.arc((200, 306, 312, 488), -90, 90, fill="#147aa1", width=5)
        d.arc((178, 335, 334, 459), 195, 345, fill="#147aa1", width=5)
    elif motif == "orderbook":
        draw_panel(d, (104, 320, 408, 460))
        for i, y in enumerate([344, 370, 396, 422]):
            d.ellipse((128, y - 7, 142, y + 7), fill=[GREEN, CYAN, GOLD, RED][i])
            line(d, [(160, y), (260 + i * 22, y)], fill=[GREEN, CYAN, GOLD, RED][i], width=6)
    elif motif == "ledger":
        round_rect(d, (154, 312, 358, 462), 16, "#ffffff")
        for y in [350, 382, 414]:
            line(d, [(190, y), (322, y)], fill="#b8860b", width=6)
    elif motif == "trend":
        round_rect(d, (126, 336, 386, 456), 16, "#ffffff")
        line(d, [(154, 416), (210, 382), (258, 398), (330, 348)], fill="#2f8af5", width=8)
        line(d, [(330, 348), (322, 385), (358, 364)], fill="#2f8af5", width=8)
    elif motif == "noise":
        draw_panel(d, (104, 322, 408, 456))
        for i in range(36):
            x = 130 + (i * 37) % 246
            y = 345 + (i * 29) % 82
            d.ellipse((x, y, x + 7, y + 7), fill=[CYAN, GOLD, PURPLE, GREEN][i % 4])
        line(d, [(132, 397), (175, 374), (220, 423), (280, 365), (366, 410)], fill="#e5e7eb", width=4)
    elif motif == "burst":
        d.ellipse((218, 320, 294, 396), fill="#fffbeb", outline=OUTLINE, width=6)
        for angle in range(0, 360, 45):
            x1 = 256 + int(math.cos(math.radians(angle)) * 58)
            y1 = 358 + int(math.sin(math.radians(angle)) * 58)
            x2 = 256 + int(math.cos(math.radians(angle)) * 84)
            y2 = 358 + int(math.sin(math.radians(angle)) * 84)
            line(d, [(x1, y1), (x2, y2)], fill=ORANGE, width=6)
        d.polygon([(196, 440), (316, 440), (256, 326)], fill=(255, 210, 77, 75), outline=RED)
    elif motif == "panic":
        d.polygon([(256, 302), (366, 464), (146, 464)], fill="#fff7ed", outline=OUTLINE)
        d.rectangle((247, 352, 265, 418), fill=RED)
        d.ellipse((245, 432, 267, 454), fill=RED)
    elif motif == "shield" or motif == "risk":
        d.polygon([(256, 306), (354, 340), (335, 438), (256, 486), (177, 438), (158, 340)], fill="#dff6ff", outline=OUTLINE)
        if motif == "shield":
            line(d, [(210, 394), (246, 430), (314, 360)], fill=GOLD, width=12)
        else:
            d.arc((194, 356, 318, 480), 205, 335, fill=GREEN, width=10)
            line(d, [(256, 420), (298, 372)], fill=GREEN, width=8)
    elif motif == "magnifier":
        d.ellipse((150, 318, 286, 454), fill="#e0faff", outline=OUTLINE, width=8)
        line(d, [(260, 428), (338, 486)], width=10)
        line(d, [(184, 386), (220, 366), (256, 386)], fill="#2f8af5", width=6)
    elif motif == "rebalance":
        d.arc((148, 322, 364, 464), 205, 340, fill=PURPLE, width=10)
        d.arc((148, 330, 364, 472), 25, 160, fill=CYAN, width=10)
        line(d, [(338, 350), (366, 342), (352, 316)], fill=PURPLE, width=10)
        line(d, [(174, 442), (146, 450), (160, 476)], fill=CYAN, width=10)
    elif motif == "crowd":
        for cx, cy, col in [(206, 374, ORANGE), (256, 350, GOLD), (306, 374, ORANGE)]:
            d.ellipse((cx - 20, cy - 20, cx + 20, cy + 20), fill=col, outline=OUTLINE, width=5)
        d.arc((164, 390, 248, 468), 205, 335, fill=OUTLINE, width=7)
        d.arc((214, 374, 298, 456), 205, 335, fill=OUTLINE, width=7)
        d.arc((264, 390, 348, 468), 205, 335, fill=OUTLINE, width=7)
    elif motif == "speech":
        round_rect(d, (126, 320, 386, 436), 22, "#ffffff")
        d.polygon([(222, 434), (250, 434), (225, 472)], fill="#ffffff", outline=OUTLINE)
        for y in [354, 386]:
            line(d, [(174, y), (334, y)], fill="#ec4899", width=7)
    elif motif == "short":
        round_rect(d, (118, 334, 394, 454), 16, "#ffffff")
        line(d, [(350, 362), (268, 432), (208, 398), (162, 426)], fill=RED, width=9)
        line(d, [(162, 426), (200, 424), (174, 396)], fill=RED, width=9)
    elif motif == "value":
        d.polygon([(256, 306), (362, 374), (256, 484), (150, 374)], fill="#dffaf0", outline=OUTLINE)
        line(d, [(150, 374), (362, 374)], fill="#16a34a", width=5)
        line(d, [(256, 306), (256, 484)], fill="#16a34a", width=5)
        line(d, [(206, 432), (236, 400), (270, 418), (318, 362)], fill=GOLD, width=7)
    elif motif == "volatility":
        draw_panel(d, (104, 330, 408, 452))
        line(d, [(128, 394), (166, 394), (194, 350), (228, 430), (260, 364), (300, 430), (338, 354), (382, 394)], fill=CYAN, width=7)
        draw_lightning(d, 256, 382, 0.65)


def make_avatar(agent_type: str, primary: str, accent: str, motif: str) -> Image.Image:
    img = make_bg(primary, accent)
    shadow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse((96, 382, 416, 420), fill=(0, 0, 0, 34))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, shadow)

    robot_layer = Image.new("RGBA", (SIZE, SIZE), (255, 255, 255, 0))
    draw_compact_robot(ImageDraw.Draw(robot_layer))
    paste_scaled_region(img, robot_layer, (88, 50, 424, 334), 0.52, 34, opacity=0.46, blur=1.25)

    icon_layer = Image.new("RGBA", (SIZE, SIZE), (255, 255, 255, 0))
    draw_icon(ImageDraw.Draw(icon_layer), motif)
    paste_scaled_region(img, icon_layer, (72, 285, 440, 492), 1.18, 172)

    d = ImageDraw.Draw(img)
    draw_label(d, agent_type)
    return img.convert("RGBA")


def main() -> None:
    with SOURCE_MAP_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    catalog = []
    for row in rows:
        agent_type = row["agent_type"]
        primary, accent, motif = THEMES.get(
            agent_type,
            (row.get("primary_color") or BLUE, row.get("accent_color") or CYAN, row.get("visual_motif") or "trend"),
        )
        img = make_avatar(agent_type, primary, accent, motif)
        img.save(PNG_DIR / f"{agent_type}.png", optimize=True)
        catalog.append(
            {
                "agent_type": agent_type,
                "display_name": LABELS.get(agent_type, row.get("display_name") or agent_type),
                "image_path": f"png/{agent_type}.png",
                "png_image_path": f"png/{agent_type}.png",
                "source_profile": f"../ExtractedExampleInvestors/unique/{agent_type}.md",
                "alt_text": f"{LABELS.get(agent_type, agent_type)} avatar",
                "visual_motif": row.get("visual_motif", ""),
                "primary_color": primary,
                "accent_color": accent,
            }
        )
    CATALOG_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"generated {len(rows)} avatars in {PNG_DIR}")
    print(f"wrote catalog {CATALOG_PATH}")


if __name__ == "__main__":
    main()

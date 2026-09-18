"""
통계 차트에서 공통으로 쓰는 색/스타일 모음.
stats.py에서 import해서 사용합니다.
(색약 대비 검증을 거친 팔레트를 그대로 재사용 - 순서를 바꾸지 마세요)
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


# --------------------------------
# 색상 (고정 팔레트 - 순서 유지)
# --------------------------------

INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"
SURFACE = "#fcfcfb"

# 범주형 색 (항상 이 순서로: blue, orange, aqua, yellow, magenta, green, violet, red)
CATEGORICAL = [
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100",
    "#e87ba4", "#008300", "#4a3aa7", "#e34948",
]

SEQ_BLUE = "#2a78d6"

GOOD = "#0ca30c"
CRITICAL = "#d03b3b"


# --------------------------------
# 한글 폰트 적용
# --------------------------------

_KOREAN_FONT_CANDIDATES = [
    "Noto Sans CJK KR", "Noto Sans CJK JP", "Noto Sans KR",
    "Malgun Gothic", "AppleGothic", "NanumGothic", "NanumGothicCoding",
]


def apply_style():
    """matplotlib 기본 스타일 + 한글 폰트를 적용합니다.
    차트를 그리기 전에 한 번 호출하세요."""

    installed = {f.name for f in fm.fontManager.ttflist}

    found_font = None

    for name in _KOREAN_FONT_CANDIDATES:

        if name in installed:

            found_font = name

            break

    if found_font is None:

        print(
            "[안내] 한글을 지원하는 폰트를 찾지 못했습니다. "
            "차트의 한글 라벨이 깨질 수 있어요. "
            "(예: 나눔고딕 설치 후 다시 실행)"
        )

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": [found_font] if found_font else ["DejaVu Sans"],
        "axes.unicode_minus": False,
        "axes.edgecolor": BASELINE,
        "axes.labelcolor": INK_SECONDARY,
        "text.color": INK_PRIMARY,
        "xtick.color": INK_MUTED,
        "ytick.color": INK_MUTED,
        "axes.facecolor": SURFACE,
        "figure.facecolor": SURFACE,
        "grid.color": GRIDLINE,
    })


def style_axes(ax):
    """모든 차트에 공통으로 적용하는 잔글씨 정리(그리드/테두리)."""

    ax.grid(axis="y", linewidth=0.6)
    ax.set_axisbelow(True)

    for spine in ["top", "right"]:

        ax.spines[spine].set_visible(False)

from collections import defaultdict

import matplotlib.pyplot as plt
from matplotlib import font_manager

from db import get_my_stats, get_leaderboard


# --------------------------------
# 색 · 폰트
# --------------------------------

ACCENT = "#2A6F97"
BASE = "#B8C4CC"
GRID = "#E3E8EB"
INK = "#2B3338"

PERIODS = {
    "1": ("최근 7일", 7),
    "2": ("최근 30일", 30),
    "3": ("전체 누적", None)
}


def set_korean_font():

    candidates = [
        "Malgun Gothic",
        "AppleGothic",
        "NanumGothic",
        "Noto Sans CJK KR"
    ]

    for name in candidates:

        try:
            font_manager.findfont(name, fallback_to_default=False)
            plt.rcParams["font.family"] = name
            break

        except Exception:
            continue

    plt.rcParams["axes.unicode_minus"] = False


def style_axes(ax):

    ax.set_facecolor("white")

    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)

    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK, length=0)


def format_minutes(minutes):

    hours = minutes // 60
    minutes = minutes % 60

    if hours == 0:
        return f"{minutes}분"

    return f"{hours}시간 {minutes}분"


# --------------------------------
# 기간 선택
# --------------------------------

def choose_period():

    print()
    print("1. 최근 7일")
    print("2. 최근 30일")
    print("3. 전체 누적")
    print("0. 돌아가기")

    choice = input("기간: ")

    if choice == "0":
        return None

    if choice not in PERIODS:
        print()
        print("잘못 입력했습니다.")
        return None

    return PERIODS[choice]


# --------------------------------
# 개인 통계
# --------------------------------

def personal_stats(nickname):

    period = choose_period()

    if period is None:
        return

    label, days = period

    rows = get_my_stats(days)

    if not rows:
        print()
        print("기록이 없습니다.")
        return

    by_date = defaultdict(int)
    by_subject = defaultdict(int)

    for row in rows:
        by_date[row["study_date"]] += row["study_minutes"]
        by_subject[row["subject"]] += row["study_minutes"]

    total = sum(by_date.values())

    print()
    print(f"[ {nickname}님 · {label} ]")
    print(f"총 공부 시간   {format_minutes(total)}")
    print(f"공부한 날      {len(by_date)}일")
    print(f"하루 평균      {format_minutes(total // len(by_date))}")

    print()
    print("과목별")

    for subject, minutes in sorted(by_subject.items(), key=lambda x: -x[1]):
        share = minutes / total * 100
        print(f"  {subject:<16}{format_minutes(minutes):>12}  ({share:.0f}%)")

    draw_personal(nickname, label, by_date, by_subject)


def draw_personal(nickname, label, by_date, by_subject):

    set_korean_font()

    dates = sorted(by_date.keys())
    values = [by_date[d] / 60 for d in dates]

    subjects = sorted(by_subject.items(), key=lambda x: x[1])
    subject_names = [s for s, _ in subjects]
    subject_values = [m / 60 for _, m in subjects]

    fig, (ax1, ax2) = plt.subplots(
        1, 2,
        figsize=(13, 5),
        gridspec_kw={"width_ratios": [2, 1]}
    )

    fig.suptitle(
        f"{nickname}님 공부 기록 · {label}",
        fontsize=14,
        color=INK
    )

    ax1.bar(
        range(len(dates)),
        values,
        color=ACCENT,
        width=0.6
    )

    ax1.set_xticks(range(len(dates)))
    ax1.set_xticklabels(
        [d[5:] for d in dates],
        rotation=90,
        fontsize=8
    )

    ax1.set_ylabel("시간", color=INK)
    ax1.set_title("날짜별", fontsize=11, color=INK, loc="left")
    ax1.grid(axis="y", color=GRID, linewidth=0.8)
    ax1.set_axisbelow(True)
    style_axes(ax1)

    bars = ax2.barh(
        range(len(subject_names)),
        subject_values,
        color=ACCENT,
        height=0.6
    )

    ax2.set_yticks(range(len(subject_names)))
    ax2.set_yticklabels(subject_names, fontsize=9)
    ax2.set_xlabel("시간", color=INK)
    ax2.set_title("과목별", fontsize=11, color=INK, loc="left")
    style_axes(ax2)

    for bar, value in zip(bars, subject_values):
        ax2.text(
            bar.get_width() + max(subject_values) * 0.02,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.1f}h",
            va="center",
            fontsize=9,
            color=INK
        )

    ax2.set_xlim(0, max(subject_values) * 1.18)

    plt.tight_layout()
    plt.show()


# --------------------------------
# 통계 비교
# --------------------------------

def compare_stats(nickname):

    period = choose_period()

    if period is None:
        return

    label, days = period

    rows = get_leaderboard(days)

    if not rows:
        print()
        print("기록이 없습니다.")
        return

    print()
    print(f"[ 순위 · {label} ]")
    print()
    print(f"{'순위':<6}{'닉네임':<16}{'공부 시간':>12}{'상위':>8}")
    print("-" * 44)

    for row in rows:

        mark = " (나)" if row["nickname"] == nickname else ""

        top = (1 - float(row["percentile"])) * 100

        print(
            f"{row['rank']:<6}"
            f"{row['nickname'] + mark:<16}"
            f"{format_minutes(row['study_minutes']):>12}"
            f"{top:>7.0f}%"
        )

    draw_compare(nickname, label, rows)


def draw_compare(nickname, label, rows):

    set_korean_font()

    ordered = sorted(rows, key=lambda r: r["study_minutes"])

    names = [r["nickname"] for r in ordered]
    values = [r["study_minutes"] / 60 for r in ordered]

    colors = [
        ACCENT if n == nickname else BASE
        for n in names
    ]

    labels = [
        f"{n} (나)" if n == nickname else n
        for n in names
    ]

    fig, ax = plt.subplots(figsize=(9, max(3, len(names) * 0.6)))

    fig.suptitle(
        f"공부 시간 비교 · {label}",
        fontsize=14,
        color=INK
    )

    bars = ax.barh(
        range(len(names)),
        values,
        color=colors,
        height=0.6
    )

    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("시간", color=INK)
    style_axes(ax)

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_width() + max(values) * 0.02,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.1f}h",
            va="center",
            fontsize=9,
            color=INK
        )

    ax.set_xlim(0, max(values) * 1.15)

    plt.tight_layout()
    plt.show()


# --------------------------------
# 통계 메뉴
# --------------------------------

def stats_menu(nickname):

    while True:

        print()
        print("==============================")
        print("         [ 통계보기 ]")
        print("==============================")

        print("1. 개인 통계")
        print("2. 통계 비교")
        print("3. 돌아가기")

        choice = input("선택: ")

        if choice == "1":
            personal_stats(nickname)

        elif choice == "2":
            compare_stats(nickname)

        elif choice == "3":
            return

        else:
            print()
            print("잘못 입력했습니다.")

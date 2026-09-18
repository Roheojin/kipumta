import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import chart_style

from db import (
    get_my_study_history,
    get_all_study_history,
    get_all_nicknames
)

from study import format_study_time


KST = "Asia/Seoul"


# --------------------------------
# 통계 메뉴 (2. 통계보기)
# --------------------------------

def stats_menu(user_id, nickname):

    while True:

        print()
        print("==============================")
        print("         [ 통계보기 ]")
        print("==============================")

        print("1. 개인 통계")
        print("2. 통계 비교")
        print("3. 돌아가기")

        print("--------------------------------")

        choice = input("선택: ")


        if choice == "1":

            show_personal_stats(user_id, nickname)


        elif choice == "2":

            show_comparison_stats(user_id, nickname)


        elif choice == "3":

            return


        else:

            print()
            print("잘못 입력했습니다.")


# --------------------------------
# 조회 결과(list[dict]) -> DataFrame
#   study_history_user_time 인덱스로 가져온 원본 세션 목록에
#   study_minutes 컬럼이 없으므로, 여기서 end_time - start_time으로
#   공부 시간(분)을 직접 계산합니다.
# --------------------------------

def _to_dataframe(rows):

    columns = ["subject", "start_time", "end_time"]

    if not rows:

        return pd.DataFrame(columns=columns + ["minutes"])


    df = pd.DataFrame(rows)

    df["start_time"] = pd.to_datetime(df["start_time"])
    df["end_time"] = pd.to_datetime(df["end_time"])

    df["minutes"] = (
        (df["end_time"] - df["start_time"]).dt.total_seconds() / 60
    )

    return df


# --------------------------------
# 2-1. 개인 통계
# --------------------------------

def show_personal_stats(user_id, nickname):

    rows = get_my_study_history(user_id)

    df = _to_dataframe(rows)

    if df.empty:

        print()
        print("아직 완료된 공부 기록이 없습니다.")

        return


    total_minutes = int(round(df["minutes"].sum()))
    session_count = len(df)
    subject_count = df["subject"].nunique()

    first_at = df["start_time"].min().tz_convert(KST)
    last_at = df["start_time"].max().tz_convert(KST)


    print()
    print("==============================")
    print(f"      [ {nickname}님의 개인 통계 ]")
    print("==============================")

    print(f"총 공부 시간: {format_study_time(total_minutes)}")
    print(f"완료한 세션 수: {session_count}회")
    print(f"공부한 과목 수: {subject_count}개")
    print(f"첫 기록: {first_at.strftime('%Y-%m-%d %H:%M')}")
    print(f"최근 기록: {last_at.strftime('%Y-%m-%d %H:%M')}")


    subject_summary = (
        df.groupby("subject")["minutes"]
        .agg(total_minutes="sum", session_count="count")
        .reset_index()
        .sort_values("total_minutes", ascending=False)
    )

    subject_summary["total_minutes"] = subject_summary["total_minutes"].round().astype(int)


    print()
    print("[ 과목별 공부 시간 ]")

    for _, row in subject_summary.iterrows():

        print(
            f"- {row['subject']}: "
            f"{format_study_time(row['total_minutes'])} "
            f"({row['session_count']}회)"
        )


    # 날짜별(한국 시간 기준) 합계 - 최근 추이용
    daily_series = df["start_time"].dt.tz_convert(KST).dt.date

    daily_summary = (
        df.assign(study_date=daily_series)
        .groupby("study_date")["minutes"]
        .sum()
        .sort_index()
        .round()
        .astype(int)
    )


    chart_path = f"stats_personal_{nickname}.png"

    draw_personal_charts(subject_summary, daily_summary, nickname, chart_path)

    print()
    print(f"차트를 저장했습니다: {chart_path}")


def draw_personal_charts(subject_summary, daily_summary, nickname, out_path):

    chart_style.apply_style()

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))


    # ---- 과목별 막대그래프 ----

    ax = axes[0]

    if not subject_summary.empty:

        colors = [
            chart_style.CATEGORICAL[i % len(chart_style.CATEGORICAL)]
            for i in range(len(subject_summary))
        ]

        ax.bar(
            subject_summary["subject"], subject_summary["total_minutes"],
            color=colors,
            edgecolor=chart_style.SURFACE,
            linewidth=0.5,
        )

        ax.set_ylabel("공부 시간 (분)")

    else:

        ax.text(
            0.5, 0.5, "데이터 없음",
            ha="center", va="center",
            color=chart_style.INK_MUTED,
        )
        ax.set_xticks([])
        ax.set_yticks([])

    ax.set_title("과목별 공부 시간", color=chart_style.INK_PRIMARY, fontsize=11)
    chart_style.style_axes(ax)


    # ---- 최근 추이 선 그래프 ----

    ax = axes[1]

    if not daily_summary.empty:

        dates = list(daily_summary.index)
        minutes = list(daily_summary.values)

        ax.plot(
            dates, minutes,
            color=chart_style.SEQ_BLUE,
            marker="o",
            markersize=5,
            linewidth=2,
        )

        ax.set_ylabel("공부 시간 (분)")

        step = max(1, len(dates) // 10)

        ax.set_xticks(dates[::step])
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
        ax.tick_params(axis="x", rotation=30)

    else:

        ax.text(
            0.5, 0.5, "데이터 없음",
            ha="center", va="center",
            color=chart_style.INK_MUTED,
        )
        ax.set_xticks([])
        ax.set_yticks([])

    ax.set_title("최근 공부 시간 추이", color=chart_style.INK_PRIMARY, fontsize=11)
    chart_style.style_axes(ax)


    fig.suptitle(
        f"{nickname}님의 공부 통계",
        fontsize=13, color=chart_style.INK_PRIMARY, y=1.03
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=chart_style.SURFACE)
    plt.close(fig)


# --------------------------------
# 2-2. 통계 비교
# --------------------------------

def show_comparison_stats(user_id, nickname):

    rows = get_all_study_history()

    if not rows:

        print()
        print("비교할 기록이 없습니다. 먼저 공부를 기록해 보세요.")

        return


    df = pd.DataFrame(rows)

    df["start_time"] = pd.to_datetime(df["start_time"])
    df["end_time"] = pd.to_datetime(df["end_time"])

    df["minutes"] = (
        (df["end_time"] - df["start_time"]).dt.total_seconds() / 60
    )


    totals = (
        df.groupby("user_id")["minutes"]
        .sum()
        .round()
        .astype(int)
        .reset_index()
        .rename(columns={"minutes": "total_minutes"})
    )

    totals["rank"] = (
        totals["total_minutes"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    totals = totals.sort_values("total_minutes", ascending=False)


    nickname_rows = get_all_nicknames()
    nickname_df = pd.DataFrame(nickname_rows) if nickname_rows else pd.DataFrame(columns=["user_id", "nickname"])

    totals = totals.merge(nickname_df, on="user_id", how="left")
    totals["nickname"] = totals["nickname"].fillna("익명")


    if user_id not in totals["user_id"].values:

        print()
        print("비교할 기록이 없습니다. 먼저 공부를 기록해 보세요.")

        return


    my_row = totals[totals["user_id"] == user_id].iloc[0]

    my_minutes = int(my_row["total_minutes"])
    my_rank = int(my_row["rank"])
    total_users = len(totals)
    avg_minutes = totals["total_minutes"].mean()


    print()
    print("==============================")
    print("         [ 통계 비교 ]")
    print("==============================")

    print(f"내 총 공부 시간: {format_study_time(my_minutes)}")
    print(f"전체 평균: {format_study_time(round(avg_minutes))}")
    print(f"내 순위: {my_rank}위 / 전체 {total_users}명")


    leaderboard = totals.head(10)

    print()
    print("[ 리더보드 TOP 10 ]")

    for _, row in leaderboard.iterrows():

        mark = " <- 나" if row["user_id"] == user_id else ""

        print(
            f"{row['rank']:>2}위  {row['nickname']:<12} "
            f"{format_study_time(row['total_minutes'])}{mark}"
        )


    chart_path = f"stats_compare_{nickname}.png"

    draw_comparison_charts(
        user_id, my_minutes, avg_minutes, leaderboard, chart_path
    )

    print()
    print(f"차트를 저장했습니다: {chart_path}")


def draw_comparison_charts(user_id, my_minutes, avg_minutes, leaderboard, out_path):

    chart_style.apply_style()

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))


    # ---- 나 vs 전체 평균 (막대 + 평균 기준선) ----

    ax = axes[0]

    ax.bar(
        ["나"], [my_minutes],
        color=chart_style.CATEGORICAL[0],
        width=0.5,
        edgecolor=chart_style.SURFACE,
    )

    ax.axhline(
        avg_minutes,
        color=chart_style.INK_MUTED,
        linestyle="--",
        linewidth=1.5,
    )

    ax.text(
        0.55, avg_minutes,
        f"전체 평균 {avg_minutes:.0f}분",
        color=chart_style.INK_SECONDARY,
        fontsize=9,
        va="bottom",
        transform=ax.get_yaxis_transform(),
    )

    ax.set_ylabel("공부 시간 (분)")
    ax.set_xlim(-0.6, 1.4)
    ax.set_title("나 vs 전체 평균", color=chart_style.INK_PRIMARY, fontsize=11)
    chart_style.style_axes(ax)


    # ---- 리더보드 (가로 막대) ----

    ax = axes[1]

    if not leaderboard.empty:

        ordered = leaderboard.iloc[::-1]

        colors = [
            chart_style.CATEGORICAL[0] if uid == user_id else chart_style.INK_MUTED
            for uid in ordered["user_id"]
        ]

        ax.barh(
            ordered["nickname"], ordered["total_minutes"],
            color=colors,
            edgecolor=chart_style.SURFACE,
        )

        ax.set_xlabel("공부 시간 (분)")

    else:

        ax.text(
            0.5, 0.5, "데이터 없음",
            ha="center", va="center",
            color=chart_style.INK_MUTED,
        )
        ax.set_xticks([])
        ax.set_yticks([])

    ax.set_title("리더보드 TOP 10", color=chart_style.INK_PRIMARY, fontsize=11)
    chart_style.style_axes(ax)


    fig.suptitle(
        "통계 비교", fontsize=13, color=chart_style.INK_PRIMARY, y=1.03
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=chart_style.SURFACE)
    plt.close(fig)

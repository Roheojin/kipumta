from datetime import datetime

from db import (
    get_open_session,
    start_session,
    end_session
)


# --------------------------------
# 공부 시간 표시
# --------------------------------

def format_study_time(minutes):

    hours = minutes // 60
    minutes = minutes % 60

    return f"{hours}시간 {minutes}분"


# --------------------------------
# 공부하기
# --------------------------------

def study_menu(user_id):

    # --------------------------------
    # 현재 공부 중인지 확인
    # --------------------------------

    session = get_open_session(user_id)


    # 공부 중
    if session is not None:

        print()
        print("진행 중인 공부가 있습니다.")

        print(
            f"과목: {session['subject']}"
        )

        print(
            f"시작: {session['start_time']}"
        )

        print()
        print("1. 종료하기")
        print("2. 돌아가기")

        choice = input("선택: ")


        if choice == "1":

            now = datetime.now().astimezone()

            success = end_session(
                user_id,
                now
            )

            if success:

                print()
                print("공부가 종료되었습니다.")

        return


    # --------------------------------
    # 공부 시작
    # --------------------------------

    print()
    print("==============================")
    print("         [ 공부하기 ]")
    print("==============================")


    subject = input(
        "공부할 과목을 입력하세요: "
    )


    now = datetime.now().astimezone()


    success = start_session(
        user_id,
        subject,
        now
    )


    if success:

        print()
        print("공부를 시작합니다.")
        print(f"과목: {subject}")
        print(
            f"시작: {now.strftime('%H:%M')}"
        )

    else:

        print()
        print("공부 시작에 실패했습니다.")

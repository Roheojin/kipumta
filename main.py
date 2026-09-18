from getpass import getpass

from db import sign_in

from users import check_nickname

from study import study_menu

from stats import stats_menu


# --------------------------------
# 로그인
# --------------------------------

def login():

    for i in range(3):

        print()
        print("================================")
        print("           키품타 (KPT)")
        print("================================")

        email = input("이메일: ")
        password = input("비밀번호: ")


        print()
        print("로그인 중...")


        user = sign_in(
            email,
            password
        )


        if user is not None:

            print("로그인 성공")

            return user.id


        print()
        print(
            f"로그인 실패. 다시 시도하세요. ({i + 1}/3)"
        )


    print()
    print("로그인 횟수를 초과했습니다.")

    return None


# --------------------------------
# 메인 메뉴
# --------------------------------

def main_menu(user_id, nickname):

    while True:

        print()
        print("--------------------------------")
        print(f"   {nickname}님, 환영합니다")
        print("--------------------------------")

        print("1. 공부하기")
        print("2. 통계보기")
        print("3. 종료하기")

        print("--------------------------------")

        choice = input("선택: ")


        # --------------------------------
        # 공부하기
        # --------------------------------

        if choice == "1":

            study_menu(user_id)


        # --------------------------------
        # 통계보기
        # --------------------------------

        elif choice == "2":

            stats_menu(nickname)


        # --------------------------------
        # 종료
        # --------------------------------

        elif choice == "3":

            print()
            print("키품타를 종료합니다.")

            break


        else:

            print()
            print("잘못 입력했습니다.")


# --------------------------------
# 프로그램 시작
# --------------------------------

user_id = login()


if user_id is not None:

    nickname = check_nickname(
        user_id
    )


    if nickname is not None:

        main_menu(
            user_id,
            nickname
        )

else:

    print()
    print("프로그램을 종료합니다.")

from db import get_my_profile, set_nickname


# --------------------------------
# 닉네임 확인
# --------------------------------

def get_nickname(user_id):

    profile = get_my_profile(user_id)

    if profile is None:

        return None

    return profile["nickname"]


# --------------------------------
# 닉네임 설정
# --------------------------------

def nickname_setting(user_id):

    for i in range(5):

        print()

        nickname = input(
            "사용할 닉네임을 입력하세요 (2~12자): "
        )


        # 길이 확인
        if len(nickname) < 2:

            print(
                f"2자 이상 입력하세요. ({i + 1}/5)"
            )

            continue


        if len(nickname) > 12:

            print(
                f"12자 이하로 입력하세요. ({i + 1}/5)"
            )

            continue


        # DB에 닉네임 저장
        success = set_nickname(
            user_id,
            nickname
        )


        if success:

            print()
            print(
                f"닉네임이 '{nickname}'로 설정되었습니다."
            )

            return nickname


        else:

            print()
            print("닉네임 저장에 실패했습니다.")


    print()
    print("닉네임 입력 횟수를 초과했습니다.")

    return None


# --------------------------------
# 로그인 후 프로필 처리
# --------------------------------

def check_nickname(user_id):

    nickname = get_nickname(user_id)


    # 닉네임이 이미 있음
    if nickname is not None:

        return nickname


    # 닉네임이 없음
    print()
    print("닉네임이 설정되어 있지 않습니다.")

    return nickname_setting(user_id)
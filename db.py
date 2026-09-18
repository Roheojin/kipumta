import os

from dotenv import load_dotenv
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions


# --------------------------------
# Supabase 연결
# --------------------------------

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
    options=ClientOptions(schema="kiwoom")
)


# --------------------------------
# 로그인
# --------------------------------

def sign_in(email, password):

    try:

        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        return response.user

    except Exception:

        return None


# --------------------------------
# 사용자 프로필 가져오기
# --------------------------------

def get_my_profile(user_id):

    try:

        response = (
            supabase
            .table("user_info")
            .select("user_id, nickname")
            .eq("user_id", user_id)
            .execute()
        )

        if response.data:

            return response.data[0]

        return None

    except Exception as e:

        print("프로필 조회 오류:", e)

        return None


# --------------------------------
# 닉네임 저장
# --------------------------------

def set_nickname(user_id, nickname):

    try:

        response = (
            supabase
            .table("user_info")
            .update({
                "nickname": nickname
            })
            .eq("user_id", user_id)
            .execute()
        )

        return len(response.data) > 0

    except Exception as e:

        print("닉네임 저장 오류:", e)

        return False


# --------------------------------
# 현재 공부 중인지 확인
# --------------------------------

def get_open_session(user_id):

    try:

        response = (
            supabase
            .table("study_history")
            .select("*")
            .eq("user_id", user_id)
            .is_("end_time", "null")
            .execute()
        )

        if response.data:

            return response.data[0]

        return None

    except Exception as e:

        print("공부 세션 조회 오류:", e)

        return None


# --------------------------------
# 공부 시작
# --------------------------------

def start_session(user_id, subject, start_time):

    try:

        data = {
            "user_id": user_id,
            "subject": subject,
            "start_time": start_time.isoformat()
        }

        response = (
            supabase
            .table("study_history")
            .insert(data)
            .execute()
        )

        return True

    except Exception as e:

        print("공부 시작 저장 오류:", e)

        return False


# --------------------------------
# 공부 종료
# --------------------------------

def end_session(user_id, end_time):

    try:

        session = get_open_session(user_id)

        if session is None:

            return False

        start_time = session["start_time"]

        from datetime import datetime

        start = datetime.fromisoformat(
            start_time.replace("Z", "+00:00")
        )

        study_time = end_time - start

        total_minutes = int(
            study_time.total_seconds() / 60
        )

        response = (
            supabase
            .table("study_history")
            .update({
                "end_time": end_time.isoformat(),
                "study_minutes": total_minutes
            })
            .eq("user_id", user_id)
            .is_("end_time", "null")
            .execute()
        )

        return True

    except Exception as e:

        print("공부 종료 저장 오류:", e)

        return False


# --------------------------------
# [통계] 내 공부 기록 (완료된 세션만)
#   study_history_user_time 인덱스 (user_id, start_time DESC)를
#   그대로 타는 조회입니다. 여기서 받은 원본 기록을 stats.py에서
#   pandas로 집계/시각화합니다.
# --------------------------------

def get_my_study_history(user_id):

    try:

        response = (
            supabase
            .table("study_history")
            .select("subject, start_time, end_time")
            .eq("user_id", user_id)
            .not_.is_("end_time", "null")
            .order("start_time", desc=True)
            .execute()
        )

        return response.data

    except Exception as e:

        print("공부 기록 조회 오류:", e)

        return []


# --------------------------------
# [통계] 전체 사용자 공부 기록 (비교용, 완료된 세션만)
# --------------------------------

def get_all_study_history():

    try:

        response = (
            supabase
            .table("study_history")
            .select("user_id, subject, start_time, end_time")
            .not_.is_("end_time", "null")
            .execute()
        )

        return response.data

    except Exception as e:

        print("전체 공부 기록 조회 오류:", e)

        return []


# --------------------------------
# [통계] 전체 닉네임 목록 (비교 결과에 이름 붙이는 용도)
# --------------------------------

def get_all_nicknames():

    try:

        response = (
            supabase
            .table("user_info")
            .select("user_id, nickname")
            .execute()
        )

        return response.data

    except Exception as e:

        print("닉네임 목록 조회 오류:", e)

        return []
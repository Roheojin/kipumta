import os

from dotenv import load_dotenv
from supabase import create_client, Client


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

SCHEMA = "kiwoom"

if not SUPABASE_URL or not SUPABASE_KEY:

    raise SystemExit(
        ".env 파일에 SUPABASE_URL과 SUPABASE_KEY를 설정하세요."
    )

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
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
            .schema(SCHEMA)
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
            .schema(SCHEMA)
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
            .schema(SCHEMA)
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
            .schema(SCHEMA)
            .table("study_history")
            .insert(data)
            .execute()
        )

        return len(response.data) > 0

    except Exception as e:

        print("공부 시작 저장 오류:", e)

        return False


# --------------------------------
# 개인 통계
# --------------------------------

def get_my_stats(p_days):

    try:

        response = supabase.rpc(
            "get_my_stats",
            {"p_days": p_days}
        ).execute()

        return response.data or []

    except Exception as e:

        print("개인 통계 조회 오류:", e)

        return []


# --------------------------------
# 비교 통계
# --------------------------------

def get_leaderboard(p_days):

    try:

        response = supabase.rpc(
            "get_leaderboard",
            {"p_days": p_days}
        ).execute()

        return response.data or []

    except Exception as e:

        print("비교 통계 조회 오류:", e)

        return []


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
            .schema(SCHEMA)
            .table("study_history")
            .update({
                "end_time": end_time.isoformat(),
                "study_minutes": total_minutes
            })
            .eq("user_id", user_id)
            .is_("end_time", "null")
            .execute()
        )

        return len(response.data) > 0

    except Exception as e:

        print("공부 종료 저장 오류:", e)

        return False

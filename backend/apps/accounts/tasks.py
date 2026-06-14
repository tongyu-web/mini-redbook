from django.utils import timezone
from django.db.models import F
from config.constants import MAX_LOGIN_FAIL_COUNT, LOGIN_LOCK_MINUTES
from .models import User

class AccountTask:
    @staticmethod
    def handle_login_fail(user):
        user.login_fail_count = F("login_fail_count") + 1
        user.save(update_fields=["login_fail_count"])
        user.refresh_from_db()
        if user.login_fail_count >= MAX_LOGIN_FAIL_COUNT:
            user.login_locked_until = timezone.now() + timezone.timedelta(minutes=LOGIN_LOCK_MINUTES)
            user.login_fail_count = 0
            user.save(update_fields=["login_locked_until", "login_fail_count"])

    @staticmethod
    def handle_login_success(user):
        user.login_fail_count = 0
        user.login_locked_until = None
        user.save(update_fields=["login_fail_count", "login_locked_until"])

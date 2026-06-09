from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class UsernameOrEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        login = username or kwargs.get(UserModel.USERNAME_FIELD)

        if login is None or password is None:
            return None

        login = login.strip()
        user = self._get_user_for_login(UserModel, login)

        if user is None:
            UserModel().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def _get_user_for_login(self, UserModel, login):
        if "@" in login:
            users = UserModel._default_manager.filter(email__iexact=login)
            if users.count() != 1:
                return None

            return users.first()

        try:
            return UserModel._default_manager.get(username__iexact=login)
        except (UserModel.DoesNotExist, UserModel.MultipleObjectsReturned):
            return None

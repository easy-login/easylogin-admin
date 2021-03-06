from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class AuthenticationWithEmailBackend(ModelBackend):
    @staticmethod
    def authenticate(username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username, deleted=0)
        except UserModel.DoesNotExist:
            print("User doesn\'t exist!")
            return None
        else:
            if user.check_password(password):
                return user
            else:
                print("Password incorrect!")
                return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

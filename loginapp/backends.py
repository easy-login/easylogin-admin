from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class AuthenticationWithEmailBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        print("donnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnne")
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
            print(user.password)
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

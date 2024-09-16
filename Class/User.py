from werkzeug.security import check_password_hash
from Utils.tools import Tools, CustomException
from Utils.jwt_manager import create_token
from Utils.querys import Querys

class User:

    def __init__(self):
        self.tools = Tools()
        self.querys = Querys()

    def login(self, data):

        email = data["email"]
        password = data["password"]

        data_user = self.querys.get_user(email)

        enc_passwd = data_user.password
        if not check_password_hash(enc_passwd, password):
            raise CustomException("Username or password incorrect.")
        
        if data_user.user_type_id != 1:
            raise CustomException("User not authorized.", 401)

        token = create_token(data)
        return self.tools.output(200, "Login successfully.", token)

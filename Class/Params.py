from Utils.tools import Tools
from Utils.querys import Querys

class Param:

    def __init__(self):
        self.tools = Tools()
        self.querys = Querys()

    def get_type_document(self):

        type_documents = self.querys.get_type_document()
        return self.tools.output(200, "Ok.", type_documents)

    def get_type_user(self):

        type_users = self.querys.get_type_user()
        return self.tools.output(200, "Ok.", type_users)

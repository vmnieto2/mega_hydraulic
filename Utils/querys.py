
from Config.db import session
from Utils.tools import Tools, CustomException
from Models.user_model import UserModel
from Models.type_document_model import TypeDocumentModel
from Models.user_type_model import TypeUserModel
# from Models.client_model import ClientModel
# from Models.loan_model import LoanModel
# from Models.payment_model import PaymentModel

class Querys:

    def __init__(self):
        self.tools = Tools()

    # Query for obtain data of user to log
    def get_user(self, email: str):

        query = session.query(
            UserModel
        ).filter(
            UserModel.email == email, UserModel.status == 1,
        ).first()
        session.close()

        if not query:
            raise CustomException("User not found.")
        
        return query
    
    # Query for have all type documents
    def get_type_document(self):

        response = list()
                
        query = session.query(
            TypeDocumentModel
        ).filter(
            TypeDocumentModel.status == 1
        ).all()
        session.close()
        
        if not query:
            raise CustomException("No data to show", 404)
        
        for key in query:
            response.append({
                "id": key.id,
                "name": key.name,
                "description": key.description
            })
        
        return response

    # Query for have all type users
    def get_type_user(self):

        response = list()
                
        query = session.query(
            TypeUserModel
        ).filter(
            TypeUserModel.status == 1
        ).all()
        session.close()
        
        if not query:
            raise CustomException("No data to show", 404)
        
        for key in query:
            response.append({
                "id": key.id,
                "name": key.name
            })
        
        return response

    # Function to verify if exists a field of any list of params
    def check_param_exists(self, model: any, param_to_find: int, field: str):

        query = session.query(
            model
        ).filter(
            model.id == param_to_find, model.status == 1
        ).first()
        session.close()

        msg = f"Field {field} doesn't exists."
        if not query:
            raise CustomException(msg)

        return True
    
    # # Check if client exists.
    # def check_if_exists_client(self, document: str):

    #     client = session.query(
    #         ClientModel
    #     ).filter(
    #         ClientModel.document == document, ClientModel.status == 1
    #     ).first()
    #     session.close()

    #     if client:
    #         raise CustomException("Client already exists.")
        
    #     return True
    
    # # Inserting data.
    # def insert_data(self, model: any, data: dict):
        
    #     try:
    #         client = model(data)
    #         session.add(client)
    #         session.commit()
    #         session.close()
    #     except Exception as ex:
    #         raise CustomException(str(ex))
        
    #     return True

    # # Check if client exists by id.
    # def check_client_by_id(self, client_id: int):

    #     client = session.query(
    #         ClientModel
    #     ).filter(
    #         ClientModel.id == client_id, ClientModel.status == 1
    #     ).first()
    #     session.close()

    #     if not client:
    #         raise CustomException("Client doesn't exists.")
        
    #     return True
    
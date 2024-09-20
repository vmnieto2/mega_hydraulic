
from Config.db import session
from Utils.tools import Tools, CustomException
from Models.user_model import UserModel
from Models.type_document_model import TypeDocumentModel
from Models.user_type_model import TypeUserModel
from Models.type_maintenance_model import TypeMaintenanceModel
from Models.report_model import ReportModel
from Models.report_type_maintenance_model import ReportTypeMaintenanceModel
# from Models.report_files_model import ReportFilesModel
# from Models.payment_model import PaymentModel

class Querys:

    def __init__(self):
        self.tools = Tools()

    # Query for obtain data of user to log
    def get_user(self, document: str):

        query = session.query(
            UserModel
        ).filter(
            UserModel.document == document, UserModel.status == 1,
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

    # Query for have all type maintenances
    def get_type_maintenance(self):

        response = list()
                
        query = session.query(
            TypeMaintenanceModel
        ).filter(
            TypeMaintenanceModel.status == 1
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
    
    # Query for insert report.
    def create_report(self, data: dict):

        try:
            report = ReportModel(data)
            session.add(report)
            session.commit()
            report_id = report.id
        except Exception as ex:
            raise CustomException(str(ex))
        finally:
            session.close()
        
        return report_id
    
    # Query for types maintenances.
    def insert_types_maintenances(self, data: dict):
        try:
            type_man = ReportTypeMaintenanceModel(data)
            session.add(type_man)
            session.commit()
            session.close()
        except Exception as ex:
            raise CustomException(str(ex))
        
        return True

    # Inserting data.
    def insert_data(self, model: any, data: dict):

        try:
            model_data = model(data)
            session.add(model_data)
            session.commit()
        except Exception as ex:
            raise CustomException(str(ex))
        finally:
            session.close()
        
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
    
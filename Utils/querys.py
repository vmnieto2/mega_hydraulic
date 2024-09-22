
from Config.db import session
from Utils.tools import Tools, CustomException
from Models.user_model import UserModel
from Models.type_document_model import TypeDocumentModel
from Models.user_type_model import TypeUserModel
from Models.type_maintenance_model import TypeMaintenanceModel
from Models.report_model import ReportModel
from Models.report_type_maintenance_model import ReportTypeMaintenanceModel
from Models.report_files_model import ReportFilesModel
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

    # Query for get the data for the report
    def get_data_report(self, report_id):

        try:

            response = dict()
                    
            query = session.query(
                ReportModel.id,
                ReportModel.intervened_item, ReportModel.activity_date,
                ReportModel.client, ReportModel.service_order,
                ReportModel.solped, ReportModel.person_receives,
                ReportModel.buy_order, ReportModel.description           
            ).filter(
                ReportModel.id == report_id, ReportModel.status == 1
            ).first()
            
            if query:
                response = {
                    "id": query.id,
                    "intervened_item": query.intervened_item,
                    "activity_date": str(query.activity_date),
                    "client": query.client,
                    "service_order": query.service_order,
                    "solped": query.solped,
                    "person_receives": query.person_receives,
                    "buy_order": query.buy_order,
                    "description": query.description,
                }

                type_maintenance = list()
                files = list()

                query2 = session.query(
                    ReportTypeMaintenanceModel.id,
                    ReportTypeMaintenanceModel.id_report,
                    TypeMaintenanceModel.name
                ).join(
                    TypeMaintenanceModel, 
                    TypeMaintenanceModel.id == ReportTypeMaintenanceModel.type_maintenance_id,
                    isouter=True
                ).filter(
                    ReportTypeMaintenanceModel.id_report == report_id,
                    TypeMaintenanceModel.status == 1
                ).all()

                if query2:
                    for key in query2:
                        type_maintenance.append({
                            "id": key.id,
                            "report_id": key.id_report,
                            "name": key.name
                        })

                response.update({"type_maintenance": type_maintenance})

                query3 = session.query(
                    ReportFilesModel.id, ReportFilesModel.path
                ).filter(
                    ReportFilesModel.id_report == report_id,
                    ReportFilesModel.status == 1
                ).all()

                if query3:
                    for key in query3:
                        files.append({
                            "id": key.id,
                            "path": key.path
                        })

                response.update({"files": files})

        except Exception as ex:
            raise CustomException(str(ex))
        finally:
            session.close()

        return response

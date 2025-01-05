
from Config.db import session
from Utils.tools import Tools, CustomException
from Models.user_model import UserModel
from Models.type_document_model import TypeDocumentModel
from Models.user_type_model import TypeUserModel
from Models.report_type_service_model import ReportTypeServiceModel
from Models.type_service_model import TypeServiceModel
from Models.type_equipment_model import TypeEquipmentModel
from Models.task_list_model import TaskListModel
from Models.task_list_by_equipment_model import TaskListEquipmentModel
from Models.client_model import ClientModel
from Models.client_lines_model import ClientLinesModel
from Models.client_user_model import ClientUserModel
from Models.report_model import ReportModel
from Models.report_details_model import ReportDetailsModel
from Models.report_files_model import ReportFilesModel

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

    # Query for have all type services
    def get_type_service(self):

        response = list()
                
        query = session.query(
            TypeServiceModel
        ).filter(
            TypeServiceModel.status == 1
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

    # Query for have all type equipments
    def get_type_equipments(self):

        response = list()
                
        query = session.query(
            TypeEquipmentModel
        ).filter(
            TypeEquipmentModel.status == 1
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

    # Query for have all task by equipment
    def get_tasks_by_equipment(self, equipment: int):

        response = list()
                
        with session:
            query = session.query(
                TaskListModel.id, TaskListModel.name
            ).join(
                TaskListEquipmentModel, 
                TaskListModel.id == TaskListEquipmentModel.task_id,
                isouter=True
            ).join(
                TypeEquipmentModel, 
                TypeEquipmentModel.id == TaskListEquipmentModel.equipment_id,
                isouter=True
            ).filter(
                TypeEquipmentModel.status == 1,
                TaskListModel.status == 1,
                TaskListEquipmentModel.status == 1,
                TaskListEquipmentModel.equipment_id == equipment
            ).all()
        
        if not query:
            raise CustomException("No data to show", 404)
        
        for key in query:
            response.append({
                "id": key.id,
                "name": key.name
            })
        
        return response

    # Query for have all lines by client
    def get_lines_by_client(self, client: int):

        response = list()
                
        with session:
            query = session.query(
                ClientLinesModel.id, ClientLinesModel.name
            ).join(
                ClientModel, 
                ClientModel.id == ClientLinesModel.client_id,
                isouter=True
            ).filter(
                ClientModel.status == 1,
                ClientLinesModel.status == 1,
                ClientLinesModel.client_id == client
            ).all()
        
        if not query:
            raise CustomException("No data to show", 404)
        
        for key in query:
            response.append({
                "id": key.id,
                "name": key.name
            })
        
        return response

    # Query for have all users by client
    def get_users_by_client(self, client: int):

        response = list()
                
        with session:
            query = session.query(
                ClientUserModel.id, ClientUserModel.full_name
            ).join(
                ClientModel, 
                ClientModel.id == ClientUserModel.client_id,
                isouter=True
            ).filter(
                ClientModel.status == 1,
                ClientUserModel.status == 1,
                ClientUserModel.client_id == client
            ).all()
        
        if not query:
            raise CustomException("No data to show", 404)
        
        for key in query:
            response.append({
                "id": key.id,
                "name": key.full_name
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
    def insert_report_details(self, data: dict):
        try:
            details = ReportDetailsModel(data)
            session.add(details)
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
                ReportModel.activity_date,
                ReportModel.client_id,
                ClientModel.name.label('client_name'),
                ReportModel.client_line_id,
                ClientLinesModel.name.label('client_line'),
                ReportModel.person_receives.label('person_receive_id'),
                ClientUserModel.full_name.label('person_receive_name'),
                ReportModel.om,
                ReportModel.equipment_type_id,
                TypeEquipmentModel.name.label('equipment_name'),
                ReportModel.equipment_name,
                ReportModel.service_description,
            ).join(
                ClientModel, 
                ClientModel.id == ReportModel.client_id,
                isouter=True
            ).join(
                ClientLinesModel, 
                ClientLinesModel.id == ReportModel.client_line_id,
                isouter=True
            ).join(
                ClientUserModel, 
                ClientUserModel.id == ReportModel.person_receives,
                isouter=True
            ).join(
                TypeEquipmentModel, 
                TypeEquipmentModel.id == ReportModel.equipment_type_id,
                isouter=True
            ).filter(
                ClientModel.status == 1,
                ClientLinesModel.status == 1,
                ClientUserModel.status == 1,
                TypeEquipmentModel.status == 1,
                ReportModel.id == report_id,
                ReportModel.status == 1
            ).first()
            
            if query:
                response = {
                    "id": query.id,
                    "activity_date": str(query.activity_date),
                    "client_id": query.client_id,
                    "client_name": query.client_name,
                    "client_line_id": query.client_line_id,
                    "client_line": query.client_line,
                    "person_receive_id": query.person_receive_id,
                    "person_receive_name": str(query.person_receive_name).upper(),
                    "om": query.om,
                    "equipment_type_id": query.equipment_type_id,
                    "equipment_name": str(query.equipment_name).upper(),
                    "service_description": str(query.service_description).capitalize(),
                }

                type_service = list()
                files = list()
                tasks = list()

                query2 = session.query(
                    ReportTypeServiceModel.report_id,
                    TypeServiceModel.id,
                    TypeServiceModel.name
                ).join(
                    TypeServiceModel, 
                    TypeServiceModel.id == ReportTypeServiceModel.type_service_id,
                    isouter=True
                ).filter(
                    ReportTypeServiceModel.report_id == report_id,
                    TypeServiceModel.status == 1
                ).all()

                if query2:
                    for key in query2:
                        type_service.append({
                            "id": key.id,
                            "report_id": key.report_id,
                            "name": key.name
                        })

                response.update({"type_service": type_service})

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

                query4 = session.query(
                    ReportModel.id,
                    ReportDetailsModel.task_id,
                    TaskListModel.name,
                    ReportDetailsModel.positive,
                    ReportDetailsModel.negative,
                    ReportDetailsModel.description,
                ).join(
                    ReportDetailsModel,
                    ReportDetailsModel.report_id == ReportModel.id
                ).join(
                    TaskListModel,
                    TaskListModel.id == ReportDetailsModel.task_id
                ).filter(
                    ReportDetailsModel.status == 1,
                    TaskListModel.status == 1,
                    ReportModel.status == 1,
                    ReportDetailsModel.report_id == report_id
                ).all()

                if query4:
                    for key in query4:
                        tasks.append({
                            "id": key.id,
                            "name": key.name,
                            "positive": key.positive,
                            "negative": key.negative,
                            "description": str(key.description).capitalize(),
                        })

                response.update({"tasks": tasks})

        except Exception as ex:
            raise CustomException(str(ex))
        finally:
            session.close()

        return response

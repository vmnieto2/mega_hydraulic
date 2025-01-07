from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from Models.client_model import ClientModel
from Models.client_lines_model import ClientLinesModel
from Models.client_user_model import ClientUserModel
from Models.type_service_model import TypeServiceModel
from Models.type_equipment_model import TypeEquipmentModel
from Models.task_list_model import TaskListModel
from Models.report_type_service_model import ReportTypeServiceModel
from Models.report_files_model import ReportFilesModel
from Utils.rules import Rules
from datetime import datetime
import os
import base64
import uuid
import re
from fastapi.responses import StreamingResponse
from io import BytesIO

UPLOAD_FOLDER = "Uploads/"

class Report:

    def __init__(self):
        self.tools = Tools()
        self.querys = Querys()

    # Funcion for create a report
    def create_report(self, data):

        try:
            data_save = {
                "activity_date": self.tools.format_date(data["activity_date"]),
                "client_id": data["client_id"],
                "client_line_id": data["client_line_id"],
                "person_receives": data["person_receives"],
                "om": data["om"],
                "equipment_type_id": data["equipment_type_id"],
                "equipment_name": data["equipment_name"],
                "service_description": data["service_description"],
                "user_id": data["user_id"]
            }

            self.querys.check_param_exists(
                ClientModel, 
                data["client_id"], 
                "Cliente"
            )

            self.querys.check_param_exists(
                ClientLinesModel, 
                data["client_line_id"], 
                "Línea"
            )

            self.querys.check_param_exists(
                ClientUserModel, 
                data["person_receives"], 
                "Persona que recibe"
            )

            self.querys.check_param_exists(
                TypeEquipmentModel, 
                data["equipment_type_id"], 
                "Tipo de equipo intervenido"
            )

            type_service = data["type_service"]
            if type_service:
                for index, type_s in enumerate(type_service):
                    Rules("/service_types", type_s)
                    self.querys.check_param_exists(
                        TypeServiceModel, 
                        type_s,
                        f"Tipo mantenimiento {index+1}"
                    )

            task_list = data["task_list"]
            if task_list:
                for index, task in enumerate(task_list):
                    Rules("/task_list", task)
                    self.querys.check_param_exists(
                        TaskListModel, 
                        task["task_id"],
                        f"Tarea {index+1}"
                    )

            id_report = self.querys.create_report(data_save)

            if type_service:
                for type_s in type_service:
                    data_type_service = {
                        "report_id": id_report,
                        "type_service_id": type_s,
                    }
                    self.querys.insert_data(
                        ReportTypeServiceModel, 
                        data_type_service
                    )

            if task_list:
                for task in task_list:
                    data_report_details_save = {
                        "report_id": id_report,
                        "task_id": task["task_id"],
                        "positive": task["positive"],
                        "negative": task["negative"],
                        "description": task["description"]
                    }
                    self.querys.insert_report_details(data_report_details_save)

            imagenes = data["files"]
            print(f"imagenes: {imagenes}")
            if imagenes:
                self.proccess_images(id_report, imagenes)

            return self.tools.output(201, "Reporte creado exitosamente.", id_report)

        except Exception as ex:
            raise CustomException(str(ex))

    # Function for process image files base64 and save them
    def proccess_images(self, id_report, imagenes):

        # Procesar y guardar cada archivo de la lista "files"
        for index, file_base64 in enumerate(imagenes):
            try:
                # Extraer el formato de la imagen
                file_extension = self.extract_file_extension(file_base64["img"])

                # Eliminar el prefijo base64 antes de decodificar
                base64_data = re.sub(r"^data:image/\w+;base64,", "", file_base64["img"])

                # Decodificar la imagen base64
                file_data = base64.b64decode(base64_data)
            except Exception as e:
                raise CustomException(f"Error al decodificar la imagen {index + 1}: {str(e)}")

            # Generar un nombre único para cada archivo
            file_name = f"{str(uuid.uuid4())}.{file_extension}"
            file_path = os.path.join(UPLOAD_FOLDER, file_name)

            # Guardar la imagen decodificada en el servidor
            try:
                with open(file_path, "wb") as file:
                    file.write(file_data)
            except Exception as e:
                raise CustomException(f"Error al guardar la imagen {index + 1}: {str(e)}")

            data_save = {
                "id_report": id_report,
                "path": file_path,
                "description": file_base64["description"],
            }
            self.querys.insert_data(ReportFilesModel, data_save)

        return True
    
    # Busca el prefijo que indica el tipo de archivo, como data:image/jpeg;base64,
    def extract_file_extension(self, file_base64: str):
        match = re.match(r"data:image/(?P<ext>\w+);base64,", file_base64)
        if not match:
            raise ValueError("Formato de imagen no válido o prefijo faltante")
        
        # Extrae la extensión (jpg, png, etc.)
        return match.group("ext")

    # Function for generate pdf of the report
    def generate_report(self, data):

        report_id = data["report_id"]

        data_report = self.querys.get_data_report(report_id)

        pdf = self.tools.gen_pdf(data_report)

        # Nombre del archivo pdf de salida
        file_name = f"reporte_{data['report_id']}_{str(datetime.now())}.pdf"

        # return self.tools.output(200, "Ok", data_report)
        # return self.tools.outputpdf(200, file_name, pdf)
        # Retornar el PDF como respuesta
        return StreamingResponse(
            BytesIO(pdf),
            headers={
                "Content-Disposition": f"attachment; filename={file_name}",
                "Content-Type": "application/pdf",
            },
        )

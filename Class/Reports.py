from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from Models.type_maintenance_model import TypeMaintenanceModel
from Models.report_files_model import ReportFilesModel
from Utils.rules import Rules
from datetime import datetime
import os
import base64
import uuid
import re

UPLOAD_FOLDER = "Uploads/"

class Report:

    def __init__(self):
        self.tools = Tools()
        self.querys = Querys()

    def create_report(self, data):

        try:
            data_save = {
                "intervened_item": data["intervened_item"],
                "activity_date": self.tools.format_date(data["activity_date"]),
                "client": data["client"],
                "service_order": data["service_order"],
                "solped": data["solped"],
                "person_receives": data["person_receives"],
                "buy_order": data["buy_order"],
                "description": data["description"],
                "user_id": data["user_id"]
            }
            maintenance_types = data["maintenance_types"]
            imagenes = data["files"]

            if maintenance_types:
                for index, type_m in enumerate(maintenance_types):
                    Rules("/maintenance_types", type_m)
                    self.querys.check_param_exists(
                        TypeMaintenanceModel, 
                        type_m, 
                        f"Tipo mantenimiento {index+1}"
                    )

            id_report = self.querys.create_report(data_save)
            if maintenance_types:
                for type_m in maintenance_types:
                    data_type_save = {
                        "id_report": id_report,
                        "type_maintenance_id": type_m
                    }
                    self.querys.insert_types_maintenances(data_type_save)

            if imagenes:
                self.proccess_images(id_report, imagenes)

            return self.tools.output(200, "Report created successfully.")

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
                "path": file_path
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
        return self.tools.outputpdf(200, file_name, pdf)
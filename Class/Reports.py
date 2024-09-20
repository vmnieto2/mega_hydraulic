from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from Models.type_maintenance_model import TypeMaintenanceModel
from Models.report_files_model import ReportFilesModel
from Utils.rules import Rules
import os
import base64
import uuid
import re

UPLOAD_FOLDER = "uploads/"

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
                for type_m in maintenance_types:
                    Rules("/maintenance_types", type_m)
                    self.querys.check_param_exists(
                        TypeMaintenanceModel, 
                        type_m, 
                        "Tipo mantenimiento"
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

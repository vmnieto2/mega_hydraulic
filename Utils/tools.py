import base64
# from Utils.constants import BASE_PATH_TEMPLATE
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
# from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import json
import os
import smtplib
from datetime import datetime
from PyPDF2 import PdfWriter, PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import textwrap
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors



class Tools:

    def outputpdf(self, codigo, file_name, data={}):
        response = Response(
            status_code=codigo,
            content=data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={file_name}"
            }
        )
        return response


    """ Esta funcion permite darle formato a la respuesta de la API """
    def output(self, codigo, message, data={}):

        response = JSONResponse(
            status_code=codigo,
            content=jsonable_encoder({
                "code": codigo,
                "message": message,
                "data": data,
            }),
            media_type="application/json"
        )
        return response

    # """ Esta funcion permite obtener el template """
    # def get_content_template(self, template_name: str):
    #     template = f"{BASE_PATH_TEMPLATE}/{template_name}"

    #     content = ""
    #     with open(template, 'r') as f:
    #         content = f.read()

    #     return content

    def result(self, msg, code=400, error="", data=[]):
        return {
            "body": {
                "statusCode": code,
                "message": msg,
                "data": data,
                "Exception": error
            }
        }

    # Función para formatear las fechas    
    def format_date(self, date):
        fecha_objeto = datetime.strptime(date, "%d-%m-%Y")
        fecha_formateada = fecha_objeto.strftime("%Y-%m-%d")
        return fecha_formateada
    
    # Función para generar un pdf
    def gen_pdf(self, data):

        # Ruta del archivo PDF original
        original_pdf_path = os.path.join('Templates', 'Mtto_Template.pdf')

        # Cargar el PDF original
        reader = PdfReader(original_pdf_path)
        writer = PdfWriter()

        # Crear un buffer en memoria para el nuevo contenido
        packet  = BytesIO()

        # Crear un objeto canvas de ReportLab
        pdf = canvas.Canvas(packet , pagesize=letter)
        pdf.setFont('Helvetica', 10)

        # Escribir datos en el PDF
        pdf.drawString(152, 600, f"{data['activity_date']}")
        pdf.drawString(152, 582, f"{data['om']}")
        pdf.drawString(152, 568, f"{data['client_name']}")
        pdf.drawString(152, 555, f"{data['client_line']}")
        pdf.drawString(152, 537, f"{data['person_receive_name']}")
        pdf.drawString(195, 500, f"{data['equipment_name']}")

        # Function for set the X mark on the report
        self.set_type_service(pdf, data["type_service"])
        y_position = 485
        y_position = self.ajust_long_text(pdf, data['service_description'], 195, y_position, 450)

        # Ajustar la lista de tareas justo debajo de la descripción
        tasks = data["tasks"]
        if tasks:
            y_position = self.ajust_list(pdf, tasks, x=40, y=y_position - 20)  # Ajusta el espaciado

        # Agregar las imágenes justo debajo de la lista de mantenimiento
        image_paths = data["files"]
        if image_paths:
            max_height = 170  # Altura mínima para imágenes
            y_position = self.ajust_images(pdf, image_paths, x=100, y=0, max_height=max_height, page_height=letter[1])

        # Guardar el PDF con los datos escritos en el buffer
        pdf.save()

        # Mover el buffer al principio
        packet.seek(0)

        # Leer el nuevo PDF con los datos
        new_pdf = PdfReader(packet)

        # Combinar cada página del PDF original con las páginas generadas
        for i, page in enumerate(reader.pages):
            if i == 0:  # Solo superponer en la primera página del original
                page.merge_page(new_pdf.pages[0])
                writer.add_page(page)
            else:
                writer.add_page(page)

        # Agregar las páginas adicionales del nuevo PDF (imágenes en este caso)
        for i in range(1, len(new_pdf.pages)):
            writer.add_page(new_pdf.pages[i])

        # Guardar el PDF final en memoria
        output_buffer = BytesIO()
        writer.write(output_buffer)

        # Mover el buffer al principio
        output_buffer.seek(0)

        return output_buffer.read()
    
    # Función para ajustar textos largos
    def ajust_long_text(self, can, text, x, y, max_width):
        """
        Función que ajusta el texto a varias líneas si es demasiado largo.
        :param can: El objeto canvas de ReportLab.
        :param text: El texto que se va a añadir.
        :param x: La posición x en el PDF.
        :param y: La posición y en el PDF.
        :param max_width: El ancho máximo en píxeles para una línea de texto.
        """
        # Configurar el tamaño de fuente
        can.setFont("Helvetica", 10)

        # Dividir el texto en líneas que se ajusten al ancho máximo
        wrapper = textwrap.TextWrapper(width=max_width // 6)  # Ajusta el divisor según el tamaño de fuente
        lines = wrapper.wrap(text=text)

        # Dibujar cada línea, ajustando la posición 'y' hacia arriba para cada línea
        for line in lines:
            can.drawString(x, y, line)
            y -= 12  # Ajusta el espaciado entre líneas

        return y  # Devuelve la posición y después de pintar el texto

    # Función para ajustar la lista de tareas
    def ajust_list(self, can, tasks, x, y):
        """
        Función para agregar la lista de tareas justo debajo de la descripción.
        :param can: El objeto canvas de ReportLab.
        :param tasks: La lista de tareas a dibujar.
        :param x: La posición x en el PDF.
        :param y: La posición y en el PDF.
        :return: La nueva coordenada 'y' después de haber escrito la lista de tareas.
        """
        y -= 12  # Mover hacia arriba para la lista

        # Crear los títulos de la tabla
        table_data = [["Tarea", "SI", "NO", "Descripción"]]

        # Añadir los datos de las tareas
        for task in tasks:
            row = [
                task["name"],
                "✔" if task["positive"] == 1 else "",
                "✔" if task["negative"] == 1 else "",
                task["description"]
            ]
            table_data.append(row)

        # Crear la tabla
        table = Table(table_data, colWidths=[230, 30, 30, 250])  # Ajusta los anchos de las columnas

        # Estilo de la tabla
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Fondo gris para la fila del encabezado
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Texto blanco para el encabezado
            ('ALIGN', (1, 1), (2, -1), 'CENTER'),  # Centrar "SI" y "NO"
            ('ALIGN', (3, 1), (3, -1), 'LEFT'),  # Alinear a la izquierda la columna "Descripción"
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fuente en negrita para el encabezado
            ('FONTSIZE', (0, 0), (-1, -1), 10),  # Tamaño de fuente
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),  # Espaciado inferior en el encabezado
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),  # Fondo blanco para las filas
            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Líneas de la tabla
        ])
        table.setStyle(style)

        # Determinar el tamaño de la tabla
        table_width, table_height = table.wrapOn(can, x, y)

        # Dibujar la tabla en la posición especificada
        table.drawOn(can, x, y - table_height)

        return y  # Devuelve la nueva coordenada y después de la lista

    # Función para ajustar las imagenes
    def ajust_images(self, can, image_files, x, y, max_height, page_height):
        """
        Función para agregar imágenes al PDF, comenzando siempre desde la segunda página.
        :param can: El objeto canvas de ReportLab.
        :param image_paths: Lista de rutas de imágenes.
        :param x: Posición x en el PDF.
        :param y: Posición y en el PDF.
        :param max_height: Altura máxima de una imagen.
        :param page_height: Altura total de la página.
        :return: La nueva coordenada y después de agregar las imágenes.
        """
        # Forzar una nueva página al inicio
        can.showPage()  
        y = page_height - 50  # Reiniciar la posición 'y' en la nueva página

        for image in image_files:
            image_path = image["path"]
            img_description = image["description"]
            if not img_description:
                img_description = ""

            try:
                # Dibujar la imagen en el PDF
                can.drawImage(image_path, x, y - max_height, width=300, height=max_height)

                # Colocar descripcion de imagen
                y -= max_height + 15
                can.drawString(x, y, f"{img_description}")

                # Actualizar la posición 'y'
                y -= max_height + 1  # Espaciado entre imágenes

                # Verificar si necesitamos una nueva página
                if y - max_height < 50:  # Si no hay espacio suficiente
                    can.showPage()
                    y = page_height - 50  # Reiniciar 'y' para la nueva página

            except Exception as e:
                print(f"Error al dibujar la imagen {image_path}: {e}")
                raise CustomException(f"Error al dibujar la imagen {image_path}: {e}")

        return y  # Devuelve la posición final de 'y'
    
    # Función para setear cuando un tipo de servicio fue elegido.
    def set_type_service(self, can, data):
        
        if data:
            for key in data:
                if key["id"] == 1:
                    can.drawString(535, 600, "✔")
                elif key["id"] == 2:
                    can.drawString(535, 583, "✔")
                elif key["id"] == 3:
                    can.drawString(535, 568, "✔")
                elif key["id"] == 4:
                    can.drawString(535, 553, "✔")
                elif key["id"] == 5:
                    can.drawString(535, 538, "✔")

    # """ Obtener archivo"""
    # def get_file_b64(self, file_path):
    #     with open(file_path, "rb") as file:
    #         # Leer el contenido binario del archivo PDF
    #         pdf_content = file.read()

    #         # Codificar el contenido binario en base64
    #         pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')

    #         return pdf_base64

    # async def send_email_error(self, service_name, code, request, response):
    #     load_dotenv()
    #     # Obtener enviroment
    #     stage = os.getenv("STAGE")
    #     remitente = os.getenv("EMAIL_USER")
    #     destinatario = os.getenv("EMAIL_DEV")

    #     template_url = f"{BASE_PATH_TEMPLATE}/notificacion_error.html"
    #     # Preapar el asunto del correo
    #     subject = f"TOYO - Project: Error service - Stage: {stage}"
    #     # Preparar el contenido del correo
    #     data_correo = {
    #         "servicio": "TOYO",
    #         "status_code": code,
    #         "consumo": service_name,
    #         "id_gestion": "000",
    #         "url": "Toyo_dev",
    #         "request": request,
    #         "response": response
    #     }

    #     msg = MIMEMultipart()
    #     msg["Subject"] = subject
    #     msg["From"] = remitente
    #     msg["To"] = destinatario

    #     with open(template_url, 'r') as template_file:
    #         template = template_file.read()
    #         template = template.format(**data_correo)
    #     msg.attach(MIMEText(template, 'html'))

    #     # Configura la conexión al servidor SMTP de Gmail
    #     server = smtplib.SMTP('smtp.gmail.com', 587)
    #     server.starttls()
    #     server.login(remitente, os.getenv('EMAIL_PASSWORD'))

    #     # Envía el correo
    #     server.sendmail(remitente, destinatario, msg.as_string())

    #     # Cierra la conexión con el servidor SMTP
    #     server.quit()

    # async def send_email(self, recipients, subject, body, attachments=None):
    #     sender = os.getenv("EMAIL_USER")

    #     msg = MIMEMultipart()
    #     msg["Subject"] = subject
    #     msg["From"] = sender
    #     msg["To"] = recipients

    #     msg.attach(MIMEText(body, 'html'))
    #     # Agregar archivos adjuntos en formato base64 al mensaje MIME
    #     if attachments:
    #         for attachment in attachments:
    #             # Decodificar el contenido base64
    #             decoded_data = base64.b64decode(attachment["file"])

    #             # Crear un objeto MIMEBase y adjuntar el archivo decodificado
    #             attachment_part = MIMEBase('application', 'octet-stream')
    #             attachment_part.set_payload(decoded_data)
    #             encoders.encode_base64(attachment_part)

    #             # Establecer el encabezado del archivo adjunto
    #             attachment_part.add_header('Content-Disposition', f'attachment; filename={attachment["name"]}')
    #             msg.attach(attachment_part)

    #     # Configurar conexion con servidor SMTP
    #     server = smtplib.SMTP('smtp.gmail.com', 587)
    #     server.starttls()
    #     server.login(sender, os.getenv('EMAIL_PASSWORD'))
    #     server.sendmail(sender, recipients, msg.as_string())
    #     # Cerrar conexion Con servidor
    #     server.quit()


class CustomException(Exception):
    """ Esta clase hereda de la clase Exception y permite
        interrumpir la ejecucion de un metodo invocando una excepcion
        personalizada """
    def __init__(self, message="", codigo=400, data={}):
        self.codigo = codigo
        self.message = message
        self.data = data
        self.resultado = {
            "body": {
                "statusCode": codigo,
                "message": message,
                "data": data,
                "Exception": "CustomException"
            }
        }

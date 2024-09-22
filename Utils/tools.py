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
        pdf.drawString(310, 545, f"{data['intervened_item']}")
        pdf.drawString(195, 522, f"{data['activity_date']}")
        pdf.drawString(195, 508, f"{data['client']}")
        pdf.drawString(195, 494, f"{data['service_order']}")
        pdf.drawString(195, 480, f"{data['solped']}")
        pdf.drawString(195, 466, f"{data['person_receives']}")
        pdf.drawString(400, 522, f"{data['buy_order']}")
        y_position = 400
        y_position = self.ajust_long_text(pdf, data['description'], 77, y_position, 550)

        # Ajustar la lista de tipos de mantenimiento justo debajo de la descripción
        maintenance_list = data["type_maintenance"]
        if maintenance_list:
            y_position = self.ajust_list(pdf, maintenance_list, x=57, y=y_position - 20)  # Ajusta el espaciado

        # Agregar las imágenes justo debajo de la lista de mantenimiento
        image_paths = data["files"]
        if image_paths:
            max_height = 170  # Altura mínima para imágenes
            y_position = self.ajust_images(pdf, image_paths, x=100, y=y_position - 20, max_height=max_height, page_height=letter[1])

        # Guardar el PDF con los datos escritos en el buffer
        pdf.save()

        # Mover el buffer al principio
        packet.seek(0)

        # Leer el nuevo PDF con los datos
        new_pdf = PdfReader(packet)

        # Combinar cada página del PDF original con la página nueva
        print(len(reader.pages))
        for i in range(len(reader.pages)):
            page = reader.pages[i]
            print(page)
            if i == 0:  # Solo superponemos los datos en la primera página
                page.merge_page(new_pdf.pages[0])
            writer.add_page(page)

        # Guardar el PDF final en memoria
        output_buffer = BytesIO()
        writer.write(output_buffer)

        # Mover el buffer al principio
        output_buffer.seek(0)

        return output_buffer.read()
    
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

    def ajust_list(self, can, maintenance_list, x, y):
        """
        Función para agregar la lista de mantenimientos justo debajo de la descripción.
        :param can: El objeto canvas de ReportLab.
        :param maintenance_list: La lista de mantenimientos a dibujar.
        :param x: La posición x en el PDF.
        :param y: La posición y en el PDF.
        :return: La nueva coordenada 'y' después de haber escrito la lista de mantenimientos.
        """
        y -= 12  # Mover hacia arriba para la lista

        # Dibujar cada mantenimiento de la lista
        for maintenance in maintenance_list:
            can.drawString(x + 20, y, f"- {maintenance['name']}")
            y -= 12  # Ajusta el espaciado entre los elementos de la lista

        return y  # Devuelve la nueva coordenada y después de la lista

    def ajust_images(self, can, image_paths, x, y, max_height, page_height, images_per_row=2):
        """
        Función para agregar imágenes desde una lista de rutas en filas de 2, y crear nuevas páginas si es necesario.
        """
        image_width = 200  # Ancho de cada imagen
        image_height = 150  # Altura de cada imagen
        spacing_x = 20  # Espacio entre las imágenes horizontalmente
        spacing_y = 20  # Espacio entre las imágenes verticalmente

        images_in_current_row = 0
        x_start = x

        cont=0

        for image_path in image_paths:
            cont+=1

            # Verifica si la imagen cabe en la página actual
            if y < max_height:
                can.showPage()  # Crea una nueva página si no hay suficiente espacio
                y = page_height - 50  # Resetea la posición 'y' en la nueva página
                x = x_start
                images_in_current_row = 0

            # Cargar la imagen desde la ruta
            if os.path.exists(image_path["path"]):
                img = ImageReader(image_path["path"])
                can.drawImage(img, x, y - image_height, width=image_width, height=image_height)  # Ajusta el tamaño de la imagen
                images_in_current_row += 1

                # Si se han añadido 2 imágenes, pasa a la siguiente fila
                if images_in_current_row >= images_per_row:
                    images_in_current_row = 0
                    y -= image_height + spacing_y  # Ajusta la posición y para la siguiente fila
                    x = x_start  # Resetea la posición x para una nueva fila de imágenes
                else:
                    x += image_width + spacing_x
        return y

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

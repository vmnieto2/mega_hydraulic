from .validator import Validator


class Rules:
    """ Esta clase se encarga de validar los datos de entrada de la API
        y si hay un error, lanza una excepcion """

    val = Validator()

    def __init__(self, path: str, params: dict):
        path_dict = {
            "/login": self.__val_login,
            "/reports/create_report": self.__val_create_report,
            "/maintenance_types": self.__val_maintenance_types,
        }
        # Se obtiene la funcion a ejecutar
        func = path_dict.get(path, None)
        if func:
            # Se ejecuta la funcion para obtener las reglas de validacion
            validacion_dict = func(params)

            # Se valida la datas
            self.val.validacion_datos_entrada(validacion_dict)
            
    # Validate data login
    def __val_login(self, params):
        validacion_dict = [
            {
                "tipo": "string",
                "campo": "documento",
                "valor": params["document"],
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "contraseña",
                "valor": params["password"],
                "obligatorio": True,
            }
        ]
        return validacion_dict

    # Validate data create report
    def __val_create_report(self, params):
        validacion_dict = [
            {
                "tipo": "string",
                "campo": "equipo intervenido",
                "valor": params["intervened_item"],
                "obligatorio": True,
            },
            {
                "tipo": "date",
                "campo": "fecha actividad",
                "valor": params["activity_date"],
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "cliente",
                "valor": params["client"],
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "orden servicio",
                "valor": params["service_order"],
                "obligatorio": False,
            },
            {
                "tipo": "string",
                "campo": "solicitud pedido",
                "valor": params["solped"],
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "persona que recibe",
                "valor": params["person_receives"],
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "orden de compra",
                "valor": params["buy_order"],
                "obligatorio": True,
            },
            {
                "tipo": "string",
                "campo": "descripción",
                "valor": params["description"],
                "obligatorio": True,
            },
            {
                "tipo": "list",
                "campo": "tipos de mantenimiento",
                "valor": params["maintenance_types"],
                "obligatorio": False,
            },
            {
                "tipo": "int",
                "campo": "usuario",
                "valor": params["user_id"],
                "obligatorio": True,
            },
            {
                "tipo": "list",
                "campo": "archivos",
                "valor": params["files"],
                "obligatorio": False,
            }
        ]
        return validacion_dict

    # Validate data for typoes of maintenance
    def __val_maintenance_types(self, params):
        validacion_dict = [
            {
                "tipo": "int",
                "campo": "tipo mantenimiento",
                "valor": params,
                "obligatorio": True,
            }
        ]
        return validacion_dict

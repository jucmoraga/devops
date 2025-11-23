from flask import request
from flask_restful import Resource
from app.utils.helper import Helper
from app.services.blacklist_crud import BlacklistCRUD
from flask_jwt_extended import jwt_required, create_access_token

#Creamos instancia del CRUD
blacklist_crud = BlacklistCRUD()

class BlacklistToken(Resource):
    def post(self):
        #Creamos token JWT
        token = create_access_token(identity = 'blacklist_service')
        return {'token': token}, 200

class BlacklistRegister(Resource):
    @jwt_required()
    def post(self):
        #Obtenemos los datos del request
        data = request.get_json()
        
        #Validamos que todos los campos necesarios esten presentes
        if not all(key in data for key in ('email', 'appId')):
            return {'msg': 'Hay campos necesarios que no están presentes en la solicitud'}, 400

        #Validamos que los campos no estén vacíos
        if not data.get('email'):
            return {'msg': 'El campo email no puede estar vacío'}, 400

        if not data.get('appId'):
            return {'msg': 'El campo appId no puede estar vacío'}, 400
        
        #Normalizamos los datos
        data = Helper.normalizeRequest(data)

        #Validamos que el email tenga un formato correcto
        if not Helper.validateEmail(data.get('email')):
            return {'msg': 'El email proporcionado no tiene un formato válido'}, 400

        #Validamos que el appId sea un UUID valido
        if not Helper.validateUUID(data.get('appId')):
            return {'msg': 'El appId proporcionado no es un UUID válido'}, 400

        #Validamos la longitud del campo blockedReason si esta presente
        # if data.get('blockedReason'):
        #     if len(data.get('blockedReason')) > 255:
        #         return {'msg': 'El campo blockedReason no puede exceder 255 caracteres'}, 400

        #Validamos que el email no este ya en la lista negra
        email_existente = blacklist_crud.getEmailFromBlacklist(data.get('email'))

        if email_existente.get('found'):
            return {'msg': 'El email ya se encuentra en la lista negra'}, 412

        #Obtenemos ip del request
        data = Helper.getIpAddress(data, request)

        #Validamos si se pudo obtener la ip
        if not data.get('ipAddress'):
            return {'msg': 'No se pudo obtener la dirección IP del cliente'}, 400

        #Guardamos el email en base de datos
        salida = blacklist_crud.addEmailToBlacklist(data)

        #Validamos si hubo un error al guardar en base de datos
        if isinstance(salida, str):
            return {'msg': f'Error al agregar el email a la lista negra: {salida}'}, 500

        return {'msg': 'Usuario agregado a la lista negra exitosamente'}, 200

class BlacklistGetEmail(Resource):
    @jwt_required()
    def get(self, email):
        #validamos que el email no este vacio
        if not email:
            return {'msg': 'Se requiere un parámetro de búsqueda'}, 400

        #Validamos que el email tenga un formato correcto
        if not Helper.validateEmail(email):
            return {'msg': 'El email proporcionado no tiene un formato válido'}, 400

        #Buscamos el email en la base de datos
        salida = blacklist_crud.getEmailFromBlacklist(email)

        #Validamos si hubo un error al buscar en base de datos
        if not salida.get('found'):
            return {'msg': f"El email {email} no se encuentra en la lista negra"}, 404

        return salida, 200

class BlacklistHealth(Resource):
    def get(self):
        return {'status': 'pong verde'}, 200

class BlacklistDelete(Resource):
    def post(self):
        #Borramos todos los registros de la lista negra
        salida = blacklist_crud.deleteAllBlacklist()

        #Validamos si hubo un error al eliminar los registros
        if isinstance(salida, str):
            return {'msg': f'Error al eliminar los registros de la lista negra: {salida}'}, 500
        
        return {'msg': 'Todos los registros de la lista negra han sido eliminados'}, 200
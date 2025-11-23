import pytest
from flask import Flask
from flask_jwt_extended import JWTManager
from app.api.api import BlacklistRegister

@pytest.fixture
def app():
    #Creamos una aplicacion de Flask para pruebas
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = 'supersecretkey'
    JWTManager(app)

    return app

def test_blacklist_register_campos_faltantes(app, mocker):
    #Mockeamos la verificacion del JWT para que siempre pase
    mocker.patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')

    #Simulamos un request JSON
    with app.test_request_context(
        '/v1/blacklists',
        method = 'POST',
        json = {'email': 'test@example.com'},
    ):
        #Importamos la clase BlacklistRegister
        resource = BlacklistRegister()

        #Llamamos el metodo post a probar la validacion de campos faltantes
        response, status = resource.post()
        
        #Salidas esperadas
        assert status == 400
        assert response == {
            'msg': 'Hay campos necesarios que no están presentes en la solicitud'
        }

def test_blacklist_register_email_vacio(app, mocker):
    #Mockeamos la verificacion del JWT para que siempre pase
    mocker.patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')

    #Simulamos un request JSON
    with app.test_request_context(
        '/v1/blacklists',
        method = 'POST',
        json = {'email': '', 'appId': '123e4567-e89b-12d3-a456-426614174000'},
    ):
        
        #Importamos la clase BlacklistRegister
        resource = BlacklistRegister()

        #Llamamos el metodo post a probar la validacion de email vacio
        response, status = resource.post()
        
        #Salidas esperadas
        assert status == 400
        assert response == {
            'msg': 'El campo email no puede estar vacío'
        }

def test_blacklist_register_appId_vacio(app, mocker):
    #Mockeamos la verificacion del JWT para que siempre pase
    mocker.patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')

    #Simulamos un request JSON
    with app.test_request_context(
        '/v1/blacklists',
        method = 'POST',
        json = {'email': 'test@example.com', 'appId': ''},
    ):
        
        #Importamos la clase BlacklistRegister
        resource = BlacklistRegister()

        #Llamamos el metodo post a probar la validacion de email vacio
        response, status = resource.post()
        
        #Salidas esperadas
        assert status == 400
        assert response == {
            'msg': 'El campo appId no puede estar vacío'
        }

def test_blacklist_register_invalid_email(app, mocker):
    #Mockeamos la verificacion del JWT para que siempre pase
    mocker.patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')

    #Simulamos un request JSON
    with app.test_request_context(
        '/v1/blacklists',
        method = 'POST',
        json = {'email': 'email-invalid', 'appId': '123e4567-e89b-12d3-a456-426614174000'},
    ):
        
        #Importamos la clase BlacklistRegister
        resource = BlacklistRegister()

        #Llamamos el metodo post a probar la validacion de email vacio
        response, status = resource.post()
        
        #Salidas esperadas
        assert status == 400
        assert response == {
            'msg': 'El email proporcionado no tiene un formato válido'
        }

def test_blacklist_register_invalid_appId(app, mocker):
    #Mockeamos la verificacion del JWT para que siempre pase
    mocker.patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')

    #Simulamos un request JSON
    with app.test_request_context(
        '/v1/blacklists',
        method = 'POST',
        json = {'email': 'test@example.com', 'appId': 'appId-invalid'},
    ):
        
        #Importamos la clase BlacklistRegister
        resource = BlacklistRegister()

        #Llamamos el metodo post a probar la validacion de email vacio
        response, status = resource.post()
        
        #Salidas esperadas
        assert status == 400
        assert response == {
            'msg': 'El appId proporcionado no es un UUID válido'
        }

def test_blacklist_register_email_ya_en_blacklist(app, mocker):
    #Mockeamos la verificacion del JWT para que siempre pase
    mocker.patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')

    #Respuesta falsa para simular que el email ya existe en la blacklist
    fake_response = {'email': 'test@example.com', 'found': True, 'blockedReason': 'Spam'}

    #Mockeamos el metodo getEmailFromBlacklist para simular que el email ya existe
    mocker.patch('app.services.blacklist_crud.BlacklistCRUD.getEmailFromBlacklist', return_value = fake_response)

    #Simulamos un request JSON
    with app.test_request_context(
        '/v1/blacklists',
        method = 'POST',
        json = {'email': 'test@example.com', 'appId': '123e4567-e89b-12d3-a456-426614174000'},
    ):

        #Importamos la clase BlacklistRegister
        resource = BlacklistRegister()

        #Llamamos el metodo post a probar la validacion de email vacio
        response, status = resource.post()

        #Salidas esperadas
        assert status == 412
        assert response == {
            'msg': 'El email ya se encuentra en la lista negra'
        }

def test_blacklist_register_no_reason(app, mocker):
    #Mockeamos la verificacion del JWT para que siempre pase
    mocker.patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')

    #Respuesta falsa para simular que el email ya existe en la blacklist
    fake_duplicate = {'email': 'test@example.com', 'found': False}

    #Mockeamos el metodo getEmailFromBlacklist para simular que el email ya existe
    mocker.patch('app.services.blacklist_crud.BlacklistCRUD.getEmailFromBlacklist', return_value = fake_duplicate)

    #Respuesta fake para traer la ip
    fake_ip_address = {
        'email': 'test@example.com', 
        'appId': '123e4567-e89b-12d3-a456-426614174000',
        'ipAddress': '192.168.1.1'
    }

    #Mockeamos el metodo getIpAddress para simular la obtencion de la ip
    mocker.patch('app.utils.helper.Helper.getIpAddress', return_value = fake_ip_address)

    #Mockeamos el metodo getEmailFromBlacklist para simular que el email no existe
    mocker.patch('app.services.blacklist_crud.BlacklistCRUD.addEmailToBlacklist', return_value = None)

    #Simulamos un request JSON
    with app.test_request_context(
        '/v1/blacklists',
        method = 'POST',
        json = {'email': 'test@example.com', 'appId': '123e4567-e89b-12d3-a456-426614174000'},
    ):

        #Importamos la clase BlacklistRegister
        resource = BlacklistRegister()

        #Llamamos el metodo post a probar la validacion de email vacio
        response, status = resource.post()

        #Salidas esperadas
        assert status == 200
        assert response == {
            'msg': 'Usuario agregado a la lista negra exitosamente'
        }

def test_blacklist_register(app, mocker):
    #Mockeamos la verificacion del JWT para que siempre pase
    mocker.patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')

    #Respuesta falsa para simular que el email ya existe en la blacklist
    fake_response = {'email': 'test@example.com', 'found': False}

    #Mockeamos el metodo getEmailFromBlacklist para simular que el email ya existe
    mocker.patch('app.services.blacklist_crud.BlacklistCRUD.getEmailFromBlacklist', return_value = fake_response)

    #Respuesta fake para traer la ip
    fake_ip_address = {
        'email': 'test@example.com', 
        'appId': '123e4567-e89b-12d3-a456-426614174000',
        'blockedReason': 'Spam',
        'ipAddress': '192.168.1.1'
    }

    #Mockeamos el metodo getIpAddress para simular la obtencion de la ip
    mocker.patch('app.utils.helper.Helper.getIpAddress', return_value = fake_ip_address)

    #Mockeamos el metodo getEmailFromBlacklist para simular que el email no existe
    mocker.patch('app.services.blacklist_crud.BlacklistCRUD.addEmailToBlacklist', return_value = None)

    #Simulamos un request JSON
    with app.test_request_context(
        '/v1/blacklists',
        method = 'POST',
        json = {'email': 'test@example.com', 'appId': '123e4567-e89b-12d3-a456-426614174000', 'blockedReason': 'Spam'},
    ):

        #Importamos la clase BlacklistRegister
        resource = BlacklistRegister()

        #Llamamos el metodo post a probar la validacion de email vacio
        response, status = resource.post()

        #Salidas esperadas
        assert status == 200
        assert response == {
            'msg': 'Usuario agregado a la lista negra exitosamente'
        }
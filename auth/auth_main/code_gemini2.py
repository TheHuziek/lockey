import json
import os
import secrets
import time
import bcrypt
import boto3
from botocore.exceptions import ClientError

# Inicialización de clientes fuera del handler para reutilización de conexiones
dynamodb = boto3.resource('dynamodb')

USERS_TABLE_NAME = os.environ.get('USERS_TABLE', 'Users')
SESSIONS_TABLE_NAME = os.environ.get('SESSIONS_TABLE', 'Sessions')
SESSION_DURATION_SECONDS = int(os.environ.get('SESSION_DURATION', 3600))  # 1 hora por defecto

users_table = dynamodb.Table(USERS_TABLE_NAME)
sessions_table = dynamodb.Table(SESSIONS_TABLE_NAME)


def build_response(status_code: int, body: dict) -> dict:
    """Estructura la respuesta HTTP para API Gateway / Function URL."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'  # Ajusta según tu política de CORS
        },
        'body': json.dumps(body)
    }


def verify_password(stored_hash: str, password: str) -> bool:
    """Verifica la contraseña ingresada contra el hash bcrypt guardado."""
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))


def create_session(username: str) -> dict:
    """Genera una llave de sesión temporal y la almacena con TTL en DynamoDB."""
    token = secrets.token_hex(32)
    now = int(time.time())
    expires_at = now + SESSION_DURATION_SECONDS

    sessions_table.put_item(
        Item={
            'session_token': token,
            'username': username,
            'created_at': now,
            'expires_at': expires_at  # DynamoDB eliminará este registro automáticamente
        }
    )

    return {
        'token': token,
        'expires_at': expires_at,
        'ttl_seconds': SESSION_DURATION_SECONDS
    }


def lambda_handler(event, context):
    try:
        # Parseo del body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})

        username = body.get('username')
        password = body.get('password')

        if not username or not password:
            return build_response(400, {'error': 'Se requieren username y password'})

        # 1. Buscar usuario en DynamoDB
        response = users_table.get_item(Key={'username': username})
        user_item = response.get('Item')

        # Control de tiempos defensivo para mitigar timing attacks
        if not user_item:
            # Ejecutamos una verificación ficticia para consumir un tiempo similar
            bcrypt.checkpw(b"dummy", b"$2b$12$eImiTXuWVfxh0Fi5YvVdA.8a.P.22/d4D8c/6t4pZtWpZ7D5Q4k9C")
            return build_response(401, {'error': 'Credenciales inválidas'})

        # 2. Verificar credenciales
        stored_password_hash = user_item.get('password_hash')
        if not stored_password_hash or not verify_password(stored_password_hash, password):
            return build_response(401, {'error': 'Credenciales inválidas'})

        # 3. Generar token temporal de sesión
        session_data = create_session(username)

        return build_response(200, {
            'message': 'Autenticación exitosa',
            'session': session_data
        })

    except ClientError as e:
        print(f"Error en DynamoDB: {e.response['Error']['Message']}")
        return build_response(500, {'error': 'Error interno del servidor'})
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return build_response(500, {'error': 'Error al procesar la solicitud'})
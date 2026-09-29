import json
import os
import bcrypt
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
USERS_TABLE_NAME = os.environ.get('USERS_TABLE', 'Users')
users_table = dynamodb.Table(USERS_TABLE_NAME)


def build_response(status_code: int, body: dict) -> dict:
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }


def lambda_handler(event, context):
    try:
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})

        username = body.get('username')
        password = body.get('password')

        if not username or not password:
            return build_response(400, {'error': 'Se requieren username y password'})

        if len(password) < 8:
            return build_response(400, {'error': 'La contraseña debe tener al menos 8 caracteres'})

        # Hash de contraseña
        salt = bcrypt.gensalt(rounds=12)
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

        # Insertar con verificación de duplicado
        users_table.put_item(
            Item={
                'username': username,
                'password_hash': password_hash
            },
            ConditionExpression='attribute_not_exists(username)'
        )

        return build_response(201, {
            'message': f"Usuario '{username}' creado exitosamente"
        })

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return build_response(409, {'error': 'El nombre de usuario ya está registrado'})
        return build_response(500, {'error': 'Error al guardar en la base de datos'})

    except Exception as e:
        print(f"Error: {str(e)}")
        return build_response(500, {'error': 'Error interno del servidor'})
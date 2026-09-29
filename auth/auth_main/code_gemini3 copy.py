import os
import getpass
import bcrypt
import boto3
from botocore.exceptions import ClientError

# Configuración
REGION_NAME = os.environ.get('AWS_REGION', 'us-east-1')
TABLE_NAME = os.environ.get('USERS_TABLE', 'Users')

dynamodb = boto3.resource('dynamodb', region_name=REGION_NAME)
table = dynamodb.Table(TABLE_NAME)


def hash_password(password: str) -> str:
    """Genera un salt y aplica bcrypt a la contraseña."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def register_user(username: str, password: str, custom_attributes: dict = None) -> bool:
    """Inserta un nuevo usuario en la tabla DynamoDB si no existe previa coincidencia."""
    password_hash = hash_password(password)

    item = {
        'username': username,
        'password_hash': password_hash,
    }

    if custom_attributes:
        item.update(custom_attributes)

    try:
        # ConditionExpression previene sobrescribir un usuario existente
        table.put_item(
            Item=item,
            ConditionExpression='attribute_not_exists(username)'
        )
        print(f"✅ Usuario '{username}' registrado exitosamente.")
        return True

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print(f"❌ Error: El usuario '{username}' ya existe.")
        else:
            print(f"❌ Error en DynamoDB: {e.response['Error']['Message']}")
        return False


if __name__ == '__main__':
    print("=== Registro de Usuarios (DynamoDB) ===")
    user_input = input("Ingresa el nombre de usuario: ").strip()
    pass_input = getpass.getpass("Ingresa la contraseña: ").strip()
    confirm_pass = getpass.getpass("Confirma la contraseña: ").strip()

    if not user_input or not pass_input:
        print("❌ Error: Usuario y contraseña no pueden estar vacíos.")
    elif pass_input != confirm_pass:
        print("❌ Error: Las contraseñas no coinciden.")
    else:
        register_user(user_input, pass_input)
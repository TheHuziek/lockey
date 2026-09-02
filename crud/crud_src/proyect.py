import lockey_crud

usuario_input = input("Ingrese su usuario: ")
password_input = input("Ingrese su contraseña: ")


if lockey_crud.validar_usuario(usuario_input, password_input):
    lista_contraseñas = lockey_crud.obtener_contraseñas(usuario_input)
    print("Acceso Permitido.")
    print("Lista de contraseñas:", lista_contraseñas)
else:
    print("Usuario o contraseña incorrectos.")
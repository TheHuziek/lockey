user = input("Ingrese su usuario: ")
password = input("Ingrese su contraseña: ")


if user == "jose@test.com":
  if password == "jose-contra":
    print("Acceso total")
  else:
    print("Acceso restringido")
    if password != "jose-contra": 
      print("Activa la verificacion en dos pasos")
    elif password != "jose-contra":
      print("Verificacion en dos pasos activada")
else:
  print("Acceso restringido")
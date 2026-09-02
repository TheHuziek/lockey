import libros

while True:
    print("\n--- Menú Biblioteca ---")
    print("1. mostrar libros disponibles")
    print("2. Mostrar información del libro")
    print("3. Salir")

    opcion = input("Elige una opción: ")
    

    if opcion == "1":
        print("Libros disponibles:")
        for titulo in libros.libros:
            print(f"- {titulo}")
    elif opcion == "2":
        titulo = input("Ingrese el título del libro: ")
        libro = libros.libros.get(titulo)
        if libro:
            print(f"Autor: {libro['autor']}")
            print(f"Año: {libro['año']}")
            print(f"Descripción: {libro['descripcion']}")
        else:
            print("Libro no encontrado.")
    elif opcion == "3":
        print("Saliendo del sistema...")
        break
    else:
        print("Opción inválida.")

usuario 

print("que quieres hacer , 1 crear usuario , 2 modificar usuario , 3 eliminar usuario, 4 salir\n")

opcion = int(input("ingresa la opcion: "))

match opcion:
    case 1:
        # user = User(name, email)
        # user.create_user()
        print(" ususario creado ")
    case 2:
        print("modificar usuario")
    case 3:
        print("eliminar usuario")
    case 4:
        print("saliendo...")
    case _:
        print("opcion no valida")


# class User
# def __init__(self, name, email):
# def create_user(self):
# def modify_user(self):
# def delete_user(self):

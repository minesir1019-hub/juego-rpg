1 al 3

print("hola escriba un numero del uno al tres")
numero = int(input())
match numero:
     case 1:
          print("uno")
     case 2:
          print("dos")
     case 3:
          print("tres")
     case _:
          print("Número no válido")

print("deme un numero del 1 al 7")
dia= int(input())
match dia:
        case 1: print("lunes")
        case 2: print("martes")
        case 3: print("miercoles")
        case 4: print("jueves")
        case 5: print("viernes")
        case 6: print("sabado")
        case 7: print("domingo")
        case _: print("Número no válido")
            
ds = int(input("qeu quiere hacer,1 info a ,2 info b,3 info c,4 salir "))
while (True):
        match ds:
            case 1: print("123214")
            case 2: print("567890")
            case 3: print("111111")
            case 4: print("saliendo del programa")
            case _: print("opción no válida")
        if ds == 4:
            break
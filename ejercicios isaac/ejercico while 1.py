n1=int(input("hola escribe el primer numero"))
n2=int(input("hola escribe un segun numero"))
el=int(input("ahora que quieres hacer , 1 sumar,2 restar,3 multiplicar,4 dividir"))
match el:
    case 1:       print("la suma de los dso nueros es", n1+n2)
    case 2:       print("la resta de los dos numeros es", n1-n2)
    case 3:       print("la multiplicacion de los dos numeros es", n1*n2)
    case 4:       print("la division de los dos numeros es", n1/n2)
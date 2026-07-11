print("cual es tu edad")
edad = int(input())
print("ahora escribe osi trbajas o no, 0 para no y 1 para si")
numero2= int(input())
if edad >= 18 and numero2 == 1:
    print("puedes trabajar")
    elif edad >= 18 and numero2 == 0:
        print("estas desempleado")
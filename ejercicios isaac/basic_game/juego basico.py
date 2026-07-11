import time
import random


class Personaje:
    def __init__(self, life, name, velocidad):
        self.life = life
        self.name = name
        self.velocidad = velocidad

# warrior hereda de Personaje

# warrior = Warrior("Isaac", 100, "Espada", "Armadura")
class Warrior(Personaje):
     def __init__ (self,life,name,weapon,armor,velocidad):
        super().__init__(life, name, velocidad)
        self.weapon=weapon
        self.armor=armor

   
class weapon:
     def __init__ (self,damage,name):
         self.damage=damage
         self.name=name

class armor:
     def __init__ (self,defense,name):
         self.defense=defense
         self.name=name

class Enemy(Personaje):
     def __init__(self,life,name,velocidad,weapon,armor,clasificasion):
        super().__init__(life, name,velocidad)
        self.weapon=weapon
        self.armor=armor
        self.classification=clasificasion



class YouEnemy(Enemy):  
    def __init__(self,life,name,velocidad,weapon,armor,clasificasion):
        super().__init__(life, name,velocidad,weapon,armor,clasificasion)      




class you(Warrior):
     def __init__(self,life,name,weapon,armor,velocidad):
        super().__init__(life, name, weapon, armor, velocidad) 

class room:
     def __init__(self,name):
        self.posibilidad=random.randint(0,5)              
        self.name=name

class door(room):
     def __init__(self,name):
        super().__init__(name)


# Metodo Combate
def combate(warrior, enemy):
    while warrior.life > 0 and enemy.life > 0:
        # Turno del jugador
        print(f"Turno de {warrior.name}:")
        print(f"Vida: {warrior.life}")
        print(f"Vida del enemigo: {enemy.life}")
        action = input("Elige una acción (atacar, huir): ")
        
        if action == "atacar":
            damage = warrior.weapon.damage - enemy.armor.defense
            damage = max(damage, 0)  # Asegurarse de que el daño no sea negativo
            enemy.life -= damage
            print(f"{warrior.name} ataca a {enemy.name} causando {damage} de daño.")
        
        elif action == "huir":
            print(f"{warrior.name} huye del combate.")
            break
        
        else:
            print("Acción no válida. Intenta de nuevo.")
            continue
        
        # Turno del enemigo
        if enemy.life > 0:
            print(f"Turno de {enemy.name}:")
            damage = enemy.weapon.damage - warrior.armor.defense
            damage = max(damage, 0)  # Asegurarse de que el daño no sea negativo
            warrior.life -= damage
            print(f"{enemy.name} ataca a {warrior.name} causando {damage} de daño.")
    
    if warrior.life <= 0:
        print(f"{warrior.name} ha sido derrotado por {enemy.name}.")
    elif enemy.life <= 0:
        print(f"{enemy.name} ha sido derrotado por {warrior.name}.")



def random_encounter1():
    encounter = random.randint(0, 5)
    if encounter == 0:
        print("No te encuentras con nada.")
    elif encounter == 1:
        print("Te encuentras con un enemigo.")
        enemy = random_enemy()
        eleccion_puerta(enemy)
    elif encounter == 2:
        print("Te encuentras con un cofre.")  
    elif encounter == 3:
        print("No te encuentras con nada.")
    elif encounter == 4:
        print("No te encuentras con nada.")
    elif encounter == 5:
        print("No te encuentras con nada.")  

def random_encounter2():
    encounter = random.randint(0, 5)
    if encounter == 0:
        print("Te encuentras con un enemigo.")
        enemy = random_enemy()
        eleccion_puerta(enemy)
    elif encounter == 1:
        print("Te encuentras con un enemigo.")
        enemy = random_enemy()
        eleccion_puerta(enemy)
    elif encounter == 2:
        print("Te encuentras con un enemigo.")  
        enemy = random_enemy()
        eleccion_puerta(enemy)
    elif encounter == 3:
        print("Te encuentras con un cofre.")
    elif encounter == 4:
        print("Te encuentras con un cofre.")
    elif encounter == 5:
        print("Te encuentras con un cofre.")

def random_encounter3():
    encounter = random.randint(0, 5)
    if encounter == 0:
        print("Te encuentras con un habitante de la mazmorra.")
    elif encounter == 1:
        print("Te encuentras con un cofre misterioso.")
    elif encounter == 2:
        print("Te encuentras con un cáliz lleno de un líquido misterioso.")  
    elif encounter == 3:
        print("Te encuentras con una abominación de la mazmorra.")
    elif encounter == 4:
        print("No te encuentras con nada.")
    elif encounter == 5:
        print("No te encuentras con nada.")    


def random_enemy():
    match random.randint(0,2):
        case 0:
            print("El enemigo es un: ", enemy1.name)
            return enemy1
        case 1:
            print("El enemigo es un: ", enemy2.name)
            return enemy2
        case 2:
            print("El enemigo es un: ", enemy3.name)
            return enemy3
     
    

def eleccion_puerta(enemy):
    while you.life > 0 and enemy.life > 0:
                
                
                match input("que quieres hacer ?\n1. Atacar\n2. Huir\n3.ver tus estadisiticas\n4. ver tu inventario"):
                    case "1":
                        time.sleep(1)
                        combate(you, enemy)
                    case "2":
                        print("huyes del enemigo y te encuentras con otra puerta")
                        break
                    case "3":
                        print(f"Estadísticas de {you.name}: Vida: {you.life}\n, Velocidad: {you.velocidad}\n,")
                    case "4":
                        print("Mostrando inventario...")
                        time.sleep(1)
                        print(f"Arma: {you.weapon.name}\n, Daño: {you.weapon.damage}\n")

# Instancias

espada_d=weapon(10,"espada de hierro")
espada_c=weapon(15,"espada de acero")
espada_b=weapon(20,"espada de acero templado")

armadura_d=armor(5,"armadura de hierro")
armadura_c=armor(10,"armadura de acero")
armadura_b=armor(15,"armadura de acero templado")

puerta_a=room("la primera puerta")
puerta_b=room("la segunda puerta")
puerta_c=room("la tercera puerta")



guerrero2=Warrior(70,"picaro",espada_c,armadura_d,15)
guerrero1=Warrior(100,"espadachin",espada_d,armadura_c,10)

enemy1=Enemy(50,"goblin comun",5,espada_d,armadura_d,"goblin picaro")
enemy2=Enemy(100,"goblin jefe",10,espada_c,armadura_c,"goblin guerrero")
enemy3=Enemy(150,"goblin rey",15,espada_b,armadura_b,"goblin rey")



print("eres  un aventurero que a buscado y encontrado una mazmorra para desafiar su echizo y ganar para quedarte con sus tesoros")
time.sleep(2)
print("asi que entras")
time.sleep(2)
print("       000    00  00000  0   0 0     0  00000  o   o  oo  oooo     0000                       ")
print("       0  0       0      00  0  0   0   0      oo  o      o   oo  00  00                      ")
print("       0000   00  0000   0 0 0  00 00   0000   o o o  oo  o    o  0    0                      ")
print("       0   0  00  0      0  00   000    0      o  oo  oo  o   oo  00  00                      ")
print("       0000   00  00000  0   0    0     00000  o   o  oo  oooo     0000                       ")


time.sleep(2)
print("eligue un gerrero") 
switch = input("1. Espadachin\n2. Picaro\n")
time.sleep(1)
  # Como hacer para que el jugador elija su personaje y se guarde en la variable you
if switch == "1": 
    print("has elegido a tu espadachin")
    you=guerrero1
elif switch == "2":
    print("has elegido a tu picaro")
    you=guerrero2

time.sleep(1)
print("empiezas a recorrer la mazmorra")
time.sleep(1)

switch = input("¿ te encuentras con tres puertas ,cual quieres abrir ?.\n1. La primera puerta\n2. La segunda puerta\n3. La tercera puerta\n")
if switch == "1":
    print("has elegido la primera puerta")
    random_encounter1()
elif switch == "2":
    print("has elegido la segunda puerta")
    random_encounter2()
elif switch == "3":
    print("has elegido la tercera puerta")
    random_encounter3()
    
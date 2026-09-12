import pygame

pygame.init()


ANCHO , ALTO = 960 , 540
pantalla = pygame.display.set_mode((ANCHO,ALTO))
pygame.display.set_caption("JUEGAZO")
reloj = pygame.time.clock()
CENTRO_PANTALLA = pygame.vector2(ANCHO / 3, ALTO / 2)





class Jugador:
        def __init__(self, nombre, arma, vida, velocidad):          
            self.vida=vida
            self.nombre=nombre
            self.velocidad=velocidad

        

arma1 = Arma("Pistola 9mm")
isa = Jugador("Isa", arma1, 100, 200)

isa.moverse()

         
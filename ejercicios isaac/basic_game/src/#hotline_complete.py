#hotline_complete
import pygame

ancho,alto = 800,600
pantalla = pygame.display.set_mode((ancho,alto))
pygame.display.set_caption("Hotline La Matanza")

class Jugador:
    def __init__(self,posicion,movimiento,vida,arma):
        self.movimiento = movimiento
        self.vida = vida
        self.posicion = posicion
        self.arma = arma

class Arma:
      def __init__(self,cadencia,municion,bala):
            self.cadencia = cadencia
            self.municion = municion
            self.bala = bala

class Camara:
    def __init__(self,posicion):
        self.posicion = posicion

class Bala:
    def __init__(self,posicion,velocidad,daño):
        self.posicion = posicion
        self.velocidad = velocidad
        self.daño = daño

bala1 = Bala(pygame.Vector2(0,0),pygame.Vector2(10,0),1)
metralleta = Arma(0.1,30,bala1)
personaje = Jugador(pygame.Vector2(400,300),pygame.Vector2(0,0),1,metralleta)



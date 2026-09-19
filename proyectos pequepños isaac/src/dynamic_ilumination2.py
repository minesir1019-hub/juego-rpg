#luz dinaminca

import pygame
import sys

import pygame
import sys
import math


class pelota:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.luz = False
        self.radio = 400
        self.velocidad_x = 0
        self.velocidad_y = 0

    def dibujar(self, pantalla):
        # Dibujar la pelota
        pygame.draw.circle(
            pantalla,
            (255, 255, 255),
            (int(self.x), int(self.y)),
            20
        )

        # Dibujar la luz si está encendida
        if self.luz:
            luz = create_light_mask(self.radio)

            pantalla.blit(
                luz,
                (
                    int(self.x - self.radio),
                    int(self.y - self.radio)
                )
            )


pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("67")

# Crear la máscara de luz
def create_light_mask(radius):

    mask = pygame.Surface(
        (radius * 2, radius * 2),
        pygame.SRCALPHA
    )

    for r in range(radius, 0, -2):

        alpha = int(255 * (r / radius) ** 2)

        pygame.draw.circle(
            mask,
            (0, 0, 0, alpha),
            (radius, radius),
            r
        )

    return mask


# Reloj
clock = pygame.time.Clock()

# Crear la pelota
jugador = pelota(400, 300)


# Bucle principal
ejecutando = True

while ejecutando:

    # Revisar eventos
    for evento in pygame.event.get():

        # Cerrar el juego
        if evento.type == pygame.QUIT:
            ejecutando = False

        # Clic izquierdo
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                jugador.luz = not jugador.luz

    # Fondo
    screen.fill((30, 30, 30))

    # Dibujar pelota y luz
    jugador.dibujar(screen)

    # Actualizar pantalla
    pygame.display.flip()

    # 60 FPS
    clock.tick(60)


pygame.quit()
sys.exit()
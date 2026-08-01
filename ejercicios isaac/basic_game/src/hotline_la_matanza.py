

from mimetypes import init

import pygame
import math

pygame.init()

ANCHO, ALTO = 960, 540
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Hotline la matanza")
reloj = pygame.time.Clock()


jugador_pos = pygame.Vector2(0, 0)
jugador_radio = 16
jugador_velocidad = 280


COLOR_FONDO = (30, 30, 35)
COLOR_DIRECCION = (255, 255, 255)
COLOR_JUGADOR = (230, 60, 60)


corriendo = True
while corriendo:
    dt = reloj.tick(60) / 1000

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False

    # Movimiento del jugador
    teclas = pygame.key.get_pressed()
    direccion = pygame.Vector2(0, 0)
    if teclas[pygame.K_w]:
        direccion.y -= 1
    if teclas[pygame.K_s]:
        direccion.y += 1
    if teclas[pygame.K_a]:
        direccion.x -= 1
    if teclas[pygame.K_d]:
        direccion.x += 1

    if direccion.length() > 0:
        direccion = direccion.normalize()
        jugador_pos += direccion * jugador_velocidad * dt

    # Dibujar todo
    pantalla.fill(COLOR_FONDO)

    # Dibujar dirección del mouse
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    pygame.draw.line(pantalla, COLOR_DIRECCION, jugador_pos, mouse_pos, 2)

    # Dibujar jugador
    pygame.draw.circle(pantalla, COLOR_JUGADOR, jugador_pos, jugador_radio)

    pygame.display.flip()
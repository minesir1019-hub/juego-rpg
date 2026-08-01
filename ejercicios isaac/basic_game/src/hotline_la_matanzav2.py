import pygame
import math

pygame.init()

ANCHO, ALTO = 960, 540
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Movimiento estilo Hotline Miami")
reloj = pygame.time.Clock()

# --- Jugador (posición en coordenadas de MUNDO, no de pantalla) ---
jugador_pos = pygame.Vector2(0, 0)
jugador_radio = 16
VELOCIDAD = 280  # píxeles por segundo

# --- Cámara ---
camara_pos = pygame.Vector2(jugador_pos)  # centro de la cámara en coords de mundo
LEAN_MOUSE = 0.35   # cuánto se corre la cámara hacia el mouse (0 a 1)
SUAVIZADO_CAMARA = 8.0  # más alto = cámara más rígida/rápida

# --- Piso: cuadraditos ---
TILE = 40
COLOR_TILE_A = (40, 40, 46)
COLOR_TILE_B = (34, 34, 40)

# --- Arma ---
LARGO_ARMA = 34
ANCHO_ARMA = 10
DISTANCIA_ARMA = jugador_radio + 6  # separación respecto al centro del jugador
COLOR_ARMA = (70, 70, 75)
COLOR_CANO = (20, 20, 20)

COLOR_JUGADOR = (230, 60, 60)

corriendo = True
while corriendo:
    dt = reloj.tick(60) / 1000

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False

    # --- Input de movimiento (WASD) ---
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

    if direccion.length_squared() > 0:
        direccion = direccion.normalize()

    jugador_pos += direccion * VELOCIDAD * dt

    # --- Mouse en coords de pantalla y de mundo ---
    mouse_screen = pygame.Vector2(pygame.mouse.get_pos())
    centro_pantalla = pygame.Vector2(ANCHO / 2, ALTO / 2)
    offset_mouse = mouse_screen - centro_pantalla  # qué tan lejos del centro está apuntando

    # --- Cámara: sigue al jugador, con un "lean" hacia donde apunta el mouse ---
    objetivo_camara = jugador_pos + offset_mouse * LEAN_MOUSE
    camara_pos += (objetivo_camara - camara_pos) * min(SUAVIZADO_CAMARA * dt, 1)

    def mundo_a_pantalla(punto_mundo):
        return punto_mundo - camara_pos + centro_pantalla

    # Ángulo de apuntado (en coords de pantalla, jugador vs mouse real)
    jugador_pantalla = mundo_a_pantalla(jugador_pos)
    hacia_mouse = mouse_screen - jugador_pantalla
    angulo = math.atan2(hacia_mouse.y, hacia_mouse.x)

    # --- Dibujado ---
    pantalla.fill(COLOR_TILE_A)

    # Piso en cuadraditos, alineado al mundo (no se mueve "pegado" a la cámara)
    inicio_x = int((camara_pos.x - centro_pantalla.x) // TILE) - 1
    fin_x = int((camara_pos.x + centro_pantalla.x) // TILE) + 1
    inicio_y = int((camara_pos.y - centro_pantalla.y) // TILE) - 1
    fin_y = int((camara_pos.y + centro_pantalla.y) // TILE) + 1

    for gx in range(inicio_x, fin_x + 1):
        for gy in range(inicio_y, fin_y + 1):
            rect_mundo = pygame.Vector2(gx * TILE, gy * TILE)
            rect_pantalla = mundo_a_pantalla(rect_mundo)
            color = COLOR_TILE_A if (gx + gy) % 2 == 0 else COLOR_TILE_B
            pygame.draw.rect(pantalla, color, (rect_pantalla.x, rect_pantalla.y, TILE, TILE))

    # --- Arma: rectángulo rotado según el ángulo de apuntado ---
    centro_arma = jugador_pantalla + pygame.Vector2(math.cos(angulo), math.sin(angulo)) * DISTANCIA_ARMA

    superficie_arma = pygame.Surface((LARGO_ARMA, ANCHO_ARMA), pygame.SRCALPHA)
    pygame.draw.rect(superficie_arma, COLOR_ARMA, (0, 0, LARGO_ARMA, ANCHO_ARMA), border_radius=2)
    pygame.draw.rect(superficie_arma, COLOR_CANO, (LARGO_ARMA - 10, 0, 10, ANCHO_ARMA))

    superficie_rotada = pygame.transform.rotate(superficie_arma, -math.degrees(angulo))
    rect_rotado = superficie_rotada.get_rect(center=centro_arma)
    pantalla.blit(superficie_rotada, rect_rotado)

    # --- Jugador (encima del arma) ---
    pygame.draw.circle(pantalla, COLOR_JUGADOR, jugador_pantalla, jugador_radio)

    pygame.display.flip()

pygame.quit()
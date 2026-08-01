import pygame
import math
import random

pygame.init()

ANCHO, ALTO = 960, 540
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Movimiento estilo Hotline Miami")
reloj = pygame.time.Clock()
fuente = pygame.font.SysFont(None, 64)
fuente_chica = pygame.font.SysFont(None, 28)

# --- Jugador (coordenadas de MUNDO) ---
jugador_pos = pygame.Vector2(0, 0)
jugador_radio = 16
VELOCIDAD = 280
jugador_vivo = True

# --- Cámara ---
camara_pos = pygame.Vector2(jugador_pos)
LEAN_MOUSE = 0.35
SUAVIZADO_CAMARA = 8.0

# --- Piso: cuadraditos ---
TILE = 40
COLOR_TILE_A = (40, 40, 46)
COLOR_TILE_B = (34, 34, 40)

# --- Arma (al costado del personaje) ---
LARGO_ARMA = 30
ANCHO_ARMA = 9
DIST_ADELANTE = 6
DIST_COSTADO = 14
COLOR_ARMA = (70, 70, 75)
COLOR_CANO = (20, 20, 20)

COLOR_JUGADOR = (230, 60, 60)

# --- Enemigos: lista, aparecen uno cada 2 segundos ---
enemigos = []  # cada uno: pygame.Vector2 en coords de mundo
enemigo_radio = 15
ENEMIGO_VELOCIDAD = 130
COLOR_ENEMIGO = (70, 190, 100)
TIEMPO_ENTRE_SPAWNS = 2.0
temporizador_spawn = 0.0
DISTANCIA_SPAWN = 550  # tan lejos del jugador aparecen (fuera de la vista)

# --- Balas (cuadrados) ---
balas = []
BALA_VELOCIDAD = 640
BALA_TAMANO = 8
BALA_ALCANCE = 750
COLOR_BALA = (240, 220, 90)

# --- Viñeta ---
VIN_ANCHO_CHICO, VIN_ALTO_CHICO = 120, 68
vignette_chica = pygame.Surface((VIN_ANCHO_CHICO, VIN_ALTO_CHICO), pygame.SRCALPHA)
cx, cy = VIN_ANCHO_CHICO / 2, VIN_ALTO_CHICO / 2
dist_max = math.hypot(cx, cy)
for vx in range(VIN_ANCHO_CHICO):
    for vy in range(VIN_ALTO_CHICO):
        d = math.hypot(vx - cx, vy - cy) / dist_max
        alpha = max(0, min(235, int((d - 0.35) / 0.65 * 235)))
        vignette_chica.set_at((vx, vy), (0, 0, 0, alpha))
vignette = pygame.transform.smoothscale(vignette_chica, (ANCHO, ALTO))


def mundo_a_pantalla(punto_mundo):
    return punto_mundo - camara_pos + pygame.Vector2(ANCHO / 2, ALTO / 2)


corriendo = True
while corriendo:
    dt = reloj.tick(60) / 1000

    disparar = False
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            disparar = True

    if jugador_vivo:
        # --- Movimiento del jugador (WASD) ---
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

        # --- Spawn de enemigos cada 2 segundos ---
        temporizador_spawn += dt
        if temporizador_spawn >= TIEMPO_ENTRE_SPAWNS:
            temporizador_spawn = 0.0
            angulo_spawn = random.uniform(0, math.tau)
            pos_spawn = jugador_pos + pygame.Vector2(
                math.cos(angulo_spawn), math.sin(angulo_spawn)
            ) * DISTANCIA_SPAWN
            enemigos.append(pos_spawn)

        # --- Enemigos persiguen al jugador ---
        for enemigo_pos in enemigos:
            hacia_jugador = jugador_pos - enemigo_pos
            if hacia_jugador.length_squared() > 0:
                hacia_jugador = hacia_jugador.normalize()
            enemigo_pos += hacia_jugador * ENEMIGO_VELOCIDAD * dt

        # --- Cámara ---
        mouse_screen = pygame.Vector2(pygame.mouse.get_pos())
        centro_pantalla = pygame.Vector2(ANCHO / 2, ALTO / 2)
        offset_mouse = mouse_screen - centro_pantalla
        objetivo_camara = jugador_pos + offset_mouse * LEAN_MOUSE
        camara_pos += (objetivo_camara - camara_pos) * min(SUAVIZADO_CAMARA * dt, 1)

        jugador_pantalla = mundo_a_pantalla(jugador_pos)
        hacia_mouse = mouse_screen - jugador_pantalla
        angulo = math.atan2(hacia_mouse.y, hacia_mouse.x)
        aim_dir = pygame.Vector2(math.cos(angulo), math.sin(angulo))
        perpendicular = pygame.Vector2(-aim_dir.y, aim_dir.x)

        offset_arma = aim_dir * DIST_ADELANTE + perpendicular * DIST_COSTADO
        centro_arma_mundo = jugador_pos + offset_arma
        centro_arma_pantalla = mundo_a_pantalla(centro_arma_mundo)

        if disparar:
            punta_mundo = centro_arma_mundo + aim_dir * (LARGO_ARMA / 2)
            balas.append({
                "pos": pygame.Vector2(punta_mundo),
                "vel": aim_dir * BALA_VELOCIDAD,
                "origen": pygame.Vector2(punta_mundo),
            })

        # --- Actualizar balas y chequear choque con enemigos ---
        for bala in balas[:]:
            bala["pos"] += bala["vel"] * dt

            impacto = False
            for enemigo_pos in enemigos[:]:
                if (bala["pos"] - enemigo_pos).length() < (BALA_TAMANO / 2 + enemigo_radio):
                    enemigos.remove(enemigo_pos)
                    impacto = True
                    break

            if impacto or (bala["pos"] - bala["origen"]).length() > BALA_ALCANCE:
                balas.remove(bala)

        # --- ¿Un enemigo toca al jugador? ---
        for enemigo_pos in enemigos:
            if (enemigo_pos - jugador_pos).length() < (enemigo_radio + jugador_radio):
                jugador_vivo = False
                break

    # ============ DIBUJADO ============
    pantalla.fill(COLOR_TILE_A)

    inicio_x = int((camara_pos.x - ANCHO / 2) // TILE) - 1
    fin_x = int((camara_pos.x + ANCHO / 2) // TILE) + 1
    inicio_y = int((camara_pos.y - ALTO / 2) // TILE) - 1
    fin_y = int((camara_pos.y + ALTO / 2) // TILE) + 1
    for gx in range(inicio_x, fin_x + 1):
        for gy in range(inicio_y, fin_y + 1):
            rect_mundo = pygame.Vector2(gx * TILE, gy * TILE)
            rect_pantalla = mundo_a_pantalla(rect_mundo)
            color = COLOR_TILE_A if (gx + gy) % 2 == 0 else COLOR_TILE_B
            pygame.draw.rect(pantalla, color, (rect_pantalla.x, rect_pantalla.y, TILE, TILE))

    for enemigo_pos in enemigos:
        pygame.draw.circle(pantalla, COLOR_ENEMIGO, mundo_a_pantalla(enemigo_pos), enemigo_radio)

    if jugador_vivo:
        superficie_arma = pygame.Surface((LARGO_ARMA, ANCHO_ARMA), pygame.SRCALPHA)
        pygame.draw.rect(superficie_arma, COLOR_ARMA, (0, 0, LARGO_ARMA, ANCHO_ARMA), border_radius=2)
        pygame.draw.rect(superficie_arma, COLOR_CANO, (LARGO_ARMA - 10, 0, 10, ANCHO_ARMA))
        superficie_rotada = pygame.transform.rotate(superficie_arma, -math.degrees(angulo))
        rect_rotado = superficie_rotada.get_rect(center=centro_arma_pantalla)
        pantalla.blit(superficie_rotada, rect_rotado)

        pygame.draw.circle(pantalla, COLOR_JUGADOR, jugador_pantalla, jugador_radio)

    for bala in balas:
        bp = mundo_a_pantalla(bala["pos"])
        pygame.draw.rect(pantalla, COLOR_BALA, (bp.x - BALA_TAMANO / 2, bp.y - BALA_TAMANO / 2, BALA_TAMANO, BALA_TAMANO))

    pantalla.blit(vignette, (0, 0))

    if not jugador_vivo:
        texto = fuente.render("MORISTE", True, (230, 60, 60))
        rect_texto = texto.get_rect(center=(ANCHO / 2, ALTO / 2 - 20))
        pantalla.blit(texto, rect_texto)
        texto2 = fuente_chica.render("Cerrá la ventana para salir", True, (220, 220, 220))
        rect_texto2 = texto2.get_rect(center=(ANCHO / 2, ALTO / 2 + 30))
        pantalla.blit(texto2, rect_texto2)

    pygame.display.flip()

pygame.quit()
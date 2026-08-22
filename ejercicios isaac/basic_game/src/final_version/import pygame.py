import pygame
import math
import random

# =========================================================
# NOTA: por ahora todo vive en un solo archivo para poder
# ejecutarlo directo. Está organizado en bloques (ARMAS,
# ENTIDADES, ASSETS/VISUAL, ENTORNO/CÁMARA, LOOP PRINCIPAL)
# pensados para poder cortar y pegar cada uno a su propio
# archivo (armas.py, entidades.py, assets.py, main.py) el
# día que se decida separar el proyecto de verdad.
# =========================================================

pygame.init()

ANCHO, ALTO = 960, 540
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Hotline - prototipo")
reloj = pygame.time.Clock()
fuente_grande = pygame.font.SysFont(None, 72)
fuente_media = pygame.font.SysFont(None, 40)
fuente_chica = pygame.font.SysFont(None, 26)

CENTRO_PANTALLA = pygame.Vector2(ANCHO / 2, ALTO / 2)

# =========================================================
# CONFIG GENERAL
# =========================================================
jugador_radio = 16
VELOCIDAD = 280
TILE = 40
COLOR_TILE_A = (40, 40, 46)
COLOR_TILE_B = (34, 34, 40)
COLOR_JUGADOR = (230, 60, 60)
DISTANCIA_SPAWN = 550
BALA_TAMANO = 8
BALA_ALCANCE = 750

# --- Dash ---
DASH_MAX_CARGAS = 3
DASH_VELOCIDAD = 780
DASH_DURACION = 0.15
DASH_RECARGA_TIEMPO = 2.0
RALENTIZADO_DURACION = 2.0
RALENTIZADO_MULT = 0.45

# --- Armas (candidato a armas.py) ---
# Orden de desbloqueo: 0 Metralleta (inicial) -> 1 Escopeta (oleada 7) -> 2 Revólver (oleada 14)
# TODO (para más adelante, no implementar todavía):
#   - Sistema de modificación/mejora de armas
#   - Rediseño visual del HUD/interfaz (el actual es solo funcional)
ARMAS = ["Metralleta", "Escopeta", "Revólver"]

METRALLETA_MUNICION_MAX = 30
METRALLETA_COOLDOWN = 0.1
METRALLETA_DANO = 1
RETROCESO_METRALLETA = 4

ESCOPETA_COOLDOWN = 0.35
ESCOPETA_PERDIGONES = 4
ESCOPETA_BALAS_RECARGA = 3
ESCOPETA_TIEMPO_RECARGA = 3.0
ESCOPETA_DIST_CERCA = 80    # a esta distancia de apuntado (o menos), cono ancho y corto
ESCOPETA_DIST_LEJOS = 520   # a esta distancia (o más), cono angosto y largo
ESCOPETA_SPREAD_MAX_GRADOS = 100
ESCOPETA_SPREAD_MIN_GRADOS = 14
ESCOPETA_VIDA_BALA_MIN = 0.35
ESCOPETA_VIDA_BALA_MAX = 1.4
RETROCESO_ESCOPETA = 16

REVOLVER_BALAS_RECARGA = 5
REVOLVER_TIEMPO_RECARGA = 2.0
REVOLVER_COOLDOWN = 0.3
REVOLVER_DANO = 3
RETROCESO_REVOLVER = 30

LARGO_ARMA = 30
ANCHO_ARMA = 9
DIST_ADELANTE = 6
DIST_COSTADO = 14
COLOR_ARMA = (70, 70, 75)
COLOR_CANO = (20, 20, 20)

# --- Enemigos (candidato a entidades.py, junto con el jugador) ---
TIPOS_ENEMIGOS = {
    "normal":   {"vida": 1,  "color": (150, 150, 150), "velocidad": 130, "radio": 15, "puntos": 10},
    "perro":    {"vida": 2,  "color": (225, 210, 60),  "velocidad": 300, "radio": 13, "puntos": 15},
    "tirador":  {"vida": 1,  "color": (70, 190, 100),  "velocidad": 95,  "radio": 15, "puntos": 20},
    "tanque":   {"vida": 4,  "color": (150, 80, 200),  "velocidad": 85,  "radio": 20, "puntos": 30},
    "kamikaze": {"vida": 1,  "color": (150, 150, 150), "velocidad": 190, "radio": 15, "puntos": 25},
    "auto":     {"vida": 10, "color": (60, 90, 220),   "velocidad": 200, "radio": 26, "puntos": 100},
}
UMBRAL_KAMIKAZE = 130
FUSIBLE_KAMIKAZE = 0.6
RADIO_EXPLOSION_KAMIKAZE = 95
COLOR_KAMIKAZE_ARMADO = (255, 90, 40)
GIRO_AUTO = 2.2
ESTELA_INTERVALO = 0.08
ESTELA_VIDA = 0.5
ESTELA_RADIO = 9
COLOR_ESTELA = (110, 110, 115)
TIRADOR_DIST_IDEAL_MIN = 250
TIRADOR_DIST_IDEAL_MAX = 320
TIRADOR_COOLDOWN = 1.6
TIRADOR_BALA_VELOCIDAD = 380
COLOR_BALA_ENEMIGA = (120, 230, 150)
ESCUDO_CADA_OLEADAS = 11
COLOR_ESCUDO = (90, 200, 230)
OLEADA_APARICION_ESCOPETA = 7
OLEADA_APARICION_REVOLVER = 14
COLOR_PICKUP_ARMA = (240, 240, 100)
PREPARACION_ENTRE_OLEADAS = 5.0
COLOR_TITULO_OLEADA = (230, 230, 230)
MINIMAPA_RADIO = 58
MINIMAPA_CENTRO = (ANCHO - MINIMAPA_RADIO - 16, MINIMAPA_RADIO + 16)
MINIMAPA_ESCALA = 0.09
COLOR_MINIMAPA_FONDO = (25, 70, 35)
COLOR_MINIMAPA_BORDE = (60, 140, 70)

# --- Cámara ---
LEAN_MOUSE = 0.35
SUAVIZADO_CAMARA = 8.0

# =========================================================
# VIÑETA (se calcula una sola vez)
# =========================================================
VIN_W, VIN_H = 120, 68
vignette_chica = pygame.Surface((VIN_W, VIN_H), pygame.SRCALPHA)
cx, cy = VIN_W / 2, VIN_H / 2
dist_max = math.hypot(cx, cy)
for vx in range(VIN_W):
    for vy in range(VIN_H):
        d = math.hypot(vx - cx, vy - cy) / dist_max
        alpha = max(0, min(235, int((d - 0.35) / 0.65 * 235)))
        vignette_chica.set_at((vx, vy), (0, 0, 0, alpha))
vignette = pygame.transform.smoothscale(vignette_chica, (ANCHO, ALTO))


def mundo_a_pantalla(punto_mundo):
    return punto_mundo - camara_pos + CENTRO_PANTALLA


# =========================================================
# ESTADO DEL JUEGO (se reinicia con reset_juego)
# =========================================================
estado_juego = "menu"  # "menu" | "jugando" | "muerto"


def generar_oleada(n):
    lista = ["normal"] * (3 + n)
    if n >= 3 and n % 3 == 0:
        lista += ["perro"] * 4
    if n >= 3:
        lista += ["tirador"] * (1 + n // 3)
    if n >= 4:
        lista += ["tanque"] * (1 + n // 4)
    if n >= 6 and n % 2 == 0:
        lista += ["kamikaze"] * 2
    if n % 10 == 0 and n > 0:
        lista += ["auto"] * 3
    random.shuffle(lista)
    return lista


def reset_juego():
    global jugador_pos, jugador_vivo, jugador_escudo, jugador_invulnerable, camara_pos
    global enemigos, balas, balas_enemigos, particulas, explosiones, escudos, estelas, pickups_armas
    global arma_actual, armas_desbloqueadas
    global metralleta_municion
    global escopeta_disparos_restantes, escopeta_recargando, escopeta_tiempo_recarga_restante
    global revolver_disparos_restantes, revolver_recargando, revolver_tiempo_recarga_restante
    global angulo_recarga_extra
    global tiempo_desde_disparo
    global dash_cargas, dash_recarga_progreso, dash_tiempo_restante, dash_direccion, ralentizado_restante
    global oleada, cola_oleada, temporizador_spawn, puntaje
    global tiempo_preparacion_restante, titulo_oleada_texto, titulo_oleada_duracion, titulo_oleada_tiempo

    jugador_pos = pygame.Vector2(0, 0)
    jugador_vivo = True
    jugador_escudo = False
    jugador_invulnerable = 0.0
    camara_pos = pygame.Vector2(0, 0)

    enemigos = []
    balas = []
    balas_enemigos = []
    particulas = []
    explosiones = []
    escudos = []
    estelas = []
    pickups_armas = []

    arma_actual = 0
    armas_desbloqueadas = {0: True, 1: False, 2: False}

    metralleta_municion = METRALLETA_MUNICION_MAX

    escopeta_disparos_restantes = ESCOPETA_BALAS_RECARGA
    escopeta_recargando = False
    escopeta_tiempo_recarga_restante = 0.0

    revolver_disparos_restantes = REVOLVER_BALAS_RECARGA
    revolver_recargando = False
    revolver_tiempo_recarga_restante = 0.0

    angulo_recarga_extra = 0.0
    tiempo_desde_disparo = 999.0

    dash_cargas = DASH_MAX_CARGAS
    dash_recarga_progreso = 0.0
    dash_tiempo_restante = 0.0
    dash_direccion = pygame.Vector2(1, 0)
    ralentizado_restante = 0.0

    oleada = 1
    cola_oleada = generar_oleada(oleada)
    temporizador_spawn = 0.0
    puntaje = 0

    tiempo_preparacion_restante = 10.0
    titulo_oleada_texto = f"Oleada {oleada}"
    titulo_oleada_duracion = 10.0
    titulo_oleada_tiempo = 0.0


reset_juego()


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================
def golpear_jugador():
    global jugador_escudo, jugador_vivo, estado_juego, jugador_invulnerable
    if jugador_invulnerable > 0:
        return
    if jugador_escudo:
        jugador_escudo = False
        jugador_invulnerable = 0.5
    else:
        jugador_vivo = False
        estado_juego = "muerto"


def crear_particulas_pop(pos, color):
    for _ in range(10):
        ang = random.uniform(0, math.tau)
        vel = pygame.Vector2(math.cos(ang), math.sin(ang)) * random.uniform(60, 220)
        particulas.append({"pos": pygame.Vector2(pos), "vel": vel, "vida": 0.4, "vida_max": 0.4, "color": color})


def crear_explosion(pos, radio, color=(255, 120, 40)):
    explosiones.append({"pos": pygame.Vector2(pos), "radio": radio, "vida": 1.0, "vida_max": 1.0, "color": color})


def crear_estela(pos):
    estelas.append({"pos": pygame.Vector2(pos), "vida": ESTELA_VIDA, "vida_max": ESTELA_VIDA})


def matar_enemigo(e):
    global puntaje
    if e in enemigos:
        enemigos.remove(e)
    puntaje += TIPOS_ENEMIGOS[e["tipo"]]["puntos"]
    crear_particulas_pop(e["pos"], e["color"])


def crear_enemigo(tipo):
    base = TIPOS_ENEMIGOS[tipo]
    ang = random.uniform(0, math.tau)
    pos_spawn = jugador_pos + pygame.Vector2(math.cos(ang), math.sin(ang)) * DISTANCIA_SPAWN
    e = {
        "pos": pos_spawn, "tipo": tipo, "vida": base["vida"], "radio": base["radio"],
        "color": base["color"], "velocidad": base["velocidad"],
    }
    if tipo == "kamikaze":
        e["estado"] = "acercandose"
        e["fusible"] = 0.0
    if tipo == "tirador":
        e["cooldown_disparo"] = random.uniform(0.3, 1.0)
    if tipo == "auto":
        dir0 = jugador_pos - pos_spawn
        e["direccion_actual"] = dir0.normalize() if dir0.length_squared() > 0 else pygame.Vector2(1, 0)
        e["temporizador_estela"] = 0.0
    enemigos.append(e)


def crear_pickup_arma(indice_arma):
    ang = random.uniform(0, math.tau)
    pos = jugador_pos + pygame.Vector2(math.cos(ang), math.sin(ang)) * random.uniform(50, 90)
    pickups_armas.append({"pos": pos, "arma_index": indice_arma})


def rect_boton(cx, cy, w, h):
    return pygame.Rect(cx - w / 2, cy - h / 2, w, h)


BOTON_EMPEZAR = rect_boton(ANCHO / 2, ALTO / 2 - 20, 220, 60)
BOTON_SALIR = rect_boton(ANCHO / 2, ALTO / 2 + 60, 220, 60)
BOTON_REINICIAR = rect_boton(ANCHO / 2, ALTO / 2 + 70, 240, 60)


def dibujar_boton(rect, texto, hover):
    color_fondo = (90, 90, 100) if hover else (60, 60, 68)
    pygame.draw.rect(pantalla, color_fondo, rect, border_radius=8)
    pygame.draw.rect(pantalla, (200, 200, 210), rect, width=2, border_radius=8)
    superficie_texto = fuente_media.render(texto, True, (240, 240, 240))
    pantalla.blit(superficie_texto, superficie_texto.get_rect(center=rect.center))


# =========================================================
# LOOP PRINCIPAL
# =========================================================
corriendo = True
while corriendo:
    dt = reloj.tick(60) / 1000
    mouse_screen = pygame.Vector2(pygame.mouse.get_pos())

    disparar = False
    click_menu = None
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if estado_juego == "jugando":
                disparar = True
            else:
                click_menu = mouse_screen
        elif evento.type == pygame.KEYDOWN and estado_juego == "jugando":
            if evento.key == pygame.K_q:
                if dash_cargas > 0:
                    dash_cargas -= 1
                    dash_tiempo_restante = DASH_DURACION
                elif ralentizado_restante <= 0:
                    ralentizado_restante = RALENTIZADO_DURACION
            elif evento.key == pygame.K_1 and armas_desbloqueadas[0]:
                arma_actual = 0
            elif evento.key == pygame.K_2 and armas_desbloqueadas[1]:
                arma_actual = 1
            elif evento.key == pygame.K_3 and armas_desbloqueadas[2]:
                arma_actual = 2
            elif evento.key == pygame.K_r:
                if arma_actual == 1 and not escopeta_recargando and escopeta_disparos_restantes < ESCOPETA_BALAS_RECARGA:
                    escopeta_recargando = True
                    escopeta_tiempo_recarga_restante = ESCOPETA_TIEMPO_RECARGA
                elif arma_actual == 2 and not revolver_recargando and revolver_disparos_restantes < REVOLVER_BALAS_RECARGA:
                    revolver_recargando = True
                    revolver_tiempo_recarga_restante = REVOLVER_TIEMPO_RECARGA

    # ---------------- MENÚ ----------------
    if estado_juego == "menu":
        pantalla.fill((22, 22, 26))
        titulo = fuente_grande.render("HOTLINE - PROTOTIPO", True, (230, 60, 60))
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO / 2, ALTO / 2 - 120)))
        dibujar_boton(BOTON_EMPEZAR, "EMPEZAR", BOTON_EMPEZAR.collidepoint(mouse_screen))
        dibujar_boton(BOTON_SALIR, "SALIR", BOTON_SALIR.collidepoint(mouse_screen))
        if click_menu:
            if BOTON_EMPEZAR.collidepoint(click_menu):
                reset_juego()
                estado_juego = "jugando"
            elif BOTON_SALIR.collidepoint(click_menu):
                corriendo = False
        pygame.display.flip()
        continue

    # ---------------- MUERTO ----------------
    if estado_juego == "muerto":
        pantalla.fill((22, 22, 26))
        texto = fuente_grande.render("MORISTE", True, (230, 60, 60))
        pantalla.blit(texto, texto.get_rect(center=(ANCHO / 2, ALTO / 2 - 60)))
        texto_p = fuente_media.render(f"Puntaje: {puntaje}", True, (230, 230, 230))
        pantalla.blit(texto_p, texto_p.get_rect(center=(ANCHO / 2, ALTO / 2)))
        dibujar_boton(BOTON_REINICIAR, "REINICIAR", BOTON_REINICIAR.collidepoint(mouse_screen))
        if click_menu and BOTON_REINICIAR.collidepoint(click_menu):
            reset_juego()
            estado_juego = "jugando"
        pygame.display.flip()
        continue

    # ================= JUGANDO =================
    tiempo_desde_disparo += dt

    # --- Movimiento / dash / ralentizado ---
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
        dash_direccion = direccion

    if dash_tiempo_restante > 0:
        jugador_pos += dash_direccion * DASH_VELOCIDAD * dt
        dash_tiempo_restante -= dt
    else:
        mult = 1.0
        if ralentizado_restante > 0:
            mult = RALENTIZADO_MULT
            ralentizado_restante -= dt
        jugador_pos += direccion * VELOCIDAD * mult * dt

    if dash_cargas < DASH_MAX_CARGAS:
        dash_recarga_progreso += dt
        if dash_recarga_progreso >= DASH_RECARGA_TIEMPO:
            dash_recarga_progreso = 0.0
            dash_cargas += 1

    if jugador_invulnerable > 0:
        jugador_invulnerable -= dt

    # --- Cámara ---
    offset_mouse = mouse_screen - CENTRO_PANTALLA
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

    # --- Recarga escopeta / revólver (la metralleta no recarga, se queda sin balas) ---
    if escopeta_recargando:
        angulo_recarga_extra += 480 * dt
        escopeta_tiempo_recarga_restante -= dt
        if escopeta_tiempo_recarga_restante <= 0:
            escopeta_recargando = False
            escopeta_disparos_restantes = ESCOPETA_BALAS_RECARGA
            angulo_recarga_extra = 0.0

    if revolver_recargando:
        angulo_recarga_extra += 720 * dt
        revolver_tiempo_recarga_restante -= dt
        if revolver_tiempo_recarga_restante <= 0:
            revolver_recargando = False
            revolver_disparos_restantes = REVOLVER_BALAS_RECARGA
            angulo_recarga_extra = 0.0

    # --- Disparo ---
    mouse_sostenido = pygame.mouse.get_pressed()[0]
    punta_mundo = centro_arma_mundo + aim_dir * (LARGO_ARMA / 2)

    if arma_actual == 0 and mouse_sostenido and metralleta_municion > 0 and tiempo_desde_disparo >= METRALLETA_COOLDOWN:
        balas.append({"pos": pygame.Vector2(punta_mundo), "vel": aim_dir * 640,
                      "origen": pygame.Vector2(punta_mundo), "tipo": "normal", "dano": METRALLETA_DANO})
        tiempo_desde_disparo = 0
        metralleta_municion -= 1
        jugador_pos -= aim_dir * RETROCESO_METRALLETA

    elif arma_actual == 1 and disparar and not escopeta_recargando and escopeta_disparos_restantes > 0:
        dist_apuntado = max(ESCOPETA_DIST_CERCA, min(ESCOPETA_DIST_LEJOS, hacia_mouse.length()))
        t = (dist_apuntado - ESCOPETA_DIST_CERCA) / (ESCOPETA_DIST_LEJOS - ESCOPETA_DIST_CERCA)
        spread_grados = ESCOPETA_SPREAD_MAX_GRADOS + (ESCOPETA_SPREAD_MIN_GRADOS - ESCOPETA_SPREAD_MAX_GRADOS) * t
        vida_bala = ESCOPETA_VIDA_BALA_MIN + (ESCOPETA_VIDA_BALA_MAX - ESCOPETA_VIDA_BALA_MIN) * t
        for i in range(ESCOPETA_PERDIGONES):
            offset_grados = random.uniform(-spread_grados / 2, spread_grados / 2)
            ang2 = angulo + math.radians(offset_grados)
            dir2 = pygame.Vector2(math.cos(ang2), math.sin(ang2))
            balas.append({"pos": pygame.Vector2(punta_mundo), "vel": dir2 * 560,
                          "origen": pygame.Vector2(punta_mundo), "tipo": "escopeta",
                          "dano": 1, "vida_restante": vida_bala})
        jugador_pos -= aim_dir * RETROCESO_ESCOPETA
        escopeta_disparos_restantes -= 1
        if escopeta_disparos_restantes <= 0:
            escopeta_recargando = True
            escopeta_tiempo_recarga_restante = ESCOPETA_TIEMPO_RECARGA

    elif arma_actual == 2 and disparar and not revolver_recargando and revolver_disparos_restantes > 0:
        balas.append({"pos": pygame.Vector2(punta_mundo), "vel": aim_dir * 720,
                      "origen": pygame.Vector2(punta_mundo), "tipo": "revolver", "dano": REVOLVER_DANO})
        jugador_pos -= aim_dir * RETROCESO_REVOLVER
        revolver_disparos_restantes -= 1
        if revolver_disparos_restantes <= 0:
            revolver_recargando = True
            revolver_tiempo_recarga_restante = REVOLVER_TIEMPO_RECARGA

    # --- Actualizar balas del jugador ---
    for bala in balas[:]:
        bala["pos"] += bala["vel"] * dt
        if bala["tipo"] == "escopeta":
            bala["vida_restante"] -= dt
            expiro = bala["vida_restante"] <= 0
        else:
            expiro = (bala["pos"] - bala["origen"]).length() > BALA_ALCANCE

        impacto = False
        for enemigo in enemigos:
            if (bala["pos"] - enemigo["pos"]).length() < (BALA_TAMANO / 2 + enemigo["radio"]):
                enemigo["vida"] -= bala["dano"]
                impacto = True
                break

        if impacto or expiro:
            balas.remove(bala)

    # --- Recoger pickups de arma ---
    for pk in pickups_armas[:]:
        if (pk["pos"] - jugador_pos).length() < (jugador_radio + 12):
            armas_desbloqueadas[pk["arma_index"]] = True
            arma_actual = pk["arma_index"]
            pickups_armas.remove(pk)

    # --- Limpiar enemigos muertos por daño ---
    for e in enemigos[:]:
        if e["vida"] <= 0:
            matar_enemigo(e)

    # --- Comportamiento de enemigos ---
    for e in enemigos[:]:
        tipo = e["tipo"]
        if tipo in ("normal", "perro", "tanque"):
            hacia = jugador_pos - e["pos"]
            if hacia.length_squared() > 0:
                hacia = hacia.normalize()
            e["pos"] += hacia * e["velocidad"] * dt

        elif tipo == "tirador":
            hacia = jugador_pos - e["pos"]
            dist = hacia.length()
            if dist > 0:
                hacia_n = hacia.normalize()
            else:
                hacia_n = pygame.Vector2(0, 0)
            i
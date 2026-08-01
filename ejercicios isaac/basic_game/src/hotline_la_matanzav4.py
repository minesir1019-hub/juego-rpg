import pygame
import math
import random

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
TIEMPO_GRACIA_INICIAL = 3.0   # segundos

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
DASH_RECARGA_TIEMPO = 3.0
RALENTIZADO_DURACION = 2.0
RALENTIZADO_MULT = 0.45

# --- Armas ---
ARMAS = ["Metralleta", "Escopeta", "Bazuca"]
METRALLETA_COOLDOWN = 0.15
METRALLETA_BALAS_RECARGA = 5
METRALLETA_TIEMPO_RECARGA = 2.0
ESCOPETA_COOLDOWN = 0.8
ESCOPETA_PERDIGONES = 4
ESCOPETA_SPREAD_GRADOS = 28
ESCOPETA_VIDA_BALA = 1.0
BAZUCA_COOLDOWN = 1.4
BAZUCA_DANO_AREA = 5
BAZUCA_RADIO_EXPLOSION = 80

LARGO_ARMA = 30
ANCHO_ARMA = 9
DIST_ADELANTE = 6
DIST_COSTADO = 14
COLOR_ARMA = (70, 70, 75)
COLOR_CANO = (20, 20, 20)

# --- Enemigos ---
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
TIRADOR_DIST_IDEAL_MIN = 250
TIRADOR_DIST_IDEAL_MAX = 320
TIRADOR_COOLDOWN = 1.6
TIRADOR_BALA_VELOCIDAD = 380
COLOR_BALA_ENEMIGA = (120, 230, 150)
PROB_ESCUDO_DROP = 0.06
COLOR_ESCUDO = (90, 200, 230)

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
    if n >= 2:
        lista += ["perro"] * (1 + n // 2)
    if n >= 3:
        lista += ["tirador"] * (1 + n // 3)
    if n >= 4:
        lista += ["tanque"] * (1 + n // 4)
    if n >= 5:
        lista += ["kamikaze"] * (1 + n // 3)
    if n % 15 == 0 and n > 0:
        lista.append("auto")
    random.shuffle(lista)
    return lista


def reset_juego():
    global jugador_pos, jugador_vivo, jugador_escudo, jugador_invulnerable, camara_pos
    global enemigos, balas, balas_enemigos, particulas, explosiones, escudos
    global arma_actual, balas_disparadas_metralleta, recargando, tiempo_recarga_restante, angulo_recarga_extra
    global tiempo_desde_disparo
    global dash_cargas, dash_recarga_progreso, dash_tiempo_restante, dash_direccion, ralentizado_restante
    global oleada, cola_oleada, temporizador_spawn, puntaje
    global tiempo_gracia

    jugador_pos = pygame.Vector2(0, 0)
    jugador_vivo = True
    jugador_escudo = False
    jugador_invulnerable = TIEMPO_GRACIA_INICIAL
    camara_pos = pygame.Vector2(0, 0)

    enemigos = []
    balas = []
    balas_enemigos = []
    particulas = []
    explosiones = []
    escudos = []

    arma_actual = 0
    balas_disparadas_metralleta = 0
    recargando = False
    tiempo_recarga_restante = 0.0
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
    tiempo_gracia = TIEMPO_GRACIA_INICIAL


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


def matar_enemigo(e):
    global puntaje
    if e in enemigos:
        enemigos.remove(e)
    puntaje += TIPOS_ENEMIGOS[e["tipo"]]["puntos"]
    crear_particulas_pop(e["pos"], e["color"])
    if random.random() < PROB_ESCUDO_DROP:
        escudos.append({"pos": pygame.Vector2(e["pos"])})


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
    enemigos.append(e)


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
            if evento.key == pygame.K_SPACE:
                if dash_cargas > 0:
                    dash_cargas -= 1
                    dash_tiempo_restante = DASH_DURACION
                elif ralentizado_restante <= 0:
                    ralentizado_restante = RALENTIZADO_DURACION
            elif evento.key == pygame.K_1:
                arma_actual = 0
            elif evento.key == pygame.K_2:
                arma_actual = 1
            elif evento.key == pygame.K_3:
                arma_actual = 2

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

    if tiempo_gracia > 0:
        tiempo_gracia -= dt

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

    # --- Recarga metralleta ---
    if recargando:
        angulo_recarga_extra += 720 * dt
        tiempo_recarga_restante -= dt
        if tiempo_recarga_restante <= 0:
            recargando = False
            angulo_recarga_extra = 0.0

    # --- Disparo ---
    if disparar and not recargando:
        punta_mundo = centro_arma_mundo + aim_dir * (LARGO_ARMA / 2)
        if arma_actual == 0 and tiempo_desde_disparo >= METRALLETA_COOLDOWN:
            balas.append({"pos": pygame.Vector2(punta_mundo), "vel": aim_dir * 640,
                          "origen": pygame.Vector2(punta_mundo), "tipo": "normal", "dano": 1})
            tiempo_desde_disparo = 0
            balas_disparadas_metralleta += 1
            if balas_disparadas_metralleta >= METRALLETA_BALAS_RECARGA:
                balas_disparadas_metralleta = 0
                recargando = True
                tiempo_recarga_restante = METRALLETA_TIEMPO_RECARGA
        elif arma_actual == 1 and tiempo_desde_disparo >= ESCOPETA_COOLDOWN:
            for i in range(ESCOPETA_PERDIGONES):
                offset_grados = random.uniform(-ESCOPETA_SPREAD_GRADOS / 2, ESCOPETA_SPREAD_GRADOS / 2)
                ang2 = angulo + math.radians(offset_grados)
                dir2 = pygame.Vector2(math.cos(ang2), math.sin(ang2))
                balas.append({"pos": pygame.Vector2(punta_mundo), "vel": dir2 * 560,
                              "origen": pygame.Vector2(punta_mundo), "tipo": "escopeta",
                              "dano": 1, "vida_restante": ESCOPETA_VIDA_BALA})
            tiempo_desde_disparo = 0
        elif arma_actual == 2 and tiempo_desde_disparo >= BAZUCA_COOLDOWN:
            balas.append({"pos": pygame.Vector2(punta_mundo), "vel": aim_dir * 480,
                          "origen": pygame.Vector2(punta_mundo), "tipo": "bazuca", "dano": BAZUCA_DANO_AREA})
            tiempo_desde_disparo = 0

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
                if bala["tipo"] == "bazuca":
                    crear_explosion(bala["pos"], BAZUCA_RADIO_EXPLOSION)
                    for e2 in enemigos:
                        if (e2["pos"] - bala["pos"]).length() <= BAZUCA_RADIO_EXPLOSION:
                            e2["vida"] -= BAZUCA_DANO_AREA
                else:
                    enemigo["vida"] -= bala["dano"]
                impacto = True
                break

        if impacto or expiro:
            balas.remove(bala)

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
            if dist > TIRADOR_DIST_IDEAL_MAX:
                e["pos"] += hacia_n * e["velocidad"] * dt
            elif dist < TIRADOR_DIST_IDEAL_MIN:
                e["pos"] -= hacia_n * e["velocidad"] * dt
            e["cooldown_disparo"] -= dt
            if e["cooldown_disparo"] <= 0 and dist > 0:
                balas_enemigos.append({"pos": pygame.Vector2(e["pos"]), "vel": hacia_n * TIRADOR_BALA_VELOCIDAD,
                                       "origen": pygame.Vector2(e["pos"])})
                e["cooldown_disparo"] = TIRADOR_COOLDOWN

        elif tipo == "kamikaze":
            dist = (jugador_pos - e["pos"]).length()
            if e["estado"] == "acercandose":
                if dist <= UMBRAL_KAMIKAZE:
                    e["estado"] = "explotando"
                    e["fusible"] = FUSIBLE_KAMIKAZE
                    e["color"] = COLOR_KAMIKAZE_ARMADO
                hacia = jugador_pos - e["pos"]
                if hacia.length_squared() > 0:
                    e["pos"] += hacia.normalize() * e["velocidad"] * dt
            else:
                e["fusible"] -= dt
                if e["fusible"] <= 0:
                    crear_explosion(e["pos"], RADIO_EXPLOSION_KAMIKAZE, COLOR_KAMIKAZE_ARMADO)
                    if (jugador_pos - e["pos"]).length() <= RADIO_EXPLOSION_KAMIKAZE:
                        golpear_jugador()
                    matar_enemigo(e)

        elif tipo == "auto":
            deseada = jugador_pos - e["pos"]
            if deseada.length_squared() > 0:
                deseada = deseada.normalize()
            e["direccion_actual"] = e["direccion_actual"] + deseada * GIRO_AUTO * dt
            if e["direccion_actual"].length_squared() > 0:
                e["direccion_actual"] = e["direccion_actual"].normalize()
            e["pos"] += e["direccion_actual"] * e["velocidad"] * dt

    # --- Balas enemigas ---
    for be in balas_enemigos[:]:
        be["pos"] += be["vel"] * dt
        if (be["pos"] - be["origen"]).length() > BALA_ALCANCE:
            balas_enemigos.remove(be)
            continue
        if (be["pos"] - jugador_pos).length() < (BALA_TAMANO / 2 + jugador_radio):
            golpear_jugador()
            balas_enemigos.remove(be)

    # --- Contacto directo enemigo-jugador ---
    for e in enemigos:
        if (e["pos"] - jugador_pos).length() < (e["radio"] + jugador_radio):
            golpear_jugador()
            break

    # --- Escudos en el piso ---
    for esc in escudos[:]:
        if (esc["pos"] - jugador_pos).length() < (jugador_radio + 10) and not jugador_escudo:
            jugador_escudo = True
            escudos.remove(esc)

    # --- Partículas y explosiones ---
    for p in particulas[:]:
        p["pos"] += p["vel"] * dt
        p["vida"] -= dt
        if p["vida"] <= 0:
            particulas.remove(p)
    for ex in explosiones[:]:
        ex["vida"] -= dt
        if ex["vida"] <= 0:
            explosiones.remove(ex)

    # --- Oleadas ---
    if jugador_vivo:
        if tiempo_gracia <= 0:
            if cola_oleada:
                temporizador_spawn += dt
                if temporizador_spawn >= 2.0:
                    temporizador_spawn = 0.0
                    crear_enemigo(cola_oleada.pop())
            elif not enemigos:
                oleada += 1
                cola_oleada = generar_oleada(oleada)
                temporizador_spawn = 0.0

    # ============ DIBUJADO ============
    pantalla.fill(COLOR_TILE_A)

    inicio_x = int((camara_pos.x - ANCHO / 2) // TILE) - 1
    fin_x = int((camara_pos.x + ANCHO / 2) // TILE) + 1
    inicio_y = int((camara_pos.y - ALTO / 2) // TILE) - 1
    fin_y = int((camara_pos.y + ALTO / 2) // TILE) + 1
    for gx in range(inicio_x, fin_x + 1):
        for gy in range(inicio_y, fin_y + 1):
            rp = mundo_a_pantalla(pygame.Vector2(gx * TILE, gy * TILE))
            color = COLOR_TILE_A if (gx + gy) % 2 == 0 else COLOR_TILE_B
            pygame.draw.rect(pantalla, color, (rp.x, rp.y, TILE, TILE))

    for esc in escudos:
        ep = mundo_a_pantalla(esc["pos"])
        pygame.draw.rect(pantalla, COLOR_ESCUDO, (ep.x - 6, ep.y - 6, 12, 12), border_radius=2)

    for ex in explosiones:
        alpha = max(0, int(180 * (ex["vida"] / ex["vida_max"])))
        s = pygame.Surface((ex["radio"] * 2, ex["radio"] * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*ex["color"], alpha), (ex["radio"], ex["radio"]), ex["radio"])
        pp = mundo_a_pantalla(ex["pos"])
        pantalla.blit(s, (pp.x - ex["radio"], pp.y - ex["radio"]))

    for p in particulas:
        pp = mundo_a_pantalla(p["pos"])
        pygame.draw.circle(pantalla, p["color"], (int(pp.x), int(pp.y)), 3)

    for be in balas_enemigos:
        bp = mundo_a_pantalla(be["pos"])
        pygame.draw.circle(pantalla, COLOR_BALA_ENEMIGA, (int(bp.x), int(bp.y)), BALA_TAMANO // 2)

    for e in enemigos:
        ep = mundo_a_pantalla(e["pos"])
        pygame.draw.circle(pantalla, e["color"], (int(ep.x), int(ep.y)), e["radio"])
        pygame.draw.circle(pantalla, (20, 20, 20), (int(ep.x), int(ep.y)), e["radio"], width=2)

    for b in balas:
        bp = mundo_a_pantalla(b["pos"])
        color_b = (255, 200, 50) if b["tipo"] == "bazuca" else (255, 230, 100)
        radio_b = 6 if b["tipo"] == "bazuca" else BALA_TAMANO // 2
        pygame.draw.circle(pantalla, color_b, (int(bp.x), int(bp.y)), radio_b)

    # --- Dibujar arma ---
    m_surf = pygame.Surface((LARGO_ARMA, ANCHO_ARMA), pygame.SRCALPHA)
    m_surf.fill(COLOR_ARMA)
    pygame.draw.rect(m_surf, COLOR_CANO, (LARGO_ARMA - 6, 1, 6, ANCHO_ARMA - 2))
    rot_deg = -math.degrees(angulo + math.radians(angulo_recarga_extra))
    rot_surf = pygame.transform.rotate(m_surf, rot_deg)
    rot_rect = rot_surf.get_rect(center=centro_arma_pantalla)
    pantalla.blit(rot_surf, rot_rect.topleft)

    # --- Dibujar jugador ---
    if jugador_vivo:
        # Parpadeo suave si es invulnerable
        if jugador_invulnerable <= 0 or int(jugador_invulnerable * 10) % 2 == 0:
            pygame.draw.circle(pantalla, COLOR_JUGADOR, (int(jugador_pantalla.x), int(jugador_pantalla.y)), jugador_radio)
            pygame.draw.circle(pantalla, (20, 20, 20), (int(jugador_pantalla.x), int(jugador_pantalla.y)), jugador_radio, width=2)
            if jugador_escudo:
                pygame.draw.circle(pantalla, COLOR_ESCUDO, (int(jugador_pantalla.x), int(jugador_pantalla.y)), jugador_radio + 4, width=2)

    # --- Viñeta de bordes ---
    pantalla.blit(vignette, (0, 0))

    # --- HUD ---
    texto_hud = fuente_chica.render(
        f"Oleada: {oleada}  |  Enemigos rest: {len(cola_oleada) + len(enemigos)}  |  Arma: {ARMAS[arma_actual]}  |  Puntaje: {puntaje}",
        True, (230, 230, 230)
    )
    pantalla.blit(texto_hud, (15, 15))

    # Indicador de recarga
    if recargando:
        txt_rec = fuente_chica.render("¡RECARGANDO!", True, (255, 80, 80))
        pantalla.blit(txt_rec, (15, 42))

    # Indicador de tiempo de gracia
    if tiempo_gracia > 0:
        txt_gracia = fuente_chica.render(f"PREPÁRATE: {tiempo_gracia:.1f}s", True, (100, 200, 255))
        pantalla.blit(txt_gracia, (15, 68))

    pygame.display.flip()

pygame.quit()
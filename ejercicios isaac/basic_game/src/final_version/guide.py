import pygame
import math
import random
from src.final_version import game_config 
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
pygame.display.set_caption("Hotline - la - matanza")
reloj = pygame.time.Clock()
fuente_grande = pygame.font.SysFont(None, 72)
fuente_media = pygame.font.SysFont(None, 40)
fuente_chica = pygame.font.SysFont(None, 26)

CENTRO_PANTALLA = pygame.Vector2(ANCHO / 2, ALTO / 2)


# --- Cámara ---
LEAN_MOUSE = 0.35
SUAVIZADO_CAMARA = 8.0

# =========================================================
# VIÑETA
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
# ESTADO DEL JUEGO
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
    global metralleta_municion, metralleta_recargando, metralleta_tiempo_recarga_restante
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

    metralleta_municion = game_config.METRALLETA_MUNICION_MAX
    metralleta_recargando = False
    metralleta_tiempo_recarga_restante = 0.0

    escopeta_disparos_restantes = game_config.ESCOPETA_BALAS_RECARGA
    escopeta_recargando = False
    escopeta_tiempo_recarga_restante = 0.0

    revolver_disparos_restantes = game_config.REVOLVER_BALAS_RECARGA
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

    tiempo_preparacion_restante = 0.0
    titulo_oleada_texto = f"Oleada {oleada}"
    titulo_oleada_duracion = 3.0
    titulo_oleada_tiempo = 3.0


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
                # Recarga manual con R
                if arma_actual == 0 and not metralleta_recargando and metralleta_municion < METRALLETA_MUNICION_MAX:
                    metralleta_recargando = True
                    metralleta_tiempo_recarga_restante = METRALLETA_TIEMPO_RECARGA
                elif arma_actual == 1 and not escopeta_recargando and escopeta_disparos_restantes < ESCOPETA_BALAS_RECARGA:
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

    # --- Recarga escopeta / revólver ---
    # --- Recarga escopeta / revólver ---
    # --- Recarga metralleta / escopeta / revólver ---
    if metralleta_recargando:
        angulo_recarga_extra += 360 * dt
        metralleta_tiempo_recarga_restante -= dt
        if metralleta_tiempo_recarga_restante <= 0:
            metralleta_recargando = False
            metralleta_municion = METRALLETA_MUNICION_MAX
            metralleta_tiempo_recarga_restante = 0.0
            angulo_recarga_extra = 0.0

    if escopeta_recargando:
        angulo_recarga_extra += 480 * dt
        escopeta_tiempo_recarga_restante -= dt
        if escopeta_tiempo_recarga_restante <= 0:
            escopeta_recargando = False
            escopeta_disparos_restantes = ESCOPETA_BALAS_RECARGA
            escopeta_tiempo_recarga_restante = 0.0
            angulo_recarga_extra = 0.0

    if revolver_recargando:
        angulo_recarga_extra += 720 * dt
        revolver_tiempo_recarga_restante -= dt
        if revolver_tiempo_recarga_restante <= 0:
            revolver_recargando = False
            revolver_disparos_restantes = REVOLVER_BALAS_RECARGA
            revolver_tiempo_recarga_restante = 0.0
            angulo_recarga_extra = 0.0

    # --- Disparo ---
    mouse_sostenido = pygame.mouse.get_pressed()[0]
    punta_mundo = centro_arma_mundo + aim_dir * (LARGO_ARMA / 2)

    # Disparo Metralleta
    if arma_actual == 0 and mouse_sostenido and not metralleta_recargando and tiempo_desde_disparo >= METRALLETA_COOLDOWN:
        if metralleta_municion > 0:
            balas.append({"pos": pygame.Vector2(punta_mundo), "vel": aim_dir * 640,
                          "origen": pygame.Vector2(punta_mundo), "tipo": "normal", "dano": METRALLETA_DANO})
            tiempo_desde_disparo = 0
            metralleta_municion -= 1
            jugador_pos -= aim_dir * RETROCESO_METRALLETA

            # Recarga automática al vaciar el cargador
            if metralleta_municion <= 0:
                metralleta_recargando = True
                metralleta_tiempo_recarga_restante = METRALLETA_TIEMPO_RECARGA

    # Disparo Escopeta
    elif arma_actual == 1 and disparar and not escopeta_recargando:
        if escopeta_disparos_restantes > 0:
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

    # Disparo Revólver
    elif arma_actual == 2 and disparar and not revolver_recargando:
        if revolver_disparos_restantes > 0:
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

    # --- Actualizar balas enemigas ---
    for b_e in balas_enemigos[:]:
        b_e["pos"] += b_e["vel"] * dt
        if (b_e["pos"] - b_e["origen"]).length() > BALA_ALCANCE:
            balas_enemigos.remove(b_e)
        elif (b_e["pos"] - jugador_pos).length() < (jugador_radio + 4):
            golpear_jugador()
            balas_enemigos.remove(b_e)

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

            if dist < TIRADOR_DIST_IDEAL_MIN:
                e["pos"] -= hacia_n * e["velocidad"] * dt
            elif dist > TIRADOR_DIST_IDEAL_MAX:
                e["pos"] += hacia_n * e["velocidad"] * dt

            e["cooldown_disparo"] -= dt
            if e["cooldown_disparo"] <= 0 and dist > 0:
                balas_enemigos.append({
                    "pos": pygame.Vector2(e["pos"]),
                    "vel": hacia_n * TIRADOR_BALA_VELOCIDAD,
                    "origen": pygame.Vector2(e["pos"])
                })
                e["cooldown_disparo"] = TIRADOR_COOLDOWN

        elif tipo == "kamikaze":
            hacia = jugador_pos - e["pos"]
            dist = hacia.length()
            if e["estado"] == "acercandose":
                if dist > 0:
                    e["pos"] += hacia.normalize() * e["velocidad"] * dt
                if dist < UMBRAL_KAMIKAZE:
                    e["estado"] = "armado"
                    e["color"] = COLOR_KAMIKAZE_ARMADO
            elif e["estado"] == "armado":
                e["fusible"] += dt
                if e["fusible"] >= FUSIBLE_KAMIKAZE:
                    crear_explosion(e["pos"], RADIO_EXPLOSION_KAMIKAZE)
                    if (e["pos"] - jugador_pos).length() < RADIO_EXPLOSION_KAMIKAZE:
                        golpear_jugador()
                    matar_enemigo(e)

        elif tipo == "auto":
            hacia = jugador_pos - e["pos"]
            if hacia.length_squared() > 0:
                dir_deseada = hacia.normalize()
                e["direccion_actual"] = e["direccion_actual"].rotate_towards(dir_deseada, GIRO_AUTO)
            e["pos"] += e["direccion_actual"] * e["velocidad"] * dt
            e["temporizador_estela"] += dt
            if e["temporizador_estela"] >= ESTELA_INTERVALO:
                crear_estela(e["pos"])
                e["temporizador_estela"] = 0.0

        # Colisión de enemigos con jugador
        if (e["pos"] - jugador_pos).length() < (e["radio"] + jugador_radio):
            golpear_jugador()

    # --- Spawner de oleadas ---
    if tiempo_preparacion_restante > 0:
        tiempo_preparacion_restante -= dt
    else:
        if cola_oleada:
            temporizador_spawn += dt
            if temporizador_spawn >= 0.8:
                tipo_spawn = cola_oleada.pop(0)
                crear_enemigo(tipo_spawn)
                temporizador_spawn = 0.0
        elif not enemigos:
            oleada += 1
            cola_oleada = generar_oleada(oleada)
            tiempo_preparacion_restante = PREPARACION_ENTRE_OLEADAS
            titulo_oleada_texto = f"Oleada {oleada}"
            titulo_oleada_duracion = 3.0
            titulo_oleada_tiempo = 3.0

            if oleada == OLEADA_APARICION_ESCOPETA and not armas_desbloqueadas[1]:
                crear_pickup_arma(1)
            if oleada == OLEADA_APARICION_REVOLVER and not armas_desbloqueadas[2]:
                crear_pickup_arma(2)

    # --- Actualizar partículas, explosiones y estelas ---
    for p in particulas[:]:
        p["pos"] += p["vel"] * dt
        p["vida"] -= dt
        if p["vida"] <= 0:
            particulas.remove(p)

    for ex in explosiones[:]:
        ex["vida"] -= dt
        if ex["vida"] <= 0:
            explosiones.remove(ex)

    for es in estelas[:]:
        es["vida"] -= dt
        if es["vida"] <= 0:
            estelas.remove(es)

    # ================= RENDERIZADO =================
    pantalla.fill(COLOR_TILE_A)

    # Dibujar suelo (grid de tiles)
    ox = int(camara_pos.x) % TILE
    oy = int(camara_pos.y) % TILE
    for x in range(-ox, ANCHO, TILE):
        for y in range(-oy, ALTO, TILE):
            tx = int((x + camara_pos.x) // TILE)
            ty = int((y + camara_pos.y) // TILE)
            if (tx + ty) % 2 == 0:
                pygame.draw.rect(pantalla, COLOR_TILE_B, (x, y, TILE, TILE))

    # Dibujar estelas
    for es in estelas:
        pos_p = mundo_a_pantalla(es["pos"])
        r = int(ESTELA_RADIO * (es["vida"] / es["vida_max"]))
        if r > 0:
            pygame.draw.circle(pantalla, COLOR_ESTELA, (int(pos_p.x), int(pos_p.y)), r)

    # Pickups de armas
    for pk in pickups_armas:
        pos_p = mundo_a_pantalla(pk["pos"])
        pygame.draw.circle(pantalla, COLOR_PICKUP_ARMA, (int(pos_p.x), int(pos_p.y)), 10)

    # Jugador
    pos_j_pantalla = mundo_a_pantalla(jugador_pos)
    pygame.draw.circle(pantalla, COLOR_JUGADOR, (int(pos_j_pantalla.x), int(pos_j_pantalla.y)), jugador_radio)

    # Arma del jugador
    ang_final = angulo + math.radians(angulo_recarga_extra)
    superficie_arma = pygame.Surface((LARGO_ARMA, ANCHO_ARMA), pygame.SRCALPHA)
    superficie_arma.fill(COLOR_ARMA)
    pygame.draw.rect(superficie_arma, COLOR_CANO, (LARGO_ARMA - 6, 1, 6, ANCHO_ARMA - 2))
    rotada = pygame.transform.rotate(superficie_arma, -math.degrees(ang_final))
    rect_rotada = rotada.get_rect(center=centro_arma_pantalla)
    pantalla.blit(rotada, rect_rotada)

    # Enemigos
    for e in enemigos:
        p = mundo_a_pantalla(e["pos"])
        pygame.draw.circle(pantalla, e["color"], (int(p.x), int(p.y)), e["radio"])

    # Balas
    for b in balas:
        p = mundo_a_pantalla(b["pos"])
        pygame.draw.circle(pantalla, (255, 230, 100), (int(p.x), int(p.y)), BALA_TAMANO // 2)

    for b_e in balas_enemigos:
        p = mundo_a_pantalla(b_e["pos"])
        pygame.draw.circle(pantalla, COLOR_BALA_ENEMIGA, (int(p.x), int(p.y)), BALA_TAMANO // 2)

    # Explosiones y Partículas
    for ex in explosiones:
        p = mundo_a_pantalla(ex["pos"])
        r = int(ex["radio"] * (1 - ex["vida"] / ex["vida_max"]))
        pygame.draw.circle(pantalla, ex["color"], (int(p.x), int(p.y)), max(1, r), width=3)

    for part in particulas:
        p = mundo_a_pantalla(part["pos"])
        pygame.draw.circle(pantalla, part["color"], (int(p.x), int(p.y)), 3)

    # Viñeta
    pantalla.blit(vignette, (0, 0))

    # --- HUD ---
    # Arma actual y Munición
    nombre_arma = ARMAS[arma_actual]
    if arma_actual == 0:
       if arma_actual == 0:
        info_mun = "RECARGANDO..." if metralleta_recargando else f"{metralleta_municion}/{METRALLETA_MUNICION_MAX}"
    elif arma_actual == 1:
        info_mun = "RECARGANDO..." if escopeta_recargando else f"{escopeta_disparos_restantes}/{ESCOPETA_BALAS_RECARGA}"
    else:
        info_mun = "RECARGANDO..." if revolver_recargando else f"{revolver_disparos_restantes}/{REVOLVER_BALAS_RECARGA}"

    t_hud = fuente_chica.render(f"Arma: {nombre_arma} | Balas: {info_mun}", True, (240, 240, 240))
    pantalla.blit(t_hud, (16, ALTO - 36))

    t_pts = fuente_chica.render(f"Puntos: {puntaje} | Oleada: {oleada}", True, (240, 240, 240))
    pantalla.blit(t_pts, (16, 16))

    # Cargas de Dash
    t_dash = fuente_chica.render(f"Dash (Q): {dash_cargas}/{DASH_MAX_CARGAS}", True, (100, 200, 255))
    pantalla.blit(t_dash, (16, 42))

    # Anuncio de Oleada
    if titulo_oleada_tiempo > 0:
        titulo_oleada_tiempo -= dt
        t_tit = fuente_grande.render(titulo_oleada_texto, True, COLOR_TITULO_OLEADA)
        pantalla.blit(t_tit, t_tit.get_rect(center=(ANCHO / 2, 80)))

    # Minimapa
    pygame.draw.circle(pantalla, COLOR_MINIMAPA_FONDO, MINIMAPA_CENTRO, MINIMAPA_RADIO)
    pygame.draw.circle(pantalla, COLOR_MINIMAPA_BORDE, MINIMAPA_CENTRO, MINIMAPA_RADIO, width=2)
    # Punto jugador en minimapa
    pygame.draw.circle(pantalla, COLOR_JUGADOR, MINIMAPA_CENTRO, 3)
    # Puntos enemigos en minimapa
    for e in enemigos:
        rel = (e["pos"] - jugador_pos) * MINIMAPA_ESCALA
        if rel.length() < MINIMAPA_RADIO - 2:
            p_mini = (int(MINIMAPA_CENTRO[0] + rel.x), int(MINIMAPA_CENTRO[1] + rel.y))
            pygame.draw.circle(pantalla, e["color"], p_mini, 2)

    pygame.display.flip()

pygame.quit()
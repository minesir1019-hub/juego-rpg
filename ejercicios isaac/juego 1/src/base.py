import pygame

pygame.init()

ANCHO, ALTO = 960, 540
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Movimiento estilo Hotline Miami")
reloj = pygame.time.Clock()
CENTRO_PANTALLA = pygame.Vector2(ANCHO / 2, ALTO / 2)










# ============================================================
# ARMAS
# ============================================================

class Arma:
    def __init__(self, nombre, daño, cadencia, velocidad_bala, color_bala):
        self.nombre = nombre
        self.daño = daño
        self.cadencia = cadencia
        self.velocidad_bala = velocidad_bala
        self.color_bala = color_bala
        self.tiempo_desde_disparo = 999
        self.balas = []

    def disparar(self, origen, direccion):
        if self.tiempo_desde_disparo < self.cadencia:
            return

        self.tiempo_desde_disparo = 0
        
        self.balas.append({
            "pos": pygame.Vector2(origen),
            "vel": direccion * self.velocidad_bala,
            "origen": pygame.Vector2(origen),
        })

    def actualizar(self, dt, alcance_max=700):
        self.tiempo_desde_disparo += dt

        for bala in self.balas[:]:
            bala["pos"] += bala["vel"] * dt

            if (bala["pos"] - bala["origen"]).length() > alcance_max:
                self.balas.remove(bala)

    def dibujar(self, pantalla, mundo_a_pantalla):
        for bala in self.balas:
            pos = mundo_a_pantalla(bala["pos"])

            pygame.draw.circle(
                pantalla,
                self.color_bala,
                (round(pos.x), round(pos.y)),
                4
            )










# ============================================================
# CAMARA
# ============================================================

class Camara:
    def __init__(self, centro_pantalla, lean_mouse=0.35, suavizado=8.0):
        self.pos = pygame.Vector2(0, 0)
        self.centro_pantalla = centro_pantalla
        self.lean_mouse = lean_mouse
        self.suavizado = suavizado

    def actualizar(self, objetivo_pos, mouse_pos, dt):
        offset_mouse = mouse_pos - self.centro_pantalla

        objetivo_camara = (
            objetivo_pos +
            offset_mouse * self.lean_mouse
        )

        self.pos += (
            objetivo_camara - self.pos
        ) * min(self.suavizado * dt, 1)

    def mundo_a_pantalla(self, punto_mundo):
        return (
            punto_mundo -
            self.pos +
            self.centro_pantalla
        )









# ============================================================
# MAPA
# ============================================================

class Mapa:
    def __init__(
        self,
        tile=40,
        color_a=(40, 40, 46),
        color_b=(34, 34, 40)
    ):
        self.tile = tile
        self.color_a = color_a
        self.color_b = color_b

    def dibujar(self, pantalla, camara, ancho, alto):
        pos = camara.pos

        inicio_x = int(
            (pos.x - ancho / 2) // self.tile
        ) - 1

        fin_x = int(
            (pos.x + ancho / 2) // self.tile
        ) + 1

        inicio_y = int(
            (pos.y - alto / 2) // self.tile
        ) - 1

        fin_y = int(
            (pos.y + alto / 2) // self.tile
        ) + 1

        for gx in range(inicio_x, fin_x + 1):
            for gy in range(inicio_y, fin_y + 1):

                punto_mundo = pygame.Vector2(
                    gx * self.tile,
                    gy * self.tile
                )

                punto_pantalla = camara.mundo_a_pantalla(
                    punto_mundo
                )

                color = (
                    self.color_a
                    if (gx + gy) % 2 == 0
                    else self.color_b
                )

                pygame.draw.rect(
                    pantalla,
                    color,
                    (
                        punto_pantalla.x,
                        punto_pantalla.y,
                        self.tile,
                        self.tile
                    )
                )










# ============================================================
# ENTIDADES
# ============================================================

class Jugador:
    def __init__(self, x, y, arma):
        self.pos = pygame.Vector2(x, y)

        self.radio = 16

        self.velocidad_caminar = 200
        self.velocidad_correr = 320

        self.arma = arma

    def mover(self, dt):
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

        # Evita que el jugador se mueva más rápido
        # al moverse en diagonal.
        if direccion.length_squared() > 0:
            direccion = direccion.normalize()

        corriendo_shift = teclas[pygame.K_LSHIFT]

        velocidad = (
            self.velocidad_correr
            if corriendo_shift
            else self.velocidad_caminar
        )

        self.pos += direccion * velocidad * dt

    def disparar(self, pos_pantalla, mouse_pos):
        direccion = mouse_pos - pos_pantalla

        if direccion.length_squared() > 0:
            direccion = direccion.normalize()

            self.arma.disparar(
                self.pos,
                direccion
            )

    def dibujar(self, pantalla, mundo_a_pantalla):
        pos_pantalla = mundo_a_pantalla(self.pos)

        pygame.draw.circle(
            pantalla,
            (230, 60, 60),
            pos_pantalla,
            self.radio
        )








# ============================================================
# INICIALIZACIÓN
# ============================================================

camara = Camara(CENTRO_PANTALLA)

mapa = Mapa()

metralleta = Arma(
    "Metralleta",
    daño=1,
    cadencia=0.12,
    velocidad_bala=640,
    color_bala=(240, 220, 90)
)

jugador = Jugador(
    0,
    0,
    metralleta
)










# ============================================================
# LOOP PRINCIPAL
# ============================================================

corriendo = True

while corriendo:

    dt = reloj.tick(60) / 1000

    mouse_pos = pygame.Vector2(
        pygame.mouse.get_pos()
    )

    disparando = pygame.mouse.get_pressed()[0]









    # --------------------------------------------------------
    # EVENTOS
    # --------------------------------------------------------

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            corriendo = False







    # --------------------------------------------------------
    # JUGADOR
    # --------------------------------------------------------




    jugador.mover(dt)

    # --------------------------------------------------------
    # CAMARA
    # --------------------------------------------------------





    camara.actualizar(
        jugador.pos,
        mouse_pos,
        dt
    )






    # --------------------------------------------------------
    # DISPARO
    # --------------------------------------------------------
    pos_pantalla_jugador = camara.mundo_a_pantalla(
        jugador.pos
    )

    if disparando:
        jugador.disparar(
            pos_pantalla_jugador,
            mouse_pos
        )





    # -------------------------------------------------------
    # ARMAS
    # --------------------------------------------------------

    jugador.arma.actualizar(dt)








    # --------------------------------------------------------
    # DIBUJADO
    # --------------------------------------------------------

    pantalla.fill((20, 20, 25))

    mapa.dibujar(
        pantalla,
        camara,
        ANCHO,
        ALTO
    )

    jugador.dibujar(
        pantalla,
        camara.mundo_a_pantalla
    )

    jugador.arma.dibujar(
        pantalla,
        camara.mundo_a_pantalla
    )

    pygame.display.flip()





# ============================================================
# CERRAR PYGAME
# ============================================================

pygame.quit()
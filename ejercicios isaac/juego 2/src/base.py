import pygame

pygame.init()

ANCHO, ALTO = 960, 540
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("JUEGAZO")
reloj = pygame.time.Clock()

# Tamaño del mundo
ANCHO_MUNDO = 3000
ALTO_MUNDO = 2000


class Arma:
    def __init__(self, aspecto, balas, recarga, daño):
        self.aspecto = aspecto
        self.balas = balas
        self.balas_maximas = balas
        self.recarga = recarga
        self.daño = daño

        # Tiempo entre disparos
        self.ultimo_disparo = 0
        self.cadencia = 200  # milisegundos


class Bala:
    def __init__(self, posicion, direccion, daño):
        self.posicion = pygame.Vector2(posicion)
        self.direccion = pygame.Vector2(direccion).normalize()
        self.velocidad = 15
        self.daño = daño
        self.radio = 5

    def mover(self):
        self.posicion += self.direccion * self.velocidad

    def dibujar(self, pantalla, camara):
        posicion_pantalla = self.posicion - camara

        pygame.draw.circle(
            pantalla,
            (255, 230, 50),
            (int(posicion_pantalla.x), int(posicion_pantalla.y)),
            self.radio
        )


class Jugador:
    def __init__(self, nombre, arma, vida, velocidad):
        self.arma = arma
        self.vida = vida
        self.nombre = nombre
        self.velocidad = velocidad

        # Posición en el MUNDO
        self.posicion = pygame.Vector2(
            ANCHO_MUNDO / 2,
            ALTO_MUNDO / 2
        )

        self.radio = 20

    def moverse(self):
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

        self.posicion += direccion * self.velocidad

        # No permitir salir del mundo
        self.posicion.x = max(
            self.radio,
            min(ANCHO_MUNDO - self.radio, self.posicion.x)
        )

        self.posicion.y = max(
            self.radio,
            min(ALTO_MUNDO - self.radio, self.posicion.y)
        )

    def dibujar(self, pantalla, camara):
        posicion_pantalla = self.posicion - camara

        pygame.draw.circle(
            pantalla,
            (50, 150, 255),
            (int(posicion_pantalla.x), int(posicion_pantalla.y)),
            self.radio
        )

    def disparar(self, balas, camara):
        tiempo_actual = pygame.time.get_ticks()

        # Controlar cadencia
        if tiempo_actual - self.arma.ultimo_disparo < self.arma.cadencia:
            return

        # Comprobar munición
        if self.arma.balas <= 0:
            return

        # Posición del mouse en pantalla
        mouse = pygame.Vector2(pygame.mouse.get_pos())

        # Convertir mouse de pantalla -> mundo
        objetivo = mouse + camara

        # Dirección desde el jugador hacia el mouse
        direccion = objetivo - self.posicion

        if direccion.length() == 0:
            return

        direccion = direccion.normalize()

        bala = Bala(
            self.posicion,
            direccion,
            self.arma.daño
        )

        balas.append(bala)

        self.arma.balas -= 1
        self.arma.ultimo_disparo = tiempo_actual


# --------------------------------
# CREAR OBJETOS
# --------------------------------

arma1 = Arma(
    "Pistola",
    12,
    2,
    25
)

jugador = Jugador(
    "Jugador1",
    arma1,
    100,
    5
)

balas = []


# --------------------------------
# BUCLE PRINCIPAL
# --------------------------------

ejecutando = True

while ejecutando:

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            ejecutando = False

        # Disparar con click izquierdo
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                jugador.disparar(balas, camara)

    # --------------------------------
    # MOVIMIENTO
    # --------------------------------

    jugador.moverse()

    # --------------------------------
    # CÁMARA
    # --------------------------------

    # La cámara intenta mantener al jugador en el centro
    camara = jugador.posicion - pygame.Vector2(
        ANCHO / 2,
        ALTO / 2
    )

    # Limitar cámara al mundo
    camara.x = max(
        0,
        min(ANCHO_MUNDO - ANCHO, camara.x)
    )

    camara.y = max(
        0,
        min(ALTO_MUNDO - ALTO, camara.y)
    )

    # --------------------------------
    # MOVER BALAS
    # --------------------------------

    for bala in balas:
        bala.mover()

    # Eliminar balas que salen del mundo
    balas = [
        bala for bala in balas
        if 0 < bala.posicion.x < ANCHO_MUNDO
        and 0 < bala.posicion.y < ALTO_MUNDO
    ]

    # --------------------------------
    # DIBUJAR
    # --------------------------------

    pantalla.fill((35, 35, 35))

    # Dibujar cuadrícula del mundo
    tamaño_celda = 100

    inicio_x = int(camara.x // tamaño_celda) * tamaño_celda
    inicio_y = int(camara.y // tamaño_celda) * tamaño_celda

    for x in range(
        inicio_x,
        int(camara.x + ANCHO) + tamaño_celda,
        tamaño_celda
    ):
        pygame.draw.line(
            pantalla,
            (50, 50, 50),
            (x - camara.x, 0),
            (x - camara.x, ALTO)
        )

    for y in range(
        inicio_y,
        int(camara.y + ALTO) + tamaño_celda,
        tamaño_celda
    ):
        pygame.draw.line(
            pantalla,
            (50, 50, 50),
            (0, y - camara.y),
            (ANCHO, y - camara.y)
        )

    # Dibujar balas
    for bala in balas:
        bala.dibujar(pantalla, camara)

    # Dibujar jugador
    jugador.dibujar(pantalla, camara)

    # --------------------------------
    # INFORMACIÓN
    # --------------------------------

    fuente = pygame.font.Font(None, 30)

    texto = fuente.render(
        f"Balas: {jugador.arma.balas}/{jugador.arma.balas_maximas}",
        True,
        (255, 255, 255)
    )

    pantalla.blit(texto, (20, 20))

    pygame.display.flip()

    reloj.tick(60)


pygame.quit()
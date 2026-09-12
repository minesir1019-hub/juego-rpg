##iluminacion dinamica 
import pygame
import sys
import math

# ============================================================
# INICIALIZAR PYGAME
# ============================================================

pygame.init()

WIDTH, HEIGHT = 800, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Entorno oscuro e iluminable")

clock = pygame.time.Clock()


# ============================================================
# FUNCIÓN PARA CREAR UNA MÁSCARA DE LUZ
# ============================================================

def create_light_mask(radius):
    """
    Crea una máscara circular con un degradado.
    El centro es completamente transparente y
    los bordes son cada vez más oscuros.
    """

    mask = pygame.Surface(
        (radius * 2, radius * 2),
        pygame.SRCALPHA
    )

    # Empezamos desde el borde hacia el centro
    for r in range(radius, 0, -2):

        # 0 = transparente
        # 255 = completamente opaco
        alpha = int(255 * (r / radius) ** 2)

        pygame.draw.circle(
            mask,
            (0, 0, 0, alpha),
            (radius, radius),
            r
        )

    return mask


# Tamaño de la iluminación
light_radius = 180

light_mask = create_light_mask(light_radius)


# ============================================================
# OBJETOS
# ============================================================

# [X, Y, Radio, Color, Nombre, Arrastrando]

objeto_luz = [
    200,
    300,
    40,
    (255, 215, 0),
    "Luz Amarilla",
    False
]

objeto_piedra = [
    500,
    300,
    45,
    (100, 100, 100),
    "Piedra Gris",
    False
]

objetos = [
    objeto_luz,
    objeto_piedra
]

objeto_seleccionado = None


# ============================================================
# BUCLE PRINCIPAL
# ============================================================

running = True

while running:

    mouse_pos = pygame.mouse.get_pos()


    # ========================================================
    # EVENTOS
    # ========================================================

    for event in pygame.event.get():

        # Cerrar ventana
        if event.type == pygame.QUIT:
            running = False


        # ----------------------------------------------------
        # CLIC DEL MOUSE
        # ----------------------------------------------------

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                for obj in objetos:

                    dx = mouse_pos[0] - obj[0]
                    dy = mouse_pos[1] - obj[1]

                    # Distancia al cuadrado
                    distancia_2 = dx * dx + dy * dy

                    # Comprobar si el mouse está dentro del objeto
                    if distancia_2 < obj[2] * obj[2]:

                        obj[5] = True
                        objeto_seleccionado = obj

                        break


        # ----------------------------------------------------
        # SOLTAR EL MOUSE
        # ----------------------------------------------------

        elif event.type == pygame.MOUSEBUTTONUP:

            if event.button == 1:

                if objeto_seleccionado:

                    objeto_seleccionado[5] = False
                    objeto_seleccionado = None


    # ========================================================
    # MOVER OBJETO
    # ========================================================

    if objeto_seleccionado:

        objeto_seleccionado[0] = mouse_pos[0]
        objeto_seleccionado[1] = mouse_pos[1]


    # ========================================================
    # DIBUJAR EL ESCENARIO
    # ========================================================

    # Fondo oscuro
    screen.fill((20, 20, 30))


    # --------------------------------------------------------
    # CUADRÍCULA
    # --------------------------------------------------------

    for x in range(0, WIDTH, 80):

        pygame.draw.line(
            screen,
            (30, 35, 45),
            (x, 0),
            (x, HEIGHT)
        )


    for y in range(0, HEIGHT, 80):

        pygame.draw.line(
            screen,
            (30, 35, 45),
            (0, y),
            (WIDTH, y)
        )


    # ========================================================
    # DIBUJAR OBJETOS
    # ========================================================

    # Luz amarilla
    pygame.draw.circle(
        screen,
        objeto_luz[3],
        (objeto_luz[0], objeto_luz[1]),
        objeto_luz[2]
    )


    # Piedra
    pygame.draw.circle(
        screen,
        objeto_piedra[3],
        (objeto_piedra[0], objeto_piedra[1]),
        objeto_piedra[2]
    )


    # Relieve de la piedra
    pygame.draw.circle(
        screen,
        (70, 70, 70),
        (objeto_piedra[0], objeto_piedra[1]),
        objeto_piedra[2] - 8
    )


    # ========================================================
    # OSCURIDAD AMBIENTAL
    # ========================================================

    ambient_light = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    # Oscuridad casi total
    ambient_light.fill(
        (5, 5, 10, 245)
    )


    # ========================================================
    # RECORTAR LA OSCURIDAD CON LA LUZ
    # ========================================================

    ambient_light.blit(
        light_mask,
        (
            objeto_luz[0] - light_radius,
            objeto_luz[1] - light_radius
        ),
        special_flags=pygame.BLEND_RGBA_SUB
    )


    # ========================================================
    # APLICAR OSCURIDAD
    # ========================================================

    screen.blit(
        ambient_light,
        (0, 0)
    )


    # ========================================================
    # ACTUALIZAR PANTALLA
    # ========================================================

    pygame.display.flip()

    clock.tick(60)


# ============================================================
# CERRAR PYGAME
# ============================================================

pygame.quit()
sys.exit()


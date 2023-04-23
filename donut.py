import pygame as pg
from numpy import array, cos, sin, pi, matmul, dot, sqrt
import pygame.font

pygame.font.init()

# CONSTANTS
width, height = 800, 800
win = pg.display.set_mode((width, height))
pg.display.set_caption("Rotating Donut")
fps = 75
origin_x = width // 2
origin_y = height // 2
font = pg.font.SysFont("comicsans", 30)


black = (0, 0, 0)
white = (200, 200, 200)

ASCII = ".,-~:;=!*#$@"
# ASCII = "@BR#$PX0woIcv:+!~.,"[::-1]

the_spacing = 0.35
phi_spacing = 0.15
phi_increment = 0.05  # increment for each frame

r1 = 1
r2 = 2
k2 = 50
k1 = width * k2 * 3 / (8 * (r1 + r2))

light_dir = array((0, 1, -1))
len_light_vec = sqrt(light_dir[0] ** 2 + light_dir[1] ** 2 + light_dir[2] ** 2)

# todo improve the getting normal for points
def get_circle_and_normal(the_spacing=the_spacing):
    the = 0
    circle = []
    normal = []
    while the <= 2 * pi:
        circle.append(array([r2 + r1 * cos(the), r1 * sin(the), 0]))
        normal.append(array([cos(the), sin(the), 0]))
        the += the_spacing
    return circle, normal


def get_torus_and_normal():
    circle, normal = get_circle_and_normal()
    torus = []
    torus_normal = []
    phi = 0
    while phi <= 2 * pi:
        for i, point in enumerate(circle):
            normal_ = normal[i]
            torus.append(rotate_y(point, phi))
            torus_normal.append(rotate_y(normal_, phi))
        phi += phi_spacing
    return torus, torus_normal


def rotate_y(point, phi):
    rotation_mat = array([(cos(phi), 0, sin(phi)), (0, 1, 0), (-sin(phi), 0, cos(phi))])
    return matmul(point, rotation_mat)


def rotate_x(point, phi):
    rotation_mat = array([(1, 0, 0), (0, cos(phi), sin(phi)), (0, -sin(phi), cos(phi))])
    return matmul(point, rotation_mat)


def rotate_z(point, phi):
    rotation_mat = array([(cos(phi), sin(phi), 0), (-sin(phi), cos(phi), 0), (0, 0, 1)])
    return matmul(point, rotation_mat)


def rotate_torus(torus, normal, phi):
    rotated_torus = []
    rotated_normal = []
    for i, point in enumerate(torus):
        normal_ = normal[i]
        rotated_torus.append(rotate_z(rotate_x(point, phi), phi))
        rotated_normal.append(rotate_z(rotate_x(normal_, phi), phi))
    return rotated_torus, rotated_normal


def project_torus(torus):
    projected_torus = []
    for x, y, z in torus:
        projected_torus.append(array((k1 * x / (k2 + z), k1 * y / (k2 + z))))
    return projected_torus


def project_point(point):
    x, y, z = point
    return k1 * x / (k2 + z), k1 * y / (k2 + z)


# todo dont draw points behind already drawn points
def update(phi):
    torus, normal = get_torus_and_normal()
    rotated_torus, rotated_normal = rotate_torus(torus, normal, phi)
    for i, point in enumerate(rotated_torus):
        normal = rotated_normal[i]
        L = dot(normal, light_dir)
        if L > 0:

            x, y = project_point(point)
            # pg.draw.circle(win, white, (origin_x + x, origin_y - y), 3 * L)

            index = round(((len(ASCII) - 1) * L / len_light_vec))
            char = ASCII[index]
            text_img = font.render(char, True, white)
            win.blit(
                text_img,
                (
                    origin_x + x - text_img.get_width() // 2,
                    origin_y - y - text_img.get_height() // 2,
                ),
            )


def main():
    running = True
    clock = pg.time.Clock()
    phi = 0
    while running:
        clock.tick(fps)
        win.fill(black)
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    running = False
        update(phi)

        phi += phi_increment
        pg.display.update()
        fps_ = int(clock.get_fps())
        # print("fps: ", fps_)


if __name__ == "__main__":
    main()

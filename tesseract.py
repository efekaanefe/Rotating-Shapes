import sys
import pygame
import numpy as np


WIDTH = 800
HEIGHT = 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

ORIGIN_X = WIDTH // 2
ORIGIN_Y = HEIGHT // 2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

EDGE_LENGTH = 1


class Tesseract:
    def __init__(self):
        self.angle = 0
        l = EDGE_LENGTH
        self.points = [
            np.array([-l, -l, -l, l]),
            np.array([l, -l, -l, l]),
            np.array([l, l, -l, l]),
            np.array([-l, l, -l, l]),
            np.array([-l, -l, l, l]),
            np.array([l, -l, l, l]),
            np.array([l, l, l, l]),
            np.array([-l, l, l, l]),  # half-way
            np.array([-l, -l, -l, -l]),
            np.array([l, -l, -l, -l]),
            np.array([l, l, -l, -l]),
            np.array([-l, l, -l, -l]),
            np.array([-l, -l, l, -l]),
            np.array([l, -l, l, -l]),
            np.array([l, l, l, -l]),
            np.array([-l, l, l, -l]),
        ]

    def rotate(self):
        theta = self.angle

        # projection matrix without perspective
        PROJECTION = np.array([[1, 0, 0], [0, 1, 0]])

        # rotation matrixes
        ROT_MATRIX_X = np.array(
            [
                [1, 0, 0],
                [0, np.cos(theta), -np.sin(theta)],
                [0, np.sin(theta), np.cos(theta)],
            ]
        )

        ROT_MATRIX_Y = np.array(
            [
                [np.cos(theta), 0, np.sin(theta)],
                [0, 1, 0],
                [-np.sin(theta), 0, np.cos(theta)],
            ]
        )

        ROT_MATRIX_Z = np.array(
            [
                [np.cos(theta), -np.sin(theta), 0],
                [np.sin(theta), np.cos(theta), 0],
                [0, 0, 1],
            ]
        )

        ROT_MATRIX_XY = np.array(
            [
                [np.cos(theta), -np.sin(theta), 0, 0],
                [np.sin(theta), np.cos(theta), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ]
        )

        ROT_MATRIX_XZ = np.array(
            [
                [np.cos(theta), 0, -np.sin(theta), 0],
                [0, 1, 0, 0],
                [np.sin(theta), 0, np.cos(theta), 0],
                [0, 0, 0, 1],
            ]
        )

        ROT_MATRIX_ZW = np.array(
            [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, np.cos(theta), -np.sin(theta)],
                [0, 0, np.sin(theta), np.cos(theta)],
            ]
        )
        projected = []

        for point in self.points:

            DISTANCE = 2
            rotated = np.dot(ROT_MATRIX_XY, point)
            # rotated = np.dot(ROT_MATRIX_XZ, rotated)
            rotated = np.dot(ROT_MATRIX_ZW, rotated)

            # w = 2 / (DISTANCE - rotated[3] / 2)
            w = 1 / (DISTANCE - rotated[3])
            PROJECTION_4D = np.array([[w, 0, 0, 0], [0, w, 0, 0], [0, 0, w, 0]])
            rotated = np.dot(PROJECTION_4D, rotated)

            rotated = np.dot(ROT_MATRIX_X, rotated)
            # rotated = np.dot(ROT_MATRIX_Y, rotated)
            # rotated = np.dot(ROT_MATRIX_Z, rotated)

            z = 2 / (DISTANCE - rotated[2] / 2)
            # PROJECTION adjusted to give perspective
            PROJECTION_3D = np.array([[z, 0, 0], [0, z, 0]])
            projected2d = np.dot(PROJECTION_3D, rotated)
            projected2d *= 100
            projected.append(projected2d)

        return projected

    def draw(self):
        def connect(offset, i, j, points):
            a = points[i + offset]
            b = points[j + offset]
            pygame.draw.line(
                WIN,
                WHITE,
                (ORIGIN_X + a[0], ORIGIN_Y + a[1]),
                (ORIGIN_X + b[0], ORIGIN_Y + b[1]),
                1,
            )

        projected = self.rotate()
        # draw corners
        for coordinate in projected:
            pygame.draw.circle(
                WIN, WHITE, (ORIGIN_X + coordinate[0], ORIGIN_Y + coordinate[1]), 5
            )
        # # draw edges
        for i in range(4):
            connect(0, i, (i + 1) % 4, projected)
            connect(0, i + 4, ((i + 1) % 4) + 4, projected)
            connect(0, i, i + 4, projected)
            connect(8, i, (i + 1) % 4, projected)
            connect(8, i + 4, ((i + 1) % 4) + 4, projected)
            connect(8, i, i + 4, projected)

        for i in range(8):
            connect(0, i, i + 8, projected)


def main():
    cube = Tesseract()
    clock = pygame.time.Clock()
    run = True
    while run:
        WIN.fill(BLACK)
        clock.tick(75)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                sys.exit()
        cube.angle += 0.01
        cube.draw()
        pygame.display.update()


if __name__ == "__main__":
    main()

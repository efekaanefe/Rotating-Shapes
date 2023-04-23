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


class Cube:
    def __init__(self):
        self.angle = 0
        self.points = [
            np.array([-EDGE_LENGTH, -EDGE_LENGTH, -EDGE_LENGTH]),
            np.array([EDGE_LENGTH, -EDGE_LENGTH, -EDGE_LENGTH]),
            np.array([EDGE_LENGTH, EDGE_LENGTH, -EDGE_LENGTH]),
            np.array([-EDGE_LENGTH, EDGE_LENGTH, -EDGE_LENGTH]),
            np.array([-EDGE_LENGTH, -EDGE_LENGTH, EDGE_LENGTH]),
            np.array([EDGE_LENGTH, -EDGE_LENGTH, EDGE_LENGTH]),
            np.array([EDGE_LENGTH, EDGE_LENGTH, EDGE_LENGTH]),
            np.array([-EDGE_LENGTH, EDGE_LENGTH, EDGE_LENGTH]),
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

        projected = []

        for point in self.points:
            rotated = np.dot(ROT_MATRIX_X, point)
            rotated = np.dot(ROT_MATRIX_Y, rotated)
            rotated = np.dot(ROT_MATRIX_Z, rotated)

            DISTANCE = 2
            z = 2 / (DISTANCE - rotated[2] / 2)
            # PROJECTION adjusted to give perspective
            PROJECTION = np.array([[z, 0, 0], [0, z, 0]])
            projected2d = np.dot(PROJECTION, rotated)
            projected2d *= 100
            projected.append(projected2d)

        return projected

    def draw(self):
        def connect(i, j, points):
            a = points[i]
            b = points[j]
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
        # draw edges
        for i in range(4):
            connect(i, (i + 1) % 4, projected)
            connect(i + 4, ((i + 1) % 4) + 4, projected)
            connect(i, i + 4, projected)


def main():
    cube = Cube()
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

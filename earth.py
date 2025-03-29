import numpy as np
import pygame
import sys
import time

pygame.init()

LAND_COLORS = [(0, 255, 0)] 
WATER_COLORS = [(0, 0, 255)] 

WORLD_MAP = [
    "............................................................................................................................................",
    "............................................................................................................................................",
    "..................................+++++++..+++++++++++++++++++..............................................................................",
    "......................+.+++++..+.+.+++++........++++++++++++++.............................+..........++++++++++++++..+.....++..............",
    "......++++++++++++++++++++++++++++++++..++++.....++++++++++.................++++++++.....+++++++++++++++++++++++++++++++++++++++++++++++++++",
    "......+++++++++++++++++++++++++++++.....++++......++++...................++++.+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++.",
    "........++.......+++++++++++++++++......++++++......................+....++++..++++++++++++++++++++++++++++++++++++++++++++++......++.......",
    "....................++++++++++++++++++.+++++++++....................++..++++++++++++++++++++++++++++++++++++++++++++++++++++.......+........",
    "......................+++++++++++++++++++++++........................+++++++++++++++++++++++++++++++++++++++++++++++++++++++................",
    "......................+++++++++++++++++++++........................++++...+.+++++....++++.+++++++++++++++++++++++++++++++...................",
    "......................+++++++++++++++++++..........................+++........+..++++++++..+++++++++++++++++++++++++...+....+...............",
    ".........................++++++++++++++............................+++++++++..+....++++++++++++++++++++++++++++++++++.......................",
    "..........................++++++......+..........................++++++++++++++++++++++++++++++++++++++++++++++++++++.......................",
    ".............................+++................................++++++++++++++++++++.++++++++....+++++++++++++++++..........................",
    "...............................++.++............................+++++++++++++++++++++.+++++.......++++.....+++++............................",
    "....................................++..........................+++++++++++++++++++++++++..........++.......+.++............................",
    "........................................+++++++..................++++++++++++++++++++++++...................................................",
    ".......................................+++++++++++........................++++++++++++++.....................+...+++........................",
    ".......................................++++++++++++++++...................++++++++++++.......................++..++........++...............",
    ".......................................+++++++++++++++++...................++++++++++.......................................++..............",
    "........................................+++++++++++++++....................+++++++++++..................................+++..+..............",
    "..........................................+++++++++++++....................+++++++++...++............................++++++++++.............",
    "...........................................+++++++++........................++++++++...+..........................+++++++++++++++...........",
    "..........................................+++++++++.........................++++++................................+++++++++++++++...........",
    "..........................................+++++++............................+++...................................+++....+++++++...........",
    "..........................................++++................................................................................+.............",
    ".........................................++++...............................................................................................",
    ".........................................+++................................................................................................",
    "............................................................................................................................................",
    "............................................................................................................................................",
    "............................................................................................................................................",
    "............................................++.....................................+.++++++++++++..+++++++++++++++++++++++++++++++++........",
    "....................+++++++...++++++++++++++++.................+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++......",
    "..........+++++++++++++++++++++++++++++++..........+....+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++......."
]

def map_texture_to_sphere(u, v):
    """Map texture coordinates to world map."""
    # Convert normalized coordinates to map indices
    map_height = len(WORLD_MAP)
    map_width = len(WORLD_MAP[0])
    
    # Map u (0 to 1) to x (0 to map_width-1)
    # Map v (0 to 1) to y (0 to map_height-1)
    x = int(u * map_width) % map_width
    y = int(v * map_height) % map_height
    
    # Return 1 for land, 0 for water
    return 1 if WORLD_MAP[y][x] == '+' else 0

def create_adaptive_sphere(radius, base_resolution_theta, base_resolution_phi):
    """Create a sphere with variable resolution"""
    vertices = []
    texture_coords = []
    
    # Use adaptive resolution along phi (latitude)
    for i in range(base_resolution_phi):
        # Calculate the current phi angle (0 to π)
        phi = i * np.pi / (base_resolution_phi - 1)
        
        # Calculate adaptive resolution for theta based on latitude
        # Reduce resolution near poles, maximize at equator
        latitude_factor = np.sin(phi)  # 0 at poles, 1 at equator
        
        # Ensure minimum resolution even at poles (at least 25% of base)
        adjusted_factor = 0.25 + 0.75 * latitude_factor
        
        # Calculate adaptive resolution for this latitude ring
        adaptive_resolution_theta = max(8, int(base_resolution_theta * adjusted_factor))
        
        # Generate points around this latitude ring
        for j in range(adaptive_resolution_theta):
            theta = j * 2 * np.pi / adaptive_resolution_theta
            
            # Calculate 3D coordinates with 90 degree rotation
            x = radius * np.sin(phi) * np.cos(theta)
            y = -radius * np.cos(phi)
            z = radius * np.sin(phi) * np.sin(theta)
            
            # Calculate texture coordinates with map alignment
            u = (1 - (j / adaptive_resolution_theta) + 0.25) % 1.0
            v = i / (base_resolution_phi - 1)
            
            vertices.append((x, y, z))
            texture_coords.append((u, v))
    
    return vertices, texture_coords

def rotate_y(point, angle):
    """Rotate a point around the y-axis."""
    x, y, z = point
    new_x = x * np.cos(angle) + z * np.sin(angle)
    new_z = -x * np.sin(angle) + z * np.cos(angle)
    return (new_x, y, new_z)

def render_earth(vertices, texture_coords, screen, width, height, angle, radius):
    """Render the Earth with land and water using pygame."""
    screen.fill((0, 0, 0))
    
    z_buffer = [[-float('inf') for _ in range(width)] for _ in range(height)]
    
    pixels = pygame.PixelArray(screen)
    
    # Rotate and project each vertex
    for ((x, y, z), (u, v)) in zip(vertices, texture_coords):
        x, y, z = rotate_y((x, y, z), angle)
        
        # Only render points that are on the front half (facing viewer)
        if z < 0:
            screen_x = int(width/2 + x)
            screen_y = int(height/2 + y)
            
            if 0 <= screen_x < width and 0 <= screen_y < height:
                if z > z_buffer[screen_y][screen_x]:
                    # Get texture value (land or water)
                    is_land = map_texture_to_sphere(u, v)
                    
                    if is_land:
                        color = LAND_COLORS[0]
                    else:
                        color = WATER_COLORS[0]
                    
                    pixels[screen_x, screen_y] = color
                    
                    z_buffer[screen_y][screen_x] = z
    
    pixels.close()

def main():
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("3D Earth Simulation (Optimized)")
    
    clock = pygame.time.Clock()
    
    radius = 200
    base_resolution_theta = 500  # Higher resolution at equator
    base_resolution_phi = 50    # Vertical resolution
    vertices, texture_coords = create_adaptive_sphere(radius, base_resolution_theta, base_resolution_phi)
    
    # Animation settings
    angle = 0
    frame_count = 0
    start_time = time.time()
    running = True
    rotation_speed = 0.1
    
    font = pygame.font.SysFont(None, 24)
    
    # Main animation loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    running = False
                # Control rotation speed
                elif event.key == pygame.K_UP:
                    rotation_speed += 0.005
                elif event.key == pygame.K_DOWN:
                    rotation_speed = max(0.001, rotation_speed - 0.005)
        
        render_earth(vertices, texture_coords, screen, width, height, angle, radius)
        
        frame_count += 1
        elapsed = time.time() - start_time
        fps = frame_count / elapsed if elapsed > 0 else 0
        
        fps_text = font.render(f"FPS: {fps:.1f} | Rotation: {rotation_speed:.3f}", True, (255, 255, 255))
        screen.blit(fps_text, (10, height - 50))
        help_text = font.render("Press UP/DOWN to change speed, Q to exit", True, (255, 255, 255))
        screen.blit(help_text, (10, height - 25))
        
        pygame.display.flip()
        
        angle += rotation_speed
        
        clock.tick(60)
    
    pygame.quit()
    print("Exited smoothly")

if __name__ == "__main__":
    main()
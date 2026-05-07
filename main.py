import random
import math

import pygame

from quad_tree import QuadTree
from circle import Circle


def resolve_collision(c1: Circle, c2: Circle) -> None:

    # Compute distance vector
    dx = c2.x - c1.x
    dy = c2.y - c1.y
    dist_sq = dx * dx + dy * dy
    
    if dist_sq == 0: return
    
    # Overlap correction
    dist = math.sqrt(dist_sq)
    overlap = (c1.radius + c2.radius) - dist
    
    nx = dx / dist
    ny = dy / dist
    
    correction_x = nx * overlap * 0.5
    correction_y = ny * overlap * 0.5
    
    c1.x -= correction_x
    c1.y -= correction_y
    c2.x += correction_x
    c2.y += correction_y

    dist = c1.radius + c2.radius
    nx = (c2.x - c1.x) / dist
    ny = (c2.y - c1.y) / dist

    # Compute the new speed for each circles
    m1 = c1.metadata.get("mass", 1)
    m2 = c2.metadata.get("mass", 1)
    
    dvx = c2.vx - c1.vx
    dvy = c2.vy - c1.vy
    
    dot_product = dvx * nx + dvy * ny
    
    # Avoid "glued" circles
    if dot_product > 0: return
    
    j = (2 * dot_product) / (m1 + m2)
    
    # Update circle speeds
    c1.vx += j * m2 * nx
    c1.vy += j * m2 * ny
    c2.vx -= j * m1 * nx
    c2.vy -= j * m1 * ny


def main() -> None:

    # Pygame setup
    screen_size = (0, 0)

    pygame.init()

    window = pygame.display.set_mode(screen_size)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 20, bold=True)

    screen_width, screen_height = window.get_size()

    # Circle properties
    number_circles = 300
    radius_range = (5, 10)
    speed_range = (1, 4)

    # Modes
    qt_approach: bool = True
    draw_qt: bool = False
    mouse_force_mode: bool = False
    selected_circle: Circle | None = None

    # Circle initializations
    circles: list[Circle] = []
    for _ in range(number_circles):
        circle_radius = random.randint(*radius_range)
        circle_angle = random.random() * 2 * math.pi
        circle_speed = random.randint(*speed_range)
        circle_mass = circle_radius
        new_circle = Circle(
            x=random.randint(circle_radius, screen_width - circle_radius),
            y=random.randint(circle_radius, screen_height - circle_radius),
            radius=circle_radius,
            vx=circle_speed * math.cos(circle_angle),
            vy=circle_speed * math.sin(circle_angle),
            metadata={"mass": circle_mass}
        )
        circles.append(new_circle)

    # Game loop
    run_loop: bool = True

    while run_loop:

        # Events / User inputs
        all_events = pygame.event.get()

        left_click: bool = False

        for event in all_events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                run_loop = False

            # Change between naive and quadtree approach
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                qt_approach = not qt_approach
            # Can display the quadtree
            if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                draw_qt = not draw_qt
            # Apply force with mouse
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                mouse_force_mode = not mouse_force_mode
            # Left click
            if event.type == pygame.MOUSEBUTTONDOWN:
                left_click = pygame.mouse.get_pressed()[0]
            

        mouse_pos = pygame.mouse.get_pos()

        if mouse_force_mode:
            Circle.vector_force[0] = (mouse_pos[0] - screen_width / 2) / (screen_width / 2) * 0.2
            Circle.vector_force[1] = (mouse_pos[1] - screen_height / 2) / (screen_height / 2) * 0.2
        else:
            Circle.vector_force = [0, 0]

        # Circle movement and quadtree generation (if optimized mode)
        quad_tree = QuadTree(0, 0, screen_width, screen_height, 4)

        for circle in circles:
            circle.update(0, 0, screen_width, screen_height)
            if qt_approach:
                quad_tree.insert(circle, circle.x, circle.y)
            
            if left_click and circle.collide_point(mouse_pos):
                selected_circle = circle

        all_collided: set[Circle] = set()
        highlighted_neighbors: set[Circle] = set()
        highlighted_quadtrees: set[QuadTree] = set()
        # Collision check
        if qt_approach:
            # Optimized approach
            for c1 in circles:
                # Grab the nearest circles using the quadtree
                other_circles: list[Circle] = quad_tree.query_elements(
                    x=c1.x - c1.radius - 10,
                    y=c1.y - c1.radius - 10,
                    w=c1.radius * 2 + 20,
                    h=c1.radius * 2 + 20
                )

                if c1 is selected_circle:
                    for qt in quad_tree.query_leafs(
                        x=c1.x - c1.radius - 10,
                        y=c1.y - c1.radius - 10,
                        w=c1.radius * 2 + 20,
                        h=c1.radius * 2 + 20
                    ):
                        highlighted_quadtrees.add(qt)

                for c2 in other_circles:
                    if c1 is selected_circle:
                        highlighted_neighbors.add(c2)

                    # Handle collision between circles
                    if (c1 is not c2) and ((c1 not in all_collided) and (c2 not in all_collided)) and c1.collide_circle(c2):
                        resolve_collision(c1, c2)
                        all_collided.add(c1)
                        all_collided.add(c2)

        else:
            # Naive approach
            for c1 in circles:
                for c2 in circles:
                    # Handle collision between circles
                    if (id(c1) < id(c2)) and c1.collide_circle(c2):
                        resolve_collision(c1, c2)
                        all_collided.add(c1)
                        all_collided.add(c2)

        # Draw background
        window.fill((50, 50, 50))

        # Display quadtree (if mode activated)
        number_leaf: int = 0
        if qt_approach and draw_qt:
            for leaf in quad_tree.all_leafs():
                pygame.draw.rect(
                    window,
                    color=(100, 255, 100) if leaf in highlighted_quadtrees else "white",
                    rect=leaf.rect,
                    width=1
                )
                number_leaf += 1


        # Draw circles
        for circle in circles:
            pygame.draw.circle(
                window,
                color=(150, 200, 255) if circle in all_collided else (80, 120, 150),
                center=circle.center,
                radius=circle.radius
            )

            if circle is selected_circle:
                pygame.draw.circle(
                window,
                color=(255, 100, 100),
                center=circle.center,
                radius=circle.radius,
                width=1
            )
            elif circle in highlighted_neighbors:
                pygame.draw.circle(
                window,
                color=(100, 200, 100),
                center=circle.center,
                radius=circle.radius,
                width=1
            )
    
        # Debug display
        dt = clock.tick(60)
        quadtree_text = f"Optimized{f' ({number_leaf} Leafs)' if draw_qt else ''}"

        display_text = f"{number_circles} circles - {quadtree_text if qt_approach else 'Naive'} algorithm"
        display_text += f" - Forces {Circle.vector_force[0]:.8f}, {Circle.vector_force[1]:.8f}"

        fps_text = f" - FPS: {(1000 / dt):.1f}"

        display_text += fps_text

        debug_surf = font.render(display_text, True, "white")

        window.blit(debug_surf, (10, 10))
        pygame.display.update() 
        
        

if __name__ == "__main__":
    main()

import pygame
import sys
from algorithms import *


# Kich thuoc cua so
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 750
INFO_PANEL_WIDTH = 350
INFO_PANEL_HEIGHT = SCREEN_HEIGHT



# kich thuoc cua moi o trong me cung
CELL_SIZE = min((SCREEN_WIDTH - INFO_PANEL_WIDTH) // COLS, (SCREEN_HEIGHT - 100) // ROWS)
MAZE_WIDTH = COLS * CELL_SIZE
MAZE_HEIGHT = ROWS * CELL_SIZE
MAZE_OFFSET_X = 15
MAZE_OFFSET_Y = 15

# mau cac thanh phan giao dien
COLOR_BACKGROUND = (50, 50, 50)
COLOR_GRID = (80, 80, 80)
COLOR_WALL = (225, 225, 225)
COLOR_START = (0, 255, 0)
COLOR_END = (255, 0, 0)
COLOR_PATH = (252, 137, 0)
COLOR_VISITED = (60, 60, 100)
COLOR_BUTTON = (0, 150, 136)
COLOR_BUTTON_HOVER = (0, 180, 160)
COLOR_BUTTON_TEXT = (255, 255, 255)
COLOR_INFO_TEXT = (230, 230, 230)
COLOR_SCROLLBAR = (100, 100, 100)
COLOR_SCROLLBAR_BG = (70, 70, 70)

# animation
ANIMATION_EVENT = pygame.USEREVENT + 1
ANIMATION_SPEED_MS = 10



def draw_maze(screen, maze):
    """Ve cac buc tuong cua me cung"""
    pygame.draw.rect(screen, COLOR_GRID, (MAZE_OFFSET_X, MAZE_OFFSET_Y, MAZE_WIDTH, MAZE_HEIGHT))
    for r in range(ROWS):
        for c in range(COLS):
            x, y = MAZE_OFFSET_X + c * CELL_SIZE, MAZE_OFFSET_Y + r * CELL_SIZE
            walls = maze[r][c]
            if walls[0]: pygame.draw.line(screen, COLOR_WALL, (x, y), (x + CELL_SIZE, y), 4)
            if walls[1]: pygame.draw.line(screen, COLOR_WALL, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 4)
            if walls[2]: pygame.draw.line(screen, COLOR_WALL, (x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE), 4)
            if walls[3]: pygame.draw.line(screen, COLOR_WALL, (x, y), (x, y + CELL_SIZE), 4)

def draw_solution(screen, path, visited, start, end):
    """Ve ket qua tim duong (o da duyet, duong di, diem dau/cuoi)"""
    if visited:
        for r, c in visited:
            if (r,c) != start and (r,c) != end:
                x = MAZE_OFFSET_X + c * CELL_SIZE
                y = MAZE_OFFSET_Y + r * CELL_SIZE
                pygame.draw.rect(screen, COLOR_VISITED, (x + 2, y + 2, CELL_SIZE - 3, CELL_SIZE - 3))
    if path:
        for r, c in path:
             if (r,c) != start and (r,c) != end:
                x = MAZE_OFFSET_X + c * CELL_SIZE
                y = MAZE_OFFSET_Y + r * CELL_SIZE
                pygame.draw.rect(screen, COLOR_PATH, (x + 2, y + 2, CELL_SIZE - 3, CELL_SIZE - 3))

    start_x, start_y = MAZE_OFFSET_X + start[1] * CELL_SIZE, MAZE_OFFSET_Y + start[0] * CELL_SIZE
    end_x, end_y = MAZE_OFFSET_X + end[1] * CELL_SIZE, MAZE_OFFSET_Y + end[0] * CELL_SIZE
    pygame.draw.rect(screen, COLOR_START, (start_x + 2, start_y + 2, CELL_SIZE - 3, CELL_SIZE - 3))
    pygame.draw.rect(screen, COLOR_END, (end_x + 2, end_y + 2, CELL_SIZE - 3, CELL_SIZE - 3))


def draw_info_panel(screen, font_small, font_large, buttons, stats, scroll_y, path_surface, path_area_rect):
    """Ve bang thong tin dieu khien ben phai"""
    panel_x = MAZE_OFFSET_X + MAZE_WIDTH + 20
    panel_y = MAZE_OFFSET_Y
    
    title_text = font_large.render("Dieu khien", True, COLOR_BUTTON_TEXT)
    screen.blit(title_text, (panel_x + (INFO_PANEL_WIDTH - title_text.get_width())//2, panel_y + 20))

    # Ve cac nut bam
    mouse_pos = pygame.mouse.get_pos()
    for name, rect in buttons.items():
        color = COLOR_BUTTON_HOVER if rect.collidepoint(mouse_pos) else COLOR_BUTTON
        pygame.draw.rect(screen, color, rect, border_radius=8)
        text_surf = font_small.render(name, True, COLOR_BUTTON_TEXT)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

    # Ve bang thong ke
    y_offset = 350
    stats_title = font_small.render("--- Thong ke ---", True, COLOR_INFO_TEXT)
    screen.blit(stats_title, (panel_x + 10, y_offset))
    y_offset += 30

    if stats:
        algo_text = font_small.render(f"Thuat toan: {stats['algo']}", True, COLOR_INFO_TEXT)
        screen.blit(algo_text, (panel_x + 10, y_offset))
        y_offset += 25

        path_len = len(stats.get('path', []))
        path_text = font_small.render(f"Do dai duong di: {path_len}", True, COLOR_INFO_TEXT)
        screen.blit(path_text, (panel_x + 10, y_offset))
        y_offset += 25

        visited_len = len(stats.get('visited', []))
        visited_text = font_small.render(f"So o da duyet: {visited_len}", True, COLOR_INFO_TEXT)
        screen.blit(visited_text, (panel_x + 10, y_offset))
        y_offset += 40
        
        # Ve khu vuc hien thi duong di (co the cuon)
        if stats.get('path'):
            path_title = font_small.render("--- Duong di ---", True, COLOR_INFO_TEXT)
            screen.blit(path_title, (panel_x + 10, y_offset))
            
            path_surface.fill(COLOR_BACKGROUND)
            path_str = " -> ".join(map(str, stats['path']))
            
            # Tinh toan va ve van ban co the xuong dong
            words = path_str.split(' ')
            lines, current_line = [], ""
            line_height = font_small.get_linesize()
            max_width = path_area_rect.width - 15
            for word in words:
                test_line = current_line + word + " "
                if font_small.size(test_line)[0] < max_width:
                    current_line = test_line
                else:
                    lines.append(current_line); current_line = word + " "
            lines.append(current_line)
            
            text_y = 0
            for line in lines:
                text_surface = font_small.render(line, True, COLOR_PATH)
                path_surface.blit(text_surface, (5, text_y))
                text_y += line_height

            screen.blit(path_surface, path_area_rect.topleft, (0, scroll_y, path_area_rect.width, path_area_rect.height))

            # Ve thanh cuon neu can
            total_height = text_y
            if total_height > path_area_rect.height:
                pygame.draw.rect(screen, COLOR_SCROLLBAR_BG, (path_area_rect.right + 2, path_area_rect.top, 8, path_area_rect.height), border_radius=4)
                thumb_height = max(15, path_area_rect.height * (path_area_rect.height / total_height))
                thumb_y = path_area_rect.top + (scroll_y / (total_height - path_area_rect.height)) * (path_area_rect.height - thumb_height)
                pygame.draw.rect(screen, COLOR_SCROLLBAR, (path_area_rect.right + 2, thumb_y, 8, thumb_height), border_radius=4)



def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Truc quan hoa Thuat toan Tim duong trong Me cung")
    clock = pygame.time.Clock()

    try:
        font_small = pygame.font.Font(None, 24)
        font_large = pygame.font.Font(None, 36)
    except Exception:
        font_small = pygame.font.SysFont("Arial", 18)
        font_large = pygame.font.SysFont("Arial", 28, bold=True)

    # --- Khoi tao cac bien trang thai ---
    maze, start_pos, end_pos = create_new_maze() # Ham nay tu file algorithms.py
    path, visited_set, stats, solver = None, set(), {}, None

    # --- Khoi tao cac bien cho khu vuc cuon ---
    panel_x = MAZE_OFFSET_X + MAZE_WIDTH + 20
    path_area_rect = pygame.Rect(panel_x + 10, 520, INFO_PANEL_WIDTH - 30, 200)
    path_surface = pygame.Surface((path_area_rect.width, 2000)) # Be mat lon de ve van ban
    scroll_y = 0

    # --- Tao cac nut bam ---
    button_width = INFO_PANEL_WIDTH - 20
    button_height = 40
    buttons = {
        "Tao me cung moi": pygame.Rect(panel_x + 10, 100, button_width, button_height),
        "Giai bang A*": pygame.Rect(panel_x + 10, 160, button_width, button_height),
        "Giai bang BFS": pygame.Rect(panel_x + 10, 220, button_width, button_height),
        "Giai bang DFS": pygame.Rect(panel_x + 10, 280, button_width, button_height),
    }

    running = True
    while running:
        # --- Xu ly su kien ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Su kien cuon chuot
            if event.type == pygame.MOUSEWHEEL:
                if path and path_area_rect.collidepoint(pygame.mouse.get_pos()):
                    # Tinh toan chieu cao tong the cua van ban de gioi han cuon
                    line_height = font_small.get_linesize()
                    path_str = " -> ".join(map(str, stats['path']))
                    words = path_str.split(' '); lines, current_line = [], ""
                    for word in words:
                        test_line = current_line + word + " "
                        if font_small.size(test_line)[0] < path_area_rect.width-15: current_line=test_line
                        else: lines.append(current_line); current_line = word + " "
                    lines.append(current_line)
                    total_text_height = len(lines) * line_height

                    scroll_y -= event.y * 20
                    scroll_y = max(0, min(scroll_y, total_text_height - path_area_rect.height))

            # Su kien click chuot
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not solver:
                    for name, rect in buttons.items():
                        if rect.collidepoint(event.pos):
                            path, visited_set, solver, scroll_y = None, set(), None, 0
                            stats = {'algo': name.replace("Giai bang ", "")}
                            pygame.time.set_timer(ANIMATION_EVENT, ANIMATION_SPEED_MS)

                            if name == "Tao me cung moi":
                                maze, start_pos, end_pos = create_new_maze()
                                pygame.time.set_timer(ANIMATION_EVENT, 0)
                            # Cac ham ..._animated nay duoc import tu algorithms.py
                            elif name == "Giai bang A*": solver = a_star_animated(maze, start_pos, end_pos)
                            elif name == "Giai bang BFS": solver = bfs_animated(maze, start_pos, end_pos)
                            elif name == "Giai bang DFS": solver = dfs_animated(maze, start_pos, end_pos)

            # Su kien animation timer
            if event.type == ANIMATION_EVENT and solver:
                try:
                    visited_set, current_path = next(solver)
                    if current_path: # Neu tim thay duong di
                        path, stats['path'], stats['visited'] = current_path, current_path, visited_set
                        solver = None
                        pygame.time.set_timer(ANIMATION_EVENT, 0)
                except StopIteration:
                    stats['visited'] = visited_set
                    solver = None
                    pygame.time.set_timer(ANIMATION_EVENT, 0)

        # --- Ve len man hinh ---
        screen.fill(COLOR_BACKGROUND)
        draw_maze(screen, maze)
        draw_solution(screen, path, visited_set, start_pos, end_pos)
        draw_info_panel(screen, font_small, font_large, buttons, stats, scroll_y, path_surface, path_area_rect)
        pygame.display.flip()
        
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

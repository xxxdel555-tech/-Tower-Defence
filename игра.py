
import pygame
import math
import random
import sys

# Инициализация Pygame
pygame.init()

# Определяем размеры для мобильной адаптации
INFO = pygame.display.Info()
if INFO.current_w < 800:  # Телефон
    WIDTH, HEIGHT = INFO.current_w, INFO.current_h - 50
else:
    WIDTH, HEIGHT = 800, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("🌲 Защита Леса")
clock = pygame.time.Clock()

# Шрифты с поддержкой русских букв
def get_font(size):
    try:
        return pygame.font.Font(None, size)
    except:
        return pygame.font.SysFont('Arial', size)

font = get_font(int(HEIGHT / 22))
small_font = get_font(int(HEIGHT / 30))
tiny_font = get_font(int(HEIGHT / 40))
big_font = get_font(int(HEIGHT / 18))

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GREEN = (15, 60, 15)
FOREST_GREEN = (34, 139, 34)
LIGHT_GREEN = (144, 238, 144)
BROWN = (101, 67, 33)
DARK_BROWN = (60, 40, 20)
GOLD = (255, 215, 0)
RED = (200, 30, 30)
ORANGE = (255, 140, 0)
PURPLE = (100, 50, 180)
CYAN = (0, 200, 200)
LIGHT_BLUE = (100, 200, 255)
YELLOW = (255, 255, 50)
GREEN_GLOW = (50, 255, 50)
DARK_RED = (150, 0, 0)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (80, 80, 80)

# Параметры игры
CELL_SIZE = max(15, int(WIDTH / 50))
PATH_POINTS = [
    (WIDTH * 0.05, HEIGHT * 0.15),
    (WIDTH * 0.25, HEIGHT * 0.15),
    (WIDTH * 0.25, HEIGHT * 0.40),
    (WIDTH * 0.55, HEIGHT * 0.40),
    (WIDTH * 0.55, HEIGHT * 0.20),
    (WIDTH * 0.80, HEIGHT * 0.20),
    (WIDTH * 0.80, HEIGHT * 0.60),
    (WIDTH * 0.45, HEIGHT * 0.60),
    (WIDTH * 0.45, HEIGHT * 0.80),
    (WIDTH * 0.85, HEIGHT * 0.80)
]
SPAWN_POS = PATH_POINTS[0]
BASE_POS = PATH_POINTS[-1]
TOTAL_WAVES = 30
MONSTER_SPACING = 20

def scale_size(base_size):
    return max(int(base_size * min(WIDTH, HEIGHT) / 800), 3)

# Типы врагов
MONSTER_TYPES = {
    'normal': {
        'hp': 20, 
        'speed': 1.0, 
        'reward': 10, 
        'color': (180, 60, 60), 
        'size': scale_size(12), 
        'name': 'Гоблин'
    },
    'runner': {
        'hp': 10, 
        'speed': 2.0, 
        'reward': 15, 
        'color': (255, 120, 30), 
        'size': scale_size(9), 
        'name': 'Бегун'
    },
    'tank': {
        'hp': 50, 
        'speed': 0.6, 
        'reward': 20, 
        'color': (80, 40, 160), 
        'size': scale_size(17), 
        'name': 'Танк'
    },
    'boss': {
        'hp': 120, 
        'speed': 0.4, 
        'reward': 40, 
        'color': (255, 215, 0), 
        'size': scale_size(22), 
        'name': 'Босс'
    }
}

# Типы башен
TOWER_TYPES = {
    'basic': {
        'name': 'Лучник',
        'color': (34, 139, 34),
        'cost': 30,
        'damage': 10,
        'range': 150,
        'fire_delay': 25,
        'upgrade_cost': 20,
        'emoji': '🏹'
    },
    'sniper': {
        'name': 'Снайпер',
        'color': (0, 100, 200),
        'cost': 50,
        'damage': 25,
        'range': 280,
        'fire_delay': 40,
        'upgrade_cost': 30,
        'emoji': '🎯'
    },
    'machine': {
        'name': 'Арбалет',
        'color': (0, 200, 200),
        'cost': 40,
        'damage': 5,
        'range': 130,
        'fire_delay': 8,
        'upgrade_cost': 25,
        'emoji': '⚡'
    },
    'cannon': {
        'name': 'Катапульта',
        'color': (200, 120, 50),
        'cost': 60,
        'damage': 35,
        'range': 160,
        'fire_delay': 45,
        'upgrade_cost': 35,
        'emoji': '💥'
    }
}

# Классы игры (те же, что и раньше, но с улучшенным интерфейсом)
class Particle:
    def __init__(self, x, y, color, size, speed, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.speed_x = random.uniform(-speed, speed)
        self.speed_y = random.uniform(-speed, speed)
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.alive = True
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False
            
    def draw(self, surf):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        size = self.size * (self.lifetime / self.max_lifetime)
        if size > 1:
            pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), int(size))

class Tree:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        
    def draw(self, surf):
        trunk_width = max(3, self.size * 0.2)
        trunk_height = self.size * 0.5
        pygame.draw.rect(surf, DARK_BROWN, 
                        (self.x - trunk_width//2, self.y, 
                         trunk_width, trunk_height))
        
        colors = [(20, 100, 20), (30, 120, 30), (40, 140, 40)]
        for i, color in enumerate(colors):
            radius = self.size * (0.5 - i * 0.1)
            offset_y = -self.size * (0.1 + i * 0.15)
            offset_x = random.randint(-self.size//4, self.size//4)
            pygame.draw.circle(surf, color, 
                             (int(self.x + offset_x), int(self.y + offset_y)), 
                             int(radius))

class Forest:
    def __init__(self):
        self.trees = []
        self.particles = []
        self.generate_forest()
        
    def generate_forest(self):
        step = max(40, int(WIDTH / 25))
        for x in range(step, WIDTH - step, step):
            for y in range(step, HEIGHT - step, step):
                on_path = False
                for i in range(len(PATH_POINTS) - 1):
                    x1, y1 = PATH_POINTS[i]
                    x2, y2 = PATH_POINTS[i+1]
                    dx = x2 - x1
                    dy = y2 - y1
                    if dx == 0 and dy == 0:
                        dist = math.hypot(x - x1, y - y1)
                    else:
                        t = ((x - x1) * dx + (y - y1) * dy) / (dx*dx + dy*dy)
                        t = max(0, min(1, t))
                        proj_x = x1 + t * dx
                        proj_y = y1 + t * dy
                        dist = math.hypot(x - proj_x, y - proj_y)
                    if dist < 35:
                        on_path = True
                        break
                
                if not on_path and random.random() < 0.2:
                    size = random.randint(int(WIDTH/50), int(WIDTH/30))
                    self.trees.append(Tree(x, y, size))
    
    def add_particles(self, x, y, color, count=10):
        for _ in range(count):
            self.particles.append(Particle(
                x, y, color, 
                random.randint(2, 5), 
                random.uniform(1, 3), 
                random.randint(20, 40)
            ))
    
    def update(self):
        for p in self.particles[:]:
            p.update()
            if not p.alive:
                self.particles.remove(p)
    
    def draw(self, surf):
        for tree in self.trees:
            tree.draw(surf)
        for p in self.particles:
            p.draw(surf)

class Monster:
    def __init__(self, monster_type, wave, index_in_wave=0):
        self.type = monster_type
        self.x, self.y = SPAWN_POS
        self.wave = wave
        
        base_hp = MONSTER_TYPES[monster_type]['hp']
        base_speed = MONSTER_TYPES[monster_type]['speed']
        base_reward = MONSTER_TYPES[monster_type]['reward']
        
        self.hp = base_hp + wave * 3
        self.max_hp = self.hp
        self.speed = base_speed + wave * 0.01
        self.reward = base_reward + wave * 1
        self.color = MONSTER_TYPES[monster_type]['color']
        self.size = MONSTER_TYPES[monster_type]['size']
        self.name = MONSTER_TYPES[monster_type]['name']
        self.alive = True
        self.distance_traveled = 0
        self.total_path_length = self.calculate_path_length()
        self.index_in_wave = index_in_wave
        
        self.poison_timer = 0
        self.poison_damage = 0
        self.freeze_timer = 0
        self.freeze_speed_multiplier = 0.5
        self.hit_flash = 0
        
    def calculate_path_length(self):
        total = 0
        for i in range(len(PATH_POINTS) - 1):
            dx = PATH_POINTS[i+1][0] - PATH_POINTS[i][0]
            dy = PATH_POINTS[i+1][1] - PATH_POINTS[i][1]
            total += math.hypot(dx, dy)
        return total
    
    def get_position_on_path(self, distance):
        if distance <= 0:
            return SPAWN_POS[0], SPAWN_POS[1]
        
        remaining = distance
        for i in range(len(PATH_POINTS) - 1):
            x1, y1 = PATH_POINTS[i]
            x2, y2 = PATH_POINTS[i+1]
            dx = x2 - x1
            dy = y2 - y1
            segment_length = math.hypot(dx, dy)
            
            if remaining <= segment_length:
                t = remaining / segment_length if segment_length > 0 else 0
                return x1 + dx * t, y1 + dy * t
            remaining -= segment_length
        
        return PATH_POINTS[-1]

    def move(self, monsters):
        current_speed = self.speed
        if self.freeze_timer > 0:
            current_speed *= self.freeze_speed_multiplier
            self.freeze_timer -= 1
        
        if self.poison_timer > 0:
            self.poison_timer -= 1
            if self.poison_timer % 10 == 0:
                self.hp -= self.poison_damage
                if self.hp <= 0:
                    self.alive = False
                    return False
        
        self.distance_traveled += current_speed
        
        if self.distance_traveled >= self.total_path_length:
            self.alive = False
            return True
        
        self.x, self.y = self.get_position_on_path(self.distance_traveled)
        return False

    def draw(self, surf):
        color = self.color
        if self.hit_flash > 0:
            color = WHITE
            self.hit_flash -= 1
        elif self.poison_timer > 0:
            color = (100, 255, 100)
        elif self.freeze_timer > 0:
            color = LIGHT_BLUE
        
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surf, BLACK, (int(self.x), int(self.y)), self.size, 2)
        
        eye_offset = self.size // 3
        eye_angle = 0
        if self.distance_traveled < self.total_path_length:
            for i in range(len(PATH_POINTS) - 1):
                x1, y1 = PATH_POINTS[i]
                x2, y2 = PATH_POINTS[i+1]
                if self.distance_traveled >= self.get_segment_distance(i) and self.distance_traveled <= self.get_segment_distance(i+1):
                    dx = x2 - x1
                    dy = y2 - y1
                    if dx != 0 or dy != 0:
                        eye_angle = math.atan2(dy, dx)
                    else:
                        eye_angle = 0
                    break
            else:
                eye_angle = 0
        
        eye_color = RED if self.type in ['boss', 'tank'] else WHITE
        
        eye_x1 = self.x + math.cos(eye_angle - 0.5) * eye_offset
        eye_y1 = self.y + math.sin(eye_angle - 0.5) * eye_offset
        eye_x2 = self.x + math.cos(eye_angle + 0.5) * eye_offset
        eye_y2 = self.y + math.sin(eye_angle + 0.5) * eye_offset
        pygame.draw.circle(surf, eye_color, (int(eye_x1), int(eye_y1)), max(2, self.size//4))
        pygame.draw.circle(surf, eye_color, (int(eye_x2), int(eye_y2)), max(2, self.size//4))
        pygame.draw.circle(surf, BLACK, (int(eye_x1), int(eye_y1)), max(1, self.size//6))
        pygame.draw.circle(surf, BLACK, (int(eye_x2), int(eye_y2)), max(1, self.size//6))
        
        bar_width = self.size * 2.5
        bar_height = max(3, self.size//4)
        health_ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surf, RED, (self.x - bar_width//2, self.y - self.size - 10, bar_width, bar_height))
        pygame.draw.rect(surf, GREEN_GLOW, (self.x - bar_width//2, self.y - self.size - 10, bar_width * health_ratio, bar_height))
        
        if self.type == 'boss':
            pygame.draw.polygon(surf, GOLD, [
                (self.x - 10, self.y - self.size - 12),
                (self.x, self.y - self.size - 20),
                (self.x + 10, self.y - self.size - 12)
            ], 2)

    def get_segment_distance(self, index):
        if index >= len(PATH_POINTS):
            return self.total_path_length
        dist = 0
        for i in range(index):
            dx = PATH_POINTS[i+1][0] - PATH_POINTS[i][0]
            dy = PATH_POINTS[i+1][1] - PATH_POINTS[i][1]
            dist += math.hypot(dx, dy)
        return dist

class Tower:
    def __init__(self, x, y, tower_type='basic', level=1):
        self.x = x
        self.y = y
        self.tower_type = tower_type
        self.level = level
        self.target = None
        self.cooldown = 0
        self.angle = 0
        
        tower_data = TOWER_TYPES[tower_type]
        self.name = tower_data['name']
        self.color = tower_data['color']
        self.base_cost = tower_data['cost']
        self.base_damage = tower_data['damage']
        self.base_range = tower_data['range']
        self.base_fire_delay = tower_data['fire_delay']
        self.upgrade_cost = tower_data['upgrade_cost']
        self.emoji = tower_data['emoji']
        
        self.update_stats()
        
    def update_stats(self):
        self.damage = self.base_damage + (self.level - 1) * 8
        self.range = self.base_range + (self.level - 1) * 15
        self.fire_delay = max(5, self.base_fire_delay - (self.level - 1) * 3)
        
    def get_upgrade_cost(self):
        return self.upgrade_cost + (self.level - 1) * 20
        
    def get_color(self):
        return self.color

    def update(self, monsters):
        if self.cooldown > 0:
            self.cooldown -= 1
        
        self.target = None
        min_dist = float('inf')
        for m in monsters:
            if not m.alive: continue
            dx = m.x - self.x
            dy = m.y - self.y
            dist = math.hypot(dx, dy)
            if dist < self.range and dist < min_dist:
                self.target = m
                min_dist = dist
        
        if self.target:
            self.angle = math.atan2(self.target.y - self.y, self.target.x - self.x)

    def fire(self, monsters):
        if self.cooldown > 0 or not self.target:
            return []
        
        self.cooldown = self.fire_delay
        bullets = []
        
        num_bullets = min(self.level, 3)
        base_angle = self.angle
        
        if self.tower_type == 'sniper':
            bullets.append(Bullet(self.x, self.y, base_angle, self.damage * 2, self.target, 'sniper'))
        elif self.tower_type == 'machine':
            for i in range(num_bullets * 2):
                angle = base_angle + random.uniform(-0.1, 0.1)
                bullets.append(Bullet(self.x, self.y, angle, self.damage, self.target, 'machine'))
        elif self.tower_type == 'cannon':
            if num_bullets == 1:
                angles = [base_angle]
            elif num_bullets == 2:
                angles = [base_angle - 0.25, base_angle + 0.25]
            else:
                angles = [base_angle - 0.35, base_angle, base_angle + 0.35]
            for a in angles:
                bullets.append(Bullet(self.x, self.y, a, self.damage, self.target, 'cannon'))
        else:
            if num_bullets == 1:
                angles = [base_angle]
            elif num_bullets == 2:
                angles = [base_angle - 0.2, base_angle + 0.2]
            else:
                angles = [base_angle - 0.3, base_angle, base_angle + 0.3]
            for a in angles:
                bullets.append(Bullet(self.x, self.y, a, self.damage, self.target, 'basic'))
        
        return bullets

    def draw(self, surf):
        color = self.get_color()
        size = max(10, 14 + self.level * 2)
        
        pygame.draw.circle(surf, DARK_BROWN, (int(self.x), int(self.y)), size + 2)
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), size)
        pygame.draw.circle(surf, BLACK, (int(self.x), int(self.y)), size, 2)
        
        end_x = self.x + math.cos(self.angle) * size
        end_y = self.y + math.sin(self.angle) * size
        pygame.draw.line(surf, BLACK, (self.x, self.y), (end_x, end_y), max(2, size//4))
        
        pygame.draw.circle(surf, GOLD, (int(self.x), int(self.y)), max(2, size//4))
        
        lvl_text = tiny_font.render(str(self.level), True, WHITE)
        surf.blit(lvl_text, (self.x - 5, self.y - 7))
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if math.hypot(mouse_x - self.x, mouse_y - self.y) < size + 5:
            s = pygame.Surface((self.range*2, self.range*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, 20), (self.range, self.range), self.range)
            surf.blit(s, (self.x - self.range, self.y - self.range))

class Bullet:
    def __init__(self, x, y, angle, damage, target, bullet_type='basic'):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 8
        self.damage = damage
        self.alive = True
        self.target = target
        self.bullet_type = bullet_type
        self.trail = []
        self.size = max(3, 4)
        self.color = YELLOW
        
        if bullet_type == 'sniper':
            self.size = max(5, 8)
            self.speed = 12
            self.color = LIGHT_BLUE
        elif bullet_type == 'machine':
            self.size = max(2, 3)
            self.speed = 10
            self.color = CYAN
        elif bullet_type == 'cannon':
            self.size = max(6, 10)
            self.speed = 6
            self.color = ORANGE

    def move(self):
        if self.target and self.target.alive:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.angle = math.atan2(dy, dx)
                self.x += math.cos(self.angle) * self.speed
                self.y += math.sin(self.angle) * self.speed
        else:
            self.x += math.cos(self.angle) * self.speed
            self.y += math.sin(self.angle) * self.speed
        
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)
        
        if self.x < -50 or self.x > WIDTH + 50 or self.y < -50 or self.y > HEIGHT + 50:
            self.alive = False

    def draw(self, surf):
        for i, pos in enumerate(self.trail):
            alpha = int(100 * (i / len(self.trail)))
            if alpha > 0:
                size = self.size * (i / len(self.trail))
                if size > 1:
                    pygame.draw.circle(surf, (self.color[0], self.color[1], self.color[2], alpha), 
                                     (int(pos[0]), int(pos[1])), int(size))
        
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), max(1, self.size // 2))

class Button:
    def __init__(self, x, y, width, height, text, color, text_color=WHITE, border_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.border_color = border_color
        self.is_hovered = False
        self.is_pressed = False
        
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
    def draw(self, surf):
        # Фон
        color = self.color
        if self.is_hovered:
            color = tuple(min(255, c + 40) for c in self.color)
        if self.is_pressed:
            color = tuple(max(0, c - 40) for c in self.color)
        
        pygame.draw.rect(surf, color, self.rect, border_radius=8)
        pygame.draw.rect(surf, self.border_color, self.rect, 2, border_radius=8)
        
        # Текст
        text_surf = small_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surf.blit(text_surf, text_rect)
        
    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            return True
        return False

class Game:
    def __init__(self):
        self.monsters = []
        self.towers = []
        self.bullets = []
        self.score = 50
        self.wave = 0
        self.monsters_per_wave = 5
        self.spawn_count = 0
        self.spawn_timer = 0
        self.game_over = False
        self.win = False
        self.selected_tower = None
        self.tower_positions = []
        self.can_place = False
        self.wave_in_progress = False
        self.wave_complete = False
        self.selected_tower_type = 'basic'
        self.first_tower_placed = False
        
        self.total_monsters_killed = 0
        self.total_damage_dealt = 0
        
        self.forest = Forest()
        
        # Создаем кнопки
        button_width = min(130, WIDTH * 0.16)
        button_height = min(40, HEIGHT * 0.06)
        button_x = WIDTH - button_width - 10
        
        # Кнопки в правом верхнем углу
        self.buttons = {}
        self.buttons['next_wave'] = Button(
            button_x, 10, button_width, button_height,
            "▶ Волна", (0, 180, 50), WHITE, WHITE
        )
        self.buttons['upgrade'] = Button(
            button_x, 10 + button_height + 5, button_width, button_height,
            "⬆ Апгрейд", (200, 150, 50), WHITE, WHITE
        )
        
        # Кнопки выбора башни в правой части
        self.tower_buttons = {}
        button_y = 10 + (button_height + 5) * 2 + 10
        btn_width = button_width // 2 - 3
        btn_height = button_height
        
        tower_types = list(TOWER_TYPES.items())
        for i, (t_type, t_data) in enumerate(tower_types):
            row = i // 2
            col = i % 2
            x_pos = WIDTH - button_width - 5 + col * (btn_width + 2)
            y_pos = button_y + row * (btn_height + 3)
            
            if y_pos + btn_height > HEIGHT - 20:
                break
                
            self.tower_buttons[t_type] = Button(
                x_pos, y_pos, btn_width, btn_height,
                f"{t_data['emoji']} {t_data['name'][:4]}",
                t_data['color'], BLACK, WHITE
            )
        
        self.info_text = "🌲 Установите первую башню!"
        self.info_timer = 0
        self.show_help = True
        self.help_timer = 180
        
        # Для скроллинга на телефоне
        self.scroll_y = 0
        self.touch_start_y = 0
        self.is_touching = False

    def get_wave_monsters(self):
        monsters = []
        normal_count = max(3, self.monsters_per_wave // 2)
        for i in range(normal_count):
            monsters.append('normal')
        
        if self.wave >= 3:
            runner_count = min(2, 1 + self.wave // 5)
            for i in range(runner_count):
                monsters.append('runner')
        
        if self.wave >= 5:
            tank_count = min(2, 1 + self.wave // 8)
            for i in range(tank_count):
                monsters.append('tank')
        
        if self.wave % 5 == 0 and self.wave > 0:
            monsters.append('boss')
            for i in range(2):
                monsters.append('normal')
        
        random.shuffle(monsters)
        return monsters

    def spawn_monsters(self):
        if self.spawn_count < self.monsters_per_wave and self.wave_in_progress:
            wave_monsters = self.get_wave_monsters()
            monster_type = wave_monsters[self.spawn_count % len(wave_monsters)]
            
            monster = Monster(monster_type, self.wave, self.spawn_count)
            
            if len(self.monsters) > 0:
                last_monster = None
                for m in reversed(self.monsters):
                    if m.alive:
                        last_monster = m
                        break
                
                if last_monster:
                    monster.distance_traveled = max(0, last_monster.distance_traveled - MONSTER_SPACING)
                    monster.x, monster.y = monster.get_position_on_path(monster.distance_traveled)
            
            self.monsters.append(monster)
            self.spawn_count += 1
            self.spawn_timer = 10

    def start_next_wave(self):
        if not self.wave_in_progress and not self.game_over and not self.win and self.first_tower_placed:
            self.wave += 1
            self.spawn_count = 0
            self.monsters_per_wave = 5 + self.wave * 2
            self.wave_in_progress = True
            self.wave_complete = False
            
            self.set_info(f"⚔️ Волна {self.wave} началась!")
        elif not self.first_tower_placed:
            self.set_info("🌲 Сначала установите первую башню!")

    def handle_click(self, pos):
        # Проверяем кнопки
        if self.buttons['next_wave'].handle_click(pos):
            self.start_next_wave()
            return
        
        if self.buttons['upgrade'].handle_click(pos):
            if self.selected_tower:
                tower = self.selected_tower
                if tower.level < 3:
                    cost = tower.get_upgrade_cost()
                    if self.score >= cost:
                        self.score -= cost
                        tower.level += 1
                        tower.update_stats()
                        self.set_info(f"⬆ Башня улучшена до {tower.level} уровня!")
                        self.forest.add_particles(tower.x, tower.y, GOLD, 15)
                    else:
                        self.set_info(f"❌ Нужно {cost}⚡")
                else:
                    self.set_info("⭐ Максимальный уровень!")
            else:
                self.set_info("👆 Выберите башню")
            return
        
        # Проверяем кнопки выбора башни
        for t_type, button in self.tower_buttons.items():
            if button.handle_click(pos):
                self.selected_tower_type = t_type
                self.set_info(f"🌲 {TOWER_TYPES[t_type]['name']} выбран")
                return

        # Проверка клика по башне
        for tower in self.towers:
            dx = pos[0] - tower.x
            dy = pos[1] - tower.y
            if math.hypot(dx, dy) < 30:
                self.selected_tower = tower
                self.set_info(f"🌲 {TOWER_TYPES[tower.tower_type]['name']} {tower.level}⭐")
                return

        # Размещение башни
        grid_x = round(pos[0] / CELL_SIZE) * CELL_SIZE
        grid_y = round(pos[1] / CELL_SIZE) * CELL_SIZE
        
        if self.can_place_tower(grid_x, grid_y):
            cost = TOWER_TYPES[self.selected_tower_type]['cost']
            if not self.first_tower_placed:
                cost = 0
                self.first_tower_placed = True
            
            if self.score >= cost:
                self.score -= cost
                new_tower = Tower(grid_x, grid_y, self.selected_tower_type, 1)
                self.towers.append(new_tower)
                self.tower_positions.append((grid_x, grid_y))
                
                self.forest.add_particles(grid_x, grid_y, GREEN_GLOW, 20)
                
                if cost == 0:
                    self.set_info("🌲 Первая башня установлена!")
                else:
                    self.set_info(f"🌲 {TOWER_TYPES[self.selected_tower_type]['name']} установлена!")
                self.selected_tower = new_tower
            else:
                self.set_info(f"❌ Нужно {cost}⚡")
        else:
            self.set_info("🚫 Нельзя поставить здесь!")

    def can_place_tower(self, x, y):
        min_dist_to_path = 30
        for i in range(len(PATH_POINTS) - 1):
            x1, y1 = PATH_POINTS[i]
            x2, y2 = PATH_POINTS[i+1]
            
            dx = x2 - x1
            dy = y2 - y1
            if dx == 0 and dy == 0:
                dist = math.hypot(x - x1, y - y1)
            else:
                t = ((x - x1) * dx + (y - y1) * dy) / (dx*dx + dy*dy)
                t = max(0, min(1, t))
                proj_x = x1 + t * dx
                proj_y = y1 + t * dy
                dist = math.hypot(x - proj_x, y - proj_y)
            
            if dist < min_dist_to_path:
                return False
        
        for tx, ty in self.tower_positions:
            if math.hypot(x - tx, y - ty) < 30:
                return False
        
        if x < 20 or x > WIDTH - 20 or y < 20 or y > HEIGHT - 20:
            return False
        
        return True

    def set_info(self, text):
        self.info_text = text
        self.info_timer = 90

    def update(self):
        if self.game_over or self.win:
            return
        
        if self.info_timer > 0:
            self.info_timer -= 1
            if self.info_timer == 0:
                self.info_text = ""
        
        if self.help_timer > 0:
            self.help_timer -= 1
            if self.help_timer == 0:
                self.show_help = False

        self.forest.update()

        if self.spawn_timer > 0:
            self.spawn_timer -= 1
        
        if self.wave_in_progress and self.spawn_timer == 0:
            self.spawn_monsters()
        
        if self.wave_in_progress and self.spawn_count >= self.monsters_per_wave:
            all_dead = True
            for m in self.monsters:
                if m.alive:
                    all_dead = False
                    break
            if all_dead:
                self.wave_in_progress = False
                self.wave_complete = True
                bonus = self.wave * 2
                self.score += bonus
                self.set_info(f"🌲 Волна {self.wave} завершена! +{bonus}⚡")

        for m in self.monsters[:]:
            if not m.alive: continue
            reached_end = m.move(self.monsters)
            if reached_end:
                self.game_over = True
                self.set_info("💀 Игра окончена!")
                self.forest.add_particles(m.x, m.y, RED, 30)

        for tower in self.towers:
            tower.update(self.monsters)
            new_bullets = tower.fire(self.monsters)
            self.bullets.extend(new_bullets)

        for b in self.bullets[:]:
            b.move()
            if not b.alive:
                self.bullets.remove(b)
                continue
            
            hit = False
            for m in self.monsters[:]:
                if not m.alive: continue
                if math.hypot(b.x - m.x, b.y - m.y) < m.size + b.size:
                    m.hp -= b.damage
                    m.hit_flash = 5
                    self.total_damage_dealt += b.damage
                    hit = True
                    
                    if b.bullet_type == 'cannon' and m.hp > 0:
                        m.poison_timer = 30
                        m.poison_damage = b.damage // 4
                    
                    if m.hp <= 0:
                        m.alive = False
                        self.score += m.reward
                        self.total_monsters_killed += 1
                        self.forest.add_particles(m.x, m.y, GREEN_GLOW, 15)
                    break
            if hit:
                self.bullets.remove(b)

        self.monsters = [m for m in self.monsters if m.alive]
        
        # Обновляем состояние кнопок
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons.values():
            button.update(mouse_pos)
        for button in self.tower_buttons.values():
            button.update(mouse_pos)

    def draw(self, surf):
        surf.fill((15, 50, 15))
        
        self.forest.draw(surf)
        
        # Рисуем тропу
        for i in range(len(PATH_POINTS) - 1):
            pygame.draw.line(surf, (60, 40, 20), PATH_POINTS[i], PATH_POINTS[i+1], max(14, int(WIDTH/50)))
            pygame.draw.line(surf, (80, 60, 30), PATH_POINTS[i], PATH_POINTS[i+1], max(10, int(WIDTH/60)))
        for i, p in enumerate(PATH_POINTS):
            color = GREEN_GLOW if i == 0 else RED if i == len(PATH_POINTS)-1 else (100, 80, 40)
            pygame.draw.circle(surf, color, p, max(6, int(WIDTH/100)))
            pygame.draw.circle(surf, BLACK, p, max(6, int(WIDTH/100)), 2)
        
        if not self.first_tower_placed:
            for x in range(CELL_SIZE, WIDTH - CELL_SIZE, CELL_SIZE):
                for y in range(CELL_SIZE, HEIGHT - CELL_SIZE, CELL_SIZE):
                    if self.can_place_tower(x, y):
                        pygame.draw.rect(surf, (0, 255, 0, 30), 
                                       (x - CELL_SIZE//2, y - CELL_SIZE//2, CELL_SIZE, CELL_SIZE), 1)
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x = round(mouse_x / CELL_SIZE) * CELL_SIZE
        grid_y = round(mouse_y / CELL_SIZE) * CELL_SIZE
        if 0 < grid_x < WIDTH and 0 < grid_y < HEIGHT:
            can_place = self.can_place_tower(grid_x, grid_y)
            color = GREEN_GLOW if can_place else RED
            pygame.draw.rect(surf, color, (grid_x - CELL_SIZE//2, grid_y - CELL_SIZE//2, CELL_SIZE, CELL_SIZE), 2)

        for t in self.towers:
            t.draw(surf)
        for m in self.monsters:
            m.draw(surf)
        for b in self.bullets:
            b.draw(surf)

        # Верхняя панель со статистикой
        panel_height = max(50, HEIGHT * 0.08)
        pygame.draw.rect(surf, (0, 0, 0, 200), (0, 0, WIDTH, panel_height))
        pygame.draw.rect(surf, (255, 255, 255, 30), (0, 0, WIDTH, panel_height), 2)
        
        # Статистика в левой части
        stat_x = 10
        stat_y = 8
        spacing = 15
        
        score_text = small_font.render(f"⚡{self.score}", True, GOLD)
        wave_text = small_font.render(f"🌊{self.wave}", True, WHITE)
        monsters_text = small_font.render(f"👾{len([m for m in self.monsters if m.alive])}", True, RED)
        kills_text = small_font.render(f"💀{self.total_monsters_killed}", True, WHITE)
        
        surf.blit(score_text, (stat_x, stat_y))
        stat_x += score_text.get_width() + 10
        surf.blit(wave_text, (stat_x, stat_y))
        stat_x += wave_text.get_width() + 10
        surf.blit(monsters_text, (stat_x, stat_y))
        stat_x += monsters_text.get_width() + 10
        surf.blit(kills_text, (stat_x, stat_y))

        # Рисуем кнопки
        for button in self.buttons.values():
            button.draw(surf)
        
        # Рисуем кнопки выбора башни
        for button in self.tower_buttons.values():
            button.draw(surf)

        # Информация о выбранной башне
        if self.selected_tower:
            tower = self.selected_tower
            info_y = HEIGHT - 55
            pygame.draw.rect(surf, (0, 0, 0, 200), (5, info_y, min(200, WIDTH*0.25), 50))
            pygame.draw.rect(surf, tower.get_color(), (5, info_y, min(200, WIDTH*0.25), 50), 2)
            
            sel_text = tiny_font.render(f"{tower.emoji} {TOWER_TYPES[tower.tower_type]['name']} {tower.level}⭐", True, WHITE)
            surf.blit(sel_text, (10, info_y + 5))
            cost_text = tiny_font.render(f"Апг: {tower.get_upgrade_cost()}⚡", True, GOLD)
            surf.blit(cost_text, (10, info_y + 25))

        # Информационное сообщение
        if self.info_text:
            info_surf = font.render(self.info_text, True, (200, 255, 150))
            rect = info_surf.get_rect(center=(WIDTH//2, HEIGHT - 15))
            pygame.draw.rect(surf, (0, 0, 0, 200), (rect.x - 10, rect.y - 5, rect.width + 20, rect.height + 10), border_radius=8)
            surf.blit(info_surf, rect)

        # Подсказка для телефона
        if self.show_help and self.wave == 0:
            help_text = big_font.render("👆 Нажмите на поле", True, WHITE)
            help_rect = help_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
            help_text2 = small_font.render("чтобы установить первую башню", True, WHITE)
            help_rect2 = help_text2.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
            
            pygame.draw.rect(surf, (0, 0, 0, 220), 
                           (WIDTH//2 - 150, HEIGHT//2 - 50, 300, 100), 
                           border_radius=15)
            surf.blit(help_text, help_rect)
            surf.blit(help_text2, help_rect2)

        # Сообщения о победе/поражении
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            surf.blit(overlay, (0, 0))
            
            go_text = big_font.render("💀 ИГРА ОКОНЧЕНА!", True, RED)
            go_rect = go_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 30))
            surf.blit(go_text, go_rect)
            
            restart_text = font.render("Нажмите R для перезапуска", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
            surf.blit(restart_text, restart_rect)
            
        if self.win:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            surf.blit(overlay, (0, 0))
            
            win_text = big_font.render("🏆 ПОБЕДА!", True, GOLD)
            win_rect = win_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 30))
            surf.blit(win_text, win_rect)
            
            restart_text = font.render("Нажмите R для перезапуска", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
            surf.blit(restart_text, restart_rect)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Левая кнопка
                        self.handle_click(event.pos)
                
                # Поддержка тач-событий для телефона
                if event.type == pygame.FINGERDOWN:
                    x = event.x * WIDTH
                    y = event.y * HEIGHT
                    self.handle_click((x, y))
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.__init__()
                    if event.key == pygame.K_1:
                        self.selected_tower_type = 'basic'
                        self.set_info("🌲 Лучник выбран")
                    elif event.key == pygame.K_2:
                        self.selected_tower_type = 'sniper'
                        self.set_info("🌲 Снайпер выбран")
                    elif event.key == pygame.K_3:
                        self.selected_tower_type = 'machine'
                        self.set_info("🌲 Арбалет выбран")
                    elif event.key == pygame.K_4:
                        self.selected_tower_type = 'cannon'
                        self.set_info("🌲 Катапульта выбрана")
                    elif event.key == pygame.K_SPACE:
                        self.start_next_wave()

            self.update()
            self.draw(screen)
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()

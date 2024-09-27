import pygame
import random

# 初始化 Pygame
pygame.init()

# 设置屏幕尺寸
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D 水平版塔防游戏")

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
DARK_RED = (139, 0, 0)
DARK_GREEN = (0, 100, 0)
DARK_GRAY = (50, 50, 50)

# 设置参数
PLAYER_TOWER_POS = (50, SCREEN_HEIGHT // 2)
ENEMY_TOWER_POS = (SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2)
PLAYER_TOWER_HEALTH = 300
ENEMY_TOWER_HEALTH = 300
GOLD = 100
GOLD_INCREASE_RATE = 10
GOLD_INCREASE_FREQUENCY = 100
ATTACK_DELAY = 1200
STOP_DISTANCE = 35
PAUSE_DURATION = 500  # ms
RETREAT_DISTANCE = 30  # 击退距离

MAIN_FONT = pygame.font.Font(None, 36)
END_FONT = pygame.font.Font(None, 72)

# 设置兵种参数
UNIT_COST = [15, 45, 50, 70, 90, 120]
UNIT_HEALTH = [15, 70, 35, 60, 95, 120]
UNIT_ATTACK = [15, 10, 35, 60, 95, 100]
SPAWN_FREQUENCY = 2000

# 设置兵种颜色
UNIT_COLORS = [YELLOW, CYAN, MAGENTA, ORANGE, PURPLE, GREEN]

class Tower(pygame.sprite.Sprite):
    def __init__(self, x, y, color, health, max_health):
        super().__init__()
        self.image = pygame.Surface((50, 100))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.health = health
        self.max_health = max_health

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0

    def draw_health_bar(self, surface):
        bar_width = 50
        bar_height = 7
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - bar_height - 5
        health_ratio = self.health / self.max_health
        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, bar_width * health_ratio, bar_height))

class Unit(pygame.sprite.Sprite):
    def __init__(self, x, y, color, speed, health, max_health, attack, direction):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = speed
        self.health = health
        self.max_health = max_health
        self.attack = attack
        self.direction = direction
        self.last_attack_time = pygame.time.get_ticks()
        self.paused = True
        self.pause_timer = pygame.time.get_ticks()

    def update(self):
        if self.paused:
            if pygame.time.get_ticks() - self.pause_timer >= PAUSE_DURATION:
                self.paused = False
        else:
            if self.direction > 0: 
                target_position = ENEMY_TOWER_POS[0] - STOP_DISTANCE
                if self.rect.right < target_position:
                    self.rect.x += self.speed
            else:
                target_position = PLAYER_TOWER_POS[0] + STOP_DISTANCE
                if self.rect.left > target_position:
                    self.rect.x += self.speed

    def take_damage(self, damage):
        initial_health = self.health
        self.health -= damage
        if self.health <= 0:
            self.kill()
        if initial_health >= self.max_health / 2 > self.health:
            self.be_knocked_back()

    def be_knocked_back(self):
        retreat_amount = RETREAT_DISTANCE if self.direction < 0 else -RETREAT_DISTANCE
        self.rect.x += retreat_amount

    def collide(self, other):
        self.take_damage(other.attack)
        other.take_damage(self.attack)

    def can_attack(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= ATTACK_DELAY:
            self.last_attack_time = current_time
            return True
        return False

    def draw_health_bar(self, surface):
        bar_width = 30
        bar_height = 4
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - bar_height - 5
        health_ratio = self.health / self.max_health
        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, bar_width * health_ratio, bar_height))

all_sprites = pygame.sprite.Group()
player_units = pygame.sprite.Group()
enemy_units = pygame.sprite.Group()

player_tower = Tower(*PLAYER_TOWER_POS, BLUE, PLAYER_TOWER_HEALTH, PLAYER_TOWER_HEALTH)
enemy_tower = Tower(*ENEMY_TOWER_POS, RED, ENEMY_TOWER_HEALTH, ENEMY_TOWER_HEALTH)
all_sprites.add(player_tower)
all_sprites.add(enemy_tower)

pygame.time.set_timer(pygame.USEREVENT, SPAWN_FREQUENCY)
pygame.time.set_timer(pygame.USEREVENT + 1, GOLD_INCREASE_FREQUENCY)

clock = pygame.time.Clock()

game_over = False
end_message = ""
end_message_color = WHITE

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif not game_over and event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if y > SCREEN_HEIGHT - 50:
                unit_index = x // (SCREEN_WIDTH // 6)
                if unit_index < len(UNIT_COST) and GOLD >= UNIT_COST[unit_index]:
                    GOLD -= UNIT_COST[unit_index]
                    new_unit = Unit(
                        PLAYER_TOWER_POS[0] + 50, 
                        PLAYER_TOWER_POS[1],
                        UNIT_COLORS[unit_index],
                        2,
                        UNIT_HEALTH[unit_index],
                        UNIT_HEALTH[unit_index],
                        UNIT_ATTACK[unit_index],
                        direction=1
                    )
                    all_sprites.add(new_unit)
                    player_units.add(new_unit)
        elif event.type == pygame.USEREVENT:
            unit_index = random.randint(0, 5)
            enemy_unit = Unit(
                ENEMY_TOWER_POS[0] - 50,
                ENEMY_TOWER_POS[1],
                UNIT_COLORS[unit_index],
                -2,
                UNIT_HEALTH[unit_index],
                UNIT_HEALTH[unit_index],
                UNIT_ATTACK[unit_index],
                direction=-1
            )
            all_sprites.add(enemy_unit)
            enemy_units.add(enemy_unit)
        elif event.type == pygame.USEREVENT + 1:
            GOLD += GOLD_INCREASE_RATE

    if not game_over:
        player_collisions = pygame.sprite.groupcollide(player_units, enemy_units, False, False)
        if player_collisions:
            for player, enemies in player_collisions.items():
                for enemy in enemies:
                    player.collide(enemy)
                    if not player.paused and not enemy.paused:
                        player.paused = True
                        player.pause_timer = pygame.time.get_ticks()
                        enemy.paused = True
                        enemy.pause_timer = pygame.time.get_ticks()

        for enemy in enemy_units:
            if enemy.rect.left <= player_tower.rect.right + STOP_DISTANCE:
                if enemy.can_attack():
                    player_tower.take_damage(enemy.attack)

        for unit in player_units:
            if unit.rect.right >= enemy_tower.rect.left - STOP_DISTANCE:
                if unit.can_attack():
                    enemy_tower.take_damage(unit.attack)

        if player_tower.health <= 0:
            game_over = True
            end_message = "Game Over! You lose."
            end_message_color = RED
        elif enemy_tower.health <= 0:
            game_over = True
            end_message = "Congratulations! You win."
            end_message_color = GREEN

        all_sprites.update()

    screen.fill(BLACK)
    
    all_sprites.draw(screen)
    
    for unit in player_units:
        unit.draw_health_bar(screen)
    for unit in enemy_units:
        unit.draw_health_bar(screen)
        
    player_tower.draw_health_bar(screen)
    enemy_tower.draw_health_bar(screen)

    gold_text = MAIN_FONT.render(f"Gold: {GOLD}", True, WHITE)
    screen.blit(gold_text, (SCREEN_WIDTH - 150, 10))

    for i, cost in enumerate(UNIT_COST):
        btn_rect = pygame.Rect(i * (SCREEN_WIDTH // 6), SCREEN_HEIGHT - 50, SCREEN_WIDTH // 6, 50)
        pygame.draw.rect(screen, WHITE, btn_rect, 2)
        cost_text = MAIN_FONT.render(f"{cost}", True, WHITE)
        screen.blit(cost_text, (btn_rect.x + 10, btn_rect.y + 10))
        preview_rect = pygame.Rect(btn_rect.x + btn_rect.width // 2 - 15, btn_rect.y - 30, 30, 30)
        pygame.draw.rect(screen, UNIT_COLORS[i], preview_rect)

    if game_over:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        game_over_text = END_FONT.render(end_message, True, end_message_color)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        
        background_rect = text_rect.inflate(20, 20)
        pygame.draw.rect(screen, DARK_GRAY, background_rect)
        
        screen.blit(game_over_text, text_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print(end_message)

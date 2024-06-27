import sys
import random
import pygame
from pygame.locals import QUIT
from pygame import mixer
import time


# Initialize Pygame
pygame.init()
mixer.init()
pygame.font.init()
font = pygame.font.SysFont(None, 36)  
# Window size
win_width = 600
win_height = 800
WHITE = (255, 255, 255)
LIME_GREEN = (50, 205, 50)
DARK_GREEN = (0, 100, 0)
clock = pygame.time.Clock()

# Set up some constants
PLAYER_ = pygame.image.load('player.png')
ENEMY_ = pygame.image.load('enemy.png')
BENEMY_ = pygame.image.load('benemy.png')
PLAYER_SIZE = (80, 80)
ENEMY_SIZE = (50, 50)
PLAYER = pygame.transform.scale(PLAYER_, PLAYER_SIZE)
ENEMY = pygame.transform.scale(ENEMY_, ENEMY_SIZE)
BENEMY = pygame.transform.scale(BENEMY_, (60,60))
powerups = pygame.sprite.Group()
# Load the background image and scale it to fit the window size
BACKGROUND_ORIGINAL = pygame.image.load('background.jpg')
BACKGROUND = pygame.transform.scale(BACKGROUND_ORIGINAL, (win_width, win_height))
screen = None
bazooka=pygame.sprite.Group()
targeted_enemies = set()
wavenumber = 1

def button(msg, x, y, w, h, inactive_color, active_color, action=None):
    pygame.init()
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(screen, active_color, (x, y, w, h))
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, w, h))

    small_font = pygame.font.SysFont(None, 25)
    text_surf = small_font.render(msg, True, WHITE)
    text_rect = text_surf.get_rect(center=((x + (w / 2)), (y + (h / 2))))
    screen.blit(text_surf, text_rect)
def render_text(screen, text, size, color, position):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=position)
    screen.blit(text_surface, text_rect)
    pygame.display.flip()

def spawn_wave():
    global enemy, boss_enemy
    boss_enemy = BossEnemy()
    enemies.add(boss_enemy)
    all_sprites.add(boss_enemy)
    for _ in range(2*wavenumber+4):
        enemy = Enemy()
        enemies.add(enemy)
        all_sprites.add(enemy)

def intro():
    intro = True
    pygame.init()
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        screen.fill(WHITE)

        # Display the game's title
        font = pygame.font.SysFont(None, 55)
        text_surf = font.render("Welcome to My Game!", True, DARK_GREEN)
        text_rect = text_surf.get_rect(center=(win_width/2, win_height/4))
        screen.blit(text_surf, text_rect)

        # Display the game's controls
        controls = ["Controls:", "Move: WASD", "Fire Bazooka: b", "Fire Bullet: space"]
        for index, control in enumerate(controls):
            control_surf = font.render(control, True, DARK_GREEN)
            control_rect = control_surf.get_rect(center=(win_width/2, win_height/2 + index * 60))
            screen.blit(control_surf, control_rect)

        # Start Button
        button("Start", win_width/2 - 50, win_height * 3/4, 100, 50, LIME_GREEN, DARK_GREEN, main)

        pygame.display.update()
        clock.tick(15)
class TripleShotPowerup(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image0 = pygame.image.load('tripleshot.png')
        self.image = pygame.transform.scale(self.image0, (45,45))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.type = "tripleshot"

class Powerup(pygame.sprite.Sprite):
    def __init__(self, type, pos):
        super().__init__()
        if type == "speed":
            self.image0 = pygame.image.load('puspeed.png')
            self.image = pygame.transform.scale(self.image0, (45,45))
            self.type = "speed"
        elif type == "bullet":
            self.image0 = pygame.image.load('pubullet.png')
            self.image = pygame.transform.scale(self.image0, (45,45))
            self.type = "bullet"
        elif type == "freeze":
            self.image0 = pygame.image.load('pufreeze.png')
            self.image = pygame.transform.scale(self.image0, (45,45))
            self.type = "freeze"
        elif type == "bazooka":
            self.image0 = pygame.image.load('bazooka.png')
            self.image = pygame.transform.scale(self.image0, (45,45))
            self.type = "bazooka"
        elif type == "tripleshot":
            self.image0 = pygame.image.load('triple.png')
            self.image = pygame.transform.scale(self.image0, (45,45))
            self.type = "tripleshot"
        self.rect = self.image.get_rect(center = pos)

class Background():
    def __init__(self):
        self.y1 = 0
        self.y2 = -win_height

    def move(self, speed):
        self.y1 += speed
        self.y2 += speed

        # If image goes off screen, reset its position
        if self.y1 >= win_height:
            self.y1 = -win_height
        if self.y2 >= win_height:
            self.y2 = -win_height

    def draw(self, screen):
        screen.blit(BACKGROUND, (0, self.y1))
        screen.blit(BACKGROUND, (0, self.y2))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image_original = PLAYER 
        self.image = self.image_original  # Use the original image for rendering
        self.rect = self.image.get_rect(center=(win_width / 2, win_height - PLAYER_SIZE[1] / 2))  # Use center instead of topleft for more intuitive placement
        self.position = pygame.math.Vector2(self.rect.x, self.rect.y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = 5
        self.last_known_direction = pygame.math.Vector2(1, 0)
        self.triple_shot = False


    def update(self):
        global bullet_limit, bazookas_left
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.velocity.x = -self.speed
        elif keys[pygame.K_d]:
            self.velocity.x = self.speed
        else:
            self.velocity.x = 0

        if keys[pygame.K_w]:
            self.velocity.y = -self.speed
        elif keys[pygame.K_s]:
            self.velocity.y = self.speed
        else:
            self.velocity.y = 0
        if not self.velocity == [0,0]:  # avoid division by zero
            self.last_known_direction = self.velocity.copy()
            self.velocity.normalize_ip()  # normalize in place
            self.velocity *= self.speed  # apply the speed back
            angle = self.velocity.angle_to(pygame.math.Vector2(1, 0))
            self.image = rotate_image(self.image_original, angle)

        self.position += self.velocity
        self.rect.topleft = self.position
        self.rect.clamp_ip(screen.get_rect())

        powerup_collisions = pygame.sprite.spritecollide(self, powerups, False)
        for entity in powerup_collisions:
            print(entity.type)
            if entity.type == "tripleshot":
                if not self.triple_shot == True:
                    self.triple_shot = True
                    print('triplelaa')
                    bullet_limit += 2
                else:
                    bazookas_left += 1
            if isinstance(entity, Powerup):
                if entity.type == "speed":
                    self.speed += 5  # Increase player's speed
                elif entity.type == "bullet":
                    if self.triple_shot == False:
                        bullet_limit += 1  # Increase bullet limit
                    else:
                        bullet_limit += 3
                elif entity.type == 'freeze':
                    for enemy in enemies:
                        enemy.freeze += 3000
                elif entity.type == "bazooka":
                    bazookas_left += 1
            entity.kill()  # Remove powerup after collecting

class Bazooka(pygame.sprite.Sprite):
    def __init__(self, position, target):
        super().__init__()
        self.image = pygame.Surface((10, 10)) # Bigger than a bullet for example
        self.image.fill((255, 165, 0))  # Orange-ish color for the bazooka
        self.rect = self.image.get_rect(center=position)
        self.speed = 10  # Faster than a bullet
        self.target = target
        self.direction = pygame.math.Vector2(target.rect.x - position[0], target.rect.y - position[1]).normalize()

    def update(self):
        # Update the direction towards the target every frame
        vector = pygame.math.Vector2(self.target.rect.x - self.rect.x, self.target.rect.y - self.rect.y).normalize()
        if vector.length() > 0:
            self.direction = vector.normalize()
        else:
            self.direction = pygame.math.Vector2(0, 0)
        move_vector = self.direction * self.speed  # direction multiplied by speed
        self.rect.move_ip(move_vector.x, move_vector.y)  

        # Check if out of screen similar to bullet logic.
        if (self.rect.bottom < 0) or (self.rect.top > win_height) or (self.rect.left > win_width) or (self.rect.right < 0):
            self.kill()

class Enemy(pygame.sprite.Sprite):
    ENEMY_IMG = ENEMY
    def __init__(self):
        super().__init__()
        self.image_original = self.ENEMY_IMG  # Non-rotated image
        self.image = self.image_original
        self.rect = self.image.get_rect(center=(random.randint(0, win_width), random.randint(0, 400)))
        self.speed = 4
        self.last_known_direction = pygame.math.Vector2(-1, 0)
        self.freeze = 0

    def update(self):
        # Random movement
        if self.freeze <= 0:
            if random.randint(0, 15) == 1:  # 2% chance to change direction
                while True:
                    self.last_known_direction = pygame.math.Vector2(random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))
                    if self.last_known_direction.length() != 0:
                        break
            if not self.last_known_direction.length() == 0:  # avoid division by zero
                angle = self.last_known_direction.angle_to(pygame.math.Vector2(1, 0))
                self.image = rotate_image(self.image_original, angle)
            self.rect.move_ip(self.speed * self.last_known_direction.x, self.speed * self.last_known_direction.y)
        else:
            self.freeze -= clock.get_time()

        # Keep the enemy inside the screen
        self.rect.clamp_ip(screen.get_rect())

class BossEnemy(Enemy):
    ENEMY_IMG = BENEMY
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = self.ENEMY_IMG
        self.powerup_dropped = False

    def update(self):
        super().update()
        # Include additional behavior if needed for the boss.
        
    def drop_powerup(self):
        if not self.powerup_dropped:
            # Drop the "triple shot" powerup at the boss's position
            powerup = TripleShotPowerup(self.rect.centerx, self.rect.centery)
            powerups.add(powerup)
            all_sprites.add("powerup")
            self.powerup_dropped = True

class Bullet(pygame.sprite.Sprite):
    def __init__(self, position, direction, shooter="player"):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill((255, 0, 0) if shooter == "player" else (0, 255, 0))
        self.rect = self.image.get_rect(center=position)
        self.speed = 10
        self.direction = direction.normalize()
        self.shooter = shooter

    def update(self):
        move_vector = self.direction * self.speed  # direction multiplied by speed
        self.rect.move_ip(move_vector.x, move_vector.y)  # move in place

    # Check if the bullet is out of the screen
        if (self.rect.bottom < 0) or (self.rect.top > win_height) or (self.rect.left > win_width) or (self.rect.right < 0):
            self.kill() 

def distance(point1, point2):
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5

def start_wave_intro():
    global wave_intro, wavenumber
    print('++')
    wavenumber+=1
    player
    wave_intro = True
    player.position = pygame.math.Vector2(win_width / 2, win_height - PLAYER_SIZE[1] / 2)
    player.rect.topleft = player.position


def main():
    global all_sprites
    global screen, bazooka
    global bullet_limit, enemies, bazookas_left, wavenumber, wave_intro, player
    wave_intro = True
    screen = pygame.display.set_mode((win_width, win_height))
    all_sprites = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    ebullets = pygame.sprite.Group()
    bullet_limit = 1
    bazookas_left = 5
    background = Background()
    scroll_speed = 2 
    FPS = 30
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            if not wave_intro:
                bullets_to_fire = 3 if player.triple_shot else 1
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and bullets_to_fire+len(bullets) <= bullet_limit:

                        direction = player.last_known_direction
                        new_bullet = Bullet(player.rect.center, direction)
                        bullets.add(new_bullet)
                        all_sprites.add(new_bullet)
                        print("main")
                        if player.triple_shot == True:  
                            print('firing')
                            left_bullet_direction = direction.rotate(30)  # rotate original direction 30 degrees to the left
                            right_bullet_direction = direction.rotate(-30)  # rotate original direction 30 degrees to the right

                            left_bullet = Bullet(player.rect.center, left_bullet_direction)
                            right_bullet = Bullet(player.rect.center, right_bullet_direction)

                            bullets.add(left_bullet, right_bullet)
                            all_sprites.add(left_bullet, right_bullet)
                    elif event.key == pygame.K_b and bazookas_left > 0:
                        untargeted = [e for e in enemies if e not in targeted_enemies]
                        if not untargeted:
                            break
                        closest_enemy = min(untargeted, key=lambda e: distance(player.rect.center, e.rect.center))
                        targeted_enemies.add(closest_enemy)
                        newbazooka = Bazooka(player.rect.center, closest_enemy)
                        all_sprites.add(newbazooka)
                        bazooka.add(newbazooka)
                        bazookas_left -= 1
                
        if wave_intro:
            screen.fill((0, 0, 0))  # Clear the screen
            render_text(screen, f"Wave {wavenumber}", 50, (255, 255, 255), (win_width / 2, win_height / 2))
            time.sleep(1)
            wave_intro = False
            pygame.display.flip()
            spawn_wave()
        else:

            all_sprites.update()
        
        
            for enemy in enemies:
                if random.randint(0, 60) == 0:  # 0.5% chance per frame to shoot
                    enemy_bullet = Bullet(enemy.rect.center, enemy.last_known_direction, shooter="enemy")
                    all_sprites.add(enemy_bullet)
                    ebullets.add(enemy_bullet)



        # Check for collision
            if pygame.sprite.spritecollide(player, enemies, False):
                mixer.Sound('die.wav').play()
                time.sleep(2)
                print("Player died!")
                main()
            collided_bullets = pygame.sprite.groupcollide(bullets, enemies, True, False)
            for bullet, hit_enemies in collided_bullets.items():
                for enemy in hit_enemies:
                    if isinstance(enemy, BossEnemy):
            # Drop the triple shot powerup for BossEnemy
                        powerup = TripleShotPowerup(enemy.rect.centerx, enemy.rect.centery)
                        print("TripleShotPowerup created at:", powerup.rect.center)
                        all_sprites.add(powerup)
                        powerups.add(powerup)
                        enemy.kill()  # Remove the BossEnemy sprite
                        mixer.Sound('die.wav').play()
                    else:
                        enemy.kill()  # Remove the regular Enemy sprite
                        mixer.Sound('die.wav').play()
                        a = random.random()
                        if random.random() < 0.25:  
                            powerup = Powerup("freeze", enemy.rect.center)
                            all_sprites.add(powerup)
                            powerups.add(powerup)
                        elif a >= 0.25 and a<0.5:
                            powerup = Powerup("speed", enemy.rect.center)
                            all_sprites.add(powerup)
                            powerups.add(powerup)
                        elif a>=0.5 and a<0.75:
                            powerup = Powerup("bullet", enemy.rect.center)
                            all_sprites.add(powerup)
                            powerups.add(powerup)
                        else:
                            powerup = Powerup("bazooka", enemy.rect.center)
                            all_sprites.add(powerup)
                            powerups.add(powerup)
            collided_bullets = pygame.sprite.spritecollide(player, ebullets, False)
        
            for bullet in collided_bullets:
                if bullet.shooter == "enemy":
                    mixer.Sound('die.wav').play()
                    time.sleep(1)
                    print("Player died!")
                    main()
                    break
            for b in bazooka:
                if pygame.sprite.collide_rect(b, b.target):
                    b.kill()  # Remove bazooka
                    b.target.kill()





            background.move(scroll_speed)

            screen.fill((0, 0, 0))
            background.draw(screen)
            all_sprites.draw(screen)
        # Render the text
            text_surface = font.render(f'Bazookas left: {bazookas_left}', True, (255, 0, 0))  # White text

# Get the screen's width and height
            screen_width = screen.get_width()
            screen_height = screen.get_height()

# Calculate position to draw text at the bottom-center
            text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height - text_surface.get_height() // 2))
            text_rect.topleft = (10, screen_height - text_surface.get_height() - 10)

# Draw the text
            screen.blit(text_surface, text_rect)
            if len(enemies) == 0:  # All enemies are defeated
                start_wave_intro()
            pygame.display.flip()

            clock.tick(FPS)
        


def rotate_image(image, angle):
    original_rect = image.get_rect()
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_rect = original_rect.copy()
    rotated_rect.center = rotated_image.get_rect().center
    rotated_image = rotated_image.subsurface(rotated_rect).copy()
    return rotated_image

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((win_width, win_height))
    pygame.display.set_caption("My Game")
    mixer.music.load('music.wav')
    pygame.mixer.music.play(-1)
    clock = pygame.time.Clock()
    
    intro()  # Start with the intro screen
    main()
import pygame, random

# INIT PYGAME
pygame.init()


# SET UP DISPLAY AND CONSTANTS 
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('TEST KNIGHT')

TEST_WORDS = {
    'word': 'an apple', 
    'correct_answer': 'яблуко',
    'translation_options':[
        'груша',
        "слива",
        "кабачок"]

}

# SET COLOR
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# SET FPS and CLOCK
FPS = 60
clock = pygame.time.Clock()

# DEFINE CLASSES
class Game():
    """A class to control a gameplay"""
    def __init__(self, player, monster_group):
        """INIT the game object"""
        self.score = 0
        self.round_number = 0

        self.round_time = 0
        self.frame_count = 0

        self.player = player
        self.monster_group = monster_group

        # SET SOUNDS and MUSIC
        self.next_level_sound = pygame.mixer.Sound('app_minigames/games/test_knight/RES/next_level.wav')

        # SET FONTS
        self.font = pygame.font.Font('app_minigames/games/test_knight/RES/Abrushow.ttf', 24)

        # # SET images
        # blue_image = pygame.image.load('app_minigames/games/test_knight/RES/blue_monster.png')
        # green_image = pygame.image.load('app_minigames/games/test_knight/RES/green_monster.png')
        # purple_image = pygame.image.load('app_minigames/games/test_knight/RES/purple_monster.png')
        # yellow_image = pygame.image.load('app_minigames/games/test_knight/RES/yellow_monster.png')
        # self.target_monster_images = [blue_image, green_image, purple_image, yellow_image]



        # self.target_monster_type = random.randint(0, 3)
        # self.target_monster_image = self.target_monster_images[self.target_monster_type]

        # self.target_monster_rect = self.target_monster_image.get_rect()
        # self.target_monster_rect.centerx = WINDOW_WIDTH//2
        # self.target_monster_rect.top = 30

    def update(self):
        """UPDATE the game object"""
        self.frame_count += 1
        if self.frame_count == FPS:
            self.round_time += 1
            self.frame_count = 0

        #CHECK for collisions
        self.check_collisions()
    
    def draw(self):
        """DRAW HUD and other to display"""
        # SET COLORs
        WHITE = (255, 255, 255)
        BLUE = (20, 176, 235)
        GREEN = (87, 201, 47)
        PURPLE = (226, 73, 243)
        YELLOW = (243, 157, 20)

        # ADD the monster colors to a list where the index 
        colors = [BLUE, GREEN, PURPLE, YELLOW]

        # SET texts
        catch_text = self.font.render("Current catch", True, WHITE)
        catch_rect = catch_text.get_rect()
        catch_rect.centerx = WINDOW_WIDTH//2
        catch_rect.top = 5

        score_text = self.font.render("Score: " + str(self.score), True, WHITE)
        score_rect = score_text.get_rect()
        score_rect.topleft = (5, 5)

        lives_text = self.font.render("Lives: " + str(self.player.lives), True, WHITE)
        lives_rect = lives_text.get_rect()
        lives_rect.topleft = (5, 35)

        round_text = self.font.render('Current round: ' + str(self.round_number), True, WHITE)
        round_rect = round_text.get_rect()
        round_rect.topleft = (5, 65)

        time_text = self.font.render('Round Time: ' + str(self.round_time), True, WHITE)
        time_rect = time_text.get_rect()
        time_rect.topright = (WINDOW_WIDTH - 10, 5)

        warp_text = self.font.render('Warps: ' + str(self.player.warps), True, WHITE)
        warp_rect = warp_text.get_rect()
        warp_rect.topright = (WINDOW_WIDTH - 10, 35)

        #BLIT the HUD
        display_surface.blit(catch_text, catch_rect)
        display_surface.blit(score_text, score_rect)
        display_surface.blit(round_text, round_rect)
        display_surface.blit(lives_text, lives_rect)
        display_surface.blit(time_text, time_rect)
        display_surface.blit(warp_text, warp_rect)
        # display_surface.blit(self.target_monster_image, self.target_monster_rect)

        # pygame.draw.rect(display_surface, colors[self.target_monster_type], (WINDOW_WIDTH//2 - 32, 30, 64, 64), 2)
        # pygame.draw.rect(display_surface, colors[self.target_monster_type], (0, 100, WINDOW_WIDTH, WINDOW_HEIGHT - 200), 4)

    def check_collisions(self):
        """CHECK collisions between player and monster"""
        # CHECK for collision between player and an individual
        # We must test the type of the monster to see if it matches the type of our target monster
        collided_monster = pygame.sprite.spritecollideany(self.player, self.monster_group)
        
        #We collided with a monster
        if collided_monster:
            pass
            # Caught the correct monster
            # print(collided_monster.translation)

            # if collided_monster.type == self.target_monster_type:
            #     self.score += 100 * self.round_number
            #     #Remove caught monster
            #     collided_monster.remove(self.monster_group)
            #     if (self.monster_group):
            #         #There are more monsters to catch
            #         self.player.catch_sound.play()
            #         self.choose_new_target()
            #     else:
            #         #The round is complete
            #         self.player.reset()
            #         self.start_new_round()
                    
            # else: #If we caught the wrong monster
            #     self.player.die_sound.play()
            #     self.player.lives -= 1
            #     #Check for game over
            #     if self.player.lives == 0:
            #         self.pause_game(f"Final Score: {str(self.score)}", "Press 'ENTER' to play again")
            #         self.reset_game()
            #     self.player.reset()


    def start_new_round(self):
        """POPULATE board with new monsters"""
        # PROVIDE a score bonus based on how quickly round was finished
        self.score += int(10000 * self.round_number / (1 + self.round_time))

        #RESET round values
        self.round_time = 0
        self.frame_count = 0
        self.round_number += 1
        self.player.warps += 1

        # REMOVE remaining monstrs from the game
        for monster in self.monster_group:
            self.monster_group.remove(monster)
        
        # ADD monsters to the monsters group
        for translation in TEST_WORDS['translation_options']:
            self.monster_group.add(Monster(random.randint(0, WINDOW_WIDTH - 48), random.randint(100, WINDOW_HEIGHT - 164), translation))
            self.monster_group.add(Monster(random.randint(0, WINDOW_WIDTH - 48), random.randint(100, WINDOW_HEIGHT - 164), translation))
            self.monster_group.add(Monster(random.randint(0, WINDOW_WIDTH - 48), random.randint(100, WINDOW_HEIGHT - 164), translation))
            self.monster_group.add(Monster(random.randint(0, WINDOW_WIDTH - 48), random.randint(100, WINDOW_HEIGHT - 164), translation))
        
        # # CHOOSE a new target monster
        # self.choose_new_target()

        # self.next_level_sound.play()

    # def choose_new_target(self):
    #     target_moster = random.choice(self.monster_group.sprites())
    #     self.target_monster_type = target_moster.type
    #     self.target_monster_image = target_moster.image

    def pause_game(self, main_text, sub_text):
        """PAUSE the GAME"""      
        

        #CREATE the main ause text
        main_text = self.font.render(main_text, True, WHITE)
        main_rect = main_text.get_rect()
        main_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

        # CREATE the sub text
        sub_text = self.font.render(sub_text, True, WHITE)
        sub_rect = sub_text.get_rect()
        sub_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 64)

        # DISPLAY the pause text
        display_surface.fill(BLACK)
        display_surface.blit(main_text, main_rect)
        display_surface.blit(sub_text, sub_rect)
        pygame.display.update()

        #PAUSE the game
        is_paused = True
        while is_paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        is_paused = False
                if event.type == pygame.QUIT:
                    is_paused = False
                    running = False


    def reset_game(self):
        """RESET THE GAME"""
        self.socre = 0
        self.round_number = 0

        self.player.lives = 5
        self.player.warps = 2

        self.start_new_round()

class Player(pygame.sprite.Sprite):
    """A PLAYER class, a user can control"""
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('app_minigames/games/test_knight/RES/knight.png')
        self.rect = self.image.get_rect()
        self.rect.centerx = WINDOW_WIDTH//2
        self.rect.bottom = WINDOW_HEIGHT

        self.lives = 5
        self.warps = 2
        self.velocity = 8

        self.catch_sound = pygame.mixer.Sound('app_minigames/games/test_knight/RES/catch.wav')
        self.catch_sound.set_volume(.1)
        self.die_sound = pygame.mixer.Sound('app_minigames/games/test_knight/RES/die.wav')
        self.die_sound.set_volume(.1)
        self.warp_sound = pygame.mixer.Sound('app_minigames/games/test_knight/RES/warp.wav')

    def update(self):
        keys = pygame.key.get_pressed()

        # MOVE the player within the bounds of the game
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.velocity
        if keys[pygame.K_RIGHT] and self.rect.right < WINDOW_WIDTH:
            self.rect.x += self.velocity
        if keys[pygame.K_UP] and self.rect.top > 100:
            self.rect.y -= self.velocity
        if keys[pygame.K_DOWN] and self.rect.bottom < WINDOW_HEIGHT - 100:
            self.rect.y += self.velocity


    def warp(self):
        if self.warps > 0:
            self.warps -= 1
            self.warp_sound.play()
            self.rect.bottom = WINDOW_HEIGHT

    def reset(self):
        self.rect.centerx = WINDOW_WIDTH//2
        self.rect.bottom = WINDOW_HEIGHT  

# class Monster(pygame.sprite.Sprite):

#     def __init__(self, x, y, image, monster_type ):
#         super().__init__()
#         self.image = image
#         self.rect = self.image.get_rect()
#         self.rect.topleft = (x, y)

#         # self.font = pygame.font.Font('app_minigames/games/test_knight/RES/Abrushow.ttf', 24)
#         # self.text_surface = self.font.render("Test word", True, WHITE)
#         # self.text_rect = self.text_surface.get_rect()
#         # self.text_rect.centerx = WINDOW_WIDTH//2
#         # self.text_rect.top = 5

        

#         # MONSTER type is an int 0 -> blue, 1 -> green, 2-> purple, 3-> yellow
#         self.type = monster_type

#         # SET random motion
#         self.dx = random.choice([-1,1])
#         self.dy = random.choice([-1, 1])
#         self.velocity = random.randint(1, 5)

#     def update(self):
#         self.rect.x += self.dx * self.velocity
#         self.rect.y += self.dy * self.velocity

#         # BOUNCE the monster of the edges of display
#         if self.rect.left < 0 or self.rect.right >= WINDOW_WIDTH:
#             self.dx = -1*self.dx
#         if self.rect.top <= 100 or self.rect.bottom >= WINDOW_HEIGHT - 100:
#             self.dy = -1 * self.dy
class Monster(pygame.sprite.Sprite):

    def __init__(self, x, y, word):
        super().__init__()
        self.translation = word
        # шрифт
        font = pygame.font.Font(None, 36)  # або твій ttf

        # генеруємо поверхню з текстом
        text_surface = font.render(word, True, (255, 255, 255))
        
        # робимо фон під текстом (опційно)
        padding = 10
        self.image = pygame.Surface(
            (text_surface.get_width() + padding*2, text_surface.get_height() + padding*2)
        )

        # колір фону залежно від типу
        colors = [
            (80, 80, 255),  # blue
            (80, 255, 80),  # green
            (180, 80, 255), # purple
            (255, 255, 80), # yellow
        ]

        self.image.fill((80, 80, 255))

        # малюємо текст по центру
        self.image.blit(text_surface, (padding, padding))

        # позиція
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # рух
        self.dx = random.choice([-1, 1])
        self.dy = random.choice([-1, 1])
        self.velocity = random.randint(1, 5)

    def update(self):
        self.rect.x += self.dx * self.velocity
        self.rect.y += self.dy * self.velocity

        if self.rect.left < 0 or self.rect.right >= WINDOW_WIDTH:
            self.dx *= -1
        if self.rect.top <= 100 or self.rect.bottom >= WINDOW_HEIGHT - 100:
            self.dy *= -1    
# CREATE a player group and object --------------------------------CREATE INSTANCES---------------------------------------------
my_player_group = pygame.sprite.Group()
my_player = Player()
my_player_group.add(my_player)

# CREATE a monster group and objects
my_monster_group = pygame.sprite.Group()

# monster = Monster(500, 500, pygame.image.load('RES/green_monster.png'), 1)
# my_monster_group.add(monster)
# monster = Monster(100, 500, pygame.image.load('RES/blue_monster.png'), 0)
# my_monster_group.add(monster)


# CREATE  game object
my_game = Game(my_player, my_monster_group)
my_game.pause_game("MONSTER WRANGLER", "Press 'ENTER' to begin")
my_game.start_new_round()

# -------------------------------------------------------------------------->>> THE MAIN GAME LOOP --->>>
running = True
while running:
    for event in pygame. event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                my_player.warp()

    # FILL the display
    display_surface.fill((0, 0, 0))

    # UPDATE and draw sprite groups
    my_player_group.update()
    my_player_group.draw(display_surface)

    my_monster_group.update()
    my_monster_group.draw(display_surface)

    # UPDATE and DRAW the GAME
    my_game.update()
    my_game.draw()

    # UPDATE display and tick clock
    pygame.display.update()
    clock.tick(FPS)

# <<<--- THE MAIN GAME LOOP <<<---

# END THE GAME
pygame.quit()
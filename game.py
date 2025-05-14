import pygame
import random
import os

pygame.init()
def reset_game():
    global cat_x, cat_y, cat_vel_y, ob, score, game_over, waiting_to_start, last_score_update_time, frame_counter, game_restart_delay, game_over_time   
    cat_x, cat_y = 100, GROUND - cat_height
    cat_vel_y = 0  # Vertical velocity
    ob = []
    score = 0
    game_over = False
    global high_score, new_high
    new_high = False
    waiting_to_start = True
    last_score_update_time = pygame.time.get_ticks()
    frame_counter = 0
    game_restart_delay = 1000  # in ms
    game_over_time = 0

#game setup
width , height = 800, 400
WHITE = (255, 255, 255)
BLUE = (0,0,255)
BLACK = (0,0,0)
GROUND = height - 165


font = pygame.font.Font("PixeloidSans-Bold.ttf", 52)
score_font = pygame.font.Font("PixeloidSans.ttf", 30) 

cat_width , cat_height = 65, 65

# cat physics
gravity = 0.6  # Gravity strength
jump_strength = -11 # Jump force

#obstacles
ob_width, ob_height = 54, 54
ob_speed=5
ob_spawn_time_min = 50
ob_spawn_time_max = 120
ob_spawn_time = random.randint(ob_spawn_time_min, ob_spawn_time_max)

RED = (255,0,0)

blink = True
blink_timer = 0

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Run On")
clock = pygame.time.Clock()
FPS = 60 

cat_img = pygame.image.load("cat.png").convert_alpha()
cat_img = pygame.transform.scale(cat_img, (cat_width, cat_height))

stone_imgs = [
    pygame.transform.scale(pygame.image.load(f"stone{i}.png").convert_alpha(), (ob_width, ob_height))
    for i in range(6)
]
bg_img = pygame.image.load("bg_full.jpg").convert()
bg_img = pygame.transform.scale(bg_img, (width, height))

cat_mask = pygame.mask.from_surface(cat_img)

stone_masks = [pygame.mask.from_surface(img) for img in stone_imgs]

#highscore
high_score_file = "highscore.txt"

if os.path.exists(high_score_file):
    with open(high_score_file, "r") as f:
        try:
            high_score = int(f.read())
        except:
            high_score = 0
else:
    high_score = 0


reset_game()

running = True
while running:
    screen.blit(bg_img, (0,0))

    #event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_over:
                current_time = pygame.time.get_ticks()
                if current_time - game_over_time > game_restart_delay:
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        reset_game()
            if waiting_to_start:
                if event.key in [pygame.K_SPACE, pygame.K_UP]:
                    waiting_to_start = False
            elif not game_over:
                if event.key == pygame.K_SPACE and cat_y == GROUND - cat_height:
                    cat_vel_y = jump_strength
    
    if not game_over:
        if not waiting_to_start:
            cat_y += cat_vel_y
            cat_vel_y += gravity

            if cat_y > GROUND - cat_height:
                cat_y = GROUND - cat_height
                cat_vel_y = 0

            #spawing new obs
            frame_counter += 1
            if frame_counter >= ob_spawn_time:
                frame_counter = 0
                ob_x = width
                ob_y = GROUND - ob_height + 10
                ob.append([ob_x, ob_y, random.choice(stone_imgs)])
                ob_spawn_time = random.randint(ob_spawn_time_min, ob_spawn_time_max)
            
            #move obstacles left
            for o in ob:
                o[0] -= ob_speed                                                                                                                

    #removes obstacles off screen
    ob = [obs for obs in ob if obs[0]> -ob_width]

    cat_rect = pygame.Rect(cat_x, cat_y, cat_width, cat_height)
    screen.blit(cat_img, (cat_x, cat_y))
 
    for o in ob:
        ob_x, ob_y, ob_img = o
        ob_rect = pygame.Rect(ob_x,ob_y, ob_width, ob_height)
        screen.blit(ob_img, (ob_x, ob_y))

        offset = (ob_x - cat_x, ob_y - cat_y)
        ob_mask = pygame.mask.from_surface(ob_img)

        if cat_mask.overlap(ob_mask, offset) and not game_over:
            print("Game Over")
            game_over = True
            game_over_time = pygame.time.get_ticks()
            blink_timer = pygame.time.get_ticks()
            blink = True
    
    # Score Update
    if not game_over and not waiting_to_start:
        current_time = pygame.time.get_ticks()
        if current_time - last_score_update_time >= 1000:
            if score >= 100:
                score += 2
            else:
                score += 1
            last_score_update_time = current_time
    
    # Score Display
    if game_over:
        now = pygame.time.get_ticks()
        if now - blink_timer > 500:  
            blink = not blink
            blink_timer = now

        if blink:
            score_text = score_font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (width - score_text.get_width() - 10, 10))

        text_surface = font.render("Game Over", True, WHITE)
        screen.blit(text_surface, (width // 2 - text_surface.get_width() // 2, height // 2 - 148))
        # High score check & display
        if score > high_score:
            high_score = score
            new_high = True
            with open(high_score_file, "w") as f:
                f.write(str(high_score))

        if new_high:
            new_text = score_font.render(f"New High Score: {high_score}", True, WHITE)
        else:
            new_text = score_font.render(f"High Score: {high_score}", True, WHITE)

        screen.blit(new_text, (width // 2 - new_text.get_width() // 2, height // 2 - 87))


    else:
        score_text = score_font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (width - score_text.get_width() - 10, 10))

    if waiting_to_start:
        press_text = score_font.render("Press spacebar to start", True, (255, 255, 255))
        screen.blit(press_text, (width // 2 - press_text.get_width() // 2, height // 2 - 110))


    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
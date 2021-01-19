# Red spaceship is on the left hand side, player 1.

import pygame
import os


BLACK_COLOR = 0, 0, 0
WHITE_COLOR = 255, 255, 255
RED_COLOR = 255, 0, 0
YELLOW_COLOR = 255, 255, 0

pygame.init()
WINDOW_SIZE = WIDTH, HEIGHT = (900, 600)
WINDOW = pygame.display.set_mode(WINDOW_SIZE)



RED_GOT_HIT = pygame.USEREVENT + 1
YELLOW_GOT_HIT = pygame.USEREVENT + 2

pygame.display.set_caption("Space Invaders v0.1")
WINDOW_ICON = pygame.image.load(os.path.join("assets", "spaceship_icon.png"))
pygame.display.set_icon(WINDOW_ICON)

RED_SHIP_ORIG = pygame.image.load(os.path.join("assets", "spaceship_red.png"))
YELLOW_SHIP_ORIG = pygame.image.load(
                                os.path.join("assets", "spaceship_yellow.png")
                                )
BACKGROUND_IMG = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "space.png")), WINDOW_SIZE
)

def process_ships(imgs, factor):
    current_ships_size = imgs[0].get_size()
    new_ships_size = tuple(map(lambda x: x // factor, current_ships_size))
    processed_imgs = []
    angles = (90, 270)
    for im, ang in zip(imgs, (90, 270)):
        scaled_im = pygame.transform.scale(im, new_ships_size)
        processed_im = pygame.transform.rotate(scaled_im, ang)
        processed_imgs.append(processed_im)

    return processed_imgs

# red ship will be pointing right and should be on LHS
red_ship, yellow_ship = process_ships(imgs=(RED_SHIP_ORIG, YELLOW_SHIP_ORIG),
                                      factor=8) 
SHIP_SIZE = SHIP_WIDTH, SHIP_HEIGHT = red_ship.get_size()
print("Ship size", SHIP_SIZE)


def draw_window(red_rec, yellow_rec, bullets, mid_border_rect, health,
                health_font):

    WINDOW.blit(BACKGROUND_IMG, (0, 0))
    pygame.draw.rect(WINDOW, WHITE_COLOR, mid_border_rect)
    
    red_health = health_font.render("Health: " + str(health["red"]),
                                    1, WHITE_COLOR)
    yellow_health = health_font.render("Health: " + str(health["yellow"]),
                                       1, WHITE_COLOR)
    WINDOW.blit(red_health, (10, 10))
    WINDOW.blit(yellow_health, (WIDTH - 10 - yellow_health.get_width(), 10))

    for key in bullets:
        col = RED_COLOR if key == "red" else YELLOW_COLOR
        for bullet in bullets[key]:
                pygame.draw.rect(WINDOW, col, bullet)

    WINDOW.blit(red_ship, (red_rec.x, red_rec.y))
    WINDOW.blit(yellow_ship, (yellow_rec.x, yellow_rec.y))
    pygame.display.update()


def handle_ships(key_pressed, rect, mid_border_rect, ship="red", velocity=5):
    # SEQ: UP DOWN RIGHT LEFT
    if ship == "red":
        if key_pressed[pygame.K_w] and (rect.top - velocity) >= 0:
            rect.y -= velocity
        if key_pressed[pygame.K_s] and (rect.bottom + velocity) <= HEIGHT:
            rect.y += velocity
        if key_pressed[pygame.K_d] and (rect.right + velocity) <= mid_border_rect.left:
            rect.x += velocity
        if key_pressed[pygame.K_a] and (rect.left - velocity) >= 0:
            rect.x -= velocity
    else:
        if key_pressed[pygame.K_UP] and (rect.top - velocity) >= 0:
            rect.y -= velocity
        if key_pressed[pygame.K_DOWN] and (rect.bottom + velocity) <= HEIGHT:
            rect.y += velocity
        if key_pressed[pygame.K_RIGHT] and (rect.right + velocity) <= WIDTH:
            rect.x += velocity
        if key_pressed[pygame.K_LEFT] and (rect.left - velocity) >= mid_border_rect.right:
            rect.x -= velocity

def handle_bullets(bullets, velocity, red_rec, yellow_rec):
    for key in bullets:
        for bullet in bullets[key]:
            if key == "red":
                bullet.x += velocity
                if bullet.colliderect(yellow_rec):
                    # post event here
                    pygame.event.post(pygame.event.Event(YELLOW_GOT_HIT))
                    bullets[key].remove(bullet)
                elif bullet.x > WIDTH:
                    bullets[key].remove(bullet)
            else: # key == "yellow"
                bullet.x -= velocity
                if bullet.colliderect(red_rec):
                    # post event here
                    pygame.event.post(pygame.event.Event(RED_GOT_HIT))
                    bullets[key].remove(bullet)
                elif bullet.x < 0:
                    bullets[key].remove(bullet)

def get_winner(health):
    winner_text = ""

    if health["red"] <= 0:
        winner_text = "yellow"
    elif health["yellow"] <= 0:
        winner_text = "red"

    return winner_text

def announce_winner(winner, winning_font, delay_ms=3000):
    winning_text = winner.title() + " Wins!"
    text = winning_font.render(winning_text, 1, WHITE_COLOR)
    WINDOW.blit(text,
        (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2)
        )
    pygame.display.update()
    pygame.time.delay(delay_ms)

def main():

    pygame.font.init()
    health_font = pygame.font.SysFont("comicsans", 40, italic=True)
    winning_font = pygame.font.SysFont("comicsans", 100)

    GAP_TO_BORDER = 50
    MID_BORDER_WIDTH = 6

    mid_left_pos = GAP_TO_BORDER, (HEIGHT // 2) - (SHIP_HEIGHT // 2)
    mid_right_pos = (WIDTH - (SHIP_WIDTH + GAP_TO_BORDER)), (HEIGHT // 2) -\
                                                            (SHIP_HEIGHT // 2)
    red_rec = pygame.Rect(mid_left_pos, SHIP_SIZE)
    yellow_rec = pygame.Rect(mid_right_pos, SHIP_SIZE)
    mid_border_rect = pygame.Rect((WIDTH//2 - MID_BORDER_WIDTH//2), 0,
                                  MID_BORDER_WIDTH, HEIGHT)

    SPACESHIP_VELOCITY = 5
    BULLET_VELOCITY = 7
    BULLET_WIDTH = 16 
    BULLET_HEIGHT = 2
    MAX_BULLETS = 3         # Max number of bullets per user on screen
    bullets = {"red": [], "yellow": []}
    MAX_HEALTH = 10
    health = {"red": MAX_HEALTH, "yellow": MAX_HEALTH}

    FPS = 60

    clock = pygame.time.Clock()
    game_over = False
    while not game_over:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                pygame.quit()

            if event.type == RED_GOT_HIT:
                health["red"] -= 1
            if event.type == YELLOW_GOT_HIT:
                health["yellow"] -= 1

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_over = True
                    pygame.quit()

                if event.key == pygame.K_LCTRL and len(bullets["red"]) < MAX_BULLETS:
                    red_bullet = pygame.Rect(red_rec.right,
                                             red_rec.centery - BULLET_HEIGHT // 2, 
                                             BULLET_WIDTH, BULLET_HEIGHT
                                            )
                    bullets["red"].append(red_bullet)
                if event.key == pygame.K_RCTRL and len(bullets["yellow"]) < MAX_BULLETS:
                    yellow_bullet = pygame.Rect(yellow_rec.x - BULLET_WIDTH,
                                            yellow_rec.centery - BULLET_HEIGHT // 2, 
                                            BULLET_WIDTH, BULLET_HEIGHT
                                            )
                    bullets["yellow"].append(yellow_bullet)



        key_pressed = pygame.key.get_pressed()
        # if key_pressed[pygame.K_ESCAPE]:
            # game_over = True
        handle_ships(key_pressed, red_rec, mid_border_rect, ship="red",
                     velocity=SPACESHIP_VELOCITY)
        handle_ships(key_pressed, yellow_rec, mid_border_rect, ship="yellow",
                     velocity=SPACESHIP_VELOCITY)
        handle_bullets(bullets, BULLET_VELOCITY, red_rec, yellow_rec)



        draw_window(red_rec, yellow_rec, bullets, mid_border_rect, health,
                    health_font)
                
                
        # Check for winners
        winner = get_winner(health) 
        if winner: # if string returned not empty, there's winner
            announce_winner(winner, winning_font)
            break

    main() # restart game until user press ESC or clsoe window

if __name__ == "__main__":
    main()

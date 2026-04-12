import pygame
import random
import sys
import json
from time import sleep, time
import os

# highscore loading
with open("high_score.json", "r") as f:
    file = json.load(f)

high_score = file["highscore"]

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.25
FLAP_STRENGTH = -6
PIPE_SPEED = 3
PIPE_GAP = 60
PIPE_WIDTH = 70

# Colors
WHITE = (255, 255, 255)
SKY_BLUE = (135, 206, 235)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) 
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 32)


class Bird:
    def __init__(self):
        self.original_image = pygame.image.load("bird.png").convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (32, 24))

        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0

        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.image)

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.centery = self.y

        angle = -self.velocity * 3
        self.rotated_image = pygame.transform.rotate(self.image, angle)
        self.rotated_rect = self.rotated_image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.rotated_image)

    def draw(self):
        screen.blit(self.rotated_image, self.rotated_rect.topleft)


class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(100, 350)

        raw_pipe = pygame.image.load("pipe.png").convert_alpha()
        self.bottom_img = pygame.transform.scale(raw_pipe, (PIPE_WIDTH, SCREEN_HEIGHT))
        self.top_img = pygame.transform.flip(self.bottom_img, False, True)

        self.top_rect = self.top_img.get_rect(midbottom=(self.x + PIPE_WIDTH//2, self.height))
        self.bottom_rect = self.bottom_img.get_rect(midtop=(self.x + PIPE_WIDTH//2, self.height + PIPE_GAP))

        self.top_mask = pygame.mask.from_surface(self.top_img)
        self.bottom_mask = pygame.mask.from_surface(self.bottom_img)
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self):
        screen.blit(self.top_img, self.top_rect)
        screen.blit(self.bottom_img, self.bottom_rect)


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect(center=(x, y))
    surface.blit(textobj, textrect)


def main():
    global high_score, file
    bird = Bird()
    pipes = [Pipe(SCREEN_WIDTH + 200)]
    score = 0
    running = False
    score_displayed = False

    while True:
        screen.fill(SKY_BLUE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("QUITTING...")
                file["highscore"] = high_score
                with open("high_score.json", "w") as f:
                    json.dump(file, fp=f, indent=4)
                sleep(0.2)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not running:
                        bird = Bird()
                        pipes = [Pipe(SCREEN_WIDTH + 200)]
                        score = 0
                        running = True
                    else:
                        bird.flap()

        if running:
            bird.update()
            bird.draw()

            if pipes[-1].x < SCREEN_WIDTH - 200:
                pipes.append(Pipe(SCREEN_WIDTH))

            for pipe in pipes:
                pipe.update()
                pipe.draw()

                top_offset = (pipe.top_rect.x - bird.rotated_rect.x, pipe.top_rect.y - bird.rotated_rect.y)
                bottom_offset = (pipe.bottom_rect.x - bird.rotated_rect.x, pipe.bottom_rect.y - bird.rotated_rect.y)

                if bird.mask.overlap(pipe.top_mask, top_offset) or \
                    bird.mask.overlap(pipe.bottom_mask, bottom_offset):
                    running = False

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    score += 1
            
            pipes = [p for p in pipes if p.x > -PIPE_WIDTH]

            if bird.rect.top <= 0 or bird.rect.bottom >= SCREEN_HEIGHT:
                running = False

            if score > high_score:
                high_score = score

            score_surface = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_surface, (10, 10))

            if high_score > 0:
                high_score_surface = font.render(f"Highscore {high_score}", True, WHITE)
                high_score_rect = high_score_surface.get_rect()
                high_score_rect.topright = (390, 10)
                screen.blit(high_score_surface, high_score_rect)

            
        else:
            draw_text("Flappy Bird", font, WHITE, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50)
            draw_text("Press SPACE to Start", font, WHITE, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20)
            if score > 0:
                score_displayed = True
                draw_text(f"Score: {score}", font, WHITE, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 90)
            else:
                score_displayed = False
            if high_score > 0:
                if score_displayed:
                    draw_text(f"Highscore: {high_score}", font, WHITE, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 150)
                else:
                    draw_text(f"Highscore: {high_score}", font, WHITE, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 90)
            else:
                draw_text(f"Start Playing", font, WHITE, screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 150)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
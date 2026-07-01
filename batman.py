import pygame
import sys

# ---------------- CONFIGURAÇÕES ----------------
WIDTH, HEIGHT = 1500, 600
FPS = 60
GROUND_Y = HEIGHT - 0
SCALE = 2.7

# Variáveis do cenário infinito
bg_offset = 0
scroll_speed = 5

# ---------------- INICIALIZAÇÃO ----------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Batman Game: Gotham City (Rodando em Pygame-CE)")
clock = pygame.time.Clock()

# --- CARREGAMENTO DO CENÁRIO (agora com background.png) ---
try:
    background_img = pygame.image.load("background.png").convert_alpha()
    # Não redimensionamos – vamos repetir a imagem
except FileNotFoundError:
    # Fallback: tenta carregar cenario.png
    try:
        background_img = pygame.image.load("cenario.png").convert_alpha()
    except FileNotFoundError:
        background_img = pygame.Surface((WIDTH, HEIGHT))
        background_img.fill((40, 40, 60))

# ---------------- IMAGENS DO PERSONAGEM ----------------
def load_images(prefix, count):
    images = []
    for i in range(1, count + 1):
        try:
            img = pygame.image.load(f"{prefix}_{i}.png").convert_alpha()
            width = int(img.get_width() * SCALE)
            height = int(img.get_height() * SCALE)
            img = pygame.transform.scale(img, (width, height))
            images.append(img)
        except FileNotFoundError:
            img = pygame.Surface((50, 50))
            img.fill((255, 0, 0))
            images.append(img)
    return images

# ---------------- CLASSE BATMAN ----------------
class Batman:
    def __init__(self):
        self.animations = {
            "idle": load_images("parado", 4),
            "walk": load_images("andando", 6),
            "punch": load_images("murro", 3),
            "jump": load_images("pulo", 6),
            "down": load_images("abaixado", 1),
            "murro_abaixado": load_images("murroabaixado", 3)
        }

        self.state = "idle"
        self.frame_index = 0
        self.anim_speed = 0.15

        self.image = self.animations[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (250, GROUND_Y)

        self.facing_right = True
        self.hold_punch = False

        self.vel_y = 0
        self.gravity = 0.8
        self.jump_force = -16

    def set_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.frame_index = 0

    def punch_start(self):
        if self.state == "down":
            self.set_state("murro_abaixado")
        elif self.state not in ["punch", "murro_abaixado"]:
            self.set_state("punch")

    def punch_release(self):
        self.hold_punch = False

    def animate(self, loop=True):
        if self.state in ["punch", "murro_abaixado"]:
            if self.hold_punch and int(self.frame_index) == 1:
                self.image = self.animations[self.state][1]
                if not self.facing_right:
                    self.image = pygame.transform.flip(self.image, True, False)
                return

        self.frame_index += self.anim_speed

        if self.frame_index >= len(self.animations[self.state]):
            if loop:
                self.frame_index = 0
            else:
                self.set_state("idle")
                return

        self.image = self.animations[self.state][int(self.frame_index)]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, keys):
        global bg_offset   # <-- permite modificar a variável global

        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        on_ground = False
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y = 0
            on_ground = True

        if self.state in ["punch", "murro_abaixado"]:
            self.animate(loop=False)
            return

        moving = False
        if not keys[pygame.K_s]:
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.facing_right = True
                moving = True
                bg_offset -= scroll_speed   # rola para a esquerda (fundo se move para trás)
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.facing_right = False
                moving = True
                bg_offset += scroll_speed   # rola para a direita

        if not on_ground:
            self.set_state("jump")
        else:
            if keys[pygame.K_s]:
                self.set_state("down")
            elif moving:
                self.set_state("walk")
            else:
                self.set_state("idle")

        if self.state == "jump":
            self.animate(loop=False)
        else:
            self.animate(loop=True)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# ---------------- INSTÂNCIA ----------------
batman = Batman()

# ---------------- LOOP PRINCIPAL ----------------
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_SPACE, pygame.K_w]:
                if batman.rect.bottom >= GROUND_Y:
                    batman.vel_y = batman.jump_force
            if event.key == pygame.K_p:
                batman.hold_punch = True
                batman.punch_start()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_p:
                batman.punch_release()   # indentação corrigida

    keys = pygame.key.get_pressed()
    batman.update(keys)

    # --- DESENHO ---
    screen.fill((0, 0, 0))

    # --- DESENHA FUNDO INFINITO COM REPETIÇÃO ---
    bg_w = background_img.get_width()
    offset = bg_offset % bg_w
    # Desenha cópias suficientes para cobrir a tela (e mais uma margem)
    for x in range(-bg_w, WIDTH + bg_w, bg_w):
        screen.blit(background_img, (x + offset, 0))

    # Desenha o Batman
    batman.draw(screen)

    pygame.display.update()

pygame.quit()
sys.exit()
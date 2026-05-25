import pygame
import sys

# ---------------- CONFIGURAÇÕES ----------------
WIDTH, HEIGHT = 800, 600
FPS = 60
GROUND_Y = HEIGHT - 50
SCALE = 1.5   # <<< AUMENTA O TAMANHO DO BONECO

# ---------------- INICIALIZAÇÃO ----------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Batman Game")
clock = pygame.time.Clock()

# ---------------- FUNÇÃO PARA CARREGAR IMAGENS ----------------
def load_images(prefix, count):
    images = []
    for i in range(1, count + 1):
        img = pygame.image.load(f"{prefix}_{i}.png").convert_alpha()

        width = int(img.get_width() * SCALE)
        height = int(img.get_height() * SCALE)
        img = pygame.transform.scale(img, (width, height))

        images.append(img)
    return images

# ---------------- CLASSE BATMAN ----------------
class Batman:
    def __init__(self):
        self.animations = {
            "idle": load_images("parado", 4),
            "walk": load_images("andando", 6),
            "punch": load_images("murro", 3)
        }

        self.state = "idle"
        self.frame_index = 0
        self.anim_speed = 0.15

        self.image = self.animations[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (100, GROUND_Y)

        self.speed = 5
        self.facing_right = True

        self.hold_punch = False

    def set_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.frame_index = 0

    def punch_start(self):
        if self.state != "punch":
            self.set_state("punch")

    def punch_release(self):
        self.hold_punch = False

    def animate(self, loop=True):
        # -------- CONGELAMENTO NO MURRO_2 --------
        if self.state == "punch":
            if self.hold_punch and int(self.frame_index) == 1:
                self.image = self.animations["punch"][1]
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
        # -------- MURRO --------
        if self.state == "punch":
            self.animate(loop=False)
            return

        # -------- ANDAR DIREITA --------
        if keys[pygame.K_RIGHT]:
            self.facing_right = True
            self.set_state("walk")
            self.rect.x += self.speed
            self.animate()
            return

        # -------- ANDAR ESQUERDA --------
        if keys[pygame.K_LEFT]:
            self.facing_right = False
            self.set_state("walk")
            self.rect.x -= self.speed
            self.animate()
            return

        # -------- PARADO --------
        self.set_state("idle")
        self.animate()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# ---------------- OBJETO ----------------
batman = Batman()

# ---------------- LOOP PRINCIPAL ----------------
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                batman.hold_punch = True
                batman.punch_start()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                batman.punch_release()

    keys = pygame.key.get_pressed()
    batman.update(keys)

    screen.fill((25, 25, 25))
    batman.draw(screen)
    pygame.display.update()

pygame.quit()
sys.exit()

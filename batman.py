import pygame
import sys
import os

# ---------------- CONFIGURAÇÕES ----------------
WIDTH, HEIGHT = 1500, 600
FPS = 60
GROUND_Y = HEIGHT - 50   # Ajuste conforme sua imagem
SCALE = 3.0

# Estados do jogo
MENU = 0
INSTRUCOES = 1
JOGANDO = 2

# ---------------- INICIALIZAÇÃO ----------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Batman Game - Gotham City")
clock = pygame.time.Clock()

# Fonte para o menu
font_title = pygame.font.Font(None, 120)
font_option = pygame.font.Font(None, 60)
font_small = pygame.font.Font(None, 40)

# Variáveis do cenário infinito
bg_offset = 0
scroll_speed = 5

# Estado inicial
game_state = MENU
selected_option = 0  # 0: Iniciar, 1: Instruções, 2: Sair

# --- CARREGAMENTO DO CENÁRIO (agora na pasta "cenarios") ---
try:
    background_img = pygame.image.load(os.path.join("cenarios", "background.png")).convert_alpha()
except FileNotFoundError:
    try:
        background_img = pygame.image.load(os.path.join("cenarios", "cenario.png")).convert_alpha()
    except FileNotFoundError:
        background_img = pygame.Surface((WIDTH, HEIGHT))
        background_img.fill((40, 40, 60))

# ---------------- IMAGENS DO PERSONAGEM ----------------
def load_images(folder, prefix, count):
    images = []
    for i in range(1, count + 1):
        filename = os.path.join(folder, f"{prefix}_{i}.png")
        try:
            img = pygame.image.load(filename).convert_alpha()
            width = int(img.get_width() * SCALE)
            height = int(img.get_height() * SCALE)
            img = pygame.transform.scale(img, (width, height))
            images.append(img)
        except FileNotFoundError:
            print(f"Erro: {filename} não encontrado")
            img = pygame.Surface((50, 50))
            img.fill((255, 0, 0))
            images.append(img)
    return images

# ---------------- CLASSE BATMAN ----------------
class Batman:
    def __init__(self):
        self.animations = {
            "idle": load_images("Sprites/batman", "parado", 4),
            "walk": load_images("Sprites/batman", "andando", 6),
            "punch": load_images("Sprites/batman", "murro", 3),
            "jump": load_images("Sprites/batman", "pulo", 6),
            "down": load_images("Sprites/batman", "abaixado", 1),
            "murro_abaixado": load_images("Sprites/batman", "murroabaixado", 3)
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
        global bg_offset

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
                bg_offset -= scroll_speed
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.facing_right = False
                moving = True
                bg_offset += scroll_speed

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

# ---------------- FUNÇÕES DO MENU ----------------
def desenha_menu():
    # Fundo (escurecido)
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(background_img, (0, 0))
    screen.blit(overlay, (0, 0))

    # Título
    titulo = font_title.render("BATMAN GAME", True, (255, 215, 0))  # dourado
    titulo_rect = titulo.get_rect(center=(WIDTH//2, 150))
    screen.blit(titulo, titulo_rect)

    # Subtítulo
    subtitulo = font_small.render("Gotham City", True, (200, 200, 200))
    subtitulo_rect = subtitulo.get_rect(center=(WIDTH//2, 210))
    screen.blit(subtitulo, subtitulo_rect)

    # Opções
    opcoes = ["Iniciar Jogo", "Instruções", "Sair"]
    cores = [(255, 255, 255) if i != selected_option else (255, 215, 0) for i in range(3)]
    for i, opcao in enumerate(opcoes):
        texto = font_option.render(opcao, True, cores[i])
        rect = texto.get_rect(center=(WIDTH//2, 350 + i * 70))
        screen.blit(texto, rect)

    # Rodapé
    rodape = font_small.render("Use ↑/↓ para navegar e Enter para selecionar", True, (150, 150, 150))
    rodape_rect = rodape.get_rect(center=(WIDTH//2, HEIGHT - 50))
    screen.blit(rodape, rodape_rect)

def desenha_instrucoes():
    # Fundo escurecido
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(background_img, (0, 0))
    screen.blit(overlay, (0, 0))

    titulo = font_title.render("INSTRUÇÕES", True, (255, 215, 0))
    titulo_rect = titulo.get_rect(center=(WIDTH//2, 80))
    screen.blit(titulo, titulo_rect)

    controles = [
        "← / A  -> Andar para esquerda",
        "→ / D  -> Andar para direita",
        "↑ / Espaço -> Pular",
        "S      -> Agachar",
        "P      -> Socar"
    ]

    for i, linha in enumerate(controles):
        texto = font_option.render(linha, True, (255, 255, 255))
        rect = texto.get_rect(center=(WIDTH//2, 200 + i * 60))
        screen.blit(texto, rect)

    voltar = font_small.render("Pressione ESC para voltar ao menu", True, (200, 200, 200))
    voltar_rect = voltar.get_rect(center=(WIDTH//2, HEIGHT - 50))
    screen.blit(voltar, voltar_rect)

# ---------------- INSTÂNCIA ----------------
batman = Batman()

# ---------------- LOOP PRINCIPAL ----------------
running = True
while running:
    clock.tick(FPS)

    # ----- EVENTOS -----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % 3
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % 3
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:  # Iniciar
                        game_state = JOGANDO
                        # Resetar posição do Batman e offset ao iniciar o jogo
                        batman.rect.bottomleft = (250, GROUND_Y)
                        batman.vel_y = 0
                        bg_offset = 0
                    elif selected_option == 1:  # Instruções
                        game_state = INSTRUCOES
                    elif selected_option == 2:  # Sair
                        running = False

        elif game_state == INSTRUCOES:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = MENU

        elif game_state == JOGANDO:
            # Eventos do jogo
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_SPACE, pygame.K_w]:
                    if batman.rect.bottom >= GROUND_Y:
                        batman.vel_y = batman.jump_force
                if event.key == pygame.K_p:
                    batman.hold_punch = True
                    batman.punch_start()
                # Tecla ESC para voltar ao menu durante o jogo
                if event.key == pygame.K_ESCAPE:
                    game_state = MENU

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_p:
                    batman.punch_release()

    # ----- ATUALIZAÇÃO -----
    if game_state == JOGANDO:
        keys = pygame.key.get_pressed()
        batman.update(keys)

    # ----- DESENHO -----
    screen.fill((0, 0, 0))

    if game_state == MENU:
        desenha_menu()

    elif game_state == INSTRUCOES:
        desenha_instrucoes()

    elif game_state == JOGANDO:
        # Desenha fundo infinito
        bg_w = background_img.get_width()
        offset = bg_offset % bg_w
        for x in range(-bg_w, WIDTH + bg_w, bg_w):
            screen.blit(background_img, (x + offset, 0))

        batman.draw(screen)

    pygame.display.update()

pygame.quit()
sys.exit()
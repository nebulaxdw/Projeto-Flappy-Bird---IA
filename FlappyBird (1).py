import pygame
import os
import random
import neat
neat_playing = True
generation = 0
SCR_WIDTH = 500
SCR_HEIGHT = 800
pipe_sprite = pygame.transform.scale2x(
    pygame.image.load(os.path.join('imgs', 'pipe.png')))
ground_sprite = pygame.transform.scale2x(
    pygame.image.load(os.path.join('imgs', 'base.png')))
bg_sprite = pygame.transform.scale2x(
    pygame.image.load(os.path.join('imgs', 'bg.png')))
player_sprites = [
    pygame.transform.scale2x(pygame.image.load(
        os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(
        os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(
        os.path.join('imgs', 'bird3.png'))),
]
pygame.font.init()
text_font = pygame.font.SysFont('sans-serif', 50)

class Player:
    sprites = player_sprites
    max_rotation = 25
    rotation_speed = 20
    animation_time = 5
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.height = self.y
        self.time = 0
        self.img_count = 0
        self.sprite = self.sprites[0]
    def jump(self):
        self.speed = -10.5
        self.time = 0
        self.height = self.y
    def mover(self):
        self.time += 1
        deltaPosition = 1.5 * (self.time**2) + self.speed * self.time
        if deltaPosition > 16:
            deltaPosition = 16
        elif deltaPosition < 0:
            deltaPosition -= 2
        self.y += deltaPosition
        if deltaPosition < 0 or self.y < (self.height + 50):
            if self.angle < self.max_rotation:
                self.angle = self.max_rotation
        else:
            if self.angle > -90:
                self.angle -= self.rotation_speed
    def drawPlayer(self, game_screen):
        # definir qual imagem do passaro vai usar
        self.img_count += 1
        if self.img_count < self.animation_time:
            self.sprite = self.sprites[0]
        elif self.img_count < self.animation_time*2:
            self.sprite = self.sprites[1]
        elif self.img_count < self.animation_time*3:
            self.sprite = self.sprites[2]
        elif self.img_count < self.animation_time*4:
            self.sprite = self.sprites[1]
        elif self.img_count >= self.animation_time*4 + 1:
            self.sprite = self.sprites[0]
            self.img_count = 0
        # se o passaro tiver caindo eu não vou bater asa
        if self.angle <= -80:
            self.sprite = self.sprites[1]
            self.img_count = self.animation_time*2
        # desenhar a imagem
        img_rotated = pygame.transform.rotate(self.sprite, self.angle)
        pos_centro_imagem = self.sprite.get_rect(
            topleft=(self.x, self.y)).center
        retangle = img_rotated.get_rect(center=pos_centro_imagem)
        game_screen.blit(img_rotated, retangle.topleft)
    def get_mask(self):
        return pygame.mask.from_surface(self.sprite)

class Obstacle:
    DISTANCE = 200
    SPEED = 5
    def __init__(self, x):
        self.x = x
        self.height = 0
        self.pos_top = 0
        self.pos_base = 0
        self.OBSTACLE_TOP = pygame.transform.flip(pipe_sprite, False, True)
        self.OBSTACLE_BASE = pipe_sprite
        self.avoided = False
        self.setHeight()
    def setHeight(self):
        self.height = random.randrange(50, 450)
        self.pos_top = self.height - self.OBSTACLE_TOP.get_height()
        self.pos_base = self.height + self.DISTANCE
    def move(self):
        self.x -= self.SPEED
    def drawObstacle(self, tela):
        tela.blit(self.OBSTACLE_TOP, (self.x, self.pos_top))
        tela.blit(self.OBSTACLE_BASE, (self.x, self.pos_base))
    def collide(self, player):
        player_mask = player.get_mask()
        topo_mask = pygame.mask.from_surface(self.OBSTACLE_TOP)
        base_mask = pygame.mask.from_surface(self.OBSTACLE_BASE)
        distance_top = (self.x - player.x, self.pos_top - round(player.y))
        distance_base = (self.x - player.x, self.pos_base - round(player.y))
        topo_ponto = player_mask.overlap(topo_mask, distance_top)
        base_ponto = player_mask.overlap(base_mask, distance_base)
        if base_ponto or topo_ponto:
            return True
        else:
            return False
            
class Ground:
    SPEED = 5
    WIDTH = ground_sprite.get_width()
    IMAGE = ground_sprite
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
    def move(self):
        self.x1 -= self.SPEED
        self.x2 -= self.SPEED
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
    def drawGround(self, screen):
        screen.blit(self.IMAGE, (self.x1, self.y))
        screen.blit(self.IMAGE, (self.x2, self.y))

def drawScreen(screen, players, obstacles, ground, pontos):
    screen.blit(bg_sprite, (0, 0))
    for player in players:
        player.drawPlayer(screen)
    for obstacle in obstacles:
        obstacle.drawObstacle(screen)
    text = text_font.render(f"Pontos: {pontos}", 1, (255, 255, 255))
    screen.blit(text, (SCR_WIDTH - 10 - text.get_width(), 10))
    if neat_playing:
        text = text_font.render(
            f"Geração: {generation}", 1, (255, 255, 255))
        screen.blit(text, (10, 10))
    ground.drawGround(screen)
    pygame.display.update()

def main(genomas, config):  # fitness function
    global generation
    generation += 1
    if neat_playing:
        redes = []
        lista_genomas = []
        players = []
        for _, genoma in genomas:
            rede = neat.nn.FeedForwardNetwork.create(genoma, config)
            redes.append(rede)
            genoma.fitness = 0
            lista_genomas.append(genoma)
            players.append(Player(230, 350))
    else:
        players = [Player(230, 350)]
    ground = Ground(730)
    obstacles = [Obstacle(700)]
    screen = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))
    score = 0
    clockTimer = pygame.time.Clock()
    isPlaying = True
    while isPlaying:
        clockTimer.tick(30)
        # interação com o usuário
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isPlaying = False
                pygame.quit()
                quit()
            if not neat_playing:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        for player in players:
                            player.jump()
        indice_cano = 0
        if len(players) > 0:
            if len(obstacles) > 1 and players[0].x > (obstacles[0].x + obstacles[0].OBSTACLE_TOP.get_width()):
                indice_cano = 1
        else:
            isPlaying = False
            break
        for i, player in enumerate(players):
            player.mover()
            lista_genomas[i].fitness += 0.1
            output = redes[i].activate((player.y,
                                        abs(player.y -
                                            obstacles[indice_cano].height),
                                        abs(player.y - obstacles[indice_cano].pos_base)))
            if output[0] > 0.5:
                player.jump()
        ground.move()
        addObstacle = False
        removeObstacles = []
        for cano in obstacles:
            for i, player in enumerate(players):
                if cano.collide(player):
                    players.pop(i)
                    if neat_playing:
                        lista_genomas[i].fitness -= 1
                        lista_genomas.pop(i)
                        redes.pop(i)
                if not cano.avoided and player.x > cano.x:
                    cano.avoided = True
                    addObstacle = True
            cano.move()
            if cano.x + cano.OBSTACLE_TOP.get_width() < 0:
                removeObstacles.append(cano)
        if addObstacle:
            score += 1
            obstacles.append(Obstacle(600))
            for genoma in lista_genomas:
                genoma.fitness += 5
        for cano in removeObstacles:
            obstacles.remove(cano)
        for i, player in enumerate(players):
            if (player.y + player.sprite.get_height()) > ground.y or player.y < 0:
                players.pop(i)
                if neat_playing:
                    lista_genomas.pop(i)
                    redes.pop(i)
        drawScreen(screen, players, obstacles, ground, score)
def rodar(caminho_config):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                caminho_config)
    populacao = neat.Population(config)
    populacao.add_reporter(neat.StdOutReporter(True))
    populacao.add_reporter(neat.StatisticsReporter())
    if neat_playing:
        populacao.run(main, 50)
    else:
        main(None, None)
if __name__ == '__main__':
    caminho = os.path.dirname(__file__)
    caminho_config = os.path.join(caminho, 'config.txt')
    rodar(caminho_config)

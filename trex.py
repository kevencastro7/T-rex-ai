__author__ = "Shivam Shekhar"

import os
import sys
import pygame
import random
from pygame import *
from random import random as rand
import math
import matplotlib.pyplot as plt



pygame.init()

scr_size = (width,height) = (600,150)
gravity = 0.6

black = (0,0,0)
white = (255,255,255)
background_col = (235,235,235)

high_score = 0

screen = pygame.display.set_mode(scr_size)
clock = pygame.time.Clock()
pygame.display.set_caption("T-Rex Rush")

jump_sound = pygame.mixer.Sound('sprites/jump.wav')
die_sound = pygame.mixer.Sound('sprites/die.wav')
checkPoint_sound = pygame.mixer.Sound('sprites/checkPoint.wav')

def sigmoid(x):
  return 1 / (1 + math.exp(-x))

def load_image(
    name,
    sizex=-1,
    sizey=-1,
    colorkey=None,
    ):

    fullname = os.path.join('sprites', name)
    image = pygame.image.load(fullname)
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)

    if sizex != -1 or sizey != -1:
        image = pygame.transform.scale(image, (sizex, sizey))

    return (image, image.get_rect())

def load_sprite_sheet(
        sheetname,
        nx,
        ny,
        scalex = -1,
        scaley = -1,
        colorkey = None,
        ):
    fullname = os.path.join('sprites',sheetname)
    sheet = pygame.image.load(fullname)
    sheet = sheet.convert()

    sheet_rect = sheet.get_rect()

    sprites = []

    sizex = sheet_rect.width/nx
    sizey = sheet_rect.height/ny

    for i in range(0,ny):
        for j in range(0,nx):
            rect = pygame.Rect((j*sizex,i*sizey,sizex,sizey))
            image = pygame.Surface(rect.size)
            image = image.convert()
            image.blit(sheet,(0,0),rect)

            if colorkey is not None:
                if colorkey is -1:
                    colorkey = image.get_at((0,0))
                image.set_colorkey(colorkey,RLEACCEL)

            if scalex != -1 or scaley != -1:
                image = pygame.transform.scale(image,(scalex,scaley))

            sprites.append(image)

    sprite_rect = sprites[0].get_rect()

    return sprites,sprite_rect


def extractDigits(number):
    if number > -1:
        digits = []
        i = 0
        while(number/10 != 0):
            digits.append(number%10)
            number = int(number/10)

        digits.append(number%10)
        for i in range(len(digits),5):
            digits.append(0)
        digits.reverse()
        return digits

class Dino():
    def __init__(self,sizex=-1,sizey=-1,geracao = 0):
        self.images,self.rect = load_sprite_sheet('dino.png',5,1,sizex,sizey,-1)
        self.images1,self.rect1 = load_sprite_sheet('dino_ducking.png',2,1,59,sizey,-1)
        self.rect.bottom = int(0.98*height)
        self.rect.left = width/15
        self.image = self.images[0]
        self.index = 0
        self.counter = 0
        self.score = 0
        self.isJumping = False
        self.isDead = False
        self.isDucking = False
        self.isBlinking = False
        self.movement = [0,0]
        self.jumpSpeed = 11.5
        self.geracao = geracao
        self.obs = [0,0,0]
        
        self.cromossomo = []
        
        for i in range(8):
            self.cromossomo.append(rand()*2 - 1.0)

        self.cromossomo = [1.35, -1.5, 0.05, -1.15, 1.05, 1.05, 0.05, 1.15]
        
        self.stand_pos_width = self.rect.width
        self.duck_pos_width = self.rect1.width

    def draw(self):
        screen.blit(self.image,self.rect)
        f=pygame.font.SysFont('Arial', 22)
        t=f.render('Geracao: '+str(self.geracao), True, (0, 0, 0))
        screen.blit(t, (10, 10))
        pygame.display.update()


    def checkbounds(self):
        if self.rect.bottom > int(0.98*height):
            self.rect.bottom = int(0.98*height)
            self.isJumping = False

    def update(self):
        if self.isJumping:
            self.movement[1] = self.movement[1] + gravity

        if self.isJumping:
            self.index = 0
        elif self.isBlinking:
            if self.index == 0:
                if self.counter % 400 == 399:
                    self.index = (self.index + 1)%2
            else:
                if self.counter % 20 == 19:
                    self.index = (self.index + 1)%2

        elif self.isDucking:
            if self.counter % 5 == 0:
                self.index = (self.index + 1)%2
        else:
            if self.counter % 5 == 0:
                self.index = (self.index + 1)%2 + 2

        if self.isDead:
           self.index = 4

        if not self.isDucking:
            self.image = self.images[self.index]
            self.rect.width = self.stand_pos_width
        else:
            self.image = self.images1[(self.index)%2]
            self.rect.width = self.duck_pos_width

        self.rect = self.rect.move(self.movement)
        self.checkbounds()

        if not self.isDead and self.counter % 7 == 6 and self.isBlinking == False:
            self.score += 1
            if self.score % 100 == 0 and self.score != 0:
                if pygame.mixer.get_init() != None:
                    checkPoint_sound.play()

        self.counter = (self.counter + 1)
        
    def random_action(self):
        action = [0,0]
        #print(self.obs)
        action[0] = sigmoid(self.cromossomo[0]*self.obs[0] + self.cromossomo[1]*self.obs[1] + self.cromossomo[2]*self.obs[2] + self.cromossomo[3])
        action[1] = sigmoid(self.cromossomo[4]*self.obs[0] + self.cromossomo[5]*self.obs[1] + self.cromossomo[6]*self.obs[2] + self.cromossomo[7])
        for i in range(len(action)):
            if action[i] >0.5:
                action[i] = 1
            else:
                action[i] = 0
        return action
    
    def get_observation(self,rect,tipo):
        if self.rect.left < rect.right:
            d =  rect.right - self.rect.left
            d = 1/d
            if d*100 > self.obs[0] and d*100<=1:
                self.obs[0] = d*100
                data = rect.centery
                if data < 65:
                    self.obs[1] = 2
                elif data <100:
                    self.obs[1] = 1
                else:
                    self.obs[1] = 0
        else:
            self.obs[0] = 0
            self.obs[1] = 0
        
    def get_speed(self,gamespeed):
        self.obs[2] = gamespeed
            
    def crossover(self, outro_individuo):
        corte = round(rand()  * len(self.cromossomo))
        
        filho1 = outro_individuo.cromossomo[0:corte] + self.cromossomo[corte::]
        filho2 = self.cromossomo[0:corte] + outro_individuo.cromossomo[corte::]
        
        filhos = [Dino(44,47,self.geracao + 1),
                  Dino(44,47,self.geracao + 1)]
        filhos[0].cromossomo = filho1
        filhos[1].cromossomo = filho2
        return filhos
    
    def mutacao(self, taxa_mutacao, taxa_aprendizagem):
        #print("Antes %s " % self.cromossomo)
        i = random.randint(0,len(self.cromossomo)-1)
        if rand() < 0.5:
            self.cromossomo[i] = self.cromossomo[i]+taxa_aprendizagem
        else:
            self.cromossomo[i] = self.cromossomo[i]-taxa_aprendizagem

        #print("Depois %s " % self.cromossomo)
        return self


class Cactus(pygame.sprite.Sprite):
    def __init__(self,speed=5,sizex=-1,sizey=-1):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.images,self.rect = load_sprite_sheet('cacti-small.png',3,1,sizex,sizey,-1)
        self.rect.bottom = int(0.98*height)
        self.rect.left = width + self.rect.width
        self.image = self.images[random.randrange(0,3)]
        self.movement = [-1*speed,0]

    def draw(self):
        screen.blit(self.image,self.rect)

    def update(self):
        self.rect = self.rect.move(self.movement)

        if self.rect.right < 0:
            self.kill()

class Ptera(pygame.sprite.Sprite):
    def __init__(self,speed=5,sizex=-1,sizey=-1):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.images,self.rect = load_sprite_sheet('ptera.png',2,1,sizex,sizey,-1)
        self.ptera_height = [height*0.85,height*0.70,height*0.55]
        self.ptera_height = [127,90,60]
        self.rect.centery = self.ptera_height[random.randrange(0,3)]
        self.rect.left = width + self.rect.width
        self.image = self.images[0]
        self.movement = [-1*speed,0]
        self.index = 0
        self.counter = 0
    def draw(self):
        screen.blit(self.image,self.rect)

    def update(self):
        if self.counter % 10 == 0:
            self.index = (self.index+1)%2
        self.image = self.images[self.index]
        self.rect = self.rect.move(self.movement)
        self.counter = (self.counter + 1)
        if self.rect.right < 0:
            self.kill()


class Ground():
    def __init__(self,speed=-5):
        self.image,self.rect = load_image('ground.png',-1,-1,-1)
        self.image1,self.rect1 = load_image('ground.png',-1,-1,-1)
        self.rect.bottom = height
        self.rect1.bottom = height
        self.rect1.left = self.rect.right
        self.speed = speed

    def draw(self):
        screen.blit(self.image,self.rect)
        screen.blit(self.image1,self.rect1)

    def update(self):
        self.rect.left += self.speed
        self.rect1.left += self.speed

        if self.rect.right < 0:
            self.rect.left = self.rect1.right

        if self.rect1.right < 0:
            self.rect1.left = self.rect.right

class Cloud(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.image,self.rect = load_image('cloud.png',int(90*30/42),30,-1)
        self.speed = 1
        self.rect.left = x
        self.rect.top = y
        self.movement = [-1*self.speed,0]

    def draw(self):
        screen.blit(self.image,self.rect)

    def update(self):
        self.rect = self.rect.move(self.movement)
        if self.rect.right < 0:
            self.kill()

class Scoreboard():
    def __init__(self,x=-1,y=-1):
        self.score = 0
        self.tempimages,self.temprect = load_sprite_sheet('numbers.png',12,1,11,int(11*6/5),-1)
        self.image = pygame.Surface((55,int(11*6/5)))
        self.rect = self.image.get_rect()
        if x == -1:
            self.rect.left = width*0.89
        else:
            self.rect.left = x
        if y == -1:
            self.rect.top = height*0.1
        else:
            self.rect.top = y

    def draw(self):
        screen.blit(self.image,self.rect)

    def update(self,score):
        score_digits = extractDigits(score)
        self.image.fill(background_col)
        for s in score_digits:
            self.image.blit(self.tempimages[s],self.temprect)
            self.temprect.left += self.temprect.width
        self.temprect.left = 0

class AlgoritmoGenetico():
    def __init__(self, tamanho_populacao):
        self.tamanho_populacao = tamanho_populacao
        self.populacao = []
        self.geracao = 0
        self.melhor_solucao = 0
        self.lista_solucoes = []
        
    def inicializa_populacao(self):
        for i in range(self.tamanho_populacao):
            self.populacao.append(Dino(44,47))
        self.melhor_solucao = self.populacao[0]
        
    def ordena_populacao(self):
        self.populacao = sorted(self.populacao,
                                key = lambda populacao: populacao.score,
                                reverse = True)
        
    def melhor_individuo(self, individuo):
        if individuo.score > self.melhor_solucao.score:
            self.melhor_solucao = individuo
            
    def soma_avaliacoes(self):
        soma = 0
        for individuo in self.populacao:
           soma += individuo.score
        return soma
    
    def seleciona_pai(self, soma_avaliacao):
        pai = -1
        valor_sorteado = rand() * soma_avaliacao
        soma = 0
        i = 0
        while i < len(self.populacao) and soma < valor_sorteado:
            soma += self.populacao[i].score
            pai += 1
            i += 1
        return pai
    
    def visualiza_geracao(self):
        melhor = self.populacao[0]
        print("G: %s Cromossomo: %s Score: %s" %
              (melhor.geracao,
               melhor.cromossomo,
               melhor.score))

    def resolver(self, taxa_mutacao, taxa_aprendizagem, numero_geracoes):
        self.inicializa_populacao()
        
        for i in range(len(self.populacao)):
            self.populacao[i] = gameplay(1,self.populacao[i],-1)
        self.ordena_populacao()
        self.melhor_solucao = self.populacao[0]
        self.lista_solucoes.append(self.melhor_solucao.score)
        self.visualiza_geracao()
        for geracao in range(numero_geracoes):
            soma_avaliacao = self.soma_avaliacoes()
            nova_populacao = []
            
            for individuos_gerados in range(0, self.tamanho_populacao, 2):
                pai1 = self.seleciona_pai(soma_avaliacao)
                pai2 = self.seleciona_pai(soma_avaliacao)
                
                filhos = self.populacao[pai1].crossover(self.populacao[pai2])
                
                nova_populacao.append(filhos[0].mutacao(taxa_mutacao,taxa_aprendizagem))
                nova_populacao.append(filhos[1].mutacao(taxa_mutacao,taxa_aprendizagem))
                
            #nova_populacao[0] = self.populacao[0]
                
            #nova_populacao[0].geracao = nova_populacao[2].geracao

            
            self.populacao = list(nova_populacao)
            
            for i in range(len(self.populacao)):
                self.populacao[i] = gameplay(1,self.populacao[i],-1)
            
            self.ordena_populacao()
            
            self.visualiza_geracao()
            
            melhor = self.populacao[0]
            self.lista_solucoes.append(melhor.score)
            self.melhor_individuo(melhor)

        print("\nMelhor solução -> G: %s Cromossomo: %s Score: %s" %
              (self.melhor_solucao.geracao,
               self.melhor_solucao.cromossomo,
               self.melhor_solucao.score))
        playerDino = Dino(44,47)
        playerDino.cromossomo = self.melhor_solucao.cromossomo
        playerDino.geracao = self.melhor_solucao.geracao
        gameplay(1,playerDino,60)
        return self.melhor_solucao.cromossomo

def gameplay(bot,playerDino,FPS):
    global high_score
    gamespeed = 4
    gameOver = False
    gameQuit = False
    #playerDino = Dino(44,47)
    new_ground = Ground(-1*gamespeed)
    scb = Scoreboard()
    highsc = Scoreboard(width*0.78)
    counter = 0

    cacti = pygame.sprite.Group()
    pteras = pygame.sprite.Group()
    clouds = pygame.sprite.Group()
    last_obstacle = pygame.sprite.Group()

    Cactus.containers = cacti
    Ptera.containers = pteras
    Cloud.containers = clouds

    retbutton_image,retbutton_rect = load_image('replay_button.png',35,31,-1)
    gameover_image,gameover_rect = load_image('game_over.png',190,11,-1)

    temp_images,temp_rect = load_sprite_sheet('numbers.png',12,1,11,int(11*6/5),-1)
    HI_image = pygame.Surface((22,int(11*6/5)))
    HI_rect = HI_image.get_rect()
    HI_image.fill(background_col)
    HI_image.blit(temp_images[10],temp_rect)
    temp_rect.left += temp_rect.width
    HI_image.blit(temp_images[11],temp_rect)
    HI_rect.top = height*0.1
    HI_rect.left = width*0.73

    while not gameQuit:
        while not gameOver:
            if pygame.display.get_surface() == None:
                #print("Couldn't load display surface")
                gameQuit = True
                gameOver = True
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        gameQuit = True
                        gameOver = True
                    if bot == 0:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                if playerDino.rect.bottom == int(0.98*height):
                                    playerDino.isJumping = True
                                    if pygame.mixer.get_init() != None:
                                        jump_sound.play()
                                    playerDino.movement[1] = -1*playerDino.jumpSpeed
    
                            if event.key == pygame.K_DOWN:
                                if not (playerDino.isJumping and playerDino.isDead):
                                    playerDino.isDucking = True
    
                        if event.type == pygame.KEYUP:
                            if event.key == pygame.K_DOWN:
                                playerDino.isDucking = False
                if bot == 1:
                    action = playerDino.random_action()
                    if action[0] == 1:
                        if playerDino.rect.bottom == int(0.98*height):
                            playerDino.isJumping = True
                            if pygame.mixer.get_init() != None:
                                jump_sound.play()
                            playerDino.movement[1] = -1*playerDino.jumpSpeed
                    if action[1] == 1:
                        if not (playerDino.isJumping and playerDino.isDead):
                            playerDino.isDucking = True
                    
            j = 0
            for c in cacti:
                c.movement[0] = -1*gamespeed
                playerDino.get_observation(c.rect,0)
                if pygame.sprite.collide_mask(playerDino,c):
                    playerDino.isDead = True
                    if pygame.mixer.get_init() != None:
                        die_sound.play()

            for p in pteras:
                p.movement[0] = -1*gamespeed               
                playerDino.get_observation(p.rect,1)
                if pygame.sprite.collide_mask(playerDino,p):
                    playerDino.isDead = True
                    if pygame.mixer.get_init() != None:
                        die_sound.play()

            if len(cacti) < 2:
                if len(cacti) == 0:
                    last_obstacle.empty()
                    last_obstacle.add(Cactus(gamespeed,40,40))
                else:
                    for l in last_obstacle:
                        if l.rect.right < width*0.7 and random.randrange(0,50) == 10:
                            last_obstacle.empty()
                            last_obstacle.add(Cactus(gamespeed, 40, 40))

            if len(pteras) == 0 and random.randrange(0,200) == 10 and counter > 500:
                for l in last_obstacle:
                    if l.rect.right < width*0.8:
                        last_obstacle.empty()
                        last_obstacle.add(Ptera(gamespeed, 46, 40))

            if len(clouds) < 5 and random.randrange(0,300) == 10:
                Cloud(width,random.randrange(height/5,height/2))

            playerDino.update()
            cacti.update()
            pteras.update()
            clouds.update()
            new_ground.update()
            scb.update(playerDino.score)
            highsc.update(high_score)

            if pygame.display.get_surface() != None:
                screen.fill(background_col)
                new_ground.draw()
                clouds.draw(screen)
                scb.draw()
                if high_score != 0:
                    highsc.draw()
                    screen.blit(HI_image,HI_rect)
                cacti.draw(screen)
                pteras.draw(screen)
                playerDino.draw()

                pygame.display.update()
            clock.tick(FPS)

            if playerDino.isDead:
                gameOver = True
                if playerDino.score > high_score:
                    high_score = playerDino.score

            if counter%700 == 699:
                new_ground.speed -= 1
                gamespeed += 1
            playerDino.get_speed(gamespeed)
            counter = (counter + 1)

        if gameQuit:
            break
        gameOver = False
        gameQuit = True
    return playerDino

def main():

    tamanho_populacao = 20
    taxa_mutacao = 0.1
    numero_geracoes = 25 
    taxa_aprendizagem = 0.05
    
    ag = AlgoritmoGenetico(tamanho_populacao)
    ag.resolver(taxa_mutacao,taxa_aprendizagem, numero_geracoes)
    plt.plot(ag.lista_solucoes)
    plt.title("Acompanhamento dos valores")
    plt.show()
    '''
    playerDino = Dino(44,47)
    playerDino.cromossomo = [1.3, -1.5,-1.0, 1.0, 1.0, 1.0]
    gameplay(1,playerDino,60)
    '''
    
main()
pygame.time.delay(2000)
pygame.quit()
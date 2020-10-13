from typing import Tuple
import pygame
import pygame.freetype
from pygame.math import Vector2
import sys     #let  python use your file system
import os      #help python identify your OS
import time
pygame.init()

'''
Variables
'''
display_width = 960
display_height = 600
win = pygame.display.set_mode((display_width,display_height)) #display size
forwardx = 560
backwardx = 100
lvl = 1
world = 0
color= 'Pink'
fps   = 27  # frame rate
ani   = 3   # animation cycles  
shootLoop = 0
bullets = []
bgcolor = (0, 255, 0)
black = (0,0,0)
white = (255, 255, 255)
options = []
options_rect = []
hearts = [pygame.image.load('1hearts.png'), pygame.image.load('2hearts.png'), pygame.image.load('3hearts.png')]

def text_objects(text, font, color):
        textSurface = font.render(text, True, color)
        return textSurface, textSurface.get_rect()

def message_display(text,tx,ty, color,fontsize):
    Textfont = pygame.font.Font('PressStart2P-Regular.ttf', fontsize)
    TextSurf, TextRect = text_objects(text, Textfont, color)
    TextRect.center = (tx,ty)
    win.blit(TextSurf, TextRect)
    return TextRect

class Option(pygame.sprite.Sprite):
        """
        Choosen option
        """
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.walk = []
            img = pygame.image.load(os.path.join('images', 'choose.png'))
            self.walk.append(img)
            self.image = self.walk[0]
            self.rect = self.image.get_rect()
            self.rect.x = display_width/2
            self.rect.y = 184

        def pick(self, options):
            for i in range(0,len(options)):
                options_rect.append(message_display(options[i],display_width/2, 200 + 64*i, black, 32))
                if options_rect[i].top <= self.rect.y <= options_rect[i].bottom:
                    message_display(options[i],display_width/2, 200 + 64*i, white,32)   

def main(lvl):
    '''
    Objects
    '''
    class player(pygame.sprite.Sprite):
        """
        Spawn a player
        """  
        def __init__(self,pos, *groups):
            pygame.sprite.Sprite.__init__(self)
            super().__init__(*groups)
            self.move = Vector2(0,0)
            self.frame = 0
            self.health = 10
            self.walk = []
            self.up = False
            self.down = True
            self.neg = 1
            self.jumping = False
            self.virus = False
            self.score = 0
            self.stars = 0
            self.map_pos = 0
            self.facing = 'right'
            self.position = Vector2(pos)
            for i in range (1,10):
                img = pygame.image.load(os.path.join('images', color +'R'+str(i)+'.png'))
                img.convert_alpha()
                img.set_colorkey(bgcolor)
                self.walk.append(img)
            self.image = self.walk[0]
            self.rect = self.image.get_rect(center=pos)
            self.hitbox = self.rect.inflate(-18,-5)
            
        def gravity(self):
            if self.down:
                self.move.y += 1
            
        def control(self, x):
            """
            control player movement
            """
            self.move.x += x

        def update(self):
            """
            Update position
            """
            #moving left
            if self.map_pos > 0:
                if self.move.x < 0:
                    if self.up is False:
                        self.down = True #turn gravity on
                    self.frame += 1
                    if self.frame > 3*ani:
                        self.frame = 0
                    self.image = pygame.transform.flip(self.walk[self.frame//ani], True, False)
                    self.map_pos -= 10
                    self.facing = 'left'
                    self.position.x += self.move.x
                    self.rect.centerx = self.position.x
                    self.hitbox.centerx = self.position.x

            #moving right

            if self.move.x > 0:
                if self.up is False:
                    self.down = True #turn gravity on
                self.frame += 1
                if self.frame > 3*ani:
                    self.frame = 0
                self.image = self.walk[self.frame//ani]
                self.map_pos += 10
                self.facing = 'right'
                self.position.x += self.move.x
                self.rect.centerx = self.position.x
                self.hitbox.centerx = self.position.x    
            
            if self.move.x == 0:
                if self.facing == 'right':
                    self.image = self.walk[0]
                else:
                    self.image = pygame.transform.flip(self.walk[0], True, False)

            #hitting enemies

            hit_list = pygame.sprite.spritecollide(self, human_list, True, collided)
            
            for enemy in hit_list:
                if self.hitbox.bottom <= enemy.hitbox.bottom and enemy.hitbox.left <= self.position.x <= enemy.hitbox.right:
                    self.score += 5
                else:
                    self.health -= 1
                    self.map_pos -= self.position.x
                    self.position.x = 0
                    self.position.y = 30
                    self.score -= 2
                     
            
            #jumping

            ground_hit_list = pygame.sprite.spritecollide(self, ground_list, False, collided)
            
            for g in ground_hit_list:
                self.move.y = 0
                self.position.y = g.rect.top - self.hitbox.height/2
                self.down = False
                self.jumping = False
                g.hitbox.center = g.position

            if self.hitbox.y > display_height:
                self.health -= 1
                self.position.x = tx
                self.position.y = ty
            
            
            plat_hit_list = pygame.sprite.spritecollide(self, plat_list, False, collided)

            for p in plat_hit_list:
                self.down = False
                self.move.y = 0
                if p.type == 'Box1.png' or p.type == 'Box2.png':
                    if self.facing == 'right' and self.position.x < p.hitbox.left:
                        self.position.x = p.rect.left - self.hitbox.width/2
                    elif self.facing == 'left' and self.position.x > p.hitbox.right:
                        self.position.x = p.rect.right + self.hitbox.width/2  

                if self.hitbox.bottom <= p.hitbox.bottom:
                    self.position.y = p.rect.top - self.hitbox.height/2
                else:
                    self.move.y = 6
                self.jumping = False
            
            if self.up:
                self.move.y += 1
                if self.move.y >= 0:
                    self.neg = 1
                    self.up = False
                    self.down = True
                    self.move.y = 0
          
            self.position.y += (self.move.y**2)*0.3*self.neg
            self.rect.center = self.position
            self.hitbox.center = self.position
             
            #power-up hits
            power_up_hit_list = pygame.sprite.spritecollide(self, power_up_list, True, collided)

            for pu in power_up_hit_list:
                if pu.type == 'powervirus.png':
                    self.virus = True
                    self.score += 3
                if pu.type == 'coinBronze.png':
                    self.score += 1
                if pu.type == 'coinSilver.png':
                    self.score += 3
                if pu.type == 'coinGold.png':
                    self.score += 5
                if pu.type == 'End.png':
                    map()

        def jump(self):
            if self.jumping is False:
                self.up = True
                self.down = False
                self.jumping = True
                self.move.y = -13
                self.neg = -1
        

    class power_up(pygame.sprite.Sprite):
        '''
        throw power up
        '''
        def __init__(self,x,y,radius,color,facing, *groups):
            pygame.sprite.Sprite.__init__(self)
            super().__init__(*groups)
            self.walk = []
            self.x = x
            self.y = y
            self.radius = radius
            self.color = color
            self.facing = facing
            self.vel = 8 * facing

        def draw(self, win):
            pygame.draw.circle(win,self.color, (self.x,self.y), self.radius)

    class enemy(pygame.sprite.Sprite):
        """
        Spawn an enemy
        """
        def __init__(self, pos, end, img_nr, char, speed=(0,0), *groups):
            pygame.sprite.Sprite.__init__(self)
            super().__init__(*groups)
            self.walk = []
            for i in range(0,img_nr):
                img = pygame.image.load(os.path.join('images', char + str(i) + '.png'))
                img.convert_alpha()
                img.set_colorkey(bgcolor)
                self.walk.append(img)
            self.image = self.walk[0]
            self.rect = self.image.get_rect(center=pos)
            self.hitbox = self.rect.inflate(0,0)
            self.position = Vector2(pos)
            self.counter = 0
            self.frame = 0
            self.directionx = 1
            self.start = pos[0]
            self.end = end
            self.speed = Vector2(speed)

        def update(self):
            '''
            enemy movement
            ''' 
            self.position.x += self.speed.x*self.directionx
            if self.position.x >= self.end - self.hitbox.width/2:
                self.directionx = -1
            if self.position.x <= self.start + self.hitbox.width/2:
                self.directionx = 1
            if self.directionx == -1:
                self.image = self.walk[self.frame]
            else:
                self.image = pygame.transform.flip(self.walk[self.frame], True, False)
            if self.frame < len(self.walk)-1:
                self.frame += 1
            else:
                self.frame = 0
            self.position.y += self.speed.y
            if self.position.y > display_height:
                self.position.y = 0
            if self.position.y < 0:
                self.position.y = display_height
            (self.hitbox.centerx,self.hitbox.centery) = self.position
            (self.rect.centerx,self.rect.centery) = self.position

    class Platform(pygame.sprite.Sprite):
        def __init__(self, xloc, yloc,imgw, imgh, img, movement=False, speed=(0,0), *groups):
            pygame.sprite.Sprite.__init__(self)
            super().__init__(*groups)
            self.type = img
            self.movement = movement
            self.image  = pygame.image.load(os.path.join('images', self.type))
            self.image.convert_alpha()
            self.image.set_colorkey(bgcolor)
            self.position = Vector2((xloc, yloc))
            self.rect = self.image.get_rect(center=(xloc, yloc))
            self.speed = Vector2(speed)
            if img[:4] == 'coin':
                self.hitbox = self.rect.inflate(-34,-34)
            elif img[:6] == 'shroom':
                self.hitbox = self.rect.inflate(0,-30)
            elif img[:4] == 'stem':
                self.hitbox = self.rect.inflate(-40,0)
            else:
                self.hitbox = self.rect.inflate(0,0)
        
        def update(self):
            '''
            platform movement
            '''

            if self.movement:
                self.position.y += self.speed.y
                if self.position.y > display_height:
                    self.position.y = 0
                if self.position.y < 0:
                    self.position.y = display_height
                (self.hitbox.centerx,self.hitbox.centery) = self.position
                (self.rect.centerx,self.rect.centery) = self.position
        

    class Level():
        def bad (lvl, eloc, *groups):
            human_list = pygame.sprite.Group()
            if lvl == 1:
                for enemies in eloc:
                    if enemies[0] == 3360 or enemies[0] == 4128:
                        y = 3
                    elif enemies[0] == 3744 or enemies[0] == 4512:
                        y = -3
                    else:
                        y = 0
                    human = enemy((enemies[0], enemies[1]), enemies[2], enemies[3], enemies[4],(3,y), *groups)
                    human_list.add(human)
            if lvl == 2:
                for enemies in eloc:
                    human = enemy((enemies[0], enemies[1]), enemies[2], enemies[3], enemies[4],(3,0), *groups)
                    human_list.add(human)

            return human_list
        
        def power_ups(lvl, ploc, *groups):
            power_up_list = pygame.sprite.Group()
            if lvl == 1:
                for power_up in ploc:
                    power = Platform(power_up[0], power_up[1], 32, 32, power_up[2], False,(0,0), *groups)
                    power_up_list.add(power)
            if lvl == 2:
                print("Level" + str(lvl))
            return power_up_list

        def ground(lvl,gloc,tx,ty, *groups):
            ground_list = pygame.sprite.Group()
            i= 0
            if lvl == 1:
                while i<= len(gloc)-1:
                    ground = Platform(gloc[i],display_height-ty, tx, ty, 'platform001.png',False,(0,0), *groups)
                    if ground.position.x <= 1000 or 1320 <= ground.position.x <= 3264  or ground.position.x >= 4800:
                        ground_list.add(ground)
                    i = i+1

            if lvl == 2:
                while i<= len(gloc)-1:
                    ground = Platform(gloc[i],display_height-ty, tx, ty, 'platform001.png',False,(0,0), *groups)
                    ground_list.add(ground)
                    i = i+1
            return ground_list

        def platform(lvl, ploc, tx, ty, *groups):
            plat_list = pygame.sprite.Group()
            i = 0
            if lvl == 1:
                while i <= len(ploc)-1:
                    j=0
                    while j<= ploc[i][2]:
                        if ploc[i][0] == 3392 or ploc[i][0] == 4160:
                            y = 3
                        elif ploc[i][0] == 3776 or ploc[i][0] == 4544:
                            y = -3
                        else:
                            y = 0
                        plat = Platform((ploc[i][0]+j*tx), ploc[i][1], tx, ty, ploc[i][3], ploc[i][4],(0,y),*groups)
                        plat_list.add(plat)
                        j += 1
                    i += 1

            if lvl == 2:
                while i <= len(ploc)-1:
                    j=0
                    while j<= ploc[i][2]:
                        plat = Platform((ploc[i][0]+j*tx), ploc[i][1], tx, ty, ploc[i][3], ploc[i][4],(0,0),*groups)
                        plat_list.add(plat)
                        j += 1
                    i += 1

            return plat_list
 
    def redrawGameWindow():
        win.blit(backdrop, backdropbox)
        all_sprites.draw(win)
        
        for sprite in all_sprites:
            # Draw rects and hitboxes.
            pygame.draw.rect(win, (0, 230, 0), sprite.rect, 2)
            pygame.draw.rect(win, (250, 30, 0), sprite.hitbox, 2)
        
        message_display('lives: '+ str(alien.health),65, 20, black, 15)
        message_display('score: '+ str(alien.score), 65, 40, black, 15)
        #human_list.draw(win)
        for bullet in bullets:
            bullet.draw(win)
        pygame.display.update()
        pygame.display.flip()
    def collided(sprite, other): 
            """
            Check if the hitboxes of the two sprites collide
            """
            return sprite.hitbox.colliderect(other.hitbox)

    def paused(pause):
        menu = 0
        choose = Option()
        choose_list = pygame.sprite.Group()
        choose_list.add(choose)
        while pause:
            options = ['Continue','Map','Main Menu','Quit']
            choose.pick(options)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        if choose.rect.y < (184 + (len(options)-1)*64):
                            choose.rect.y += 64
                            menu += 1
                        else:
                            choose.rect.y = 184
                            menu = 0
                    if event.key == pygame.K_UP:
                        if choose.rect.y > 184:
                            choose.rect.y -= 64
                            menu -= 1
                        else:
                            choose.rect.y = 184 + (len(options)-1)*64 
                            menu = len(options)-1 
                    if event.key == pygame.K_SPACE:
                        if menu == 0:
                            pause = False
                        elif menu == 1:
                            map()
                        elif menu == 2:
                            main_menu()
                        else:
                            pygame.quit()
                            quit()
            pygame.display.update()
            clock.tick(15)

    '''
    Set-up
    '''
    run = True
    if lvl == 1:
        backdrop = pygame.image.load(os.path.join('images','background.png'))
    if lvl == 2:
        backdrop = pygame.image.load(os.path.join('images','bg_mushroom.png'))
    backdropbox = win.get_rect()
    clock = pygame.time.Clock()
    pygame.display.set_caption("Back Home") #game name
    all_sprites = pygame.sprite.Group()
    alien = player((20,30),all_sprites)
    steps = 10 # how many pixels to move

    #enemies (x, y, end, img numbers, character image file)
    eloc = [] 
    if lvl == 1:
        eloc.append([200,392.5,456, 2,'snailWalk'])
        eloc.append([584,392.5,840, 2, 'snailWalk'])
        eloc.append([1032,display_height-207.5,1096, 2,'snailWalk'])
        for a in range(0,9):
            eloc.append([1952 + 96*a,display_height-64-14,2016 + 96*a, 2,'slimeWalk'])
        for a in range(0,4):
            for b in range(0,2):
                eloc.append([3360 + 384*a, 103 + 300*b,(3360 + 384*a)+192, 2,'snailWalk'])
    if lvl == 2:
        eloc.append([413,display_height-195,623, 1,'ladyBug'])
        pass
    human_list = Level.bad(lvl, eloc,all_sprites)

    #ground
    gloc = []
    tx   = 64
    ty   = 32
    
    if lvl == 1:
        i = -10
        while i <= (display_width/tx)+tx:
            gloc.append(i*tx)
            i += 1
    if lvl == 2:
        for i in range(-5,8):
            gloc.append(i*tx)  
        for i in range(62,79):
            gloc.append(i*tx)
    ground_list = Level.ground(lvl, gloc, tx, ty, all_sprites)

    #platform
    ploc = []
    if lvl == 1:
        ploc.append((232, display_height-ty-128, 3,'platform011.png', False))
        ploc.append((424, display_height-ty-256, 3,'platform011.png', False))
        ploc.append((616,display_height-ty-128, 3,'platform011.png', False))
        for a in range(1,5):
            ploc.append((1000 + 64*a, display_height-ty-128*a,0,'platform011.png', False))
        for a in range(0,5):
            for b in range(0+a,10-a):
                ploc.append((1936 + 96*b,display_height-80-32*a,0,'Box1.png', False))
        for a in range(0,3):
            ploc.append((3136 + 64*a, display_height-96-64*a,2-a,'Box2.png', False))
        for a in range(0,4):
            for b in range(1,5):
                ploc.append((3392 + 384*a, 150*b,2,'platform011.png', True))
    if lvl == 2:
        ploc.append((518,display_height-35,0,'stemVine.png', True))
        ploc.append((518,display_height-105,0,'stemVine.png', True))
        ploc.append((518,display_height-145,0,'shroomRedAltMid.png', True))
        ploc.append((448,display_height-145,0,'shroomRedAltLeft.png', True))
        ploc.append((588,display_height-145,0,'shroomRedAltRight.png', True))
    plat_list = Level.platform(lvl, ploc, tx, ty, all_sprites)
    #bulletSound = pygame.mixer.Sound('bullet.mp3') tem que ser em formato WAV pra funcionar
    #music = pygame.mixer.music.load('music.mp3')
    #pygame.mixer.music.play(-1)

    #power-ups
    ploc = []
    if lvl == 1:
        for coin in range(0,4):
            ploc.append([232+64*coin, display_height-ty-128-67,'coinBronze.png'])
            ploc.append([616+64*coin, display_height-ty-128-67,'coinBronze.png'])
            ploc.append([424+64*coin, display_height-ty-256-67,'coinBronze.png'])
        ploc.append([1000 + 64*2,display_height-ty-128*2-67,'coinBronze.png'])
        ploc.append([1000 + 64*3,display_height-ty-128*3-67,'coinSilver.png'])
        ploc.append([1000 + 64*4,display_height-ty-128*4-67,'coinGold.png'])
        for coin in range(0,9):
            ploc.append([1320 + 32*coin, display_height-ty-64*(9-coin),'coinGold.png'])
        ploc.append([tx*((display_width/tx)+tx),display_height-ty-70,'End.png'])
    if lvl == 2:
        pass
    power_up_list = Level.power_ups(lvl,ploc, all_sprites)
    pause = False

    '''
    mainloop
    '''
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == ord('a'):
                    alien.control(-steps)
                if event.key == pygame.K_RIGHT or event.key == ord('d'):
                    alien.control(steps)
                if event.key == pygame.K_UP or event.key == ord('w'):
                    alien.jump()
                if event.key == pygame.K_p:
                    paused(True)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == ord('a'):
                    alien.control(steps)
                if event.key == pygame.K_RIGHT or event.key == ord('d'):
                    alien.control(-steps)
        
        #scroll world forward
        if alien.position.x >= forwardx:
            scroll = alien.position.x - forwardx
            alien.position.x = forwardx
            alien.rect.centerx = alien.position.x
            alien.hitbox.centerx = alien.position.x
            for p in plat_list:
                p.position.x -= scroll
                p.rect.centerx = p.position.x
                p.hitbox.centerx = p.position.x
            for g in human_list:
                g.start -= scroll
                g.end -= scroll
                g.position.x -= scroll
                g.rect.centerx = g.position.x
                g.hitbox.centerx = g.position.x
            for ground in ground_list:
                ground.position.x -= scroll
                ground.rect.centerx = ground.position.x
                ground.hitbox.centerx = ground.position.x
            for pu in power_up_list:
                pu.position.x -= scroll
                pu.rect.centerx = pu.position.x
                pu.hitbox.centerx = pu.position.x

        #scroll world backward
        if alien.position.x <= backwardx:
            scroll = backwardx - alien.position.x
            alien.position.x = backwardx
            alien.rect.centerx = alien.position.x
            alien.hitbox.centerx = alien.position.x
            for p in plat_list:
                p.position.x += scroll
                p.rect.centerx = p.position.x
                p.hitbox.centerx = p.position.x
            for g in human_list:
                g.start += scroll
                g.end += scroll
                g.position.x += scroll
                g.rect.centerx = g.position.x
                g.hitbox.centerx = g.position.x
            for ground in ground_list:
                ground.position.x += scroll
                ground.rect.centerx = ground.position.x
                ground.hitbox.centerx = ground.position.x
            for pu in power_up_list:
                pu.position.x += scroll
                pu.rect.centerx = pu.position.x
                pu.hitbox.centerx = pu.position.x
        redrawGameWindow() 
        for human in human_list:
            human.update()
        for plat in plat_list:
            plat.update()
        for ground in ground_list:
            if ground.type == 'platform001.png':
                if alien.down == True:
                    offset = Vector2(0,-20)
                    ground.hitbox.center = ground.position + offset
                else:
                    ground.hitbox.center = ground.position
        for plat in plat_list:
            if plat.type == 'platform011.png':
                if alien.down == True:
                    offset = Vector2(0,-15)
                    plat.hitbox.center = plat.position + offset
                else:
                    plat.hitbox.center = plat.position
            if plat.type[:6] == 'shroom':
                if alien.down == True:
                    offset = Vector2(0,-20) 
                else:
                    offset = Vector2(0,-15)
                plat.hitbox.center = plat.position + offset



        alien.update() #update position   
        alien.gravity()
        clock.tick(fps)
    pygame.quit()


#main menu

def main_menu():
    run = True
    menu = [0,0]
    next = 1
    pygame.mouse.set_visible(False)
    players = 0
    choose = Option()
    choose_list = pygame.sprite.Group()
    choose_list.add(choose)
    character = []
    while run:  
        win.blit(backdrop, backdropbox)
        if menu [0] == 0:
            options = ['Start','Load Game','Settings','Quit']
            choose.pick(options)
                          
        if menu [0] == 1:
            if menu[1] == 0:
                options = ['1 Player','2 Players', 'Back']
            elif menu[1] == 1 or menu[1] == 2 :
                options = ['Blue Alien','Green Alien', 'Pink Alien','Back']
            choose.pick(options)
        
        if menu[0] == 2:
            options = ['Load 1','Load 2', 'Load 3', 'Back']
            choose.pick(options)
        
        if menu[0] == 3:
            if menu[1] == 0:
                options = ['Volume', 'Keys Select', 'Back']
            if menu[1] == 1:
                options = ['Music', 'SFX', 'Back']
            if menu[1] == 2:
                options = ['Left', 'Right', 'Jump', 'Power-UP', 'Back']
            choose.pick(options)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()     
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    if choose.rect.y < (184 + (len(options)-1)*64):
                        choose.rect.y += 64
                        next += 1
                    else:
                        choose.rect.y = 184
                        next = 1
                if event.key == pygame.K_UP:
                    if choose.rect.y > 184:
                        choose.rect.y -= 64
                        next -= 1
                    else:
                        choose.rect.y = 184 + (len(options)-1)*64 
                        next = len(options) 
                if event.key == pygame.K_SPACE:
                    if menu[0] == 0:
                        map()
                    else:
                        if next == len(options):
                            if menu[1] == 0:
                                menu[0] = 0
                            else:
                                menu[1] = 0
                        else:
                            if menu[0] == 1:
                                menu[1] == next
                                

                    next = 1
                    choose.rect.y = 184    
        choose_list.draw(win)
        pygame.display.update()

def map():
    backdrop = pygame.image.load(os.path.join('images','map_background.png'))
    class Option(pygame.sprite.Sprite):
        """
        Choose World and level
        """
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.walk = []
            img = pygame.image.load(os.path.join('images',color + 'badge.png'))
            self.walk.append(img)
            self.image = self.walk[0]
            self.rect = self.image.get_rect()
            self.rect.x = 30
            self.rect.y = display_height/2
        
        def pick(self):
            for i in range(1,6):
                levels_rect.append(message_display('level ' + str(i), 53.5 + 94*(i-1), 86.5 , black, 10))
                if levels_rect[i-1].left <= self.rect.x <= levels_rect[i-1].right :
                    lvl = i
                    message_display('level ' + str(i), 53.5 + 94*(i-1), 86.5 , white, 10)
    run = True
    pygame.mouse.set_visible(False)
    choose = Option()
    choose_list = pygame.sprite.Group()
    choose_list.add(choose)
    levels_rect = []
    choose.rect.y = 26.5 + 53*world
    unlock = 0
    while run:
        win.blit(backdrop, backdropbox)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    if choose.rect.x < 405:
                        choose.rect.x += 94
                    else:
                        choose.rect.x = 30

                if event.key == pygame.K_LEFT:
                    if  choose.rect.x >30:
                        choose.rect.x -= 94
                    else:
                        choose.rect.x = 406
                if event.key == pygame.K_SPACE:
                    main(lvl)
        for l in range(0,11):
            if choose.rect.x == 30+94*l:
                lvl = l+1
        for w in range(0,6):
            message_display('World ' + str(5-w), display_width/2, 10 + 100*w , black, 10)
        choose_list.draw(win)
        choose.pick()
        pygame.display.update()

if __name__ == '__main__':
    main(2)


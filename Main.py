#This is Christian's change
#This is Megaladon"s
#git-cola test
#Important
VERSION_NUMBER = "v0.3.0 Beta"

#Imports
import pygame,sys,os,math,time,pygame.gfxdraw,random,pygame.mixer
from pygame.locals import *




#Constants
PGNAME = "MiniWorld"
BGCOLOR = (255,255,255)
FPSCOLOR = (64,64,64)
FPS_MAX = 90
DATA_DIR = "Data"
BLOCKSIZE = 16


def centerImage(SCREEN_W, SCREEN_H, IMG_W, IMG_H): 

  return ((SCREEN_W / 2) - (IMG_W / 2), (SCREEN_H / 2) - (IMG_H / 2))


#Inits
pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()

hit = pygame.mixer.Sound("Data/Other/lightsaber.wav")
miss = pygame.mixer.Sound("Data/Other/swoosh.wav")

#Screen
STARTSCREEN_W = 1001
STARTSCREEN_H= 552
screen = pygame.display.set_mode((STARTSCREEN_W,STARTSCREEN_H))
pygame.display.set_caption(PGNAME)
pygame.display.set_icon(pygame.image.load("Data/Graphics/EIcon.png"))
screen.fill(BGCOLOR)

screen.blit(pygame.transform.scale(pygame.image.load("Data/Graphics/QgVDt1l.jpg"),(1001,552)),(0,0))

pygame.display.update()

time.sleep(2)

screen.fill(BGCOLOR)
GIRL_W = 500
GIRL_H = 497

centercoords = centerImage(STARTSCREEN_W, STARTSCREEN_H, GIRL_W, GIRL_H)
screen.blit(pygame.transform.scale(pygame.image.load("Data/Graphics/hot-fit-girls-women-7.jpg"),(500,497)),centercoords)

pygame.display.update()

time.sleep(3)

#Functions
#Make a textured background
def makeTextureBG(texture,size):
    texSurf = pygame.surface.Surface(size)
    pygame.gfxdraw.textured_polygon(texSurf,((0,0),
                                             (size[0],0),
                                             size,
                                             (0,size[1]))
                                             ,texture,0,0)
    return texSurf

#Distance formula
def distance(pt1,pt2):
    return math.sqrt(((pt2[0]-pt1[0])**2)+((pt2[1]-pt1[1])**2))

#Classes
#Player
class Player(pygame.sprite.Sprite):

    #Init
    def __init__(self,x,y,image):
        #Call the parent init function
        pygame.sprite.Sprite.__init__(self)

        #Pos,image,rect
        self.pos = [x,y]
        self.velocity = [0,0]
        self.image = image
        
        self.rect = pygame.rect.Rect(self.pos[0],self.pos[1]+12,16,4)

        #Inventory
        self.inventory = [Item(spriteItemWoodSword,15,30,"Wooden Sword"),
                          Item(spriteItemStoneSword,30,90,"Stone Sword"),
                          Item(spriteItemIronSword,45,230,"Iron Sword"),
                          Item(spriteItemDiamondSword,50,500,"Diamond Sword"),
                          0,
                          0,
                          0,
                          0]
        self.selected = 0

        #Life
        self.life = 0

        #Stats
        self.hp = 90

        #How fast the player decelerates
        self.velocityDecay = [2,2]

    #Update
    def update(self):
        #Globals
        global restart

        #Increase lifetime
        self.life += 1
        
        #Get x and y to make code more readable
        x = self.pos[0]
        y = self.pos[1]
        
        #Basically saying it is inside the screen
        if x > 0 and x < screen.get_width() - 16 and y > 0 and y < screen.get_height() - 16:

            #Follow velocity
            #Increase the y and update rect
            self.pos[1] += self.velocity[1]
            self.rect = pygame.rect.Rect(self.pos[0],self.pos[1]+12,16,4)

            #If colliding, go back
            if pygame.sprite.spritecollide(self,walls,False):
                self.pos[1] -= self.velocity[1]

            #Increase the x and update rect
            self.pos[0] += self.velocity[0]
            self.rect = pygame.rect.Rect(self.pos[0],self.pos[1]+12,16,4)

            #If colliding, go back
            if pygame.sprite.spritecollide(self,walls,False): 
                self.pos[0] -= self.velocity[0]
                
        else:
            restart = 1

        #Touching mobs
        collisions = pygame.sprite.spritecollide(self,mobs,0)

        for mob in collisions:
            if random.randint(0,100) < 40:
                self.hp -= mob.damage

        #Check health
        if self.hp <= 0:
            restart = 1

        #Draw health
        scaledHp = self.hp/90*24

        pygame.draw.rect(screen,(192,0,0),(self.pos[0] - 4,self.pos[1] - 6,24,4),1)
        pygame.draw.rect(screen,(192,0,0),(self.pos[0] - 4,self.pos[1] - 6,scaledHp,4))

        #Check inventory
        for item in self.inventory:
            if item != 0:
                if item.life <= 0:
                    self.inventory.remove(item)
                    self.inventory.append(0)

        #Change Image
        if self.life % 3 == 0:
            if self.velocity[1] > 0:
                self.image = spritePlayerD
            if self.velocity[1] < 0:
                self.image = spritePlayerU
            if self.velocity[0] > 0:
                self.image = spritePlayerR
            if self.velocity[0] < 0:
                self.image = spritePlayerL

        #Decrease the velocity
        for i in range(2):
            if self.velocity[i] > 0:
                self.velocity[i] -= self.velocityDecay[i]
            if self.velocity[i] < 0:
                self.velocity[i] += self.velocityDecay[i]

        screen.blit(self.image,self.pos)

#Mob
class Mob(pygame.sprite.Sprite):

    #Init
    def __init__(self,x,y,images,speed,damage,hp,behavior):
        #Call the parent init function
        pygame.sprite.Sprite.__init__(self)

        #Pos,image,rect
        self.pos = [x,y]
        self.velocity = [0,0]
        self.images = images
        self.image = images[0]
        
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos

        #Life
        self.life = 0

        #Behavior - chase player or not
        self.behavior = behavior

        #How fast the mob decelerates
        self.velocityDecay = [speed,speed]

        #Stats
        self.speed = speed
        self.damage = damage
        self.hp = hp
        self.maxHp = hp

        #Add to group
        self.add(mobs)

    #Update
    def update(self):
        #Globals
        global restart

        if self.behavior == 1:
            #AI
            if distance(self.pos,player.pos) <= 100:
                if player.pos[0] > self.pos[0]:
                    self.velocity[0] = self.speed
                if player.pos[0] < self.pos[0]:
                    self.velocity[0] = -self.speed
                    
                if player.pos[1] > self.pos[1]:
                    self.velocity[1] = self.speed
                if player.pos[1] < self.pos[1]:
                    self.velocity[1] = -self.speed

        if self.behavior == 0 and random.randint(0,100) < 40:
            #Move randomly
            self.velocity[1] = random.randint(0,4)-2
            self.velocity[0] = random.randint(0,4)-2

        #Increase lifetime
        self.life += 1
        
        #Get x and y to make code more readable
        x = self.pos[0]
        y = self.pos[1]
        
        #Basically saying it is inside the screen
        if x > 0 and x < screen.get_width() - 16 and y > 0 and y < screen.get_height() - 16:

            #Follow velocity
            #Increase the y and update rect
            self.pos[1] += self.velocity[1]
            self.rect.topleft = self.pos

            #If colliding, go back
            if pygame.sprite.spritecollide(self,walls,False):
                self.pos[1] -= self.velocity[1]

            #Increase the x and update rect
            self.pos[0] += self.velocity[0]
            self.rect.topleft = self.pos

            #If colliding, go back
            if pygame.sprite.spritecollide(self,walls,False): 
                self.pos[0] -= self.velocity[0]
                
        else:
            restart = 1

        #If attacked
        if ((pygame.mouse.get_pos()[0] > self.pos[0] and pygame.mouse.get_pos()[0] < self.pos[0] + self.image.get_width() and\
           pygame.mouse.get_pos()[1] > self.pos[1] and pygame.mouse.get_pos()[1] < self.pos[1] + self.image.get_height() and\
           pygame.mouse.get_pressed()[2]) or attack) and distance(self.pos,player.pos) < 50:

            if player.inventory[player.selected] != 0:
                self.hp -= player.inventory[player.selected].damage
                
                player.inventory[player.selected].life -= 1

            else:
                self.hp -= 5
 
	    hit.play()

        #Check health
        if self.hp <= 0:
            self.kill()

        #Draw health
        scaledHp = self.hp/self.maxHp*24

        pygame.draw.rect(screen,(192,0,0),(self.pos[0] - 4,self.pos[1] - 6,24,4),1)
        pygame.draw.rect(screen,(192,0,0),(self.pos[0] - 4,self.pos[1] - 6,scaledHp,4))    

        #Change Image
        if self.life % 3 == 0:
            if self.velocity[1] > 0:
                self.image = self.images[0]
            if self.velocity[1] < 0:
                self.image = self.images[1]
            if self.velocity[0] > 0:
                self.image = self.images[2]
            if self.velocity[0] < 0:
                self.image = self.images[3]
                
        #Decrease the velocity
        for i in range(2):
            if self.velocity[i] > 0:
                self.velocity[i] -= self.velocityDecay[i]
            if self.velocity[i] < 0:
                self.velocity[i] += self.velocityDecay[i]

        screen.blit(self.image,self.pos)
        
#Tile
class Tile(pygame.sprite.Sprite):

    def __init__(self,x,y,image):

        pygame.sprite.Sprite.__init__(self)
        self.pos = [x,y]
        self.image = image
        
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        
        self.add(tiles)

    def update(self):
            
        screen.blit(self.image,self.pos)

#Wall
class Wall(pygame.sprite.Sprite):

    def __init__(self,x,y,image):

        pygame.sprite.Sprite.__init__(self)
        self.pos = [x,y]
        self.image = image
        
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        
        self.add(walls)

    def update(self):
            
        screen.blit(self.image,self.pos)

#Item
class Item(object):

    def __init__(self,image,damage,life,identification = "No item id!"):

        #Image and ID
        self.image = image
        self.id = identification

        #Stats
        self.damage = damage
        self.life = life

#Load Resources
#cd Data
os.chdir(DATA_DIR)

font = pygame.font.Font("Other/PressStart2P.ttf",20)
spritePlayerL = pygame.image.load("Graphics/MPlayerL.png")
spritePlayerR = pygame.image.load("Graphics/MPlayerR.png")
spritePlayerU = pygame.image.load("Graphics/MPlayerU.png")
spritePlayerD = pygame.image.load("Graphics/MPlayerD.png")
spriteMobBugs = [pygame.image.load("Graphics/MBugR.png"),pygame.image.load("Graphics/MBugL.png"),pygame.image.load("Graphics/MBugD.png"),pygame.image.load("Graphics/MBugU.png")]
spriteTileGrass = pygame.image.load("Graphics/TGrass.png")
spriteTileStone = pygame.image.load("Graphics/TStone.png")
spriteTileRug = pygame.image.load("Graphics/TRug.png")
spriteWallBlock = pygame.image.load("Graphics/WBlock.png")
spriteWallTop = pygame.image.load("Graphics/WTop.png")
spriteWallFence = pygame.image.load("Graphics/WFence.png")
spriteWallWater = pygame.image.load("Graphics/WWater.png")
spriteBGK = makeTextureBG(pygame.image.load("Graphics/BGK.png"),screen.get_size())
spriteBGW = makeTextureBG(pygame.image.load("Graphics/BGW.png"),screen.get_size())
spriteBGP = pygame.image.load("Graphics/BGP.png")
spriteFrame = pygame.image.load("Graphics/GItemFrame.png")
spriteFrameSelected = pygame.image.load("Graphics/GItemFrameSelected.png")
spriteItemWoodSword = pygame.image.load("Graphics/IWoodenSword.png")
spriteItemStoneSword = pygame.image.load("Graphics/IStoneSword.png")
spriteItemIronSword = pygame.image.load("Graphics/IIronSword.png")
spriteItemDiamondSword = pygame.image.load("Graphics/IDiamondSword.png")

#Cursor
CURSOR = (               #sized 24x24
  "           XX           ",
  "           XX           ",
  "           XX           ",
  "           XX           ",
  "         ......         ",
  "       ..oooooo..       ",
  "      .oo  XX  oo.      ",
  "     .o    XX    o.     ",
  "     .o    XX    o.     ",
  "    .o     XX     o.    ",
  "    .o     XX     o.    ",
  "XXXX.oXXXXXXXXXXXXo.XXXX",
  "XXXX.oXXXXXXXXXXXXo.XXXX",
  "    .o     XX     o.    ",
  "    .o     XX     o.    ",
  "     .o    XX    o.     ",
  "     .o    XX    o.     ",
  "      .oo  XX  oo.      ",
  "       ..oooooo..       ",
  "         ......         ",
  "           XX           ",
  "           XX           ",
  "           XX           ",
  "           XX           ",
)

cursor = pygame.cursors.compile(CURSOR)

pygame.mouse.set_cursor((24,24),(12,12),cursor[0],cursor[1])

#Game variables
levelNumber = 1

#Screen
screen = pygame.display.set_mode((800,600))

#Add version number
#Add version Number
spriteBGP.blit(font.render(str(VERSION_NUMBER),0,(192,192,192)),(300,200))

#Blit BG
screen.blit(spriteBGP,(0,0))
pygame.display.update()

#Startup loop
flag = 0
while True:

    for event in pygame.event.get():

        #Did the user quit?
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        #Did the user press space?
        if event.type == KEYDOWN:
            if event.unicode == " ":
                flag = 1

    if flag:
        break

#Main Loop
while True:

    #Set up variables
    restart = 0

    #Set up groups
    walls = pygame.sprite.Group()
    tiles = pygame.sprite.Group()
    mobs = pygame.sprite.Group()

    #Load level
    limage = pygame.image.load("Levels/"+str(levelNumber)+".png")

    #Add the contents of the image to the level
    for j in range(limage.get_height()):
        
        for i in range(limage.get_width()):
            
            px = limage.get_at((i,j))
            
            if px[0] == 192:           #Grass
                t = Tile(i*BLOCKSIZE,j*BLOCKSIZE,spriteTileGrass)
            if px[0] == 128:           #Stone
                t = Tile(i*BLOCKSIZE,j*BLOCKSIZE,spriteTileStone)
            if px[0] == 255:           #Rug
                t = Tile(i*BLOCKSIZE,j*BLOCKSIZE,spriteTileRug)

            if px[1] == 255:           #Block Wall
                w = Wall(i*BLOCKSIZE,j*BLOCKSIZE,spriteWallBlock)
            if px[1] == 192:           #Block Top
                w = Wall(i*BLOCKSIZE,j*BLOCKSIZE,spriteWallTop)
            if px[1] == 128:           #Block Fence
                w = Wall(i*BLOCKSIZE,j*BLOCKSIZE,spriteWallFence)
            if px[1] == 64:            #Block Water
                w = Wall(i*BLOCKSIZE,j*BLOCKSIZE,spriteWallWater)

            if px[2] == 255:
                m = Mob(i*BLOCKSIZE,j*BLOCKSIZE,spriteMobBugs,2,5,20,0)
        

    #Get extra data and theme (.edt)
    edt = open("Levels/"+str(levelNumber)+".edt","r")
    data = edt.readlines()
    edt.close()
                
        
    #BG
    if int(data[1][:2]) == 01:
        mainBG = spriteBGK
    else:
        mainBG = spriteBGW

    #Player
    player = Player(int(data[2][:2]),int(data[3][:2]),spritePlayerU)

    while True:
        #Not Attacking 
        attack = 0
        
        screen.blit(mainBG,(0,0))
        
        for event in pygame.event.get():
            #Did the user quit?
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            #Keydown
            if event.type == KEYDOWN:

                #Selected
                if event.unicode == "a":
                    if player.selected > 0:
                        player.selected -= 1

                if event.unicode == "s":
                    if player.selected < 7:
                        player.selected += 1

                #Deleted
                if event.unicode == "x":
                    player.inventory[player.selected] = 0

                #Attacked
                if event.unicode == " ":
                    attack = 1
                    miss.play()
                    
        #Moved
        if pygame.mouse.get_pressed()[0]:
            mouse = pygame.mouse.get_pos()
            
            if player.pos[0] < mouse[0]:
                player.velocity[0] = 2
            if player.pos[0] > mouse[0]:
                player.velocity[0] = -2
            if player.pos[1] < mouse[1]:
                player.velocity[1] = 2
            if player.pos[1] > mouse[1]:
                player.velocity[1] = -2

        #To check for keypresses
        if pygame.key.get_pressed()[K_LEFT]:
            player.velocity[0] = -2
        if pygame.key.get_pressed()[K_RIGHT]:
            player.velocity[0] = 2
        if pygame.key.get_pressed()[K_UP]:
            player.velocity[1] = -2
        if pygame.key.get_pressed()[K_DOWN]:
            player.velocity[1] = 2
       
        #Restart
        if restart == 1:
            break

        #Update sprites
        tiles.update()
        walls.update()
        mobs.update()

        player.update()

        #Draw inventory
        pygame.draw.rect(screen,(64,64,64),(0,560,800,40))
        
        for i in range(320,480,20):
            screen.blit(spriteFrame,(i,570))
            
            if player.inventory[(i-320)/20] != 0:
                screen.blit(player.inventory[(i-320)/20].image,(i+2,572))

        #Selected Item
        screen.blit(spriteFrameSelected,(320+player.selected*20,570))

        if player.inventory[player.selected] != 0:
            screen.blit(font.render(player.inventory[player.selected].id,0,(255,255,255)),(512,572))

        #Update
        pygame.display.update()
        clock.tick(FPS_MAX)

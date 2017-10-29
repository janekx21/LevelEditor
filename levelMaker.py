import time
import random
import sys
import math
import pygame as pygame
from pygame.locals import *
import json
import subprocess
import os
import array

# TEST IMPORTS:

import gspread
from oauth2client.service_account import ServiceAccountCredentials





SIZE = (64*16,64*9)

pygame.init()
SCREEN = pygame.display.set_mode(SIZE)

BLOCKSSURFACE = pygame.image.load("src/pics/blocks.png")
PLAYERSSURFACE = pygame.image.load("src/pics/player.png")
GRASSBLOCKTTILE = pygame.image.load("src/pics/bsp4Tile.png")
NEWTESTBOCK = pygame.image.load("src/pics/4x4Tiles.png")
GRASSBLOCKATILE = pygame.image.load("src/pics/GrassBlockATile.png")

GRAVITY = .4

MAPWIDTH = 8
MAPHEIGHT = 8
MAP = [		0,0,0,0,0,0,4,0		,
			0,0,0,0,0,0,0,0		,
			0,0,0,0,0,0,5,6		,
			0,0,0,0,0,1,1,1		,
			1,1,1,1,0,0,0,0		,
			0,0,0,0,0,0,0,0		,
			0,0,0,0,0,0,0,0		,
			0,0,0,0,0,0,0,0		,
]
SOLID = [False,True,True,True,True,False,False,False,
		False,False,False,False,False,False,False,False,
		False,False,False,False,False,False,False,False,
		False,False,False,False,False,False,False,False,
		False,False,False,False,False,False,False,False,
		]

BLOCKS = []
KEYDOWN = []
KEYUP = []
KEYPRESS = []

TODOBLOCKS = []

SELECTIONINDEX = 0
MENUOUT = False
MODE = "play"

TIME = 0

def upLoadMap(stringObject):
	scope = ['https://spreadsheets.google.com/feeds']

	credentials = ServiceAccountCredentials.from_json_keyfile_name('OnlineLevelEditor-ce46bdb7fe28.json', scope)

	gc = gspread.authorize(credentials)

	wks = gc.open("Maps").sheet1

	print(stringObject)
	js = json.loads(stringObject)

	lis = [js["name"],"Sterne","non","non","non","non","non",stringObject]

	wks.append_row(lis)


def clamp(value,minia,maxia):
	return max(min(value, maxia), minia)
def lerp(a,b,t):
	return (b-a)*t+a

class Vec:
	def __init__(self,x,y):
		self.x = x
		self.y = y
	def __add__(self,o):
		return Vec(self.x+o.x,self.y+o.y)
	def __sub__(self,o):
		return Vec(self.x-o.x,self.y-o.y)
	def __div__(self,o):
		return Vec(self.x/o.x,self.y/o.y)
	def __mul__(self,o):
		if type(o) == type(self):
			return Vec(self.x*o.x,self.y*o.y)
		return Vec(self.x*o,self.y*o)
	def __repr__(self):
		return (self.x,self.y)
	def __str__(self):
		return str(self.__repr__())
	def t(self):
		return (self.x,self.y)
	def lerp(self,o,t):
		return Vec(lerp(self.x,o.x,t),lerp(self.y,o.y,t))

CAMPOS = Vec(0,0)

def getCollisionFlag(rectA,rectB,DEBUG,Push):
	flags = [False,False,False,False]
	blocks = []

	a = Vec(rectA.x,rectA.y)
	b = Vec(rectB.x,rectB.y)

	w = .5 * (rectA.width+rectB.width)
	h = .5 * (rectA.height+rectB.height)

	ca =  a + Vec(rectA.width/2,rectA.height/2)
	cb =  b + Vec(rectB.width/2,rectB.height/2)
	dx = ca.x - cb.x
	dy = ca.y - cb.y

	if DEBUG:
		pygame.draw.rect(SCREEN,(0,255,0),rectB.move(-CAMPOS.x,-CAMPOS.y),1)
		pygame.draw.rect(SCREEN,(255,0,0),rectA.move(-CAMPOS.x,-CAMPOS.y),1)
	if abs(dx) <=w and abs(dy) <=h:
		if abs(dx) ==w and abs(dy) ==h:
			pass
		else:
			if DEBUG:
				pygame.draw.rect(SCREEN,(255,255,0),rectB.move(-CAMPOS.x,-CAMPOS.y),2)
				pygame.draw.rect(SCREEN,(255,0,0),rectA.move(-CAMPOS.x,-CAMPOS.y),1)

			wy = w * dy
			hx = h * dx
			if wy > hx:
				if wy > -hx:
					#up
					abstand = rectB.y + rectB.height - rectA.y
					flags[0] = abstand+64.0
					if Push:
						if abstand >0:
							rectA.y += abstand
				else:
					# left
					abstand = rectA.x +rectA.width - rectB.x
					rectA.x +rectA.width - rectB.x
					flags[3] = abstand+64.0
					if Push:
						if abstand >0:
							rectA.x -= abstand
			else:
				if wy > -hx:
					#right
					abstand = rectB.x + rectB.width - rectA.x
					flags[1] = abstand+64.0
					if Push:
						if abstand >0:
							rectA.x += abstand
				else:
					#down
					abstand = rectA.y + rectA.height - rectB.y
					# JANEK WAS HEREffdf
					flags[2] = abstand+64.0
					if Push:
						if abstand >0:
							rectA.y -= abstand
		return flags,Vec(rectA.x,rectA.y)
	else:
		return False,False

class Block:
	def __init__(self,id,pos):
		self.id = id;
		self.image = pygame.Surface((64, 64),SRCALPHA)
		x = self.id%8*64
		y = self.id//8*64
		self.image.blit(BLOCKSSURFACE,(0,0),(x,y,64,64),pygame.BLEND_RGBA_ADD)
		self.pos = pos
		if id >0 and id < len(SOLID)-1:
			self.solid = SOLID[id]
		else:
			self.solid = False
		BLOCKS.append(self)
		
	def draw(self):
		SCREEN.blit(self.image,(self.pos-CAMPOS).t(),None)
	def setId(self,id):
		self.image = pygame.Surface((64, 64),SRCALPHA)
		self.id = id
		x = self.id%8*64
		y = self.id//8*64
		self.image.blit(BLOCKSSURFACE,(0,0),(x,y,64,64),pygame.BLEND_RGBA_ADD)
	def collWithPlayer(self):
		pass

	def getNaibors(self):
		global BLOCKS
		lis = [False,False,False,False,False,False,False,False]
		for block in BLOCKS:
			if block.pos.x == self.pos.x and block.pos.y == self.pos.y - 64:
				lis[0] = block
			if block.pos.x == self.pos.x - 64 and block.pos.y == self.pos.y - 64:
				lis[1] = block
			if block.pos.x == self.pos.x - 64 and block.pos.y == self.pos.y:
				lis[2] = block
			if block.pos.x == self.pos.x  - 64 and block.pos.y == self.pos.y + 64:
				lis[3] = block
			if block.pos.x == self.pos.x and block.pos.y == self.pos.y + 64:
				lis[4] = block
			if block.pos.x == self.pos.x + 64 and block.pos.y == self.pos.y + 64:
				lis[5] = block
			if block.pos.x == self.pos.x + 64 and block.pos.y == self.pos.y:
				lis[6] = block
			if block.pos.x == self.pos.x + 64 and block.pos.y == self.pos.y - 64:
				lis[7] = block
		return lis
	def mapupdate(self):
		pass

	def update(self):
		#self.pos += Vec(.1,0)
		pass
	def onLevelStart(self):
		pass
	def onLevelEnd(self):
		pass
		
	def __repr__(self):
		return {"x":self.pos.x,"y":self.pos.y,"i":self.id}

class TTileBlock(Block):
	def __init__(self,id,pos):
		Block.__init__(self,id,pos)
		TODOBLOCKS.append(self)
	def	mapupdate(self):
		if self.solid:
			naibors = self.getNaibors()
			ix = self.pos.x//64
			iy = self.pos.y//64
			self.image = pygame.Surface((64, 64),SRCALPHA)
			maplist = [0,2,1,2,2,3,2,3]

			i = 0
			grad = 180
			if not naibors[2]:
				i+=4
			if not naibors[0]:
				i+=1
			if not naibors[1]:
				i+=2

			
			if i == 4 or i == 6:
				grad += 90
			i = maplist[i]

			tmp = pygame.Surface((32, 32),SRCALPHA)
			tmp.blit(GRASSBLOCKTTILE,(0,0),(i%2*32,i//2*32,32,32),pygame.BLEND_RGBA_ADD)
			tmp = pygame.transform.rotate(tmp,grad)
			self.image.blit(tmp,(0,0))
			
			i = 0
			grad = 90
			if not naibors[6]:
				i+=4
			if not naibors[0]:
				i+=1
			if not naibors[7]:
				i+=2

			
			if i == 1 or i == 3:
				grad += 90
			i = maplist[i]

			tmp = pygame.Surface((32, 32),SRCALPHA)
			tmp.blit(GRASSBLOCKTTILE,(0,0),(i%2*32,i//2*32,32,32),pygame.BLEND_RGBA_ADD)
			tmp = pygame.transform.rotate(tmp,grad)
			self.image.blit(tmp,(32,0))

			i = 0
			grad = 270
			if not naibors[2]:
				i+=4
			if not naibors[4]:
				i+=1
			if not naibors[3]:
				i+=2

			
			if i == 1 or i == 3:
				grad += 90
			i = maplist[i]

			tmp = pygame.Surface((32, 32),SRCALPHA)
			tmp.blit(GRASSBLOCKTTILE,(0,0),(i%2*32,i//2*32,32,32),pygame.BLEND_RGBA_ADD)
			tmp = pygame.transform.rotate(tmp,grad)
			self.image.blit(tmp,(0,32))

			i = 0
			grad = 0
			if not naibors[6]:
				i+=4
			if not naibors[4]:
				i+=1
			if not naibors[5]:
				i+=2

			
			if i == 4 or i == 6:
				grad += 90
			i = maplist[i]

			tmp = pygame.Surface((32, 32),SRCALPHA)
			tmp.blit(GRASSBLOCKTTILE,(0,0),(i%2*32,i//2*32,32,32),pygame.BLEND_RGBA_ADD)
			tmp = pygame.transform.rotate(tmp,grad)
			self.image.blit(tmp,(32,32))

class ATileBlock(Block):
	def __init__(self,id,pos):
		Block.__init__(self,id,pos)
		TODOBLOCKS.append(self)
	def	mapupdate(self):
		if self.solid:
			ix = self.pos.x//64
			iy = self.pos.y//64
			indexmap = [27,3,26,2,19,11,18,10,24,0,25,1,16,8,17,9]
			index = 0
			block = getBlockAt(ix,iy+1)
			if block:
				if block.id == self.id:
					index+=1
			block =	getBlockAt(ix-1,iy)
			if block:
				if block.id == self.id:
					index+=2

			block =	getBlockAt(ix,iy-1)
			if block:
				if block.id == self.id:
					index+=4

			block =	getBlockAt(ix+1,iy)
			if block:
				if block.id == self.id:
					index+=8

			index = indexmap[index]

			self.image = pygame.Surface((64, 64),SRCALPHA)
			x = index%8*64
			y = index//8*64

			self.image.blit(GRASSBLOCKATILE,(0,0),(x,y,64,64),pygame.BLEND_RGBA_ADD)
class JumpPad(Block):
	def update(self):
		if Rect((self.pos+Vec(0,64-8)).t(),(64,8)).colliderect(PLAYER.pos.t(),(32,64)):
			PLAYER.pos.y -= 1
			PLAYER.vel.y = -20
			PLAYER.canJump = 0
class InvisibleBlock(Block):
	def __init__(self,id,pos):
		Block.__init__(self,id,pos)
		self.visible = True
	def draw(self):
		if self.visible:
			SCREEN.blit(self.image,(self.pos-CAMPOS).t(),None)
	def update(self):
		global MODE
		if self.visible:
			self.visible = False
		if MODE == "edit":
			self.visible = True
	def collWithPlayer(self):
		self.visible = True

class EditorBlock(Block):
	def draw(self):
		global MODE
		if MODE == "edit":
			SCREEN.blit(self.image,(self.pos-CAMPOS).t(),None)
	def onLevelStart(self):
		pass
	def onLevelEnd(self):
		pass
class PlayerStart(EditorBlock):
	def onLevelStart(self):
		global PLAYER
		PLAYER.pos = self.pos
		PLAYER.vel = Vec(0,0)
	def onLevelEnd(self):
		pass
class Spawn(EditorBlock):
	def __init__(self,pos,id,eid):
		EditorBlock.__init(self,pos,id)
	def onLevelStart(self):
		if s.eid == 0:
			Entety(self.pos)

ENTETYS = []
class Entety:
	def __init__(self,pos):
		self.eid = 0 # Vanilla
		self.pos = pos
		self.hp = 3
		ENTETYS.append(self)
	def update(self):
		pass
	def draw(self):
		global SCREEN,CAMPOS
		pygame.draw.rect(SCREEN,(255,255,0),((self.pos-CAMPOS).t(),(64,64)))

class Slime(Entety):
	def __init__(self,pos):
		Entety.__init__(self,pos)
		self.eid = 1 # Slime


class Flyer:
	def __init__(self,pos):
		self.pos = pos
		self.speed = 10
		self.menuout = False
	def update(self,events):
		global KEYPRESS,CAMPOS,TODOBLOCKS,SELECTIONINDEX,SIZE

		if K_f in KEYDOWN:
			if self.menuout:
				self.menuout = False
			else:
				self.menuout = True

		CAMPOS= lerp(CAMPOS,self.pos-Vec(SIZE[0]/2,SIZE[1]/2),.1)
		mov = Vec(0,0)
		if pygame.K_d in KEYPRESS:mov.x += self.speed
		if pygame.K_w in KEYPRESS:mov.y -= self.speed
		if pygame.K_a in KEYPRESS:mov.x -= self.speed
		if pygame.K_s in KEYPRESS:mov.y += self.speed
		self.pos += mov

		mpos = pygame.mouse.get_pos()

		if pygame.mouse.get_pressed()[0]:
			if mpos[0] < 8*64 and mpos[1] < 8*64 and self.menuout:
				ix= int(mpos[0]) // 64
				iy= int(mpos[1]) // 64
				SELECTIONINDEX = ix+iy*8
			else:
				ix= int((mpos[0]+CAMPOS.x) // 64)
				iy= int((mpos[1]+CAMPOS.y) // 64)
				if not getBlockAt(ix,iy):
					setBlock(SELECTIONINDEX,ix,iy)
		else:
			if len(TODOBLOCKS) >0:
				for block in BLOCKS:
					block.mapupdate()
					TODOBLOCKS = []
		if pygame.mouse.get_pressed()[2]:
			ix= int((mpos[0]+CAMPOS.x) // 64)
			iy= int((mpos[1]+CAMPOS.y) // 64)

			b = getBlockAt(ix,iy)
			if b:
				removeBlock(b)

	def draw(self):
		global SCREEN,SIZE
		pygame.draw.rect(SCREEN,(255,200,200),((0,0),SIZE),8)
		if self.menuout:
			self = pygame.Surface((8*64,8*64), pygame.SRCALPHA)
			self.fill((0,0,0,80))
			SCREEN.blit(self,(0,0))
			SCREEN.blit(BLOCKSSURFACE,(0,0))#,(SELECTIONINDEX%8*64,SELECTIONINDEX//8*64,64,64))
			pygame.draw.rect(SCREEN,(255,255,255),(SELECTIONINDEX%8*64,SELECTIONINDEX//8*64,64,64),2)
		else:
			SCREEN.blit(BLOCKSSURFACE,(0,0),(SELECTIONINDEX%8*64,SELECTIONINDEX//8*64,64,64))
class Player:
	def __init__(self,pos):
		self.pos = pos
		self.image = pygame.Surface((64, 64),pygame.SRCALPHA)
		self.image.blit(PLAYERSSURFACE,(0,0),(0,0,32,64),pygame.BLEND_RGBA_ADD)
		self.speed = 1
		self.maxSpeed = 4
		self.vel = Vec(0,0)
		self.jumpHeigt = 13
		self.walking = False
		self.onGround = False
		self.canJump = 0
	def update(self,events):
		global KEYPRESS,CAMPOS,SIZE,TIME
		mov = Vec(0,0)
		col = self.checkColl()
		'''
		if type(col[0])!=type(False):
			self.pos.y += col[0]-64
		if type(col[1])!=type(False):
			self.pos.x += col[1]-64
		if col[2]:
			self.pos.y -= col[2]-64
		if type(col[3])!=type(False):
			self.pos.x -= col[3]-64
		print(col[2])
		'''
		if not col[1]: # left
			if pygame.K_a in KEYPRESS:
				mov.x -= self.speed
		else:
			self.vel.xca = 0

		if not col[3]: # right
			if pygame.K_d in KEYPRESS:
				mov.x += self.speed
		else:
			self.vel.x = 0
		if mov.x == 0:

			if not col[1] and not col[3]:
				self.vel.x*=1-float(self.speed)/float(self.maxSpeed)
				if self.vel.x < .1 and self.vel.x > -.1:
					self.vel.x = 0
				
			else:
				self.vel.x = 0
			
			self.walking = False
		else:
			self.vel += mov
			self.walking = True

		if col[0]: # up
			self.vel.y = 0
			self.pos.y += 1
		
		if not col[2]: # down
			if self.vel.y < 0:
				self.vel.y += GRAVITY
			else:
				self.vel.y += GRAVITY*1.5
			self.onGround = False
		else:
			self.vel.y = 0
			self.pos.y = self.pos.y//1
			self.onGround = True
			self.canJump = 2
		if self.canJump > 0:
			if pygame.K_SPACE in KEYDOWN:
				if not col[0]:
					self.jump()
					self.canJump -= 1
		
		self.vel.x = clamp(self.vel.x,-self.maxSpeed,self.maxSpeed)
		self.vel.y = clamp(self.vel.y,-64,64)

		#self.vel.x = clamp(self.vel.x,-1,1)
		#self.vel.y = clamp(self.vel.y,-1,45)


		self.pos += self.vel

		CAMPOS= lerp(CAMPOS,self.pos-Vec(SIZE[0]/2,SIZE[1]/2)+Vec(16,32) + self.vel,.1)

		if not self.walking and self.onGround:
			if TIME % 30==0:
				self.animationState(0)
			if TIME % 30==16:
				self.animationState(1)
		else:
			if self.onGround:
				if self.vel.x > 0:
					index = TIME//5%4+8
				else:
					index = TIME//5%4+16
			else:
				if self.vel.y <0:
					index = 24
				else:
					index = 25
			self.animationState(index)
	def jump(self):
		self.vel.y = -self.jumpHeigt

	def animationState(self,state):
		x = state%8*32;
		y = state//8*64;
		self.image = pygame.Surface((64, 64),pygame.SRCALPHA)
		#self.image.blit(BLOCKSSURFACE,(0,0),(x,y,32,64),pygame.BLEND_RGBA_ADD)
		self.image.blit(PLAYERSSURFACE,(0,0),(x,y,32,64))
	def draw(self):
		SCREEN.blit(self.image,(self.pos-CAMPOS).t(),None)
	def checkColl(self):
		global SCREEN
		'''

		for block in BLOCKS:
			if block.solid:
				if pygame.Rect(block.pos.t(),(64,64)).colliderect((self.pos+offset).t(),(32,64)):
					return True
		return False
		'''
		flags = [False,False,False,False]#up left down right
		for block in BLOCKS:
			if block.solid:#																								DEBUG
				co,npos = getCollisionFlag(pygame.Rect((self.pos+Vec(0,14)).t(),(32,50)),pygame.Rect(block.pos.t(),(64,64)),False,True)
				if co:
					block.collWithPlayer()
					for i,so in enumerate(co):
						if so:
							flags[i] = so
					self.pos = npos-Vec(0,14)
		#print(flags)
		return flags
		

def setBlock(id,ix,iy):
	global BLOCKS,TODOBLOCKS
	index = ix + iy*MAPWIDTH
	if id == 0:
		print("ID = 0!")
		return
	if len(BLOCKS)<4000:
		if id == 1:
			TTileBlock(id,Vec(ix*64,iy*64))
		elif id == 2:
			ATileBlock(id,Vec(ix*64,iy*64))
		elif id == 3:
			InvisibleBlock(id,Vec(ix*64,iy*64))
		elif id == 9:
			JumpPad(id,Vec(ix*64,iy*64))
		elif id == 32:
			PlayerStart(id,Vec(ix*64,iy*64))
		elif id == 33:
			Slime(Vec(ix*64,iy*64))
		else:
			Block(id,Vec(ix*64,iy*64))
	else:
		print("TOO MUTCH BLOCKE")
	
	
def removeBlock(block):
	global BLOCKS
	BLOCKS.remove(block)
	for block in BLOCKS:
		block.mapupdate()

def getBlockAt(ix,iy):
	for block in BLOCKS:
		if block.pos.x //64 == ix:
			if block.pos.y //64 ==iy:
				return block
def getLevel():
	arr = []
	for block in BLOCKS:
		c = [str(block.pos.x),str(block.pos.y),str(block.id)]
		arr.append(",".join(c))
	obj = {"data":";".join(arr),"name":"coolest level name ever"}
	return obj

for i,block in enumerate(MAP):
	if block != 0:
		setBlock(block,i%MAPWIDTH,i//MAPWIDTH)

for block in BLOCKS:
	block.mapupdate()

PLAYER = Player(Vec(32,64))
FLYER = Flyer(Vec(0,0))
CLOCK = pygame.time.Clock()
while True:
	CLOCK.tick(60)
	mpos = pygame.mouse.get_pos()
	events = pygame.event.get()
	KEYUP = []
	KEYDOWN = []
	for event in events:
		if event.type == pygame.KEYDOWN:
			if event.key not in KEYDOWN:
				KEYDOWN.append(event.key)
			if event.key == pygame.K_ESCAPE:
				pygame.quit()
				sys.exit()
			if event.key == pygame.K_e:
				SELECTIONINDEX+=1
				print(SELECTIONINDEX)
			if event.key == pygame.K_q:
				SELECTIONINDEX-=1
				print(SELECTIONINDEX)
			if event.key == pygame.K_F1:
				st = json.dumps(getLevel(), separators=(',',':'))
				upLoadMap(st)
				#path = r"map.json"
				#with open(path, 'w') as f:
				# 	f.write(st)
				#subprocess.Popen([sys.executable ,"uploadMap.py",os.path.join(os.getcwd(),path)])#,shell=True)

			if event.key == pygame.K_F2:
				print(len(BLOCKS))

		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		if event.type == pygame.KEYDOWN:
			if event.key not in KEYPRESS:
				KEYPRESS.append(event.key)
		if event.type == pygame.KEYUP:
			if event.key not in KEYUP:
				KEYUP.append(event.key)
			if event.key in KEYPRESS:
				KEYPRESS.remove(event.key)

	
	if pygame.K_r in KEYDOWN:
		if MODE == "play":
			MODE = "edit"
		elif MODE == "edit":
			MODE = "play"
			for block in BLOCKS:
				block.onLevelStart()
	SCREEN.fill((100,100,255))
	
	if MODE == "play":
		for block in BLOCKS:
			block.update()
		for entety in ENTETYS:
			entety.update()
		PLAYER.update(events)
	elif MODE == "edit":
		FLYER.update(events)
	for block in BLOCKS:
		block.draw()
	for entety in ENTETYS:
		entety.draw()
	PLAYER.draw()
	if MODE == "edit":
		FLYER.draw()

	# 800 BLOCKS
	pygame.display.set_caption(str(CLOCK.get_fps()))
	pygame.display.flip()
	TIME += 1
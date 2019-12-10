#-*- coding: utf-8 -*-
# Inintialization
import math
import pygame as pg
import random as rnd

# Init
pg.init()
pg.font.init()
# font can be loaded from file - replace 'None' to do that
inf_font = pg.font.Font(None,32)

# Program window 
margin_top, margin_bot, margin_left, margin_right, margin_scr  = 40,10,10,10,10
display_width,display_height   = 800, 600

# Game Screen
screen_width  = display_width  - margin_left - margin_right
screen_height = display_height - margin_top  - margin_bot
window = pg.display.set_mode((display_width, display_height))
pg.display.set_caption('PyArkan')

# Global vars
lives_max = 3
brick_columns, brick_rows  = 10,10
bricks_total = brick_columns * brick_rows
brick_width  = int((screen_width - 2*margin_scr)/brick_columns)
brick_height = int(brick_width/4)
ball_diameter, ball_speed  = 25,2
desk_acseleration, desk_elasticity = 2, 0.5
gravity = 9.82
koef_elasticity_groud = 0.5

class Vector:
	def __init__(self,dx,dy): self.dx,self.dy  = dx,dy

# Greate a base game object
class Sprite:
	def __init__(self,pos,speed):
		# Initialisations
		self.visible = True
		#Position
		self.pos = pos
		# Speed
		self.speed = speed
		self.fixed = True
		self.mass = 1000
		self.alpha = 255
	def mirrorx(self):
		self.speed.dx = -self.speed.dx
	def mirrory(self):
		self.speed.dy = -self.speed.dy
	def render(self):
		if self.alpha < 255:
			self.bitmap.set_alpha(self.alpha)
		if self.visible:
			screen.blit(pg.transform.scale(self.bitmap,(self.size.dx,self.size.dy)),(self.pos.dx,self.pos.dy))		
	def move(self):
		self.pos.dx += self.speed.dx
		self.pos.dy += self.speed.dy
	def ElasticCollision(self,sa,sb):
		tsx = sa.speed.dx
		sa.speed.dx = (2*sb.mass*sb.speed.dx + sa.speed.dx*(sa.mass - sb.mass))/(sa.mass + sb.mass)
		sb.speed.dx = (2*sa.mass*tsx + sb.speed.dx*(sb.mass - sa.mass))/(sa.mass + sb.mass)
		tsy = sa.speed.dy
		sa.speed.dy = (2*sb.mass*sb.speed.dy + sa.speed.dy*(sa.mass - sb.mass))/(sa.mass + sb.mass)
		sb.speed.dy = (2*sa.mass*tsy + sb.speed.dy*(sb.mass - sa.mass))/(sa.mass + sb.mass)
	def go(self):
		if not self.fixed:
			self.move()
			if (self.pos.dx > (screen_width - self.size.dx) and self.speed.dx > 0) or (self.pos.dx < 0 and self.speed.dx < 0):
				self.mirrorx()
			elif (self.pos.dy + self.size.dy) > screen_height:
				self.pos.dy = screen_height - self.size.dy
				if self.speed.dy > 0:
					self.mirrory()
			elif self.pos.dy < 0:
				self.pos.dy = 0	
				if self.speed.dy < 0:
					self.mirrory()

class Brick(Sprite):
	def __init__(self,x,y):
		# Load image
		self.type = str(rnd.randrange(1,5))
		self.fname = "brick" + self.type + ".png"
		self.bitmap = pg.image.load(self.fname).convert()
		self.size = Vector(brick_width,brick_height)
		Sprite.__init__(self,Vector(x,y),Vector(0,0))
		self.collision = 0
	def go(self):
		Sprite.go(self)
		if not self.fixed:
			self.speed.dy += gravity/200
			if (self.pos.dy+self.size.dy>=screen_height):
				self.speed.dy *= koef_elasticity_groud
				self.speed.dx *= koef_elasticity_groud
	def interactwith(self,ball):
		self.go()
#		if (abs(self.speed.dx) < 0.01 and 
#			abs(self.speed.dy) < 0.01 and 
#			abs(self.pos.dy + self.size.dy - screen_height) < 1):
		if self.alpha == 5:
			self.visible = False
			return
		if self.alpha <= 150 and self.alpha > 5:
			self.alpha -= 1
			if self.fixed:
				self.mass = 3
				self.fixed = False
		if Intersect(ball,self):
			if self.collision == 0:
				self.collision = 1;
				if self.fixed:
					if self.type == '1':
						self.alpha -= 100
					else:
						self.alpha = 150
					BallCollision(ball,self)
#				else:
#					self.ElasticCollision(self,ball)
		elif self.collision != 0:
			self.collision = 0
		
class Ball(Sprite):
	def __init__(self,desky):
		# Load image
		self.fname = "ball" + str(rnd.randrange(1,8)) + ".png"
		self.bitmap = pg.image.load(self.fname).convert()
		# Load Transparence color from pixel at 0,0
		self.tranColor = self.bitmap.get_at((0,0))
		# Set transparence color
		self.bitmap.set_colorkey(self.tranColor)
		# Other attributes
		self.size = Vector(ball_diameter,ball_diameter)
		self.speedmod = ball_speed
		self.angle = 30+rnd.randrange(120)
		Sprite.__init__(self,
			Vector(
				margin_scr+int((screen_width-self.size.dx)/2),
				desky-self.size.dy
			),Vector(
				self.speedmod*math.cos(self.angle*math.pi/180),
				-self.speedmod*math.sin(self.angle*math.pi/180)
			)
		)
		self.mass = 1
	def go(self):
		self.speed.dy += gravity/10000
		if (self.pos.dy + self.size.dy) >= screen_height:
			if self.alpha>140:
				self.alpha = 140
			elif self.alpha==0:
				self.visible = False
			else:
				self.alpha-=5
		else:
			Sprite.go(self)
		
class Desk(Sprite):
	def __init__(self):
		# Load image
		self.fname = "desk.png"
		self.bitmap = pg.image.load(self.fname).convert()
		# Load Transparence color from pixel at 0,0
		self.tranColor = self.bitmap.get_at((0,0))
		# Set transparence color
		self.bitmap.set_colorkey(self.tranColor)
		self.size = Vector(
			self.bitmap.get_width(),
			self.bitmap.get_height()
		)
		self.initsize = Vector(self.size.dx,self.size.dy)
		self.elast = desk_elasticity
		# Call Parent init
		Sprite.__init__(self,Vector(
			margin_scr+int((screen_width-self.size.dx)/2),
			screen_height-self.size.dy-margin_scr),
			Vector(0,0)
		)
	def render(self):
		screen.blit(pg.transform.scale(self.bitmap,(int(self.size.dx),int(self.size.dy))),(int(self.pos.dx),int(self.pos.dy)))		
	def go(self):
		if not self.fixed:
			if self.speed.dx != 0:
				self.speed.dx -= math.copysign(self.size.dx*self.speed.dx/screen_width/3,self.speed.dx)
				if abs(self.speed.dx) < 0.1:
					self.speed.dx = 0
			self.move()
			if self.pos.dx <=0:
				dx = abs(self.speed.dx) * math.sqrt(self.mass/self.elast/500)
				self.pos.dx = 0
				self.size.dx = self.initsize.dx - dx
				self.speed.dx += self.elast * dx
			elif self.pos.dx >= screen_width - self.size.dx:
				dx = abs(self.speed.dx) * math.sqrt(self.mass/self.elast/500)
				self.size.dx = self.initsize.dx - dx
				self.pos.dx = screen_width - self.size.dx
				self.speed.dx -= self.elast * dx
			if self.size.dx != self.initsize.dx:
				dx = self.initsize.dx - self.size.dx
				if abs(dx) < 1:
					self.size.dx = self.initsize.dx
				elif self.pos.dx == 0:
					self.speed.dx += dx * self.elast
				elif self.pos.dx + self.size.dx == screen_width:
					self.speed.dx -= dx * self.elast
				else:
					self.size.dx += math.copysign(desk_acseleration,dx)
def Intersect(sa,sb):
	if ((sa.pos.dx+sa.size.dx > sb.pos.dx) and 
		(sa.pos.dx < sb.pos.dx+sb.size.dx) and 
		(sa.pos.dy+sa.size.dy > sb.pos.dy) 
		and (sa.pos.dy < sb.pos.dy+sb.size.dy)):
		return 1
	else:
		return 0

def speedvec2angle(vec,phi):
	R = math.sqrt(vec.dx**2 + vec.dy**2)
	vec.dx = -R*math.sin(phi)
	vec.dy = -R*abs(math.cos(phi))

def BallCollision(sa,sb):
	if   (int(sa.pos.dx + sa.size.dx/2) > sb.pos.dx and int(sa.pos.dx + sa.size.dx/2) < (sb.pos.dx+sb.size.dx)):
		sa.mirrory()
	elif (int(sa.pos.dy + sa.size.dy/2) > sb.pos.dy and int(sa.pos.dy + sa.size.dy/2) < (sb.pos.dy+sb.size.dx)):
		sa.mirrorx()	
		
def DeskCollision(sa,sb):	# sa = ball, sb = desk
	if   ((sa.pos.dx + sa.size.dx) > sb.pos.dx and sa.pos.dx < (sb.pos.dx+sb.size.dx)):
		if   sa.pos.dx < sb.pos.dx + sa.size.dx:
			speedvec2angle(sa.speed,(sb.pos.dx + sa.size.dx - sa.pos.dx)*math.pi/sa.size.dx/5)
		elif sa.pos.dx > sb.pos.dx + sb.size.dx - sa.size.dx:
			speedvec2angle(sa.speed,(sb.pos.dx + sb.size.dx - sa.pos.dx - sa.size.dx)*math.pi/sa.size.dx/5)
		else:
			sa.mirrory()
	elif ((sa.pos.dy + sa.size.dy) > sb.pos.dy and sa.pos.dy < (sb.pos.dy+sb.size.dx)):
		sa.mirrorx()	
def GetScoreLivesInfo(score):
	score_txt = str(score)
	while len(score_txt)<9:
		score_txt = '0' + score_txt	
	return "Lives: " + '®'*lives + ' ¤'*(lives_max - lives) +' || Score: ' + score_txt + ' || Bricks: ' + str(bricks_total)
		
# Create game surface
screen = pg.Surface((screen_width, screen_height))
# Fill game surface with gray
#screen.fill((50,50,50))
wall = pg.image.load("wall.png").convert()
# Create block of information
info_str = pg.Surface((screen_width, margin_top - margin_bot - 2))
# Fill infoblock
info_str.fill((50,50,92))

# Initialise game objects
bricks = []
for i in range(brick_rows):
	for j in range(brick_columns):
		bricks.append(Brick(margin_scr+j*brick_width,margin_scr+i*brick_height))
desk = Desk()
ball = Ball(desk.pos.dy)

# New Game Level starting here
score, lives = 0, lives_max
pg.key.set_repeat(1,1)
done  = True
# Create Game Maine Loop
while lives>0 and done:
	# Proceed Events
	for e in pg.event.get():
		# Cycle events
		if e.type == pg.QUIT:
			done = False
		elif e.type == pg.KEYDOWN:
			if e.key == pg.K_ESCAPE:
				done = False
			elif e.key == pg.K_SPACE:
				if ball.fixed:
					ball.fixed = False
			elif e.key == pg.K_LEFT or e.key == pg.K_a:
				if desk.fixed and not ball.fixed:
					desk.fixed = False
				desk.speed.dx -= desk_acseleration
			elif e.key == pg.K_RIGHT or e.key == pg.K_d:
				if desk.fixed and not ball.fixed:
					desk.fixed = False
				desk.speed.dx += desk_acseleration
	# Clear game screen with gray
	# screen.fill((50,50,50))
	screen.blit(pg.transform.scale(wall,(screen_width,screen_height)),(0,0))	
	# Clear Information
	info_str.fill((50,50,92))
	# Render objects
	i=0
	if Intersect(ball,desk):
		if desk.collision == 0:
			desk.collision = 1;
			DeskCollision(ball,desk)	
	else:
		desk.collision=0
	while i < bricks_total:
		if bricks[i].visible:
			bricks[i].render()
			bricks[i].interactwith(ball)
		else:
			del bricks[i]
			bricks_total -= 1
			score += 25
			continue
		i+=1
	if bricks_total == 0:
		done = False
	ball.render()
	desk.render()
	desk.go()
	ball.go()
	if not ball.visible:
		del ball
		ball = Ball(desk.pos.dy)
		desk.pos.dx = margin_scr+int((screen_width-desk.size.dx)/2)
		ball.fixed = True
		desk.fixed = True
		lives-=1
	# Show Information
	info_str.blit(
		inf_font.render(GetScoreLivesInfo(score),1,(30,140,30)),
		(2,2)
	)
	# Render Game Information Block
	window.blit(info_str,(margin_left,margin_bot))
	# Render Game Surface
	window.blit(screen,(margin_left,margin_top))	# Game window, top-left init point
	pg.display.flip()				# To refresh window. This row must be in the end of game cycle.
	# Time delay
	pg.time.delay(5)

# Game over
end_font = pg.font.SysFont("comicsansms", 72)
end_text = end_font.render("GAME OVER",True,(230,50,50))
alpha = 255
while done:
	for e in pg.event.get():
		if e.type == pg.QUIT:
			done = False
		elif e.type == pg.KEYDOWN:
			if e.key == pg.K_ESCAPE:
				done = False
	pg.time.delay(20)
	info_str.blit(inf_font.render(GetScoreLivesInfo(score),1,(30,140,30)),(2,2))
	window.blit(info_str,(margin_left,margin_bot))
	window.blit(end_text,((screen_width//4, screen_height//2)))
	if alpha > 0: alpha -= 2
	screen.set_alpha(alpha)
	window.blit(screen,(margin_left,margin_top))
	pg.display.flip()
	
	
pg.quit()
quit()

import pygame
import neat
import time
import os
import random
pygame.font.init()

WIN_WIDTH = 250
WIN_HEIGHT = 500



BIRD_IMGS = [pygame.image.load(os.path.join("imgs","bird1.png")),pygame.image.load(os.path.join("imgs","bird2.png")),pygame.image.load(os.path.join("imgs","bird3.png"))]
PIPE_IMG = pygame.image.load(os.path.join("imgs","pipe.png"))
BASE_IMG = pygame.image.load(os.path.join("imgs","base.png"))
BG_IMG = pygame.image.load(os.path.join("imgs","bg.png"))

STAT_FONT = pygame.font.SysFont("comicsans",30)


class Bird:
	IMGS = BIRD_IMGS
	MAX_ROTATION = 20
	ROT_VEL = 15
	ANIMATION_TIME = 5

	def __init__(self,x,y):
		self.x = x
		self.y = y
		self.tilt = 0
		self.tick_count = 0
		self.vel = 0
		self.height = self.y
		self.img_count = 0 
		self.img = self.IMGS[0]

	def jump(self):
		self.vel = -8.5
		self.tick_count = 0
		self.height = self.y
	
	def move(self):
		self.tick_count += 1 #tick since last jump
		d = self.vel * self.tick_count + 1.5*self.tick_count**2

		if d >= 16:
			d = 16
		if d < 0:
			d-=2

		self.y = self.y + d
		
		if d < 0 or self.y < self.height + 50: # moving up and tilt the bird
			if self.tilt < self.MAX_ROTATION:
				self.tilt = self.MAX_ROTATION
		else:
			if self.tilt> -90:
				self.tilt -= self.ROT_VEL

	def draw(self,win):
		self.img_count += 1

		if self.img_count < self.ANIMATION_TIME: # show for first 5 frame te first image
			self.img = self.IMGS[0]
		elif self.img_count < self.ANIMATION_TIME*2: # show for second 5 frame te first image and so on
			self.img = self.IMGS[1]
		elif self.img_count < self.ANIMATION_TIME*3:
			self.img = self.IMGS[2]
		elif self.img_count < self.ANIMATION_TIME*4:
			self.img = self.IMGS[1]
		elif self.img_count == self.ANIMATION_TIME*4+1:
			self.img = self.IMGS[0]
			self.img_count = 0
		
		if self.tilt <= -80:
			self.img = self.IMGS[1]
			self.img_count = self.ANIMATION_TIME*2
		
		rotate_image = pygame.transform.rotate(self.img, self.tilt)
		new_rect = rotate_image.get_rect(center=self.img.get_rect(topleft = (self.x,self.y)).center) # rotate image at center not topleft 
		win.blit(rotate_image, new_rect.topleft)

	def get_mask(self):
		return pygame.mask.from_surface(self.img)

class Pipe:
	Gap = 130
	Vel = 5
	def __init__(self,x):
		self.x = x
		self.height = 0
		

		self.top = 0
		self.bottom = 0
		self.PIPE_TOP = pygame.transform.flip(PIPE_IMG,False,True)
		self.PIPE_BOTTOM = PIPE_IMG

		self.passed = False
		self.set_height()
	def set_height(self):
		self.height = random.randrange(50,250)
		self.top = self.height - self.PIPE_TOP.get_height()
		self.bottom = self.height + self.Gap
	
	def move(self):
		self.x -= self.Vel
	def draw (self,win):
		win.blit(self.PIPE_TOP,(self.x,self.top))
		win.blit(self.PIPE_BOTTOM,(self.x,self.bottom))

	def collide(self,bird):
		bird_mask = bird.get_mask()
		top_mask = pygame.mask.from_surface(self.PIPE_TOP)
		bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

		top_offset = (self.x - bird.x, self.top - round(bird.y))
		bottom_offset = (self.x - bird.x,self.bottom -round(bird.y))

		b_point = bird_mask.overlap(bottom_mask,bottom_offset)
		t_point = bird_mask.overlap(top_mask,top_offset)

		if t_point or b_point:
			return True
		return False

class Base:
	Vel = 5
	WIDTH = BASE_IMG.get_width()
	IMG = BASE_IMG

	def __init__(self,y):
		self.y = y
		self.x1 = 0
		self.x2 = self.WIDTH
	
	def move(self):
		self.x1 -= self.Vel
		self.x2 -= self.Vel

		if self.x1 + self.WIDTH <0:
			self.x1 = self.x2 + self.WIDTH

		if self.x2 + self.WIDTH <0:
			self.x2 = self.x1 + self.WIDTH
	
	def draw (self,win):
		win.blit(self.IMG,(self.x1, self.y))
		win.blit(self.IMG,(self.x2, self.y))

		


def draw_window(win,birds,pipes,base,score):
	win.blit(BG_IMG,(0,0))

	for pipe in pipes:
		pipe.draw(win)

	text = STAT_FONT.render("Score:" + str(score),1,(255,255,255))
	win.blit(text,(WIN_WIDTH-10-text.get_width(),10))

	base.draw(win)
	for bird in birds:
		bird.draw(win)
	pygame.display.update()


def main(genomes, config):
	
	nets=[]
	ge = []
	birds = []
	
	for _, g in genomes:
		net = neat.nn.FeedForwardNetwork.create(g,config)
		nets.append(net)
		birds.append(Bird(100,120))
		g.fitness = 0
		ge.append(g)


	base = Base(410)
	pipes = [Pipe(460)]
	win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
	score = 0

	clock = pygame.time.Clock()

	run =True

	while run:
		clock.tick(30)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()



		pipe_ind = 0
		if len(birds)>0:
			if len(pipes) >1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
				pipe_ind = 1
		else:
			run = False
			break

		for x,bird in enumerate(birds):
			bird.move()
			ge[x].fitness += 0.1

			output = nets[x].activate((bird.y,abs(bird.y-pipes[pipe_ind].height),abs(bird.y - pipes[pipe_ind].bottom)))

			if output[0]>0.5:
				bird.jump()

		#bird.move()
		rem =[]
		add_pipe = False
		for pipe in pipes:
			for x, bird in enumerate(birds):
				if pipe.collide(bird):
					ge[x].fitness -= -1
					birds.pop(x)
					nets.pop(x)
					ge.pop(x)

				if not pipe.passed and pipe.x < bird.x:
					pipe.passed = True
					add_pipe = True
			
			if pipe.x + pipe.PIPE_TOP.get_width() < 0:
				rem.append(pipe)

			pipe.move()

		if add_pipe:
			score += 1
			pipes.append(Pipe(350))
			for g in ge:
				g.fitness += 5

		for r in rem:
			pipes.remove(r)

		for x,bird in enumerate(birds):
			if bird.y + bird.img.get_height()>=500 or bird.y < 0:
				birds.pop(x)
				nets.pop(x)
				ge.pop(x)

		if score > 200:
			break

		base.move()
		draw_window(win,birds,pipes, base, score)



def run(config_path):
	config = neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,
							 	neat.DefaultSpeciesSet, neat.DefaultStagnation,
								config_path)
	p = neat.Population(config)

	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)

	winner = p.run(main,50)

if __name__ == "__main__":
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir,"config.txt")
	run(config_path)
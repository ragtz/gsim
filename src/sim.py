from gsim.src.model import *
import numpy as np
import pygame
import random
import sys          

class GSim(object):
    def __init__(self, width, height, frame_files):
        pygame.init()
        self.canvas = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()

        self.slide = 0
        self.numFramesDone = 0
        self.enter = False
        self.recording = False

        self.model = GSimModel(width, height)
        for f in frame_files:
            self.model.addFrameFromFile(f)

        self.enterTxt = pygame.font.SysFont("monospace", 35).render("Press 'Enter' to continue", True, (0,0,0))

    def clicked(self, obj, x, y):
        if isinstance(obj, Shape) and not isinstance(obj, Target) and not isinstance(obj, Stage) and not isinstance(obj, Table):   
            return x > obj.x and x < obj.x + obj.w and y > obj.y and y < obj.y + obj.w
        elif isinstance(obj, Gripper):
            return x > obj.x - obj.r and x < obj.x + obj.r and y > obj.y - obj.r and y < obj.y + obj.r
        else:
            return False

    def done(self):
        return self.numFramesDone == self.model.getNumFrames()

    def next(self):
        if self.slide == 0:
            self.slide = 1

        elif self.slide == 1:
            if not self.model.getCurrentFrame().isActive():
                self.model.upFrame()

                if self.numFramesDone < self.model.getNumFrames():
                    self.numFramesDone += 1

                if self.done() and self.model.getCurrentFrameId() == self.model.getNumFrames()-1:
                    self.slide = 2

    def back(self):
        if self.slide == 1:
            self.model.downFrame()

        elif self.slide == 2:
            self.slide = 1

    def update(self):
        self.canvas.fill((255,255,255))

        if self.slide == 0:
            pass
        elif self.slide == 1:
            self.model.draw(self.canvas)

            if self.enter:
                self.canvas.blit(self.enterTxt, (10, 10))
        else:
            pass        

        pygame.display.flip()
        
    def run(self):
        mouse_pos = (0, 0)
        gripper_selected = True #False
        t = 0

        while True:
            dt = self.clock.tick(50)
            t += dt
            print self.slide, self.numFramesDone, self.model.getCurrentFrameId()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                elif event.type == pygame.MOUSEMOTION:
                    x, y = event.pos

                    if gripper_selected:
                        self.model.moveGripper(x, y)
                        if not self.model.getCurrentFrame().isActive():
                            #gripper_selected = False
                            self.enter = True

                            #if self.model.getCurrentFrameId() == self.model.getNumFrames()-1:
                            #    self.done = True

                    mouse_pos = (x, y)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
            
                    if event.button == 1:
                        if gripper_selected:
                            self.model.closeGripper()
                        elif self.clicked(self.model.getGripper(), x, y):
                            gripper_selected = True
                    #elif event.button == 3:
                    #        gripper_selected = False

                #elif event.type == pygame.MOUSEBUTTONUP:
                #    self.model.openGripper()

                elif event.type == pygame.KEYDOWN:
                    x, y = mouse_pos

                    if self.done():
                        if event.key == pygame.K_RIGHT:
                            self.next()

                        elif event.key == pygame.K_LEFT:
                            self.back()
                    else:
                        if event.key == pygame.K_RETURN:
                            self.next()
                            self.enter = False

                        #if slide == 0:
                        #    if event.key == pygame.K_RETURN:
                        #        self.next()
                        #elif slide == 1:
                        #    if event.key == pygame.K_RETURN and not self.model.getCurrentFrame().isActive():
                        #        self.next()
                        #        self.enter = False
                
                        #if event.key == pygame.K_RETURN and not self.model.getCurrentFrame().isActive():
                        #    self.next()
                        #    self.enter = False

                self.update()

class SortTaskSim(object):
    def __init__(self, width=1000, height=1000):
        pygame.init()
        self.canvas = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.recording = False
        
        self.model = SortTaskModel(width, height)
        self.model.addGripper('gripper', 850, 800)
        self.model.addTable('table', 300, 700, 400, 200)
        self.model.addBin('red', 200, 400, 50, 50)
        self.model.addBin('green', 475, 200, 50, 50)
        self.model.addBin('blue', 750, 400, 50, 50)

        self.gripperStart = Rectangle('start', 800, 750, 100, 100, (255, 255, 255))

        self.recordTxt = pygame.font.SysFont("monospace", 35).render("Recording...", True, (0,0,0))
        self.redTxt = pygame.font.SysFont("monospace", 25).render("Red", True, (255, 0, 0))
        self.greenTxt = pygame.font.SysFont("monospace", 25).render("Green", True, (0, 255, 0))
        self.blueTxt = pygame.font.SysFont("monospace", 25).render("Blue", True, (0, 0 , 255))
        self.startTxt = pygame.font.SysFont("monospace", 25).render("Start", True, (0, 0 , 0))

        self.data = []
        self.numTraj = 0

    def clicked(self, obj, x, y):
        if isinstance(obj, Block):
            return x > obj.x and x < obj.x + obj.w and y > obj.y and y < obj.y + obj.h
        elif isinstance(obj, Gripper):
            return x > obj.x - obj.r and x < obj.x + obj.r and y > obj.y - obj.r and y < obj.y + obj.r
        else:
            return False

    def record(self, t):
        if self.model.numBlocks() > 0:     
            gripper = self.model.getGripper('gripper')
            block = self.model.getBlock('b0')

            x_g = gripper.x
            y_g = gripper.y
            s_g = gripper.state
            x_b = block.x + block.w/2
            y_b = block.y + block.h/2
            (r_b, g_b, b_b) = block.c

            idx = self.numTraj-1

            self.data[idx]['t'].append(t)
            self.data[idx]['gripper'].append([x_g, y_g, s_g])
            self.data[idx]['block'].append([x_b, y_b, r_b, g_b, b_b])

    def saveData(self, filename):
        if not filename == None:
            for i in range(len(self.data)):
                self.data[i]['t'] = np.array(self.data[i]['t'])
                self.data[i]['gripper'] = np.array(self.data[i]['gripper'])
                self.data[i]['block'] = np.array(self.data[i]['block'])

            np.save(filename, np.array(self.data, dtype=np.dtype(object)))
    
    def sampleColor(self, mean, std_dev):
        (r, g, b) = mean

        r = np.clip(random.gauss(r, std_dev), 0, 255)
        g = np.clip(random.gauss(g, std_dev), 0, 255)
        b = np.clip(random.gauss(b, std_dev), 0, 255)

        return (r, g, b)

    def sampleRed(self):
        return self.sampleColor((255, 0, 0), 50)

    def sampleGreen(self):
        return self.sampleColor((0, 255, 0), 50)

    def sampleBlue(self):
        return self.sampleColor((0, 0, 255), 50)
    
    def update(self):
        self.canvas.fill((255,255,255))

        redBin = self.model.getBin('red')
        greenBin = self.model.getBin('green')
        blueBin = self.model.getBin('blue')

        x, y = redBin.getPosition()
        w, h = redBin.getSize()
        (tw, th) = (self.redTxt.get_width(), self.redTxt.get_height())
        self.canvas.blit(self.redTxt, (x+(w-tw)/2, y+h+th/2))

        x, y = greenBin.getPosition()
        w, h = greenBin.getSize()
        (tw, th) = (self.greenTxt.get_width(), self.greenTxt.get_height())
        self.canvas.blit(self.greenTxt, (x+(w-tw)/2, y+h+th/2))

        x, y = blueBin.getPosition()
        w, h = blueBin.getSize()
        (tw, th) = (self.blueTxt.get_width(), self.blueTxt.get_height())
        self.canvas.blit(self.blueTxt, (x+(w-tw)/2, y+h+th/2))

        x, y = self.gripperStart.getPosition()
        w, h = self.gripperStart.getSize()
        (tw, th) = (self.startTxt.get_width(), self.startTxt.get_height())
        self.canvas.blit(self.startTxt, (x+(w-tw)/2, y+h+th/2))

        self.gripperStart.draw(self.canvas)
        self.model.draw(self.canvas)

        if self.recording:
            self.canvas.blit(self.recordTxt, (10, 10))

        pygame.display.flip()
        
    def run(self, filename=None):
        mouse_pos = None
        gripper_selected = False
        t = 0
        
        while True:
            dt = self.clock.tick(50)
            t += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if len(self.data) > 0:
                        self.saveData(filename)
                    sys.exit()
                    
                elif event.type == pygame.MOUSEMOTION:
                    x, y = event.pos

                    if gripper_selected:
                        self.model.moveGripper('gripper', x, y)

                    mouse_pos = (x, y)
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos

                    if event.button == 1:
                        if gripper_selected:
                            self.model.closeGripper('gripper')
                        elif self.clicked(self.model.getGripper('gripper'), x, y):
                            gripper_selected = True
                    elif event.button == 3:
                        gripper_selected = False

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.model.openGripper('gripper')
          
                elif event.type == pygame.KEYDOWN: 
                    x, y = mouse_pos
       
                    if event.key == pygame.K_r and self.model.numBlocks() == 0:
                        #self.model.addBlock('b'+str(self.model.numBlocks()), x, y, 15, 15, (255, 0, 0))
                        self.model.addBlock('b'+str(self.model.numBlocks()), x, y, 15, 15, self.sampleRed())
                        
                    elif event.key == pygame.K_g and self.model.numBlocks() == 0:
                        #self.model.addBlock('b'+str(self.model.numBlocks()), x, y, 15, 15, (0, 255, 0))
                        self.model.addBlock('b'+str(self.model.numBlocks()), x, y, 15, 15, self.sampleGreen())
                        
                    elif event.key == pygame.K_b and self.model.numBlocks() == 0:
                        #self.model.addBlock('b'+str(self.model.numBlocks()), x, y, 15, 15, (0, 0, 255))
                        self.model.addBlock('b'+str(self.model.numBlocks()), x, y, 15, 15, self.sampleBlue())

                    elif event.key == pygame.K_c:
                        self.model.removeBlocks()

                    elif event.key == pygame.K_SPACE and self.model.numBlocks() >= 0:
                        self.recording = not self.recording
                        if self.recording:
                            self.data.append({'t': [], 'gripper': [], 'block': []})
                            self.numTraj += 1
                
                if self.recording:
                    self.record(t)

                self.update()
 
if __name__ == '__main__':
    sim = GSim(1300, 1000, ['../worlds/w1.yaml', '../worlds/w2.yaml', '../worlds/w3.yaml'])

    if len(sys.argv) == 1:
        sim.run()
    else:
        sim.run(sys.argv[1])


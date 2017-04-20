import pygame
import yaml
import numpy as np

class Shape(object):
    def __init__(self, x=None, y=None, w=None, c=None):
        self.x = x
        self.y = y
        self.w = w
        self.c = c

    def setPosition(self, x, y):
        self.x = x
        self.y = y

    def setWidth(self, w):
        self.w = w

    def setColor(self, c):
        self.c = c

    def getPosition(self):
        return (self.x, self.y)

    def getWidth(self):
        return self.w

    def getColor(self):
        return self.c

    def draw(self, canvas):
        pass

class Circle(Shape):
    def draw(self, canvas):
        r = self.w/2
        pos = (self.x + r, self.y + r)
        pygame.draw.circle(canvas, self.c, pos, r)
        pygame.draw.circle(canvas, (0, 0, 0), pos, r, 4)

class Square(Shape):
    def draw(self, canvas): 
        pygame.draw.rect(canvas, self.c, [self.x, self.y, self.w, self.w])
        pygame.draw.rect(canvas, (0, 0, 0), [self.x, self.y, self.w, self.w], 4)

class Triangle(Shape):
    def draw(self, canvas):
        plist = [(self.x, self.y + self.w),
                 (self.x + self.w, self.y + self.w),
                 (self.x + self.w/2, self.y)]
        pygame.draw.polygon(canvas, self.c, plist) 
        pygame.draw.polygon(canvas, (0, 0, 0), plist, 4)

class Star(Shape):
    def draw(self, canvas):
        r0 = self.w/2
        rad0 = 0
        r1 = self.w/5
        rad1 = np.pi/5
        drad = 2*np.pi/5 
        plist = []

        for i in range(10):
            if i%2 == 0:
                plist.append((r0*np.cos(rad0), r0*np.sin(rad0)))
                rad0 += drad
            else:
                plist.append((r1*np.cos(rad1), r1*np.sin(rad1)))
                rad1 += drad

        plist = self._changeCoords(plist)
        pygame.draw.polygon(canvas, self.c, plist)
        pygame.draw.polygon(canvas, (0, 0, 0), plist, 4)

    def _changeCoords(self, plist):
        plist_new = []
        for p in plist:
            x, y = p
            plist_new.append((self.x - y + self.w/2, self.y - x + self.w/2))
        return plist_new

class Diamond(Shape):
    def draw(self, canvas):
        plist = [(self.x + self.w/2, self.y),
                 (self.x + 3*self.w/4, self.y + self.w/2),
                 (self.x + self.w/2, self.y + self.w),
                 (self.x + self.w/4, self.y + self.w//2)]
        pygame.draw.polygon(canvas, self.c, plist)
        pygame.draw.polygon(canvas, (0, 0, 0), plist, 4)

class Target(Shape):
    def draw(self, canvas):
        pygame.draw.line(canvas, (0, 0, 0), (self.x, self.y), (self.x + self.w, self.y + self.w), 10)
        pygame.draw.line(canvas, (0, 0, 0), (self.x + self.w, self.y), (self.x, self.y + self.w), 10)

class Stage(Shape):
    def draw(self, canvas):
        pygame.draw.rect(canvas, (0, 0, 0), [self.x, self.y, self.w, self.w], 4)

class Table(Shape):
    def draw(self, canvas):
        pygame.draw.rect(canvas, (0, 0, 0), [self.x, self.y, self.w, self.w], 4)

class Gripper(object):
    def __init__(self, x=None, y=None, r=40, width=5):        
        self.x = x
        self.y = y
        self.r = r
        self.width = width
        self.state = 0
        self.obj = None

    def setPosition(self, x, y):
        self.x = x
        self.y = y

    def openGripper(self):
        self.state = 0
        self.obj = None

    def closeGripper(self):
        self.state = 1

    def graspObject(self, obj):
        self.state = 1
        self.obj = obj

    def closed(self):
        return True if self.state else False
        
    def opened(self):
        return not self.closed()

    def hasObject(self):
        return not self.obj == None

    def draw(self, canvas):
        if self.state:
            pygame.draw.circle(canvas, (0, 0, 0), (self.x, self.y), 2*self.r/3)
        else:
            pygame.draw.circle(canvas, (0, 0, 0), (self.x, self.y), self.r, self.width)

shape_map = {0: Circle,
             1: Square,
             2: Triangle,
             3: Star,
             4: Diamond}
color_map = {0: (0, 0, 255),
             1: (255, 0, 0),
             2: (0, 255, 0),
             3: (255, 0, 255),
             4: (255, 255, 0),
             5: (0, 255, 255)}
        
class Frame(object):
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.gripper = None
        self.table = None
        self.stage = None
        self.target = None
        self.tobj = None
        self.objs = []
        self.active = True

    def near(self, gripper, obj):
        return abs(gripper.x - (obj.x + obj.w/2)) < obj.w/10 and abs(gripper.y - (obj.y + obj.w/2)) < obj.w/10

    def validPosition(self, x, y):
        return x > 0 or x < self.w or y > 0 or y < self.h

    def addGripper(self, x, y):
        if self.validPosition(x, y):
            self.gripper = Gripper(x, y)
        else:
            raise Exception("Gripper is outside frame")

    def addTable(self, x, y, w):
        if self.validPosition(x, y) and self.validPosition(x+w, y+w):
            self.table = Table(x, y, w)
        else:
            raise Exception("Table is outside frame")

    def addStage(self, x, y, w):
        if self.validPosition(x, y) and self.validPosition(x+w, y+w):
            self.stage = Stage(x, y, w)
        else:
            raise Exception("Stage is outside frame")

    def addTarget(self, x, y, w):
        if self.validPosition(x, y) and self.validPosition(x+w, y+w):
            self.target = Target(x, y, w)
        else:
            raise Exception("Target is outside frame")

    def addTaskObject(self, x, y, w, s, c):    
        if self.validPosition(x, y) and self.validPosition(x+w, y+w):
            self.tobj = shape_map[s](x, y, w, color_map[c])
        else:
            raise Exception("Task object is outside frame")

    def addObject(self, x, y, w, s, c):   
        if self.validPosition(x, y) and self.validPosition(x+w, y+w):
            self.objs.append(shape_map[s](x, y, w, color_map[c]))
        else:
            raise Exception("Object is outside frame")

    def moveGripper(self, x, y):
        if self.active:
            self.gripper.setPosition(x, y)

            if self.gripper.hasObject():
                # move object with gripper
                obj = self.gripper.obj
                w = obj.w
                obj.setPosition(x-w/2, y-w/2)

                # deactivate if near target
                if self.near(self.gripper, self.target):
                    self.deactivate()

    def openGripper(self):
        if self.active:
            self.gripper.openGripper()

    def closeGripper(self):
        if self.active:
            if self.near(self.gripper, self.tobj):
                self.gripper.graspObject(self.tobj)
            else:
                self.gripper.closeGripper()

    def getGripper(self):
        return self.gripper

    def getTable(self):
        return self.table

    def getStage(self):
        return self.stage

    def getTarget(self):
        return self.target

    def getTaskObject(self):
        return self.tobj

    def getObjects(self):
        return self.objects

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def isActive(self):
        return self.active

    def draw(self, canvas):
        self.table.draw(canvas)
        self.stage.draw(canvas)
        self.target.draw(canvas)

        for obj in self.objs:
            obj.draw(canvas)

        self.tobj.draw(canvas)

        #if self.active:
        #    self.gripper.draw(canvas)


class GSimModel(object):
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.frames = []
        self.i = None
        self.n = 0
 
    def addFrame(self, frame):
        if len(self.frames) == 0:
            self.i = 0
        self.frames.append(frame)
        self.n += 1

    def addFrameFromFile(self, f):
        if len(self.frames) == 0:
            self.i = 0

        try:
            d = yaml.load(open(f))
            w = d['width']
            h = d['height']
            table_params = d['table']
            stage_params = d['staging_area']
            target_params = d['target']
            tobj_params = d['task_object']
            objs_params = d['objects']
        except:
            raise Exception("Parameters missing from world file")

        if w != self.w or h != self.h:
            raise Exception("Frame dimension does not agree with GSimModel")

        frame = Frame(w, h)
        frame.addGripper(9*w/10, h/10)

        x, y, w = table_params
        frame.addTable(x, y, w)
        
        x, y, w = stage_params
        frame.addStage(x, y, w)

        x, y, w = target_params
        frame.addTarget(x, y, w)

        w, s, c = tobj_params
        x = frame.getStage().x + frame.getStage().w/2 - w/2
        y = frame.getStage().y + frame.getStage().w/2 - w/2
        frame.addTaskObject(x, y, w, s, c)
        
        objs = []
        for obj_params in objs_params:
            x, y, w, s, c = obj_params
            frame.addObject(x, y, w, s, c)

        self.frames.append(frame)
        self.n += 1

    def getFrame(self, i):
        return self.frames[i]

    def getCurrentFrame(self):
        return self.getFrame(self.i)

    def getCurrentFrameId(self):
        return self.i

    def getNumFrames(self):
        return self.n

    def upFrame(self):
        if self.i + 1 < len(self.frames):
            self.i += 1

    def downFrame(self):
        if self.i - 1 >= 0:
            self.i -= 1

    def getGripper(self):
        return self.getCurrentFrame().getGripper()

    def moveGripper(self, x, y):
        self.getCurrentFrame().moveGripper(x, y)

    def openGripper(self):
        self.getCurrentFrame().openGripper()

    def closeGripper(self):
        self.getCurrentFrame().closeGripper()
                
    def draw(self, canvas):
        self.getCurrentFrame().draw(canvas)


class SortTaskModel(object):
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.tables = {}
        self.bins = {}
        self.blocks = {}
        self.grippers = {}
        
    def dist(self, x1, y1, x2, y2):
        return ((x1-x2)**2 + (y1-y2)**2)**0.5
        
    def near(self, gripper, block):
        return abs(gripper.x - (block.x + block.w/2)) < block.w/2 + gripper.r and abs(gripper.y - (block.y + block.h/2)) < block.h/2 + gripper.r

    def validPosition(self, x, y):
        return x > 0 or x < self.w or y > 0 or y < self.h

    def addTable(self, name, x, y, w, h):
        if self.validPosition(x, y) and self.validPosition(x+w, y+h):
            self.tables[name] = Table(name, x, y, w, h)

    def addBin(self, name, x, y, w, h):
        if self.validPosition(x, y) and self.validPosition(x+w, y+h):
            self.bins[name] = Bin(name, x, y, w, h)

    def addBlock(self, name, x, y, w, h, c):
        if self.validPosition(x, y) and self.validPosition(x+w, y+h):
            self.blocks[name] = Block(name, x, y, w, h, c)
    
    def addGripper(self, name, x, y):
        if self.validPosition(x, y):
            self.grippers[name] = Gripper(name, x, y)

    def removeTable(self, name):
        del self.tables[name]

    def removeBin(self, name):
        del self.bins[name]

    def removeBlock(self, name):
        del self.blocks[name]

    def removeGripper(self, name):
        del self.grippers[name]

    def removeTables(self):
        self.tables = {}

    def removeBins(self):
        self.bins = {}

    def removeBlocks(self):
        self.blocks = {}

    def removeGrippers(self):
        self.grippers = {}

    def numTables(self):
        return len(self.tables)

    def numBins(self):
        return len(self.bins)

    def numBlocks(self):
        return len(self.blocks)

    def numGrippers(self):
        return len(self.grippers)
       
    def getTable(self, name):
        if name in self.tables:
            return self.tables[name]
        else:
            return None

    def getTables(self):
        return self.tables.values()

    def getBin(self, name):
        if name in self.bins:
            return self.bins[name]
        else:
            return None

    def getBins(self):
        return self.bins.values()

    def getBlock(self, name):
        if name in self.blocks:
            return self.blocks[name]
        else:
            return None
 
    def getBlocks(self):
        return self.blocks.values()
        
    def getGripper(self, name):
        if name in self.grippers:
            return self.grippers[name]
        else:
            return None

    def getGrippers(self):
        return self.grippers.values()

    def moveGripper(self, name, x, y):
        if name in self.grippers:
            gripper = self.grippers[name]
            gripper.setPosition(x, y)

            if gripper.hasBlock():
                block = gripper.block
                w = block.w
                h = block.h
                block.setPosition(x-w/2, y-h/2)

    def moveBlock(self, name, x, y):
        if name in self.blocks:
            self.blocks[name].setPosition(x, y)

    def openGripper(self, name):
        if name in self.grippers:
            self.grippers[name].openGripper()

    def closeGripper(self, name):
        if name in self.grippers:
            gripper = self.grippers[name]

            nearestBlock = None
            minDist = float('inf')

            for block in self.getBlocks():
                dist = self.dist(gripper.x, gripper.y, block.x, block.y)
                if dist < minDist:
                    nearestBlock = block
                    minDist = dist
            
            if not nearestBlock == None and self.near(gripper, nearestBlock):
                gripper.graspBlock(nearestBlock)
            else:
                gripper.closeGripper()
                
    def draw(self, canvas):
        for table in self.tables.values():
            table.draw(canvas)
            
        for bbin in self.bins.values():
            bbin.draw(canvas)
            
        for block in self.blocks.values():
            block.draw(canvas)
            
        for gripper in self.grippers.values():
            gripper.draw(canvas)


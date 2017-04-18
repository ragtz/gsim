import pygame

class Rectangle(object):
    def __init__(self, name, x=None, y=None, w=None, h=None, c=None):
        self.name = name
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.c = c

    def setPosition(self, x, y):
        self.x = x
        self.y = y

    def setSize(self, w, h):
        self.w = w
        self.h = h

    def setColor(self, c):
        self.c = c

    def getPosition(self):
        return (self.x, self.y)

    def getSize(self):
        return (self.w, self.h)

    def getColor(self):
        return self.c

    def draw(self, canvas):
        pygame.draw.rect(canvas, self.c, [self.x, self.y, self.w, self.h])
        pygame.draw.rect(canvas, (0, 0, 0), [self.x, self.y, self.w, self.h], 2)

class Table(Rectangle):
    def __init__(self, name, x=None, y=None, w=None, h=None):
        super(Table, self).__init__(name, x, y, w, h, c=(155, 85, 15))

class Bin(Rectangle):
    def __init__(self, name, x, y, w, h):
        super(Bin, self).__init__(name, x, y, w, h, c=(135, 135, 135))

class Block(Rectangle):
    def __init__(self, name, x, y, w, h, c):
        super(Block, self).__init__(name, x, y, w, h, c)

class Gripper(object):
    def __init__(self, name, x=None, y=None, r=20, width=5):
        self.name = name        
        self.x = x
        self.y = y
        self.r = r
        self.width = width
        self.state = 0
        self.block = None

    def setPosition(self, x, y):
        self.x = x
        self.y = y

    def openGripper(self):
        self.state = 0
        self.block = None

    def closeGripper(self):
        self.state = 1

    def graspBlock(self, block):
        self.state = 1
        self.block = block

    def closed(self):
        return True if self.state else False
        
    def opened(self):
        return not self.closed()

    def hasBlock(self):
        return not self.block == None

    def draw(self, canvas):
        if self.state:
            pygame.draw.circle(canvas, (0, 0, 0), (self.x, self.y), 2*self.r/3)
        else:
            pygame.draw.circle(canvas, (0, 0, 0), (self.x, self.y), self.r, self.width)
        

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
    
    
    
    
    
    
    
    


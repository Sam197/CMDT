import pygame
from config import *  # pylint: disable=W0614
import pygame.freetype
from math import floor

class Tile:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.txt = None
        self.gridX = int(x/GRIDTILESIZE)
        self.gridY = int(y/GRIDTILESIZE)
        self.boundsRect = pygame.Rect((self.x, self.y, GRIDTILESIZE, GRIDTILESIZE))
        self.selected = False
        self.hasLine = False

    def __repr__(self):
        return(f"Tile coords({self.gridX},{self.gridY})")

    def isCollide(self, screen, pos):
        if self.boundsRect.collidepoint(pos):
            self.selected = True            
            return True
        else:
            self.selected = False
            return False

    def draw(self, screen):
        if self.selected:
            pygame.draw.rect(screen, HIGHLIGHT_BLUE, self.boundsRect)

class Atom:

    def __init__(self, x, y, txt):
        self.x = x
        self.y = y
        self.txt = txt
        self.font = pygame.freetype.Font('MonospaceTypewriter.ttf', size=int(FONT_SIZE*GRIDTILESIZE/100))
    
    def __repr__(self):
        return(f"Free Atom of text {self.txt}")

    def update(self, pos):
        self.x, self.y = pos

    def draw(self, screen):
        self.font.render_to(screen, (self.x, self.y), self.txt, BLACK)


class TiledAtom(Tile, Atom):
    
    def __init__(self, x, y, txt):
        Tile.__init__(self, x, y)
        Atom.__init__(self, x, y, txt)
        fx = self.font.get_rect(txt).width 
        fy = self.font.get_rect(txt).height
        tx, ty = self.boundsRect.center
        self.fontOffsetX = int((tx-x) - (fx/2))
        self.fontOffsetY = int((ty-y) - (fy/2))
        self.txtRect = pygame.Rect(0,0,0,0)


    def __repr__(self):
        return(f"Tiled Atom grid {self.gridX}:{self.gridY}, txt {self.txt}")

    def reverseTxt(self):
        nS = self.txt[::-1]
        self.txt = nS

    def draw(self, screen):
        if self.selected:
            self.colour = HIGHLIGHT_BLUE
        else:
            self.colour = BLACK
        pygame.draw.rect(screen, WHITE, self.txtRect)
        self.txtRect = self.font.render_to(screen, (self.x + self.fontOffsetX, self.y + self.fontOffsetY), self.txt, self.colour)
        self.txtRect.left = self.x + self.fontOffsetX
        self.txtRect.top = self.y + self.fontOffsetY       

class OHGroup(TiledAtom):

    def __init__(self, x, y, txt = "OH"):
        TiledAtom.__init__(self, x, y, txt)
        self.txtRect = None
    
    def __repr__(self):
        return(f"OH group at {self.gridX}, {self.gridY}")

class Dot:

    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
        
    def __repr__(self):
        return("This isn't nessacry - what is spell?")

    def update(self, pos):
        self.x, self.y = pos

    def draw(self, screen):
        pygame.draw.circle(screen, BLACK, (self.x, self.y), DOT_RADIUS)


class Line:

    def __init__(self, start, end = (0,0), numOfBonds = 1):
        self.startPos = start
        self.endPos = end
        self.selected = False
        self.startGridX = floor(start[0]/GRIDTILESIZE)
        self.startGridY = floor(start[1]/GRIDTILESIZE)
        self.endGridX = floor(end[0]/GRIDTILESIZE)
        self.endGridY = floor(end[1]/GRIDTILESIZE)
        self.numOfBonds = numOfBonds    #As in 1 is a single bond, 2 double, 3 triple, AND THE FORBIDDEN 4 QUADRUPLE BOND
        self.lineRect = None
        self.colour = BLACK
        self.orentation = None
        self.startCollide = False
        self.endCollide = False
        x1, y1 = start
        x2, y2 = end
        if x1 - x2 == 0:
            self.orentation = "Vertical"
        elif y1 - y2 == 0:
            self.orentation = "Horizontal"
        else:
            self.orentation = "Diagonal" 

    def __repr__(self):
        return(f"Line from {self.startPos} to {self.endPos}")

    def update(self, pos):
        self.endPos = pos
    
    def isCollide(self, pos):
        if self.lineRect.collidepoint(pos):
            self.colour = HIGHLIGHT_BLUE
            return True
        else:
            self.colour = BLACK
            return False
        
    def endsCollide(self, grid, screen):
        if grid[self.startGridY][self.startGridX].txt != None:
            grid[self.startGridY][self.startGridX].draw(screen)
        if grid[self.endGridY][self.endGridX].txt != None:
            grid[self.endGridY][self.endGridX].draw(screen)
        
    def update_Bond_Number(self):
        self.numOfBonds += 1
        if self.numOfBonds > BOND_LIMIT:
            self.numOfBonds = 1

    def draw(self, screen):
        if self.numOfBonds == 1 or self.numOfBonds == 3:
            self.lineRect = pygame.draw.line(screen, self.colour, self.startPos, self.endPos, int(LINEWIDTH*GRIDTILESIZE/100))
        if self.numOfBonds != 1:
            x1, y1 = self.startPos
            x2, y2 = self.endPos 
            if self.numOfBonds == 2 or self.numOfBonds == 4:            
                offset = int(BASE_BOND_OFFSET_DOUBLE*GRIDTILESIZE/100)
            if self.numOfBonds == 3:
                offset = int(BASE_BOND_OFFSET_TRIPLE*GRIDTILESIZE/100)
            if self.orentation == "Vertical":
                pygame.draw.line(screen, self.colour, (x1-offset, y1), (x2-offset,y2), int(LINEWIDTH*GRIDTILESIZE/100))
                pygame.draw.line(screen, self.colour, (x1+offset, y1), (x2+offset, y2), int(LINEWIDTH*GRIDTILESIZE/100))
            else:
                pygame.draw.line(screen, self.colour, (x1, y1-offset), (x2, y2-offset), int(LINEWIDTH*GRIDTILESIZE/100))
                pygame.draw.line(screen, self.colour, (x1, y1+offset), (x2, y2+offset), int(LINEWIDTH*GRIDTILESIZE/100))
            if FORBIDDEN and self.numOfBonds == 4:
                if self.orentation == "Vertical":
                    pygame.draw.line(screen, self.colour, (x1-int(0.5*offset), y1), (x2-int(0.5*offset),y2), int(LINEWIDTH*GRIDTILESIZE/100))
                    pygame.draw.line(screen, self.colour, (x1+int(0.5*offset), y1), (x2+int(0.5*offset), y2), int(LINEWIDTH*GRIDTILESIZE/100))
                    pygame.draw.line(screen, self.colour, (x1-(2*offset), y1), (x2-(2*offset),y2), int(LINEWIDTH*GRIDTILESIZE/100))
                    pygame.draw.line(screen, self.colour, (x1+(2*offset), y1), (x2+(2*offset), y2), int(LINEWIDTH*GRIDTILESIZE/100))
        

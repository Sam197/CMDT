import pygame
from classes import *  # pylint: disable=W0614
from config import *  # pylint: disable=W0614
import time
from math import floor
from tkinter import *  # pylint: disable=W0614
from tkinter import messagebox, filedialog
if SERVER_CLIENT_ENABLED:
    import client

pygame.init()  # pylint: disable=no-member

if not FORBIDDEN and BOND_LIMIT > 3:
    raise Exception("Can't have more than a triple bond...........")

def makeGrid():
    if SCREENX % GRIDTILESIZE != 0 or SCREENY % GRIDTILESIZE != 0:
        raise Exception("Screen not divisble by TileSize")
    masterGrid = []
    for y in range(0, SCREENY, GRIDTILESIZE):
        row = []
        for x in range(0, SCREENX, GRIDTILESIZE):
            row.append(Tile(x, y))  
        masterGrid.append(row)
        del row

    return masterGrid

def outList(grid, entities):
    gridOut = []
    for row in grid:
        for obj in row:
            if obj.txt != None:
                gridOut.append(f"{obj.x}-{obj.y}-{obj.txt}-\n")
    entitiesOut = []
    for obj in entities:
        entitiesOut.append(f"{obj.startPos[0]}-{obj.startPos[1]}-{obj.endPos[0]}-{obj.endPos[1]}-{obj.numOfBonds}-\n")
    
    return gridOut, entitiesOut

def inString(fullList):
    grid = makeGrid()
    entities = []
    for i, item in enumerate(fullList):
        if i == 0:
            continue
        if item == "~\n":
            ix = i
            break
        else:
            curObj = item.split("-")
            newObj = TiledAtom(int(curObj[0]), int(curObj[1]), curObj[2])
            grid[newObj.gridY][newObj.gridX] = newObj

    for i in range(ix+1, len(fullList)):
        curEntity = fullList[i].split("-")
        entities.append(Line((int(curEntity[0]),int(curEntity[1])), (int(curEntity[2]),int(curEntity[3])), int(curEntity[4])))
    
    return grid, entities

# def inString(fullList):
#     grid = []
#     row = []
#     entities = []
#     x = 0
#     y = 0
#     for i, item in enumerate(fullList):
#         if i == 0:
#             continue
#         if item == "~\n":
#             ix = i
#             break
#         elif item == "ET\n":
#             row.append(Tile(x*GRIDTILESIZE, y*GRIDTILESIZE))
#         elif item == "NL\n":
#             grid.append(row)
#             del row
#             row = []
#             y += 1
#             x = -1
#         else:
#             row.append(TiledAtom(x*GRIDTILESIZE, y*GRIDTILESIZE, item[:-1]))
#         x += 1

#     for i in range(ix+1, len(fullList)):
#         curEntity = fullList[i].split("-")
#         entities.append(Line((int(curEntity[0]),int(curEntity[1])), (int(curEntity[2]),int(curEntity[3])), int(curEntity[4])))
    
#     return grid, entities

def save(grid, entities):
    gOut, eOut = outList(grid, entities)
    root = Tk()
    root.withdraw()
    root.filename = filedialog.asksaveasfile(mode = "w")
    try:
        with open(root.filename.name, 'w') as outFile:
            outFile.write(f"{SCREENX}-{SCREENY}-\n")
            outFile.writelines(gOut)
            outFile.write("~\n")
            outFile.writelines(eOut)
        messagebox.showinfo('Save', 'Saved Sucessfully')
    except:
        messagebox.showinfo("Did Not Save", "Unspecified Error") 
    root.destroy()

def load():

    root = Tk()
    root.withdraw()
    root.filename = filedialog.askopenfile(mode = "r")
    name = root.filename.name
    with open(name, "r") as inFile:
        stringList = inFile.readlines()
    root.destroy()
    x, y, _ = stringList[0].split("-")
    if int(x) > SCREENX or int(y) > SCREENY:
        raise Exception("Loaing a bigger file into smaller screen bounds")
    return inString(stringList)

def checkSave(grid, entities):
    pass

def main():

    screen = pygame.display.set_mode((SCREENX,SCREENY))
    masterGrid = makeGrid()
    entities = []
    free_Entity = None
    newAtom = False
    newLine = False
    drawLine = False
    bondEdit = False
    reverseTxt = False
    erase = False

    #masterGrid, entities = load()

    clock = pygame.time.Clock()
    running = True

    while running:

        clock.tick(60)
        start = time.time()
        screen.fill(WHITE)

        for row in masterGrid:
            for obj in row:
                if not bondEdit:
                    if not erase:
                        obj.isCollide(screen, pygame.mouse.get_pos()) 
                    elif erase and obj.txt != None:
                        obj.isCollide(screen, pygame.mouse.get_pos())
                obj.draw(screen)    

        for obj in entities:
            obj.draw(screen)
            obj.endsCollide(masterGrid, screen)
            if bondEdit or erase:
                obj.isCollide(pygame.mouse.get_pos())



        for event in pygame.event.get():
            if event.type == pygame.QUIT:   # pylint: disable=no-member
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:        # pylint: disable=no-member   
                left, middle, right = pygame.mouse.get_pressed()
                #if (left and newAtom) or (left and newLine) or (left and drawLine) or (left and reverseTxt):
                if left:
                    if bondEdit or erase:
                        for obj in entities:
                            if obj.isCollide(pygame.mouse.get_pos()):
                                if bondEdit:
                                    obj.update_Bond_Number()
                                elif erase:
                                    entities.remove(obj)
                    if not bondEdit:
                        x, y = pygame.mouse.get_pos()                        
                        for ly, row in enumerate(masterGrid):
                            for lx, obj in enumerate(row):
                                if obj.isCollide(screen, (x,y)):
                                    if newAtom:
                                        masterGrid[ly][lx] = TiledAtom(obj.x, obj.y, free_Entity.txt)
                                        free_Entity = None            
                                        newAtom = False
                                    elif newLine and not drawLine:
                                        free_Entity = Line(obj.boundsRect.center)
                                        obj.hasLine = True
                                        drawLine = True
                                    elif newLine and drawLine:
                                        entities.append(Line(free_Entity.startPos, obj.boundsRect.center))
                                        obj.hasLine = True
                                        free_Entity = Line(obj.boundsRect.center)
                                    elif reverseTxt:
                                        obj.reverseTxt()
                                    elif erase:
                                        masterGrid[obj.gridY][obj.gridX] = Tile(floor(x/GRIDTILESIZE)*GRIDTILESIZE, floor(y/GRIDTILESIZE)*GRIDTILESIZE)                    
                if right:
                    newAtom = False
                    newLine = False
                    drawLine = False
                    reverseTxt = False
                    bondEdit = False
                    erase = False
                    free_Entity = None

            if event.type == pygame.KEYDOWN:        # pylint: disable=no-member
                free_Entity = None
                newLine = False
                drawLine = False
                newAtom = False
                bondEdit = False
                reverseTxt = False
                erase = False
                if event.key == pygame.K_s and event.mod & pygame.KMOD_CTRL:       # pylint: disable=no-member
                    save(masterGrid, entities)
                elif event.key == pygame.K_o and event.mod & pygame.KMOD_CTRL:      # pylint: disable=no-member
                    masterGrid, entities = load()
                elif event.key == pygame.K_l:     # pylint: disable=no-member
                    if newLine:
                        newLine = False
                        free_Entity = None
                    else:
                        newLine = True
                        free_Entity = Dot()              
                elif event.key == pygame.K_c:       # pylint: disable=no-member
                    free_Entity = Atom(0,0, "C")
                    newAtom = True
                elif event.key == pygame.K_o and event.mod & pygame.KMOD_SHIFT:     # pylint: disable=no-member
                    free_Entity = Atom(0,0, "OH")
                    newAtom = True
                elif event.key == pygame.K_o:       # pylint: disable=no-member 
                    free_Entity = Atom(0,0, "O")
                    newAtom = True
                elif event.key == pygame.K_n:       # pylint: disable=no-member
                    free_Entity = Atom(0,0, "N")
                    newAtom = True
                elif event.key == pygame.K_a:
                    free_Entity = Atom(0,0, "OOH")
                    newAtom = True
                elif event.key == pygame.K_b:       # pylint: disable=no-member
                    if bondEdit:
                        bondEdit = False
                        for obj in entities:
                            obj.colour = BLACK
                    else:
                        bondEdit = True
                        for row in masterGrid:
                            for obj in row: obj.selected = False
                elif event.key == pygame.K_r:       # pylint: disable=no-member
                    reverseTxt = True
                elif event.key == pygame.K_e:       # pylint: disable=no-member
                    for row in masterGrid:
                        for obj in row: obj.selected = False
                    erase = True



        if free_Entity != None:
            free_Entity.update(pygame.mouse.get_pos())
            free_Entity.draw(screen)

        pygame.display.flip()
        try:
            pygame.display.set_caption(str(int(1/(time.time()-start))))
        except:
            pass

    
    #save(masterGrid, entities)

if __name__ == "__main__":
    main()
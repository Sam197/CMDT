from config import *  # pylint: disable=W0614
from classes import *  # pylint: disable=W0614
import time
from math import floor
from tkinter import *  # pylint: disable=W0614
from tkinter import messagebox, filedialog

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

def getMinSize(grid, entities):
    maxX = 0
    maxY = 0
    for row in grid:
        for obj in row:
            if obj.txt != None:
                if obj.gridX > maxX:
                    maxX = obj.gridX
                if obj.gridY > maxY:
                    maxY = obj.gridY
    
    for obj in entities:
        if obj.startGridX > maxX:
            maxX = obj.startGridX
        if obj.endGridX > maxX:
            maxX = obj.endGridX
        if obj.startGridY > maxY:
            maxY = obj.startGridY
        if obj.endGridY > maxY:
            maxY = obj.endGridY

    return maxX, maxY

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
    root.filename = filedialog.asksaveasfile(mode = "w", defaultextension = ".txt")
    mX, mY = getMinSize(grid, entities)
    try:
        s = time.time()
        with open(root.filename.name, 'w') as outFile:
            outFile.write(f"{mX*GRIDTILESIZE}-{mY*GRIDTILESIZE}-\n")
            outFile.writelines(gOut)
            outFile.write("~\n")
            outFile.writelines(eOut)
        print(time.time()-s)
        messagebox.showinfo('Save', 'Saved Sucessfully')
    except:
        messagebox.showinfo("Did Not Save", "Unspecified Error") 
    root.destroy()

def load():

    root = Tk()
    root.withdraw()
    root.filename = filedialog.askopenfile(mode = "r")
    name = root.filename.name
    s = time.time()
    with open(name, "r") as inFile:
        stringList = inFile.readlines()
    root.destroy()
    x, y, _ = stringList[0].split("-")
    if int(x) > SCREENX or int(y) > SCREENY:
        raise Exception("Loaing a bigger file into smaller screen bounds")
    pl = inString(stringList)
    print(time.time()-s)
    return pl

def checkSave(grid, entities):
    root = Tk()
    root.withdraw()
    res =  messagebox.askyesnocancel("New File", "Would you like to save the current file?")
    if res != None:
        if res:
            save(grid, entities)
        grid = makeGrid()
        entities = []
    root.destroy()
    return grid, entities
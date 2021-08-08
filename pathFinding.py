#######################
#path finding 
#breadth first grapgh search for AIs
##########################

def pathFindng(AI,destination,grid):
    pathList = [[AI.gridPosition]]
    counter = 0
    while counter < 30000:
        counter +=1
        frontierPath = pathList.pop(0)
        #move in all directions 
        for move in [(0,1),(0,-1),(1,0),(-1,0)]:
            newPath = doMove(frontierPath,move)
            if isLegalPath(newPath,grid):
                pathList.append(newPath)
                if isSol(newPath,destination):
                    #real will change ai destination
                    AI.path = newPath
                    return newPath

def doMove(frontierPath,move):
    frontier = frontierPath[-1]
    newFrontier = (frontier[0]+move[0],frontier[1]+move[1])
    newPath = frontierPath + [newFrontier]
    return newPath

def isLegalPath(path,grid):
    frontier = path[-1]
    return onGrid(frontier,grid) and noCollision(frontier,grid)

def noCollision(frontier,grid):
    row,col = frontier
    return grid[row][col]!=1

def onGrid(frontier,grid):
    row,col = frontier
    return (row>=0 and
            col>=0 and
            row<len(grid) and
            col<len(grid[0]))

def isSol(path,destination):
    frontier = path[-1]
    return frontier == destination 

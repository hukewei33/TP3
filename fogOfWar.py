#############################
#fog of war funcs
#recursive floodfill function to determine fog of war
########################
import copy

def fow (grid,gridCoord):
    #player can look in all 4 directions in the start of func
   return fowHelper(grid,gridCoord,[(0,1),(0,-1),(1,0),(-1,0)],3)

def fowHelper(grid,gridCoord,allowed,depth):
    if depth == 0:
        return {gridCoord}
    else:
        subset = {gridCoord}
        #create list of explorable direction
        newAllowed = []
        for move in allowed:
            #do move
            newRow,newCol = gridCoord[0]+move[0],gridCoord[1]+move[1]
            #if move is legal
            if onGrid(grid,newRow,newCol) and grid[newRow][newCol]!=1 :
                #record that move as valid
                newAllowed.append(move)
        #explore allowed move further with rules modified
        for allowedMove in newAllowed:
            (allowedRow,allowedCol) = (gridCoord[0]+allowedMove[0],
            gridCoord[1]+allowedMove[1])
            #modify newAllowed so light does not travel back
            modifiedNewAllowed= copy.copy(newAllowed)
            oppositeDirection = (allowedMove[0]*-1,allowedMove[1]*-1)
            if oppositeDirection in modifiedNewAllowed:
                modifiedNewAllowed.remove(oppositeDirection)
            #add set of grid visible from that direciton into subset
            subset=subset.union(fowHelper(grid,(allowedRow,allowedCol),modifiedNewAllowed,depth-1))
        return subset

def onGrid(grid,row,col):
    return (row>=0 and
            row<len(grid) and
            col >=0 and
            col <len(grid[0]))
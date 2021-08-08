import pathFinding
import random
import bullets
import fogOfWar
############################
#Player and AI design
# provides framework for movement, and decicison making for AI and companion 
########################## 
#from 15-112 hw starterFiles http://www.cs.cmu.edu/~112/notes/hw9.html
import decimal
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

##############

class players(object):
    def __init__(self, startGrid,startCoord,radius):
        #grid position is tuple of (row,col)
        self.gridPosition = startGrid
        self.coordPosition = startCoord
        self.health = 2
        self.radius = radius
        self.reload =0
        # h for horizontal and v for verticle 
        self.bodyOrientation = "h"
        self.gunAngle = 0
        self.healCounter = 100

    @staticmethod
    def heal(self):
        if self.health <2:
            self.healCounter-=1
            if self.healCounter <0:
                self.healCounter = 100
                self.health+=1

class men(players):
    def __init__(self,startGrid,startCoord,radius,canSee):
        super().__init__(startGrid,startCoord,radius)
        #self.canSee will be updated to include list/set of visible grids
        self.canSee = canSee

class AI(players):   
    def __init__(self,startGrid,startCoord,radius,path = []):
        super().__init__(startGrid,startCoord,radius)
        #self.nextMove = None
        self.path = path
        self.objective = None
        self.canShoot = None
        self.alive = True

class Corpses(players):
    def __init__(self,startGrid,startCoord,radius,bodyOrientation,gunAngle):
        super().__init__(startGrid,startCoord,radius)
        #dispears after timer runs out
        self.timer = 99
        self.bodyOrientation = bodyOrientation
        self.gunAngle = gunAngle
    
########################################
#movement codes
#####################################

def AIMovement(ai,margin,gridWidth,gridHeight,gridMap):
    if len(ai.path)>1:
        startPoint = ai.path[0]
        endPoint = ai.path[1]
        #get dRow,dCol of movement
        gridMovement = (endPoint[1]-startPoint[1],endPoint[0]-startPoint[0])
        #move 1 pixel per movement counter
        (dx,dy)= gridMovement
        #change body orintation
        if dy ==0:
            ai.bodyOrientation = "h"
        else:
            ai.bodyOrientation = "v"
        #move 3 pixels per timer fired
        for _ in range (3):
            (x,y) = ai.coordPosition
            #implement change
            ai.coordPosition = (x+dx,y+dy)
            ai.gridPosition = coordToGrid(ai.coordPosition,margin,gridWidth,gridHeight)
            #check if AI has reached endpoint
            if ai.coordPosition == gridToCoord(endPoint,margin,gridWidth,gridHeight):
                #AI has reached end point, end point is now start point 
                ai.path.pop(0)
                #recheck AI's line of sight
                ai.canShoot = fogOfWar.fow(gridMap,ai.gridPosition)
                break 

def coordToGrid(coord,margin,gridWidth,gridHeight):
    (x,y) = coord
    row = int((y-margin)/gridHeight)
    col = int((x-margin)/gridWidth)
    return (row,col)

def gridToCoord(grid,margin,gridWidth,gridHeight):
    (row,col) = grid
    x = margin + (col+0.5)*gridWidth
    y = margin + (row+0.5)*gridHeight
    return (roundHalfUp(x),roundHalfUp(y))   

#############################################
# AI decision making codes
##########################################

def AIStatergy(ais,menOnPoint):
    if menOnPoint:
        for ai in ais:
            ai.objective = "hold point"
    else:
        #determine ai with lowest health to guard the point
        lowestHealthIndex = 0
        for i in range (len(ais)):
            if ais[i].health < ais[lowestHealthIndex].health:
                lowestHealthIndex = i
        #make other AIs patrol, make lowest health AI hold point
        for ai in ais:
            ai.objective = "patrol"
        if len(ais)>0:
            ais[lowestHealthIndex].objective = "hold point"

def implementChoice(ai,player,grid,rallyPoints,shots,companion):
    isNearShot,shotToChase = nearShots(ai,shots,"men")
    #first priority is self preservation 
    
    if companion.alive and  ai.health<1 and isNear(ai,companion,4):
        runAway(ai,companion,grid)
    elif ai.health<1 and isNear(ai,player,4):
        runAway(ai,player,grid)
    #second higest priority is combat when near player or companion, overrides objective
    elif companion.alive and isNear(ai,companion,4):
        chase(ai,companion.gridPosition,grid)
    elif isNear(ai,player,4):
        chase(ai,player.gridPosition,grid)
    #thrid highest priority is to chase shots
    elif isNearShot:
        chase(ai,shotToChase.grid,grid)
    #follow objectives
    elif ai.objective == "hold point":
        holdPoint(ai,grid,rallyPoints)
    elif ai.objective == "patrol":
        patrol(ai,grid)

###################################
#companion code
####################################

def companionDecision(companion,player,AIs,shots,grid):
    isNearShot,shotToChase = nearShots(companion,shots,"AI")
    isNearAI,AIToChace = nearAI(companion,AIs)
    #first priority is self preservation
    if companion.health<1 and isNearAI:
        runAway(companion,AIToChace,grid)
    #second is to chase AI
    elif isNearAI:
        chase(companion,AIToChace.gridPosition,grid)
    #third is to chase shots
    elif isNearShot:
        chase(companion,shotToChase.grid,grid)
    #fourth is to accompany player
    else:
        accompany(companion,player,grid)

def nearAI(companion,AIs):
    for ai in AIs:
        if isNear(companion,ai,4):
            return (True,ai)
    return (False,None)

def accompany(companion,player,grid):
    #if player is very near, randomly go to a point near it
    if isNear(companion,player,2):
        guard(companion,player,grid)
    #if player is slightly further, move towards player
    elif isNear(companion,player,5):
        chase(companion,player.gridPosition,grid)
    #if player is too far, just randomly patrol
    else:
        patrol(companion,grid)

def guard(companion,player,grid):
    destination = patrolDestination(companion,grid,3)
    #research for destination if destination is on player
    while player.gridPosition==grid[destination[0]][destination[1]]:
        destination = patrolDestination(companion,grid,3)
    pathFinding.pathFindng(companion,destination,grid)

#########################################
#objective implementation 
#########################################
def runAway(ai,player,grid):
    #only set path is current path destination is near player
    dr,dc = ai.path[-1]
    pr,pc = player.gridPosition
    if  (pr-dr)**2+(pc-dc)**2<4**2:
        runDestination = None
        while runDestination == None:
            r,c = patrolDestination(ai,grid,5)
            #make sure distination is not near player
            if (pr-r)**2+(pc-c)**2>4**2:
                runDestination=(r,c)
        pathFinding.pathFindng(ai,runDestination,grid) 

def holdPoint(ai,grid,rallyPoints):
    #only assign path if there is not path currently
    if len(ai.path) <2:
        row,col = ai.gridPosition 
        #if AI not on control point, move to control point
        if grid[row][col] != 2:
            #find out which quardrant is it in
            if row<len(grid)//2:
                #1 or 2 quad
                if col < len(grid[0])//2:
                    quad = 2
                else: quad =1
            else:
                if col < len(grid[0])//2:
                    quad = 3
                else: quad =4   
            #go to the corresponding rallypoints
            destination = rallyPoints[quad-1]
            pathFinding.pathFindng(ai,destination,grid)
        #if AI in control point, randomly patrol control point
        else:
            destination = patrolDestination(ai,grid,5,"hill")
            pathFinding.pathFindng(ai,destination,grid) 

#rush player
def chase(ai,des,grid):
    pathFinding.pathFindng(ai,des,grid)

def patrol(ai,grid):
    #only assign path if there is not path currently
    if len(ai.path) <2:
        destination = patrolDestination(ai,grid,5)
        pathFinding.pathFindng(ai,destination,grid)        

##############################################
# helper funcs
##############################################
    
def nearShots(ai,cues,enemy):
    r1,c1 = ai.gridPosition
    for cue in cues:
        if cue.type == "shot" and cue.firer == enemy:
            r2,c2 = cue.grid
            if (r1-r2)**2+(c1-c2)**2<=6**2:
                return (True,cue)
    return (False,None)


def nearBullets(ai,bullets):
    r1,c1 = ai.gridPosition
    for bullet in bullets:
        r2,c2 = bullet.gridPosition
        if (r1-r2)**2+(c1-c2)**2<=6**2:
            return (True,bullet)
    return (False,None)

def isNear(ai,player,x):
    r1,c1 = ai.gridPosition
    r2,c2 = player.gridPosition
    #check if they are within x blocks away
    return (r1-r2)**2+(c1-c2)**2<=x**2

def patrolDestination(ai,grid,x,condition=None):
    row,col = ai.gridPosition
    while True:
        #generate
        dR = random.randint(-x,x)
        dC = random.randint(-x,x)
        newGrid = (row+dR,col+dC)
        if isLegalCoord(newGrid,grid,condition):
            return newGrid

def isLegalCoord(coord,grid,condition):
    if condition == None:
        return onGrid(coord,grid) and noCollision(coord,grid)
    elif condition == "hill":
        return onGrid(coord,grid) and noCollision(coord,grid) and inHill(coord,grid)

def noCollision(coord,grid):
    row,col = coord
    return grid[row][col]!=1

def inHill(coord,grid):
    row,col = coord
    return grid[row][col]==2

def onGrid(coord,grid):
    row,col = coord
    return (row>=0 and
            col>=0 and
            row<len(grid) and
            col<len(grid[0]))

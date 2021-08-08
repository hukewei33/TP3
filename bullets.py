##########################
#bullets
#object and funciton for buller movement,collision and hit detection
#########################

import math

class bullets(object):
    def __init__(self,startCoord,angle,firer,gridPosition):
        self.coord = startCoord
        self.angle = math.radians(angle)
        self.firer = firer
        self.gridPosition = gridPosition

    def moveBullet(self):
        x,y = self.coord
        #bullet moves by 15 pixels lenght per timerfired
        dis = 15       
        newX = x + (math.cos(self.angle)*dis)
        newY = y - (math.sin(self.angle)*dis)
        self.coord = (newX,newY)

def bulletCollision(bulletGrid,grid):
    row,col = bulletGrid
    if grid[row][col]==1:
        return True
    return False

def bulletHit(bullet,men,companion,AIs,playerSize):
    x,y = bullet.coord
    if bullet.firer == "men":
        return bulletNearEnough(x,y,AIs,playerSize)   
    else:
        if companion.alive:
            return bulletNearEnough(x,y,[men,companion],playerSize)
        else:
            return bulletNearEnough(x,y,[men],playerSize)
        
def bulletNearEnough(x,y,targetList,targetSize):
    hitTarget = False
    for target in targetList:
        if target.coordPosition == None: continue 
        tX,tY = target.coordPosition
        if (x-tX)**2+(y-tY)**2 <= targetSize**2:
            target.health-=1
            hitTarget = True            
    return hitTarget
############################
#this is the main game file
##########################
#from PIL import Image
from tkinter import *
import random,math,copy
from cmu_112_graphics import *
#cmu_112_graphics from http://www.cs.cmu.edu/~112/notes/notes-animations-part1.html

#from 15-112 hw starterFiles http://www.cs.cmu.edu/~112/notes/hw9.html
import decimal
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

#################
#import game files
####################
import gameMap
import playerAndAI
import fogOfWar
import pathFinding
import bullets
import cues

#########################
#app structure
#######################

class GameMode(Mode):

    def startGame (mode,mapInfo,hasCompanion):
        #load map
        # to change to map2, change line below to: mode.gridMap = gameMap.mapGrid(gameMap.map2,gameMap.map2RallyPoints)
        #mode.gridMap = gameMap.mapGrid(gameMap.map2,gameMap.map2RallyPoints)
        mode.gridMap = gameMap.mapGrid(mapInfo[0],mapInfo[1])
        #store of map info
        mode.margin = 30
        mode.noRows=len(mode.gridMap.grid)
        mode.noCols=len(mode.gridMap.grid[0])
        mode.mapWidth = mode.width - 2* mode.margin
        mode.mapHeight = mode.height - 2*mode.margin
        mode.gridHeight = mode.mapHeight//mode.noRows
        mode.gridWidth = mode.mapWidth//mode.noCols*1.5
        #create player at bottom right of map
        menStartingGrid = (mode.noRows-1,mode.noCols-1)
        menStartingCoord = mode.gridToCoord(menStartingGrid)
        #radius of men and AI = 0.4 of smallest demention of grid
        mode.chrRadius = int(min(mode.gridWidth,mode.gridHeight)*(2/7))
        #decide what the men can see initally
        menCanSee = fogOfWar.fow(mode.gridMap.grid,menStartingGrid)
        mode.men = playerAndAI.men(menStartingGrid,menStartingCoord,mode.chrRadius,menCanSee)
        mode.men.health=3
        #initialise men's companion
        mode.hasCompanion = hasCompanion
        if hasCompanion:
            companionStartingGrid = (mode.noRows-2,mode.noCols-1)
            comapnionStartingCoord = mode.gridToCoord(companionStartingGrid)
            mode.companion = playerAndAI.AI(companionStartingGrid,comapnionStartingCoord,mode.chrRadius)
            mode.companion.health=3
        else:
            mode.companion = playerAndAI.AI(None,None,None)
            mode.companion.alive = False
        #initialise 3 AI players at the other 3 corners of the map
        AI1StartingGrid = (0,0)
        AI1StartingCoord = mode.gridToCoord(AI1StartingGrid)
        AI2StartingGrid = (0,mode.noCols-1)
        AI2StartingCoord = mode.gridToCoord(AI2StartingGrid)
        AI3StartingGrid = (mode.noRows-1,0)
        AI3StartingCoord = mode.gridToCoord(AI3StartingGrid)
        #Store AIs in a list
        mode.AIs = [playerAndAI.AI(AI1StartingGrid,AI1StartingCoord,mode.chrRadius),
                    playerAndAI.AI(AI2StartingGrid,AI2StartingCoord,mode.chrRadius),
                    playerAndAI.AI(AI3StartingGrid,AI3StartingCoord,mode.chrRadius)]
        #initially no one is on point
        mode.menOnPoint = False
        mode.AIOnPoint = False
        #store AI corpses in a list
        mode.corpses = []
        #store visual cues and track prints in a list
        mode.cues=[]
        mode.trackPrints = []
        #initialise crosshair
        mode.crossHairX,mode.crossHairY = 0,0
        #initlaise list of bullets
        mode.bullets = []
        #game move infomation
        mode.menPoints=0
        mode.AIPoints=0
        mode.timeLeft = 600
        #load images
        #image from https://sftextures.com/2014/07/22/brown-mud-wet-dirt-soil-with-water-spots-and-footsteps-from-river-beach-seamless-texture/
        mode.backgroundImageO = mode.loadImage("mud1.jpg")
        mode.backgroundImage= mode.scaleImage(mode.backgroundImageO,mode.width/mode.backgroundImageO.size[1] )
        #image from https://www.amazon.com/Backdrop-Digital-Artificial-Background-Photography/dp/B07CZF8JMY
        mode.grass1 = mode.loadImage("grass2.jpg")
        mode.grass1 = mode.grass1.crop((0,0,mode.gridWidth,mode.gridHeight))
        mode.grass2 = mode.loadImage("grass1.png")
        mode.grass2 = mode.grass2.crop((0,0,mode.gridWidth,mode.gridHeight))
        #cheats
        mode.godMode = False
        mode.app._root.configure(cursor='none')
        #starting Cues
        mode.startCueTimer = 15
        #sidescrolling
        mode.scrollX = mode.mapWidth//2
        mode.scrollMarginX = mode.mapWidth//2
        mode.makePlayerVisible()

    def appStarted(mode):
        mode.gameStarted = False
        # 0 represents mouse in left half, 1 is right half for landing screen
        mode.mouseHalf=0
        #mode.startGame()
        #image from https://www.wearethemighty.com/articles/6-massive-tank-battles-from-us-history
        mode.tank1O= mode.loadImage("tank1.png")
        mode.tank1W,mode.tank1H = mode.tank1O.size
        mode.tank1 = mode.scaleImage(mode.tank1O,((mode.width)/mode.tank1H)**3*3/4)
        mode.tank2O= mode.loadImage("tank2.png")
        mode.tank2 = mode.scaleImage(mode.tank2O,((mode.width)/mode.tank1H)**3*3/4)
        mode.rightTanks= [mode.tank1,mode.tank2]
        #image from https://commons.wikimedia.org/wiki/File:Challenger_2_main_battle_tank_on_Hohne_Ranges,_Germany.jpg
        mode.tank3O= mode.loadImage("tank3.png")
        mode.tank3W,mode.tank3H = mode.tank3O.size
        mode.tank3 = mode.scaleImage(mode.tank3O,((mode.width)/mode.tank3H))
        mode.tank4O= mode.loadImage("tank4.jpg")
        mode.tank4 = mode.scaleImage(mode.tank4O,((mode.width)/mode.tank3H))
        mode.leftTanks= [mode.tank4,mode.tank3]

    def sizeChanged(mode):
        mode.tank1 = mode.scaleImage(mode.tank1O,((mode.width)/mode.tank1H)**3*3/4)
        mode.tank2 = mode.scaleImage(mode.tank2O,((mode.width)/mode.tank1H)**3*3/4)
        mode.rightTanks= [mode.tank1,mode.tank2]
        #image from https://commons.wikimedia.org/wiki/File:Challenger_2_main_battle_tank_on_Hohne_Ranges,_Germany.jpg
        mode.tank3 = mode.scaleImage(mode.tank3O,((mode.width)/mode.tank3H)*1.3)
        mode.tank4 = mode.scaleImage(mode.tank4O,((mode.width)/mode.tank3H)*1.3)
        mode.leftTanks= [mode.tank4,mode.tank3]
        if mode.gameStarted:
            mode.backgroundImage= mode.scaleImage(mode.backgroundImageO,mode.width/mode.backgroundImageO.size[1])

    #######################################
    #player movements
    ##########################################

    def keyPressed(mode,event):
        if not mode.gameStarted:
            if event.key == "Space":
                mode.app.setActiveMode(mode.app.tutorial)
                mode.app.tutorial.appStarted()
        else:
            #each movement moves player by a third of its radius
            m = mode.chrRadius//3
            if event.key =="Up" or event.key =="w":
                mode.tryToMove(mode.men,(0,-m))
                mode.men.bodyOrientation = "v"
            elif event.key == "Down"or event.key =="s":
                mode.tryToMove(mode.men,(0,m))
                mode.men.bodyOrientation = "v"
            elif event.key == "Left"or event.key =="a":
                mode.tryToMove(mode.men,(-m,0))
                mode.men.bodyOrientation = "h"
            elif event.key == "Right"or event.key =="d":
                mode.tryToMove(mode.men,(m,0))
                mode.men.bodyOrientation = "h"
            #cheats
            elif event.key=="g":
                mode.godMode= not mode.godMode
            elif event.key =="h":
                mode.app.setActiveMode(mode.app.tutorial)
                mode.app.tutorial.appStarted()
            elif event.key == "l":
                mode.app.setActiveMode(mode.app.lose)
            elif event.key == "k":
                mode.app.setActiveMode(mode.app.win)

    def tryToMove(mode,obj,movement):
        objX,objY = obj.coordPosition
        dx,dy = movement
        newX,newY = objX+dx,objY+dy
        newCoords = (newX,newY)
        #iterate through 4 slides and 4 corners of object to avoid clipping
        for i in [-1,0,1]:
            changeX = i*mode.chrRadius
            for j in [-1,0,1]:
                changeY = j*mode.chrRadius
                if not (mode.inMap((newX+changeX,newY+changeY)) and
                    mode.noCollision((newX+changeX,newY+changeY))):
                    return None
        #change character location
        obj.coordPosition = newCoords
        newGrid= mode.CoordToGrid(newCoords)
        obj.gridPosition = newGrid
        #after each successful move, update visible blocks
        obj.canSee = fogOfWar.fow(mode.gridMap.grid,newGrid)
        #create trackprint
        mode.trackPrints.append(cues.tracks(newCoords,newGrid,"track",mode.men.bodyOrientation))
        #side scroll
        mode.makePlayerVisible()

    #adapted from http://www.cs.cmu.edu/~112/notes/notes-animations-part2.html#events
    def makePlayerVisible(mode):
        playerX = mode.men.coordPosition[0]
        playerY = mode.men.coordPosition[1]
        # scroll to make player visible as needed
        if (playerX < mode.scrollX + mode.scrollMarginX):
            mode.scrollX = playerX - mode.scrollMarginX
        if (playerX > mode.scrollX + mode.mapWidth - mode.scrollMarginX):
            mode.scrollX = playerX - mode.mapWidth + mode.scrollMarginX

    def noCollision(mode,newCoords):
        row,col = mode.CoordToGrid(newCoords)
        return mode.gridMap.grid[row][col]!=1

    ###########################################
    #shooting and bulltets
    ###########################################

    def mouseMoved(mode,event):
        if not mode.gameStarted:
            if event.x>mode.width//2:
                mode.mouseHalf=1
            else:
                mode.mouseHalf=0
        elif mode.gameStarted:
            mode.crossHairX = event.x
            mode.crossHairY = event.y
            #orientate gun
            x,y = mode.men.coordPosition
            yDiff = y-event.y
            xDiff = event.x-x+mode.scrollX
            if xDiff == 0:
                if yDiff >0:
                    mode.men.gunAngle = math.radians(90)
                else:
                    mode.men.gunAngle = math.radians(270)
            else:
                angle = math.degrees(math.atan(yDiff/xDiff))
                if xDiff <0:
                    angle +=180
                mode.men.gunAngle = math.radians(angle)

    def mousePressed(mode,event):
        if not mode.gameStarted:
            if event.x>mode.width//2:
                mode.startGame(gameMap.map1,False)
                mode.gameStarted = True
            else:
                mode.startGame(gameMap.map2,True)
                mode.gameStarted = True

        if mode.gameStarted:
            #gun must be reloaded before shooting
            if mode.men.reload==0 or mode.godMode:
                #define player position
                x,y = mode.men.coordPosition
                yDiff = y-event.y
                xDiff = event.x-x+mode.scrollX
                firerName = "men"
                if xDiff == 0:
                    if yDiff >0:
                        mode.shoot(x,y,90,firerName,mode.men,mode.men.gridPosition)
                    else:
                        mode.shoot(x,y,270,firerName,mode.men,mode.men.gridPosition)
                else:
                    angle = math.degrees(math.atan(yDiff/xDiff))
                    if xDiff <0:
                        angle +=180
                    mode.shoot(x,y,angle,firerName,mode.men,mode.men.gridPosition)
                mode.cues.append(cues.cue(mode.men.coordPosition,mode.men.gridPosition,"shot","men"))

    def shoot(mode,x,y,angle,firerName,firerObj,gridPosition):
        mode.bullets.append(bullets.bullets((x,y),angle,firerName,gridPosition))
        firerObj.reload = 10

    def lineOfFire(mode,AI,target):
        if AI.canShoot == None:
            return False
        else: return target.gridPosition in AI.canShoot

    def shootAtPlayer(mode,AI,target,firerName):
        #gun must be reloaded before shooting
        if AI.reload==0:
            spread = random.randint(-20,20)
            px,py = target.coordPosition
            ax,ay = AI.coordPosition
            xDiff,yDiff = px-ax,ay-py
            if xDiff == 0:
                if yDiff >0:
                    angle = 90+spread
                    mode.shoot(ax,ay,angle,firerName,AI,AI.gridPosition)
                else:
                    angle = 270+spread
                    mode.shoot(ax,ay,angle,firerName,AI,AI.gridPosition)
            else:
                angle = math.degrees(math.atan(yDiff/xDiff))+spread
                if xDiff <0:
                    angle +=180
                mode.shoot(ax,ay,angle,firerName,AI,AI.gridPosition)
            AI.gunAngle = math.radians(angle)
            mode.cues.append(cues.cue(AI.coordPosition,AI.gridPosition,"shot",firerName))

    #############################################
    #Timer fired
    #############################################
    def timerFired (mode):
        if mode.gameStarted:
            mode.bulletMoveAndHit()
            mode.checkGameConditions()
            mode.AIStatergyAndMovement()
            mode.companionMovement()
            mode.reloadReset()
            mode.checkForDeath()
            mode.decay()
            mode.createFootSteps()
            mode.healChrs()

    def healChrs(mode):
        playerAndAI.players.heal(mode.men)
        if mode.companion.alive:
            playerAndAI.players.heal(mode.companion)
        for ai in mode.AIs:
            playerAndAI.players.heal(ai)

    def createFootSteps(mode):
        for ai in mode.AIs:
            #only has 10% of creating footstep
            choice = random.randint(0,10)
            if playerAndAI.isNear(ai,mode.men,6) and choice ==1:
                newFootStep = cues.cue(ai.coordPosition,ai.gridPosition,"footstep")
                mode.cues.append(newFootStep)

    def decay(mode):
        #decay startCueTimer
        mode.startCueTimer-=1
        #decay corpses
        i = 0
        while i<len(mode.corpses):
            if mode.corpses[i].timer<0:
                mode.corpses.pop(i)
            else:
                mode.corpses[i].timer-=1
                i+=1
        #decay visual cues
        j = 0
        while j<len(mode.cues):
            if mode.cues[j].timer<1:
                mode.cues.pop(j)
            else:
                mode.cues[j].timer-=1
                j+=1
        #decay trackPrints
        k = 0
        while k<len(mode.trackPrints):
            if mode.trackPrints[k].timer<1:
                mode.trackPrints.pop(k)
            else:
                mode.trackPrints[k].timer-=1
                k+=1

    def checkForDeath(mode):
        #checks ai health
        j = 0
        while j< len(mode.AIs):
            if mode.AIs[j].health<0:
                #remove dead AI
                deadAI=mode.AIs.pop(j)
                #create Corpse
                mode.corpses.append(playerAndAI.Corpses(deadAI.gridPosition,deadAI.coordPosition,mode.chrRadius,
                deadAI.bodyOrientation,deadAI.gunAngle))
                #award player for points
                mode.menPoints += 50
            else:j+=1
        #check companion death
        if mode.hasCompanion and mode.companion.alive and mode.companion.health<0:
            mode.AIPoints+=50
            mode.companion.alive = False
            mode.corpses.append(playerAndAI.Corpses(mode.companion.gridPosition,mode.companion.coordPosition,mode.chrRadius,
                mode.companion.bodyOrientation,mode.companion.gunAngle))

    def bulletMoveAndHit(mode):
        i = 0
        while i <len(mode.bullets):
            mode.bullets[i].moveBullet()
            #check for bullet, remove health if hit
            # then check for collison, remove bullet if any conditions met
            r,c = mode.CoordToGrid(mode.bullets[i].coord)
            mode.bullets[i].gridPosition=(r,c)
            if (bullets.bulletHit(mode.bullets[i],mode.men,mode.companion,mode.AIs,mode.chrRadius) or
                not (mode.inMap(mode.bullets[i].coord))
                or mode.gridMap.grid[r][c]==1):
                impactBullet = mode.bullets.pop(i)
                #add explosion
                mode.cues.append(cues.cue(impactBullet.coord, impactBullet.gridPosition,"explosion"))
            else:i+=1

    def checkGameConditions(mode):
        mode.controlPoints()
        mode.lose()
        mode.win()
        mode.timeLeft-=1

    def AIStatergyAndMovement(mode):
        #decide on AI startergy
        playerAndAI.AIStatergy(mode.AIs,mode.menOnPoint)
        #move AI
        for AI in mode.AIs:
            #AI needs to be in center of grid before making desision
            if AI.coordPosition == mode.gridToCoord(AI.gridPosition):
                #check map and change path if required
                playerAndAI.implementChoice(AI,mode.men,mode.gridMap.grid,mode.gridMap.rallyPoints,mode.cues,mode.companion)
            playerAndAI.AIMovement(AI,mode.margin,mode.gridWidth,mode.gridHeight,mode.gridMap.grid)
            #create trackPrint
            mode.trackPrints.append(cues.tracks(AI.coordPosition,AI.gridPosition,"track",AI.bodyOrientation))
            #check if AI will shoot companion
            if mode.hasCompanion and mode.companion.alive and mode.lineOfFire(AI,mode.companion):
                mode.shootAtPlayer(AI,mode.companion,"AI")
                #check if AI will shoot player
            elif mode.lineOfFire(AI,mode.men):
                mode.shootAtPlayer(AI,mode.men,"AI")

    def companionMovement(mode):
        if mode.hasCompanion and mode.companion.health >-1:
            if mode.companion.coordPosition == mode.gridToCoord(mode.companion.gridPosition):
                playerAndAI.companionDecision(mode.companion,mode.men,mode.AIs,mode.cues,mode.gridMap.grid)
            #move the companion
            playerAndAI.AIMovement(mode.companion,mode.margin,mode.gridWidth,mode.gridHeight,mode.gridMap.grid)
            #create trackPrint
            mode.trackPrints.append(cues.tracks(mode.companion.coordPosition,mode.companion.gridPosition,"track",mode.companion.bodyOrientation))
            #check if conpanion will shoot at each ai
            for ai in mode.AIs:
                if mode.lineOfFire(mode.companion,ai):
                    mode.shootAtPlayer(mode.companion,ai,"men")

    #lets AI and players reload their guns
    def reloadReset(mode):
        if mode.men.reload>0:
            mode.men.reload-=1
        if mode.hasCompanion and mode.companion.reload>0:
            mode.companion.reload-=1
        for ai in mode.AIs:
            if ai.reload>0:
                ai.reload-=1

    ##################################
    #game mode codes
    ###################################
    #award points for capture
    def controlPoints(mode):
        mode.menOnPoint = (mode.gridMap.grid[mode.men.gridPosition[0]][mode.men.gridPosition[1]]==2 or
                            (mode.hasCompanion and mode.companion.alive and
                            mode.gridMap.grid[mode.companion.gridPosition[0]][mode.companion.gridPosition[1]]))
        mode.AIOnPoint = False
        for AI in mode.AIs:
            if mode.gridMap.grid[AI.gridPosition[0]][AI.gridPosition[1]]==2:
                mode.AIOnPoint = True
        if mode.menOnPoint and not mode.AIOnPoint: mode.menPoints +=1
        elif not mode.menOnPoint and  mode.AIOnPoint: mode.AIPoints +=1

    #win condition
    def win(mode):
        if len(mode.AIs)==0:
            mode.app.setActiveMode(mode.app.win)
        elif mode.timeLeft <0 and (mode.menPoints>mode.AIPoints):
            mode.app.setActiveMode(mode.app.win)

    #loose Condition
    def lose(mode):
        if mode.men.health <0 and not (mode.godMode):
            mode.app.setActiveMode(mode.app.lose)
        elif mode.timeLeft <0 and (mode.menPoints<=mode.AIPoints):
            mode.app.setActiveMode(mode.app.lose)

    #########################################
    #view to model and model to view func
    #########################################
    #returns the coord of the centre of the grid
    def gridToCoord(mode,grid):
        (row,col) = grid
        x = mode.margin + (col+0.5)*mode.gridWidth
        y = mode.margin + (row+0.5)*mode.gridHeight
        return (roundHalfUp(x),roundHalfUp(y))

    def CoordToGrid(mode,coord):
        (x,y) = coord
        row = int((y-mode.margin)/mode.gridHeight)
        col = int((x-mode.margin)/mode.gridWidth)
        return (row,col)

    def inMap(mode,newCoords):
        x,y = newCoords
        return ((x>mode.margin) and
                (x<mode.margin + mode.noCols*mode.gridWidth) and
                (y>mode.margin) and
                (y<mode.margin+mode.noRows*mode.gridHeight))

    #############
    #draw funcs
    #############

    def redrawAll(mode,canvas):
        if not mode.gameStarted:
            font = 'Arial 15 bold'
            canvas.create_text(mode.width//2,mode.height//2,
            text = "press 1 for small map, 2 for large map",font = font)
            mode.drawStartMenu(canvas)
        else:
            mode.drawBackGround(canvas)
            mode.drawMap(canvas)
            mode.drawTrackPrints(canvas)
            mode.drawMen(canvas)
            mode.drawCompanion(canvas)
            mode.drawAI(canvas)
            mode.drawCrosshair(canvas)
            mode.drawBullets(canvas)
            mode.drawScoreBoard(canvas)
            mode.drawCorpses(canvas)
            mode.drawCues(canvas)
            mode.drawHealthBar(canvas)
            mode.drawStartCue(canvas)

    def drawStartCue(mode,canvas):
        if mode.startCueTimer>0:
            #draw centerBox
            offset = mode.gridWidth*1
            x,y = mode.width/4,mode.height/2
            canvas.create_rectangle(x-offset,y-offset/2,x+offset,y+offset/2,width=0, fill = "salmon")
            canvas.create_text(x,y,text = "Capture This Way!",font ='Times 10 bold',width = offset,justify = "center")
            canvas.create_polygon(x-offset,y-offset/2,x-offset,y+offset/2,x-1.5*offset,y,width=0, fill = "salmon")
            #draw arrow pointing to player
            mode.drawPlayerCue(canvas)

    def drawPlayerCue(mode,canvas):
        x,y = mode.width//2,mode.height*3/4
        canvas.create_rectangle(x+2*mode.gridWidth,y+mode.gridHeight,x-2*mode.gridWidth,y-mode.gridHeight,width=0, fill = "cyan2")
        canvas.create_text(x,y,text = "Your Team is Here!",font ='Times 10 bold',width = 2*mode.gridWidth,justify = "center" )

    def drawStartMenu(mode,canvas):
        c1 = ["CadetBlue3","CadetBlue1"]
        c2 = ["orchid1","orchid3"]
        #change to image
        #canvas.create_rectangle(0,0,mode.width//2,mode.height,width = 0, fill = c2[mode.mouseHalf])
        canvas.create_image(mode.width*1/4, mode.height//2, image=ImageTk.PhotoImage(mode.leftTanks[mode.mouseHalf]))
        canvas.create_image(mode.width*3/4, mode.height//2, image=ImageTk.PhotoImage(mode.rightTanks[mode.mouseHalf]))
        #draw game title
        font1 = 'Times 25 bold'
        canvas.create_rectangle(1/4*mode.width,mode.height//20,3/4*mode.width,mode.height//4,width=0, fill ="seashell2")
        canvas.create_text(mode.width//2, mode.height*0.15,text = "Man VS Machine", font = font1)
        #box for help
        font2 = 'Times 15 bold'
        canvas.create_rectangle(1/4*mode.width,mode.height//3,3/4*mode.width,mode.height*(0.4),width=0, fill ="seashell2")
        canvas.create_text(mode.width//2, mode.height*0.3667, text = "Press [Space] for tutorial", font = font2)
        #game mode description
        offset = mode.width//4
        boxSize = mode.width//8
        for i in [-1,1]:
            canvas.create_rectangle(mode.width//2+i*offset-boxSize,
            mode.height*(0.75),mode.width//2+i*offset+boxSize,mode.height*(0.9),
            width = 0,fill ="seashell2" )
        font3= 'Times 13 bold'
        canvas.create_text(mode.width//2-offset, mode.height*(0.82),
        text = "Fight Together Easy", font = font3, width = 2*boxSize, justify = "center")
        canvas.create_text(mode.width//2+offset, mode.height*(0.82),
        text = "Fight Alone Hard", font = font3, width = 2*boxSize, justify = "center")

    def drawBackGround(mode,canvas):
        canvas.create_rectangle(0,0,mode.width,mode.height, fill = "green3")
        canvas.create_image(mode.width//2, mode.height//2+mode.margin//2, image=ImageTk.PhotoImage(mode.backgroundImage))

    def drawHealthBar(mode,canvas):
        x = mode.width//2
        y = int((1.5)*mode.margin+mode.mapHeight)
        xOffset = mode.width//4
        yOffset = mode.margin//2
        canvas.create_rectangle(x+xOffset,y-yOffset,x-xOffset,y+yOffset, width = 0, fill ="ivory3")
        menHealth = mode.men.health
        mode.displayHealth(canvas,"men",x-xOffset//2,y,menHealth)
        if mode.hasCompanion:
            comHealth = mode.companion.health
            mode.displayHealth(canvas,"companion",x+xOffset//2,y,comHealth)

    def displayHealth(mode,canvas,name,x,y,health):
        #whoose health?
        font = 'Arial 6 bold'
        canvas.create_text(x-mode.width//8,y,text = f"{name}'s Health",font = font, width = 60,anchor="w")
        #create healthbar
        yOffset = mode.margin//2
        canvas.create_rectangle(x,y-yOffset,x+mode.width//8,y+yOffset,width = 0,fill = "red")
        totalHealth = 4
        if health<-1: health = -1
        healthPercent = (health+1)/totalHealth
        canvas.create_rectangle(x,y-yOffset,x+mode.width//8*healthPercent,y+yOffset,width = 0,fill = "green")

    def drawTrackPrints(mode,canvas):
        #as footstep decay, its gets lighter
        color = ["sandy brown","tan2","chocolate2","chocolate3","tan4"]
        for track in mode.trackPrints:
            #only draw tracks if player see
            if track.grid  in mode.men.canSee:
                c = track.timer//10
                x,y = track.coord
                #sideScroller
                x=x-mode.scrollX
                r = mode.chrRadius
                if track.bodyOrientation =="h":
                    for i in [-1,1]:
                        canvas.create_line(x-r,y+i*r/3*2,x+r,y+i*r/3*2,width = 2,fill = color[c])
                else:
                    for i in [-1,1]:
                        canvas.create_line(x+i*r/3*2,y-r,x+i*r/3*2,y+r,width = 2,fill = color[c])

    def drawCues(mode,canvas):
        #as footstep decay, its gets lighter
        color = ["gray20","gray29","gray35","gray40","gray44"]
        for cue in mode.cues:
            x,y = cue.coord
            #sidescroller
            x=x-mode.scrollX
            r = mode.chrRadius//2
            if cue.type == "explosion" and cue.timer>44:
                mode.drawFire(canvas,x,y,r)
            elif cue.type == "shot" and cue.firer=="AI" and cue.timer>44:
                #canvas.create_oval(x-r,y-r,x+r,y+r,fill = "red",width = 0)
                mode.drawShot(canvas,x,y,mode.chrRadius*2/3)
            #only draw footsteps and bangs if player can't see
            if cue.grid not in mode.men.canSee:
                if cue.type == "footstep":
                    c = 4-cue.timer//10
                    canvas.create_oval(x-r,y-r,x+r,y+r,fill = color[c],width = 0)

    def drawShot(mode,canvas,x,y,r):
        i = r/2
        canvas.create_polygon(x,y+r,x+i,y+i,x+r,y,x+i,y-i,x,y-r,x-i,y-i,x-r,y,x-i,y+i,smooth=1,width =0,fill = "red")

    def drawFire(mode,canvas,x,y,r):
        color = ["firebrick1","yellow"]
        for i in range(2):
            offset = r/(i+1)
            canvas.create_polygon(x,y+offset,x-offset,y,x-offset/2,y,x,y-offset,
            x+offset/2,y,x+offset,y,width = 0, fill = color[i], smooth =1)

    def drawMap(mode,canvas):
        canvas.create_rectangle(mode.margin-mode.scrollX,mode.margin,mode.margin+mode.gridWidth*mode.noCols-mode.scrollX,
        mode.margin+mode.gridHeight*mode.noRows,fill = "tan4",width = 0)
        #draw individual walls and control zone
        for row in range(mode.noRows):
            for col in range(mode.noCols):
                #sidescroller
                gX = mode.margin + col*mode.gridWidth-mode.scrollX
                gY = mode.margin +row*mode.gridHeight
                #draw visible grids
                if mode.gridMap.grid[row][col]==0 and (row,col)in mode.men.canSee:
                    canvas.create_rectangle(gX,gY,gX+mode.gridWidth,gY+mode.gridHeight,fill = "sandy brown",width = 0)
                #draw walls
                elif mode.gridMap.grid[row][col]==1:
                    canvas.create_rectangle(gX,gY,gX+mode.gridWidth,
                    gY+mode.gridHeight,fill = "gray20",width = 0)
                    mode.drawPattern1(canvas,row,col)
                #draw objective point
                elif mode.gridMap.grid[row][col]==2:
                    #further check is the grid is seen by the player
                    if (row,col)in mode.men.canSee:
                        #canvas.create_rectangle(gX,gY,gX+mode.gridWidth,gY+mode.gridHeight,fill = "green yellow",width = 0)
                        canvas.create_image(gX+mode.gridWidth//2,gY+mode.gridHeight//2,image=ImageTk.PhotoImage(mode.grass2))
                    else:
                        #canvas.create_rectangle(gX,gY,gX+mode.gridWidth,gY+mode.gridHeight,fill = "green4",width = 0)
                        canvas.create_image(gX+mode.gridWidth//2,gY+mode.gridHeight//2,image=ImageTk.PhotoImage(mode.grass1))

    #adapted from 112 hw2 solution: http://www.cs.cmu.edu/~112/notes/hw2.html
    def drawPattern1(mode,canvas,r,c):
        heightDiff = mode.gridHeight // (4-1)
        widthDiff = mode.gridWidth // (4-1)
        x,y = mode.margin+c*mode.gridWidth,mode.margin+r*mode.gridHeight
        #sideScroller
        x-=mode.scrollX
        canvas.create_line(x,y,x+mode.gridWidth,y+mode.gridHeight)
        canvas.create_line(x+mode.gridWidth,y,x,y+mode.gridHeight)
        for i in range (1,4-1):
            canvas.create_line(x+i*widthDiff,y, x, y+i*heightDiff)
            canvas.create_line(x+i*widthDiff,y,x+mode.gridWidth,y+mode.gridHeight-i*heightDiff)
            canvas.create_line(x+i*widthDiff,y+mode.gridHeight,x,y+mode.gridHeight-i*heightDiff)
            canvas.create_line(x+i*widthDiff,y+mode.gridHeight,x+mode.gridWidth,y+i*heightDiff)

    def drawMen(mode,canvas):
        #change color with respect to health
        color = ["yellow4","yellow3","yellow2","yellow"]
        x,y = mode.men.coordPosition
        r = mode.men.radius
        #draw body
        c = mode.men.health
        if mode.godMode: c = 3
        mode.drawChr(canvas,x,y,r,color[c],mode.men.bodyOrientation,mode.men.gunAngle,mode.men.health)

    def drawCompanion (mode,canvas):
        if mode.hasCompanion and mode.companion.health>-1:
            color = ["SkyBlue4","SkyBlue3","SkyBlue2","SkyBlue1"]
            x,y = mode.companion.coordPosition
            r = mode.companion.radius
            #draw body
            c = mode.companion.health
            if mode.godMode: c = 3
            mode.drawChr(canvas,x,y,r,color[c],mode.companion.bodyOrientation,mode.companion.gunAngle,mode.companion.health)

    def drawChr(mode,canvas,x,y,r,c,bodyOrientation,GunOrientation,health=0):
        x = x-mode.scrollX
        if bodyOrientation =="h":
            #drawBody facing horizontal
            canvas.create_rectangle(x-r,y-r/3*2,x+r,y+r/3*2,fill = c,width = 0)
            for i in [-1,1]:
                canvas.create_line(x-r,y+i*r/3*2,x+r,y+i*r/3*2,width = 2,fill = "gray50")
        else:
            #drawBody facing verticle
            canvas.create_rectangle(x-r/3*2,y-r,x+r/3*2,y+r,fill = c,width = 0)
            for i in [-1,1]:
                canvas.create_line(x+i*r/3*2,y-r,x+i*r/3*2,y+r,width = 2,fill = "gray50")
        #draw gun
        gunLength = mode.chrRadius
        gunTipCoord = (x+gunLength*math.cos(GunOrientation),y-gunLength*math.sin(GunOrientation))
        canvas.create_line(x,y,gunTipCoord[0],gunTipCoord[1],width =2)

    def drawAI(mode,canvas):
        color = ["red4","red3","red","hot pink"]
        for AI in mode.AIs:
            #turn off fow for testing
            if AI.gridPosition in mode.men.canSee or mode.godMode:
                x,y = AI.coordPosition
                r = AI.radius
                #in godMode, AI color represents their current objecitve
                if AI.objective == "hold point"and mode.godMode: c = 0
                elif mode.godMode: c = 3
                #AI color normally represent their health
                else:c = AI.health
                #canvas.create_oval(x-r,y-r,x+r,y+r,fill = color[c])
                mode.drawChr(canvas,x,y,r,color[c],AI.bodyOrientation,AI.gunAngle,AI.health)

    def drawCorpses(mode,canvas):
        for corpse in mode.corpses:
            #turn off fow for testing
            if corpse.gridPosition in mode.men.canSee or mode.godMode:
                x,y = corpse.coordPosition
                r = corpse.radius
                mode.drawChr(canvas,x,y,r,"black",corpse.bodyOrientation,corpse.gunAngle)

    def drawCrosshair(mode,canvas):
        #crosshair changes to red when u can't shoot
        color = ["black","red"]
        if mode.men.reload==0: c = 0
        else: c=1
        r = min(mode.gridHeight,mode.gridWidth) //3
        x = mode.crossHairX
        y = mode.crossHairY
        canvas.create_oval(x-r,y-r,x+r,y+r)
        canvas.create_line(x,y-r,x,y+r,fill = color[c])
        canvas.create_line(x-r,y,x+r,y,fill = color[c])

    def drawBullets(mode,canvas):
        color = ["green","red"]
        for bullet in mode.bullets:
            if mode.CoordToGrid(bullet.coord) in mode.men.canSee:
                x,y = bullet.coord
                x-=mode.scrollX
                r = min(mode.gridHeight,mode.gridWidth) //15
                if bullet.firer == "men":c =0
                else: c = 1
                canvas.create_oval(x-r,y-r,x+r,y+r,fill = color[c],width = 0)

    def drawScoreBoard(mode,canvas):
        canvas.create_rectangle(0,0,mode.width,mode.margin,fill="gray90")
        font = 'Arial 10 bold'
        y = mode.margin//2
        x = mode.width//2
        xOffset = mode.width//4
        color = ["seaShell2","orangeRed2"]
        #index used to deside if any score is highlighted
        i,j = 0,0
        if mode.menOnPoint and not mode.AIOnPoint:
            j = 1
        elif not mode.menOnPoint and mode.AIOnPoint:
            i = 1
        canvas.create_rectangle(x+1.5*xOffset,0,x+0.5*xOffset,mode.margin,fill = color[j],width = 0)
        canvas.create_rectangle(x-1.5*xOffset,0,x-0.5*xOffset,mode.margin,fill = color[i],width = 0)
        canvas.create_text(x+xOffset,y,text = f"Men score = {mode.menPoints}",font = font)
        canvas.create_text(x-xOffset,y,text = f"AI score = {mode.AIPoints}",font = font)
        canvas.create_text(x,y,text=f"time left:{mode.timeLeft}",font = font)

#####################################################################
#other apps
##########################################################
class Win(Mode):
    def appStarted(mode):
        mode.timecounter = 0
        #image from https://www.flickr.com/photos/tclaud/44019365014
        mode.tankSaluteO = mode.loadImage("tankSalute.jpg")
        mode.tankSalute = mode.scaleImage(mode.tankSaluteO ,mode.width/mode.tankSaluteO.size[1])

    def sizeChanged(mode):
        mode.tankSalute = mode.scaleImage(mode.tankSaluteO ,mode.width/mode.tankSaluteO.size[1])

    def redrawAll(mode,canvas):
        canvas.create_image(mode.width//2, mode.height//2, image=ImageTk.PhotoImage(mode.tankSalute))
        font1 = 'Times 19 bold'
        offset = mode.height//2
        canvas.create_rectangle(1/4*mode.width,mode.height//20+offset,3/4*mode.width,mode.height//4+offset,width=0, fill ="seashell2")
        canvas.create_text(mode.width//2, mode.height*0.15+offset,text = "Victory\n press any key to replay", font = font1, width = mode.width//2, justify = "center")

    def keyPressed(mode,event):
        if mode.timecounter>20:
            mode.app.setActiveMode(mode.app.gameMode)
            mode.app.gameMode.appStarted()

    def mousePressed(mode,event):
        if mode.timecounter>20:
            mode.app.setActiveMode(mode.app.gameMode)
            mode.app.gameMode.appStarted()

    def timerFired (mode):
        mode.timecounter +=1

class Lose(Mode):
    def appStarted(mode):
        mode.timecounter = 0
        #image from http://www.gamevfxartist.com/blog/examples/2012/10/19/tank-previs
        mode.burningTankO = mode.loadImage("burningTank.jpg")
        mode.burningTank = mode.scaleImage(mode.burningTankO ,mode.width/mode.burningTankO.size[1])

    def sizeChanged(mode):
        mode.burningTank = mode.scaleImage(mode.burningTankO,mode.width/mode.burningTankO.size[1])

    def redrawAll(mode,canvas):
        canvas.create_image(mode.width//2, mode.height//2, image=ImageTk.PhotoImage(mode.burningTank))
        font1 = 'Times 19 bold'
        canvas.create_rectangle(1/4*mode.width,mode.height//20,3/4*mode.width,mode.height//4,width=0, fill ="seashell2")
        canvas.create_text(mode.width//2, mode.height*0.15,text = "Defeat\n press any key to replay", font = font1, width = mode.width//2, justify = "center")

    def keyPressed(mode,event):
        if mode.timecounter>20:
            mode.app.setActiveMode(mode.app.gameMode)
            mode.app.gameMode.appStarted()

    def mousePressed(mode,event):
        if mode.timecounter>20:
            mode.app.setActiveMode(mode.app.gameMode)
            mode.app.gameMode.appStarted()

    def timerFired (mode):
        mode.timecounter +=1

class Tutorial (Mode):
    def appStarted(mode):
        mode.slideNo = 0
        mode.slide1O = mode.loadImage("tutorial1.png")
        mode.slide1 = mode.scaleImage(mode.slide1O, (mode.width/mode.slide1O.size[1])**2*6/7)
        mode.slide2O = mode.loadImage("tutorial2.png")
        mode.slide2 = mode.scaleImage(mode.slide2O, (mode.width/mode.slide2O.size[1])**2*6/7)
        mode.slide = [mode.slide1,mode.slide2]

    def sizeChanged(mode):
        mode.slide1 = mode.scaleImage(mode.slide1O, (mode.width/mode.slide1O.size[1])**2*6/7)
        mode.slide2 = mode.scaleImage(mode.slide2O, (mode.width/mode.slide2O.size[1])**2*6/7)
        mode.slide = [mode.slide1,mode.slide2]

    def redrawAll(mode,canvas):
        if mode.slideNo <2:
            canvas.create_image(mode.width//2, mode.height//2, image=ImageTk.PhotoImage(mode.slide[mode.slideNo]))

    def keyPressed(mode,event):
        if mode.slideNo <2:
            mode.slideNo+=1

    def timerFired(mode):
        if mode.slideNo>1:mode.app.setActiveMode(mode.app.gameMode)

    def mousePressed(mode,event):
        if mode.slideNo <2:
            mode.slideNo+=1

############################################################
#main app
###########################################################

class MyModalApp (ModalApp):
    def appStarted (app):
        app.gameMode = GameMode()
        app.tutorial = Tutorial()
        app.win = Win()
        app.lose = Lose()
        app.setActiveMode(app.gameMode)

app = MyModalApp(width=700, height=500)

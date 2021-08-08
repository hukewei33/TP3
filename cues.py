###############################
#visual cues
#object of visual cues
##########################################3
class cue (object):
    def __init__(self,coord,grid,cueType,firer = "AI"):
        self.coord = coord
        self.grid = grid
        self.timer = 49
        self.type = cueType
        self.firer = firer

class tracks(cue):
    def __init__(self,coord,grid,cueType,bodyOrientation):
        super().__init__(coord,grid,cueType,firer= None)
        self.bodyOrientation =bodyOrientation
import random, pygame, sys
from pygame.locals import *

FPS = 30 # frames per second, the general speed of the program
GRIDSIZE=5
BOXSIZE=60
XMARGIN=15
YMARGIN=XMARGIN
TOPMARGIN=BOXSIZE*2+YMARGIN

WINDOWWIDTH =BOXSIZE*GRIDSIZE+2*XMARGIN  # size of window's width in pixels
WINDOWHEIGHT = BOXSIZE*GRIDSIZE+YMARGIN+TOPMARGIN # size of windows' height in pixels

#            R    G    B
GRAY     = (100, 100, 100)
NAVYBLUE = ( 60,  60, 100)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
NICEBLUE     = (  0, 100, 255)

BGCOLOR = NICEBLUE

def main():
    global FPSCLOCK, DISPLAYSURF
    pygame.init()
    FPSCLOCK = pygame.time.Clock()

    mousex, mousey=0,0

    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    pygame.display.set_caption('Squares')
    GameBoard=Board(); #the grid to keep track of what's where
                                    #this is redundant data to make things faster
    DISPLAYSURF.fill(BGCOLOR)
    
    #initialize players
    comp=player(BLUE);
    human=player(RED);
    players=[comp,human];
    
    while True:
        mouseClicked = False

        DISPLAYSURF.fill(BGCOLOR)
        drawBoard(GameBoard,comp,human)

        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True
                
        boxx, boxy = getBoxAtPixel(mousex, mousey)
            
        #check if an actual box was clicked
        if(all([not boxx==None,not boxy==None,mouseClicked])):
            #print boxx,boxy #for debugging
            if((boxx,boxy) in GameBoard.empty_spots): #if it's an empty spot
                GameBoard.empty_spots.remove((boxx,boxy))
                #GameBoard.grid[boxx][boxy]='f' #now it's full
                #print "you just placed: ",boxx, boxy
                CheckForFormedSquare(human,(boxx,boxy)) #and updates the score accordingly
                human.placed.append((boxx,boxy))
                
                a=comp_turn(GameBoard,comp,human) #checks for square and updates
                if a==False:
                    GameEnd(comp,human)

                    
                
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def drawBoard(GameBoard,comp,human):
    #draw scores
    FontObj=pygame.font.SysFont('freesanbold.ttf',BOXSIZE)
    human_scoreSurf=FontObj.render(str(human.score), True, human.color)
    human_score_rect=human_scoreSurf.get_rect()
    human_score_rect.center=(XMARGIN,TOPMARGIN/2)
    human_score_rect.left=XMARGIN
    human_score_rect.top=TOPMARGIN/4
    DISPLAYSURF.blit(human_scoreSurf,human_score_rect)

    FontObj=pygame.font.SysFont('freesanbold.ttf',BOXSIZE)
    comp_scoreSurf=FontObj.render(str(comp.score), True, comp.color)
    comp_score_rect=comp_scoreSurf.get_rect()
    comp_score_rect.right=WINDOWWIDTH-XMARGIN
    comp_score_rect.top=TOPMARGIN/4
    DISPLAYSURF.blit(comp_scoreSurf,comp_score_rect)

    #draw vertical and horizontal gridlines
    for i in range(GRIDSIZE+1):
        pygame.draw.line(DISPLAYSURF, WHITE, (XMARGIN+i*BOXSIZE,TOPMARGIN), ( XMARGIN+i*BOXSIZE,TOPMARGIN+GRIDSIZE*BOXSIZE), 4)
        pygame.draw.line(DISPLAYSURF, WHITE, (XMARGIN,TOPMARGIN+i*BOXSIZE), (XMARGIN+GRIDSIZE*BOXSIZE,TOPMARGIN+i*BOXSIZE), 4)

    #draw the circles
    for player in (human,comp):
        for blob_loc in player.placed:
            pygame.draw.circle(DISPLAYSURF, player.color, getPixelAtBox(*blob_loc), BOXSIZE/2, 0)

class player(object):
    def __init__(self,color):
        self.placed=[] #placed tokens, a list of tuples (row,column)
        self.squares=[]
        self.score=0;
        self.color=color
    def update_score(self,side_len):
        self.score+=(side_len)**2

class Board(object):
        def __init__(self):
            #Board.grid=[['e']*GRIDSIZE for __ in range(GRIDSIZE)]
            Board.empty_spots=[(x,y) for x in range(GRIDSIZE) for y in range(GRIDSIZE)]

def getBoxAtPixel(x, y):

    boxx=(x-XMARGIN)/BOXSIZE
    boxy=(y-TOPMARGIN)/BOXSIZE
    #if it's not in a box, return Nones
    if any([boxx<0,boxx>GRIDSIZE-1,boxy<0,boxy>GRIDSIZE-1]):
        return (None,None)
    return (boxx,boxy)

def getPixelAtBox(boxx, boxy):
    "returns the center of the box, in x,y"
    x=XMARGIN+boxx*BOXSIZE+BOXSIZE/2
    y=TOPMARGIN+boxy*BOXSIZE+BOXSIZE/2
    return(x,y)

def comp_turn(GameBoard,comp,human):
    #find a random empty spot and go into it
    #get empty spots:
    if len(GameBoard.empty_spots)==0:
        return False
    #choose a random empty spot    
    choice=random.randrange(len(GameBoard.empty_spots))
    boxx,boxy=GameBoard.empty_spots[choice]
    
    CheckForFormedSquare(comp,(boxx,boxy))
    
    comp.placed.append(GameBoard.empty_spots[choice])

    #GameBoard.grid[boxx][boxy]='f'
    GameBoard.empty_spots.remove((boxx,boxy))
    return True

def CheckForFormedSquare(player,(boxx,boxy)):
    #just do this naively
    tokens=player.placed[:] #list of tokens
    for token in tokens:
        #check for vertical line
        if(token[0]==boxx): #on the same same vertical value
            side_len=token[1]-boxy            
        #    print token, side_len
             #look for the two possible boxes it could have made:
             #each time remove some token so that the same square won't be counted twice
            #the first one is where this vertical line is on one side of the box 
            needed_token1=(boxx+side_len,boxy)
            needed_token2=(boxx+side_len,boxy+side_len) 
            if (needed_token1 in tokens) and (needed_token2 in tokens):
                #print 'found square:',(boxx,boxy),token,needed_token1,needed_token2
                player.update_score(side_len+1)
                player.squares.append(((boxx,boxy),token,needed_token1,needed_token2))
                
            needed_token1=(boxx-side_len,boxy)
            needed_token2=(boxx-side_len,boxy+side_len)
            if (needed_token1 in tokens) and (needed_token2 in tokens):
                #print 'found square:',(boxx,boxy),token,needed_token1,needed_token2
                player.update_score(side_len+1)
                player.squares.append(((boxx,boxy),token,needed_token1,needed_token2))

        
def GameEnd(comp,human):
    pass

main()
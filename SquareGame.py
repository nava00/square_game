import random, pygame, sys
from pygame.locals import *
import copy
from minimax import *

FPS = 30 # frames per second, the general speed of the program
GRIDSIZE=7
BOXSIZE=60
XMARGIN=15
YMARGIN=XMARGIN
TOPMARGIN=BOXSIZE*2+YMARGIN
DEPTH=2

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
    comp=Player(BLUE);
    human=Player(RED);
    players=[comp,human];
    #initialize ai object
    ai=AI(comp,human,DEPTH,game_over,state_score,blank_spots,new_state)
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
            if((boxx,boxy) in GameBoard.empty_spots): #if it's an empty spot
                GameBoard.empty_spots.remove((boxx,boxy))
                human.update((boxx,boxy))
                drawBoard(GameBoard,comp,human)
                a=comp_turn(ai,GameBoard,comp,human) #checks for square and updates
                if a==False:
                    GameEnd(comp,human,GameBoard)
                    comp=Player(BLUE);
                    human=Player(RED);
                    GameBoard=Board();
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
    #draw the squares, if there are any
    for player in (human,comp):
        for sqnum,square in enumerate(player.squares):
            if(sqnum>len(player.squares)-2): #only draw the last two squares
                offset=square[-1] #so there's not too much overlap
                dark_color=[int(val/2+2*abs(offset)) for val in player.color]#slightly diff colors
                square_pts=[(getPixelAtBox(*pt)[0]+offset,getPixelAtBox(*pt)[1]+offset) for pt in square[:-1]]
                pygame.draw.polygon(DISPLAYSURF,dark_color,square_pts,len(player.squares)-sqnum+2)
            #print "drew the square", square


class Player(object):
    def __init__(self,color):
        self.placed=[] #placed tokens, a list of tuples (row,column)
        self.squares=[];
        self.score=0;
        self.color=color
    def __copy__(self):
        new_guy=Player(self.color)
        new_guy.placed=copy.deepcopy(self.placed)
        new_guy.score=copy.deepcopy(self.score)
        return new_guy
    def update_score(self,side_len):
        self.score+=(side_len)**2
    def update(self,move):
        CheckForFormedSquare(self,move)
        self.placed.append(move)


class Board(object):
    def __init__(self):
        Board.empty_spots=[(x,y) for x in range(GRIDSIZE) for y in range(GRIDSIZE)];
    def __copy__(self):
        newBoard=Board();
        newBoard.empty_spots=copy.copy(self.empty_spots);
        return newBoard

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

def comp_turn_dumb(GameBoard,comp,human):
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

def comp_turn(ai,GameBoard,comp,human):
    if len(GameBoard.empty_spots)==0:
        return False
    #store old gameboard
    orig_empty_spots=copy.deepcopy(GameBoard.empty_spots)

    score,ai_move=ai.get_move([human,comp,GameBoard]);
    #print "computer went to:", ai_move
    GameBoard.empty_spots=orig_empty_spots
    comp.update(ai_move)    
    GameBoard.empty_spots.remove(ai_move)
    if(len(GameBoard.empty_spots)==0):
        return False
    return True


def CheckForFormedSquare(player,(boxx,boxy)):
    #just do this naively
    tokens=player.placed[:] #list of tokens
    #print player.color," proposed move:",(boxx,boxy)
    for token in tokens:
        #check for vertical line
        if(token[0]==boxx): #on the same same vertical value
            side_len=token[1]-boxy
            if(side_len==0):
                continue
        #    print token, side_len
             #look for the two possible boxes it could have made:
             #each time remove some token so that the same square won't be counted twice
            #the first one is where this vertical line is on one side of the box 
            needed_token1=(boxx+side_len,boxy)
            needed_token2=(boxx+side_len,boxy+side_len) 
            if (needed_token1 in tokens) and (needed_token2 in tokens):
                #print 'found square:',(boxx,boxy),token,needed_token1,needed_token2 
                #print "side lenth is ", side_len
                player.update_score(abs(side_len)+1)
                offset=random.randrange(-BOXSIZE/5, BOXSIZE/5)
                player.squares.append(((boxx,boxy),token,needed_token2,needed_token1,offset))
                
            needed_token1=(boxx-side_len,boxy)
            needed_token2=(boxx-side_len,boxy+side_len)
            if (needed_token1 in tokens) and (needed_token2 in tokens):
                #print 'found square:',(boxx,boxy),token,needed_token1,needed_token2
                #print "side lenth is ", side_len
                offset=random.randrange(-BOXSIZE/10, BOXSIZE/10)
                player.update_score(abs(side_len)+1)
                player.squares.append(((boxx,boxy),token,needed_token2,needed_token1,offset))

        
def GameEnd(comp,human,GameBoard):
    NewGame=False;
    while not NewGame:
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True
            elif event.type == KEYUP and event.key ==121:
                NewGame=True;

        #draw GameOver Word        
        DISPLAYSURF.fill(BGCOLOR)
        drawBoard(GameBoard,comp,human)
        #draw "game over" and "play again Y/N"
        FontObj=pygame.font.SysFont('freesanbold.ttf',BOXSIZE*3/4)
        OverSurf=FontObj.render("Game Over", True, (0,0,0))
        Overrect=OverSurf.get_rect()
        Overrect.center=(XMARGIN+GRIDSIZE*BOXSIZE/2,TOPMARGIN+GRIDSIZE*BOXSIZE/2)
        DISPLAYSURF.blit(OverSurf,Overrect)
        FontObj=pygame.font.SysFont('freesanbold.ttf',BOXSIZE*1/2)
        OverSurf=FontObj.render("again? (y/n)", True, (0,0,0))
        Overrect=OverSurf.get_rect()
        Overrect.center=(XMARGIN+GRIDSIZE*BOXSIZE/2,TOPMARGIN+GRIDSIZE*BOXSIZE/2+BOXSIZE)
        DISPLAYSURF.blit(OverSurf,Overrect)

        pygame.display.update()
        FPSCLOCK.tick(FPS)
    return True;
        


def state_score(state,human,comp):
    #state=[human,comp,GameBoard]
    #print "scores",state[0].score,state[1].score
    return state[1].score-state[0].score
    #return state[0].score-state[1].score

def game_over(state,human,comp):
     #state=[human,comp,GameBoard]
    num_tokens=len(state[0].placed)+len(state[1].placed);
    return(num_tokens==(GRIDSIZE**2));

def blank_spots(state,player):
     #state=[human,comp,GameBoard]
    return copy.copy(state[2].empty_spots)

def new_state(state,player,move):
    newState=[0,0,0];#copy.copy(state);
    #move is of the form [1,2]
    
    #make copies of everything
    newState[0]=copy.copy(state[0]);
    newState[1]=copy.copy(state[1]);
    newState[2]=copy.copy(state[2]);
    
    if state[0].color==player.color: #we're the human
        newState[0].update(move)
    if state[1].color==player.color:
        newState[1].update(move)
    
    newState[2].empty_spots.remove(move)

    return newState


main()

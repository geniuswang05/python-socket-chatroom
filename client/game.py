
import pygame
from sys import exit

pygame.init()
screen = pygame.display.set_mode((540,700))
pygame.display.set_caption('Tic-Tac-Toe TOGETHER')
clock=pygame.time.Clock()
#titlefont = pygame.font.Font(None, 50)

#title_surface = titlefont.render('Tic-Tac-Toe TOGETHER', False, 'White') 
board_surface = pygame.Surface((540,540))
#bkg = pygame.image.load('pictures/board.tiff')

line=pygame.Surface((10,540))
line2=pygame.Surface((540,10))
button=pygame.Surface((80,50))
bottom=pygame.Surface((540,50))
bottom2=pygame.Surface((540,540))
button.fill('White')
board_surface.fill('White')
line.fill('Black')
line2.fill('Black')

play1=pygame.image.load('pictures/X.jpeg').convert()
play2=pygame.image.load('pictures/circle.jpeg').convert()

play1=pygame.transform.scale(play1, (170,170))
play2=pygame.transform.scale(play2, (170,170))


gamer='Player1'
win=None
draw=False
board=[[0,0,0],[0,0,0],[0,0,0]]
gameend=False


def winning():
    global win, draw,board
    for col in range(3):
        if(board[0][col]==board[1][col]==board[2][col] and board[0][col]!=0):
            win=board[0][col]
            pygame.draw.line(screen, 'Red', (0,90+(col)*180),(540,(90+(col)*180)),10)
            break
    for row in range(3):
        if(board[row][0]==board[row][1]==board[row][2] and board[row][0]!=0):
            win=board[row][0]
            pygame.draw.line(screen, 'Red', (90+(row)*180,0),(90+(row)*180,540),10)
            break
    if board[0][0]==board[1][1]==board[2][2]and board[0][0]!=0:
        win=board[0][0]
        pygame.draw.line(screen, 'Red', (0,0),(540,540),10)
    if board[2][0]==board[1][1]==board[0][2]and board[1][1]!=0:
        win=board[1][1]
        pygame.draw.line(screen, 'Red', (540,0),(0,540),10)
    unfull=False
    for i in range(3):
        for j in range(3):
            if board[i][j]==0:
                unfull=True
    if unfull==False and win==None:
        draw=True
def status():
    global draw
    if win == None:
        title = gamer+"'s turn!"
    else:
        title = gamer+' WON!!'
    if draw:
        title = 'Draw, no winner'
    font= pygame.font.Font(None, 40)
    text=font.render(title, True, 'White')
    screen.blit(bottom,(10,560))
    screen.blit(text,(10,560))
    
    if win != None or draw:
        title ='Restart the game?'
        text=font.render(title, True, 'White')
        screen.blit(text,(10,610))
        yesb="YES"
        nob="NO"
        font= pygame.font.Font(None, 20)
        ytext=font.render(yesb, True, 'Black')
        ntext=font.render(nob, True, 'Black')
        
        screen.blit(button,(320,610))
        screen.blit(ytext,(330,620))
        
        screen.blit(button,(430,610))
        screen.blit(ntext,(440,620))
    
def restart():
    global board,win,gamer,draw
    gamer='Player1'
    win=None
    draw=False
    board=[[0,0,0],[0,0,0],[0,0,0]]
    screen.blit(board_surface, (0,0))
    
def gaming(row,col):
    global board , gamer
    posy = (col)*180
    posx = (row)*180
    board[row][col]=gamer
    if gamer=='Player1':
        screen.blit(play1, (posx,posy))
        gamer ='Player2'
    else:
        screen.blit(play2, (posx,posy))
        gamer ='Player1'
    pygame.display.update()

screen.blit(board_surface, (0,0))

status()

while True:
    err0r=False
    screen.blit(line,(-5,0))
    screen.blit(line,(175,0))
    screen.blit(line,(355,0))
    screen.blit(line,(535,0))
    screen.blit(line2,(0,-5))
    screen.blit(line2,(0,175))
    screen.blit(line2,(0,355))
    screen.blit(line2,(0,535))
    
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            x,y = pygame.mouse.get_pos()
            
            row= x//180
            col= y//180
            
                
            if row<=2 and col<=2 and win==None:  
                if board[row][col]!=0:
                    err0r=True
                    warning="The block is occupied!!"
                    font= pygame.font.Font(None, 40)
                    text2=font.render(warning, True, 'Red')
                    screen.blit(text2,(10,650))
                if err0r==False:
                    screen.blit(bottom2,(10,560))
                    gaming(row,col)
                    winning()
                    status()
            if win!=None or draw:
                if x>=320 and x<=400 and y<=660 and y >=610:
                    restart()
                    screen.blit(bottom2,(10,560))
                    status()
                if x>=430 and x<=510 and y<=660 and y >=610:
                    pygame.quit()
                    exit()
            
                
            
            
        
#    screen.blit(bkg, (0,0))
#    screen.blit(title_surface, (300,10))
    
 
 
    
            
    pygame.display.update()
    clock.tick(60)
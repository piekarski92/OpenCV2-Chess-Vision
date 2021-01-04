import cv2
import numpy as np
import time
import tkinter as Tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from stockfish import Stockfish

global bdict
global lastmove
global stockfish
global board
global flip

cap = cv2.VideoCapture(0)
CONTINUE = True

def find_pieces(piece, imgcrop,img,light,dark):
    global bdict, lastmove
    piece_pic = piece + '.png'
    pieceColor = list(piece)[0]

    lower = dark[0][0]
    upper = light[0][0]
    mask = cv2.inRange(imgcrop, lower, upper)
    lastMoveImg = cv2.bitwise_and(imgcrop, imgcrop, mask = mask)
    
    template = cv2.imread(piece_pic,0)
    scale = 0.45
    temp_r = cv2.resize(template, (0,0), fx=scale, fy=scale)

    for b in board:
        for k in range(0,8):
            img_slice,y,x,sq = findSlice(imgcrop,b[k])
            lastMv = findSlice(lastMoveImg,b[k])
            lastMvChk = np.where(lastMv[0]>=130)
            
            imgsg = cv2.cvtColor(img_slice, cv2.COLOR_BGR2GRAY)
            res = cv2.matchTemplate(imgsg,temp_r,cv2.TM_CCOEFF_NORMED)
            if pieceColor == 'w':
                threshold = 0.6
            if pieceColor == 'b':
                threshold = 0.7
            npoint = np.where( res >= threshold)
            if npoint[0].size != 0:
                cv2.rectangle(imgcrop, (x,y), (x + sq, y + sq), (0,0,255), 2)
                cv2.putText(imgcrop,piece,(x,y+10),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2,cv2.LINE_AA)
                bdict[b[k]]=piece
                if len(lastMvChk[0])>1000:
                    lastmove = [pieceColor,b[k]]


def populateBoard(b):
    for i in range(0,8):
        for k in range(97,105):
            name=chr(k)+str(i+1)
            b[-(97-k)][i]=name
    return np.rot90(board,1,(0,1))

def popDictionary():
    board = {}
    for i in range(0,8):
        for k in range(97,105):
            name=chr(k)+str(i+1)
            board.update({name:'X'})
    return board

def findSlice(img,loc):
    w,h,l = img.shape
    sq = int(w/8)
    ltr = ord(list(loc)[0])-97
    num = int(list(loc)[1])-1

    if not flip:
        x=(7-num)*sq
        y=ltr*sq
        return img[(7-num)*sq:(8-num)*sq,ltr*sq:(ltr+1)*sq,],x,y,sq
    else:
        x=(num)*sq
        y=(7-ltr)*sq
        return img[num*sq:(num+1)*sq,(7-ltr)*sq:(8-ltr)*sq,],x,y,sq

def drawArrow(img,bestMove):
    w,h,l = img.shape
    bM = list(bestMove)
    sq = int(w/8)
    ltrst = ord(bM[0])-97
    numst = int(bM[1])-1
    ltred = ord(bM[2])-97
    numed = int(bM[3])-1

    if not flip:
        ys = int((7-numst)*sq +sq/2)
        xs = int(ltrst*sq+sq/2)
        ye = int((7-numed)*sq+sq/2)
        xe = int(ltred*sq+sq/2)
    else:
        ys = int(numst*sq +sq/2)
        xs = int((7-ltrst)*sq+sq/2)
        ye = int(numed*sq+sq/2)
        xe = int((7-ltred)*sq+sq/2)

    cv2.arrowedLine(img,(xs,ys),(xe,ye),(255, 0, 0),2)

def getFEN(d,b):
    FEN = ''
    ctr = 0
    
    for i in range(0,8):
        for k in range(0,8):
            curSquare = b[i][k]
            pColor = list(d[curSquare])
            piece=''
            if pColor[0] == 'w':
                piece = pColor[1].capitalize()
            if pColor[0] == 'b':
                piece = pColor[1]
            if d[curSquare] == 'X':
                ctr=ctr+1
                if k==7 and ctr!=0:
                    FEN = FEN+str(ctr)
            if d[curSquare] != 'X':
                FEN = FEN+str(ctr)+piece
                ctr=0
        FEN=FEN+'/'
        ctr=0
    return FEN.replace('0','')

def nextMove(move):
    if move == 'w':
        return 'b'
    else:
        return 'w'
    
#####TKINTER Functions#####
def key_event(event):
    global CONTINUE
    if event.char == 'q':
      print('Good bye')
      CONTINUE = False
      root.destroy()

def copyToClip():
    root.withdraw()
    root.clipboard_clear()
    root.clipboard_append(Pos1.get())

def naviToFile():
    dirname = filedialog.askopenfilename(parent=root,initialdir="/",title='Please select a directory')
    if len(dirname ) > 0:
        E1.delete(0,last=Tk.END)
        E1.insert(0,dirname)

def launchStockFish():
    global stockfish
    dirname = str(E1.get())
    stockfish = Stockfish(dirname)

def getBestMove():
    global stockfish
    try:
        stockfish.set_fen_position(Pos1.get())
        bestMove = stockfish.get_best_move_time(2000)
        print('Stockfish pinged')
        return bestMove
    except NameError or TypeError:
        print("Stockfish not loaded.")

def flipBoard():
    global board, flip
    flip = not flip
    board = np.rot90(board,2)

def quitProgram():
    global CONTINUE
    cv2.destroyAllWindows()
    CONTINUE = False
    print('Good bye')
    root.destroy()

#####TKINTER GUI Objects#####
root = Tk.Tk()
frame = Tk.Frame(root)
frame.pack()
root.bind("<Key>", key_event)
load = Image.open("header.jpg")
header_img = ImageTk.PhotoImage(load)
Pos1 = Tk.StringVar()
LstMv = Tk.StringVar()
BstMv = Tk.StringVar()
BrdGUI = Tk.StringVar()
ChkBtn = Tk.IntVar()
StkFishDir = Tk.StringVar()
Pos1.set('')
LstMv.set('no moves yet')
ChkBtn.set(0)

broot = Tk.Frame(root)
broot.pack(side=Tk.BOTTOM)

L1 = Tk.Label(root, textvariable = Pos1)
L2 = Tk.Label(root, textvariable = LstMv)
L3 = Tk.Label(root, textvariable = BstMv)
LP = Tk.Label(root, image = header_img)
C1 = Tk.Checkbutton(root,text='Begin Evaluation',variable=ChkBtn,onvalue=1, offvalue=0)

B1 = Tk.ttk.Button(root, text = 'Browse', command = naviToFile)
BQ = Tk.ttk.Button(broot, text = 'Quit', command = quitProgram)
Blaunch = Tk.ttk.Button(broot, text = 'Launch', command = launchStockFish)
BBmv = Tk.ttk.Button(root, text = 'Best Move', command = getBestMove)
BF = Tk.ttk.Button(broot, text = 'Flip Board', command = flipBoard)

LE1 = Tk.Label(root, text="Stockfish Directory:")
E1 = Tk.Entry(root)
E1.insert(0,"F:\stockfish\stockfish_20090216_x64_bmi2.exe")

LP.pack(side=Tk.TOP)

L1.pack(fill=Tk.X)
L2.pack()
L3.pack()
LE1.pack(fill=Tk.X)
C1.pack()

E1.pack(side=Tk.LEFT,ipadx=100)
B1.pack(side=Tk.RIGHT)

Blaunch.pack(side=Tk.LEFT)
BF.pack(side=Tk.LEFT)
BQ.pack(side=Tk.LEFT)

root.title('Chess Vision')
#####################

pieces = ['wp','wr','wn','wb','wq','wk','bp','br','bn','bb','bq','bk']
board = (np.zeros((8,8))).astype(str)
board = populateBoard(board)
bdict = popDictionary()

BrdGUI.set(np.array2string(board))

lastmove=['','']
imglight = cv2.imread('light_hglt.jpg')
imgdark = cv2.imread('dark_hglt.jpg')

tstart=time.time()
evalMs = 1
bestMove='a1h8'
lastPos = ''
flip = False

while CONTINUE:
    
    root.update()
    ret, img = cap.read()
    offset = int((img.shape[1]-img.shape[0])/2)
    imgcrop = img[0:img.shape[0],offset:offset+img.shape[0]]
    for p in pieces:
        find_pieces(p,imgcrop,img,imglight,imgdark)

    Pos = getFEN(bdict,board) + ' ' + nextMove(lastmove[0])
    Pos1.set(Pos)
    tnow=time.time()
    if ChkBtn.get()==1:
        if (tnow-tstart)>evalMs and Pos!=lastPos and ('k' in Pos and 'K' in Pos):
            bestMove = getBestMove()
            lastPos = Pos
            tstart=time.time()
        drawArrow(imgcrop,bestMove)
        
        
    lstmv_str = "Last Move: " + lastmove[0] + " to " + lastmove[1]
    LstMv.set(lstmv_str)
    bdict = popDictionary()

    cv2.imshow('frame',imgcrop)
    
cv2.destroyAllWindows()

import sys,wave,math,time,pygame,numpy,random,ast,pyperclip
from pygame.locals import *
from math import sin,cos,tan,asin,acos,atan,pi,log,sinh,cosh,tanh,sqrt,atan2,ceil
fps = 120
rpf = 2
test = [0,0,0]
noteList = []
entities = []
actions = []
inactions = []
started = False
sampleLength = 256
instr = [[-1,0],[-1,0]]
try:
    file = open("settings.ini","r+")
    try:
        #print(file.read())
        settings = ast.literal_eval(file.read())
        if settings == None or len(settings) != 8:
            [throwException]
    except:
        file.close()
        [throwException]
except:
    settings = [[1024,512],[1024,512],0.5,0,1,0.01,[[-1,0],[-1,0]],1]
    file = open("settings.ini","w+")
    file.write(str(settings))
unison = settings[7]
instr = settings[6]
transform_length = settings[4]
file.close()
hscale = 4
vscale = 2
screenSize = list(settings[0])
screenSize2 = tuple(settings[1])
systemVar = [0,0,0,0,0]
sampleRate = int(44100)
playing = False
insno = 0
detune = float(settings[5])
diffTime = avgTime = 0.2
measureSize = [1,5,500]
display = changedSize = True
frames = 0
brightness = 0
shifted = False
controlled = False
draw_increment = 0
flash = [0,0]
col = (0,0,0)
bitDepth = 8
lastCol = currCol = 0
lastval = currval = 0
pressed = 0
volume = float(settings[2])
mode = int(settings[3])
undoing = []
redoing = []
validhex = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f','A','B','C','D','E','F']
equation = "sin(x)"
equations1 = ['CUSTOM','PASTEDATA','MODIFY','sin','square','saw','triangle','flower','spikes','tan','asin','atan','quarter pulse','slanted sin','double sin','hexagon','sinsaw','trapezium','overdrive','string','noise']
equations2 = ['custom','data','flip','sin(x)','square(x)/2','((z-.5)%1-.5)*2','-(abs((z+.25)%1*2-1)-.5)*2','sin(x)-(sin(x*16)/8)','sin(x)*(1+abs(sin(x*8))/-2)',
              'tan(x/2)/48','asin((x-pi)/pi)/-sqrt(2)','atan(pi-x)/1.3','min(square(x),square(x+pi/2))','sin(((x/sqrt(pi)-sqrt(pi)))**2)*square(x)','sin(x)/2+sin(x*2+pi/4)/2',
              'square(x)*min(abs((-(abs((z+.25)%1*2-1)-.5)/2*sqrt(3)*pi)),sqrt(3)/2)','max(sin(x),-((z-.5)%1-.5)*2)*square(x)',
              'square(x)*min(abs((-(abs((z+.25)%1*2-1)-.5)/2*sqrt(3)*pi)),sqrt(3)/6)*2','raisec((sin(x)+sin(2*x))/3+raisec((z-.5)%1-.5,2)*2,1.5)*2',
              '(((z-.5)%1-.5)*2)*(min(abs((-(abs((z+.25)%1*2-1)-.5)/2*sqrt(3)*pi)),sqrt(3)/32)*18)','random.randint(-256,256)/256']
operations = (["= (set)","+ (add)","- (subtract)","× (multiply)","÷ (divide)","^ (power)","% (modulo)","& (and)","| (or)","⊕ (xor)"],["=","+","-","*","/","**","%","&","|","^"])
rounds = [.125,.375,.625,.875,.25,.5,.75,1/3,2/3]
def square(x):
    return(abs(sin(x+.0000001))/sin(x-.0000001))
def raisec(n,power):
    if n.real >= 0:
        return abs(n)**power
    else:
        return -abs(n)**power
def roundf(n):
    if round(n + 1) - round(n) == 1:
        return(int(round(n)))
    return(int(n + abs(n) / n * 0.5))
def ultra_round(n):
    global rounds
    a = math.floor(n)
    b = n%1
    c = round(b,1)
    for i in range(0,len(rounds)):
        if abs(b-rounds[i]) < .02:
            c = rounds[i]
    return a+c
#         a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z
table1 = [-1, 7, 4, 3,16,-1, 6, 8,24,10,-1,-1,11, 9,26,28,12,17, 1,19,23, 5,14, 2,21, 0]
#         0, 1, 2, 3, 4, 5, 6, 7, 8, 9
table2 = [27,-1,13,15,-1,18,20,22,-1,25]

xcam = 0
pitch = pitchD = 261.6255653005987
pitchO = 96
data = [0]
data *= 256
data *= 100
end = False
changed = False


def pquit():
    global end,screenSize,screenSize2,volume,mode,transform_length,instr,unison
    end = True
    try:
        file = open("settings.ini","w+")
        file.write(str([screenSize,screenSize2,volume,mode,transform_length,detune,instr,unison]))
        file.close()
        pygame.quit()
        sys.exit(0)
    except:
        try:
            sys.exit(1)
        except:
            raise
def text_objects(text,font,colour):
    textSurface = font.render(text,True,colour)
    textSurface2 = font.render(text[:-1],True,colour)
    return textSurface,textSurface2.get_rect()
def message_display(text,size,colour,pos):
    global systemVar,screenSize
    largeText = pygame.font.SysFont('calibri',size)
    TextSurf,TextRect = text_objects(text,largeText,colour)
    TextRect.center = pos
    systemVar[4].blit(TextSurf, TextRect)
def msgbox(message1,message2=""):
    update()
    if not(message2==""):
        waitInput([[str(message1),str(message2)],(["OK",(int(screenSize[0]/2),int(screenSize[1]-60)),0,0])])
    else:
        waitInput([[str(message1)],(["OK",(int(screenSize[0]/2),int(screenSize[1]-60)),0,0])])
    return(1)
def enterbox(message,default,domain=None):
    update()
    try:
        inputval = waitInput([[str(message)],([default,[int(screenSize[0]/2),int(screenSize[1]*.5-80)],1+4*(domain!=None),1,domain]),(["OK",(int(screenSize[0]/2),int(screenSize[1]-60)),0,0])])[0]
        return(inputval)
    except:
        return(None)
def choicebox(message,choices):
    global vscale
    update()
    choiceS = []
    for i in range(0,len(choices)):
        if len(choices) < 3:
            columns = len(choices)
        else:
            columns = 3
        row = int(i/columns)
        choiceS.append([str(choices[i]),[(i%columns-(columns/2)+.5)*180+screenSize[0]/2,int(105+27*row*vscale)],2,0])
    choiceS.append(["OK",(int(screenSize[0]/2),int(screenSize[1]-60)),0,0])
    try:
        inputval = waitInput([[message]]+choiceS)-1
        if inputval < 0:
            inputval = 0
        inputval = choices[inputval]
        return(inputval)
    except:
        return(None)
def pickbox(message,choices):
    global vscale
    update()
    choiceS = []
    for i in range(0,len(choices)):
        if len(choices) < 3:
            columns = len(choices)
        else:
            columns = 3
        row = int(i/columns)
        choiceS.append([str(choices[i]),[(i%columns-(columns/2)+.5)*180+screenSize[0]/2,int(105+27*row*vscale)],4,0])
    choiceS.append(["OK",(int(screenSize[0]/2),int(screenSize[1]+80)),0,-1])
    try:
        inputval = waitInput([[message]]+choiceS)-1
        if inputval < 0:
            inputval = 0
        inputval = choices[inputval]
        return(inputval)
    except:
        return(None)
def multenterbox(message,choices,defaults=False,types=False,move_direction=False):
    global vscale
    update()
    choiceS = []
    for i in range(0,len(choices)):
        row = int(i/2)
        choiceS.append([str(choices[i]),[(i%2-.75)*480+screenSize[0]/2,int(105+27*row*vscale)],3,0])
        if types[i] == None:
            choiceS.append([str(defaults[i]),[(i%2-.25)*480+screenSize[0]/2,int(105+27*row*vscale)],1,0])
        else:
            choiceS.append([str(defaults[i]),[(i%2-.25)*480+screenSize[0]/2,int(105+27*row*vscale)],5,0,types[i]])
    choiceS.append(["OK",(int(screenSize[0]/2),int(screenSize[1]-60)),0,0])
    if move_direction:
        choiceS.append(["  >",(int(screenSize[0]/2+160),int(screenSize[1]-60)),0,0])
        choiceS.append(["  <",(int(screenSize[0]/2-160),int(screenSize[1]-60)),0,0])
    try:
        inputval = waitInput([[message]]+choiceS)
        if move_direction:
            if inputval == "  >":
                return(1)
            elif inputval == "  <":
                return(-1)
        return(inputval)
    except:
        return(None)
def waitInput(listA):
    global display,vscale,final_return,returns,boxes,frames
    boxes = list(listA)
    currframe = 0
    while mouseCheck[1] or keyCheck[2][K_SPACE] or keyCheck[2][K_RETURN]:
        update()
    while True:
        if keyCheck[2][K_ESCAPE]:
            return(None)
        for e in range(0,len(boxes[0])):
            message_display(boxes[0][e],48,(255,255,255),((screenSize[0]/2),(50+e*60)))
        final_return = [False,0]
        for i in range(1,len(boxes)):
            boxstr = str(boxes[i][0])
            if boxes[i][2] == 0:
                colour_top = 8
                if ((mposition[0][0]-boxes[i][1][0])**2+(mposition[0][1]-boxes[i][1][1])**2) < 4096:
                    colour_top = 16
                    if mouseCheck[1]:
                        if boxes[i][3]:
                            boxes[i][3] = 1
                        else:
                            boxes[i][3] = 16
                if keyCheck[2][K_RETURN] and boxes[i][0] == "OK":
                    colour_top = 16
                    if boxes[i][3]:
                        boxes[i][3] = 1
                    else:
                        boxes[i][3] = 16
                if boxes[i][3] > 1:
                    boxes[i][3] -= 1
                    colour_top = colour_top*boxes[i][3]-1
                elif boxes[i][3] == 1:
                    if boxes[i][0] != "OK":
                        final_return[1] = boxes[i][0]
                        final_return[0] = -1
                        break
                    final_return[0] = boxes[i][0]
                    break
                else:
                    colour_top = colour_top*16-1
                if display:
##                    try:
##                        if len(sprites) == 0:
##                            sprites.append(None)
##                    except:
##                        sprites = [None]
##                        sprites[0] = pygame.Surface((64,64)).convert_alpha()
##                        sprites[0].fill((0,0,0,0))
                    reg_polygon_complex(systemVar[4],boxes[i][1],(colour_top,colour_top,colour_top),6,64,48,currframe/16,255,4,8)
                    reg_polygon_complex(systemVar[4],boxes[i][1],(colour_top,colour_top,colour_top),6,55,41,currframe/16,127,4,40)
                    #blit_complex(systemVar[4],sprites[0],(boxes[i][1][0]-32,boxes[i][1][1]-32),255,currframe)
                    systemVar[4].blit(systemVar[1].render(boxes[i][0],1,(colour_top,colour_top,colour_top)),[boxes[i][1][0]-18,boxes[i][1][1]-10])
            elif boxes[i][2] == 1:
                colour_top = 127
                colour_mid = 255
                if mposition[0][0]-boxes[i][1][0] < 127 and mposition[0][0]-boxes[i][1][0] > -127 and mposition[0][1]-boxes[i][1][1] < 25 and mposition[0][1]-boxes[i][1][1] > -25:
                    colour_top = 255
                    if mouseCheck[1]:
                        for j in range(1,len(boxes)):
                            if boxes[j][2] >= 1:
                                boxes[j][3] = 0
                        boxes[i][3] = 16
                if boxes[i][3]:
                    if boxes[i][3] > 1:
                        boxes[i][3] -= 1
                    if boxes[i][3] < 1:
                        boxes[i][3] = 1
                    colour_top = 255
                    colour_mid = 0
                    if keyCheck[0][K_LSHIFT] or keyCheck[0][K_RSHIFT]:
                        shifted = True
                    else:
                        shifted = False
                    if keyCheck[0][K_LCTRL] or keyCheck[0][K_RCTRL]:
                        controlled = True
                        if keyCheck[4][K_v]:
                            boxes[i][0] += pyperclip.paste()
                        elif keyCheck[4][K_c]:
                            pyperclip.copy(boxes[i][0])
                        elif keyCheck[4][K_BACKSPACE]:
                            boxes[i][0] = ""
                    else:
                        controlled = False
                        for n in range(0,26):
                            if eval("keyCheck[4][K_"+chr(n+97)+"]"):
                                if shifted:
                                    currChar = n+65
                                else:
                                    currChar = n+97
                                boxes[i][0] += chr(currChar)
                        symS = ["!","@","#","$","%","^","&","*","(",")"]
                        for n in range(0,10):
                            if eval("keyCheck[4][K_"+str(n)+"]"):
                                if shifted:
                                    currChar = symS[n-1]
                                else:
                                    currChar = str(n)
                                boxes[i][0] += currChar
                        if keyCheck[4][K_SPACE]:
                            boxes[i][0] += " "
                        if keyCheck[4][K_COMMA]:
                            if shifted:
                                boxes[i][0] += "<"
                            else:
                                boxes[i][0] += ","
                        if keyCheck[4][K_PERIOD]:
                            if shifted:
                                boxes[i][0] += ">"
                            else:
                                boxes[i][0] += "."
                        if keyCheck[4][K_EQUALS]:
                            if shifted:
                                boxes[i][0] += "+"
                            else:
                                boxes[i][0] += "="
                        if keyCheck[4][K_MINUS]:
                            if shifted:
                                boxes[i][0] += "_"
                            else:
                                boxes[i][0] += "-"
                        if keyCheck[4][K_SLASH]:
                            if shifted:
                                boxes[i][0] += "?"
                            else:
                                boxes[i][0] += "/"
                        if keyCheck[4][K_BACKSLASH]:
                            if shifted:
                                boxes[i][0] += "|"
                            else:
                                boxes[i][0] += "\\"
                        if keyCheck[4][K_BACKSPACE]:
                            boxes[i][0] = boxes[i][0][:-1]
                    if currframe&32:
                        boxstr += "|"
                    else:
                        boxstr += " "
                colour_bottom = boxes[i][3]*16
                boxsize = 180
                txt = 24
                if display:
                    if len(boxes) <= 3:
                        boxsize = 512
                        txt = round(min(32,36-log(len(boxstr),1.2)))
                        pygame.draw.rect(systemVar[4],(colour_bottom,colour_bottom,colour_bottom),[boxes[i][1][0]-boxsize/2-96,boxes[i][1][1]-vscale*12+1,boxsize+192,vscale*23])
                    else:
                        pygame.draw.rect(systemVar[4],(colour_bottom,colour_bottom,colour_bottom),[boxes[i][1][0]-boxsize/2-32,boxes[i][1][1]-vscale*12+1,boxsize+64,vscale*23])
                    reg_polygon_complex(systemVar[4],boxes[i][1],(colour_top,colour_top,colour_top),4,boxsize,vscale*16,pi/4,255,4,6)
                    if boxsize != 512:
                        reg_polygon_complex(systemVar[4],boxes[i][1],(colour_top/2,colour_top/2,colour_top/2),4,boxsize-9,vscale*16-7,pi/4,127,2,3)
                    message_display(boxstr,txt,(colour_top,colour_mid,colour_mid),boxes[i][1])
            elif boxes[i][2] == 2 or boxes[i][2] == 4:
                colour_top = 127
                colour_mid = 255
                if mposition[0][0]-boxes[i][1][0] < 85 and mposition[0][0]-boxes[i][1][0] > -85 and mposition[0][1]-boxes[i][1][1] < 23 and mposition[0][1]-boxes[i][1][1] > -23:
                    colour_top = 255
                    if mouseCheck[1]:
                        for j in range(1,len(boxes)):
                            if boxes[j][2] == 2:
                                boxes[j][3] = 0
                        boxes[i][3] = 16
                if boxes[i][3]:
                    if boxes[i][3] > 1:
                        boxes[i][3] -= 1
                    elif boxes[i][3] == 1:
                        if boxes[i][2] == 4:
                            final_return[0] = True
                    final_return[1] = i
                    colour_top = 255
                    colour_mid = 0
                colour_bottom = boxes[i][3]*16
                boxstr += " "
                if display:
                    pygame.draw.rect(systemVar[4],(colour_bottom,colour_bottom,colour_bottom),[boxes[i][1][0]-85,boxes[i][1][1]-vscale*12+1,169,vscale*23])
                    reg_polygon_complex(systemVar[4],boxes[i][1],(colour_top,colour_top,colour_top),4,120,vscale*16,pi/4,255,4,6)
                    reg_polygon_complex(systemVar[4],boxes[i][1],(colour_top/2,colour_top/2,colour_top/2),4,111,vscale*16-7,pi/4,127,2,3)
                    message_display(boxstr,18,(colour_top,colour_mid,colour_mid),boxes[i][1])
            elif boxes[i][2] == 3:
                colour_top = 127
                colour_mid = 255
                colour_bottom = 16
                boxstr += " "
                if display:
                    pygame.draw.rect(systemVar[4],(colour_bottom,colour_bottom,colour_bottom),[boxes[i][1][0]-85,boxes[i][1][1]-vscale*12,169,vscale*23])
                    reg_polygon_complex(systemVar[4],boxes[i][1],(colour_top,colour_top,colour_top),4,120,vscale*16,pi/4,255,4,6)
                    message_display(boxstr,18,(colour_top,colour_mid,colour_mid),boxes[i][1])
            elif boxes[i][2] == 5:
                colour_top = 127
                colour_message = (127,127,127)
                colour_mid = 255
                shifted = False
                if boxes[i][3]:
                    if boxes[i][3] >= 1:
                        boxes[i][3] -= 1
                    colour_mid = 0
                    if keyCheck[0][K_LSHIFT] or keyCheck[0][K_RSHIFT]:
                        shifted = True
                    else:
                        shifted = False
                    if keyCheck[0][K_LCTRL] or keyCheck[0][K_RCTRL]:
                        controlled = True
                        if keyCheck[4][K_v]:
                            boxes[i][0] += pyperclip.paste()
                        elif keyCheck[4][K_c]:
                            pyperclip.copy(boxes[i][0])
                        elif keyCheck[4][K_BACKSPACE]:
                            boxes[i][0] = ""
                custom = False
                if boxes[i][4] != None:
                    if type(boxes[i][4][0]) is tuple:
                        startval = boxes[i][4][0][0]
                        endval = boxes[i][4][0][1]
                        custom = True
                    else:
                        startval = boxes[i][4][0]
                        endval = boxes[i][4][1]
                boxsize = 180
                if len(boxes) <= 3:
                    boxsize = 512
                if (mposition[0][0]-boxes[i][1][0] < boxsize/2+64 and mposition[0][0]-boxes[i][1][0] > -boxsize/2-64 and mposition[0][1]-boxes[i][1][1] < boxsize/11 and mposition[0][1]-boxes[i][1][1] > -boxsize/11) or boxes[i][3] > 14:
                    if keyCheck[0][K_LSHIFT] or keyCheck[0][K_RSHIFT]:
                        colour_message = (0,255,0)
                        colour_top = 255
                    if colour_top != 255:
                        colour_top = 255
                        colour_message = (191,191,191)
                    if mouseCheck[0]:
                        for j in range(1,len(boxes)):
                            if boxes[j][2] >= 1 and boxes[j][2] != 5:
                                boxes[j][3] = 0
                            elif boxes[j][2] == 5:
                                boxes[j][3] = 1
                        boxes[i][3] = 15
                        boxes[i][0] = (endval-startval)*(mposition[0][0]-boxes[i][1][0])/(boxsize+64)+startval+(endval-startval)/2
                        if boxes[i][0] > endval:
                            boxes[i][0] = endval
                        elif boxes[i][0] < startval:
                            boxes[i][0] = startval
                        if type(boxes[i][4]) is tuple:
                            boxes[i][0] = round(boxes[i][0])
                        elif boxes[i][3] and not shifted:
                            boxes[i][0] = round(ultra_round(boxes[i][0]),4)
                        boxes[i][0] = str(boxes[i][0])
                        boxstr = boxes[i][0]
                if custom:
                    boxstr = boxes[i][4][1][int(boxes[i][0])+startval]
                colour_bottom = boxes[i][3]*16
                if boxes[i][3] == 0:
                    colour_bottom = 32
                if colour_top != 127 and boxes[i][3] == 1:
                    colour_bottom = 64
                movepos = (ast.literal_eval(str(boxes[i][0]))-startval)/(endval-startval)
                colour_dial = colourCalculation(movepos*1536+256)
                d_sides = 4
                if display:
                    if boxsize == 512:
                        pygame.draw.rect(systemVar[4],(colour_bottom,colour_bottom,colour_bottom),[boxes[i][1][0]-boxsize/2-32,boxes[i][1][1]-vscale+1,boxsize+64,vscale*2])
                        reg_polygon_complex(systemVar[4],[boxes[i][1][0]-boxsize/2-32+movepos*(boxsize+64),boxes[i][1][1]+1],colour_dial,d_sides,20,20,frames/16,128,5,16,True)
                        reg_polygon_complex(systemVar[4],[boxes[i][1][0]-boxsize/2-32+movepos*(boxsize+64),boxes[i][1][1]+1],colour_dial,d_sides,20,20,frames/-16,127,5,16,True)
                        message_display(boxstr+" ",24,colour_message,[boxes[i][1][0],boxes[i][1][1]-22])
                    else:
                        pygame.draw.rect(systemVar[4],(colour_bottom,colour_bottom,colour_bottom),[boxes[i][1][0]-boxsize/2-32,boxes[i][1][1]-vscale+1,boxsize+64,vscale*2])
                        reg_polygon_complex(systemVar[4],[boxes[i][1][0]-boxsize/2-32+movepos*(boxsize+64),boxes[i][1][1]+1],colour_dial,d_sides,12,12,frames/16,128,4,8,True)
                        reg_polygon_complex(systemVar[4],[boxes[i][1][0]-boxsize/2-32+movepos*(boxsize+64),boxes[i][1][1]+1],colour_dial,d_sides,12,12,frames/-16,127,4,8,True)
                        message_display(boxstr+" ",16,colour_message,[boxes[i][1][0],boxes[i][1][1]-15])
        if final_return[0] != 0:
            break
        currframe = (frames) % 4096
        update()
    returns = []
    for r in range(1,len(boxes)):
        if boxes[r][2]%4 == 1:
            returns.append(boxes[r][0])
    while mouseCheck[0]:
        update()
    if len(returns) and final_return[0] != -1:
        return(returns)
    else:
        return(final_return[1])
def reg_polygon_complex(dest,centre,colour,sides,width,height,angle=math.pi/4,alpha=255,thickness=0,repetition=1,filled=False):
    global display
    if display:
        if width < 0:
            width = 0
        if height < 0:
            height = 0
        newS = pygame.Surface([width*2,height*2],pygame.SRCALPHA,32).convert_alpha()
        repetition = int(repetition)
        draw_direction = ((repetition>=0)*2-1)
        if draw_direction >= 0:
            a = draw_direction
            b = repetition+1
        else:
            a = repetition+1
            b = -draw_direction
        angle += (sides>=48)*.1*draw_direction
        if sides > 32:
            sides = 0
        elif sides < 0:
            sides = 0
        draw_direction *= max(thickness,3)-2
        loop = a
        setted = filled
        while loop < b+draw_direction:
            if loop-b > 0:
                loop = b
            move_direction = loop/repetition+.2
            points = []
            colourU = [colour[0]*move_direction+8,colour[1]*move_direction+8,colour[2]*move_direction+8]
            for i in range(0,3):
                if colourU[i] > 255:
                    colourU[i] = 255
            try:
                size = (min(width,height)-loop)
                if thickness > size:
                    thickness = size
                thickness = int(thickness)
                if setted:
                    thickness = 0
                    setted = False
                elif not filled:
                    thickness = int(thickness/2)+2
                if sides:
                    for p in range(0,sides):
                        points.append([width+(width-loop)*math.cos(angle+p*2*math.pi/sides),height+(height-loop)*math.sin(angle+p*2*math.pi/sides)])
                    pygame.draw.polygon(newS,colourU,points,thickness)
                else:
                    if thickness > loop:
                        thickness = 0
                    pygame.draw.ellipse(newS,colourU,(width-loop,height-loop,loop*2,loop*2),thickness)
            except:
                pass
            loop += draw_direction
        blit_complex(dest,newS,[centre[0]-width,centre[1]-height],alpha,0)
def blit_complex(dest,source,position,alpha,angle):
    try:
        newS = pygame.Surface([source.get_width(),source.get_height()]).convert()
        xpos = position[0]
        ypos = position[1]
        newS.blit(dest,(-xpos,-ypos))
        newS.blit(source,(0,0))
        newS.set_alpha(alpha)
        if angle:
            newS = pygame.transform.rotate(newS,-angle)
        dest.blit(newS,position)
    except:
        return False
    return True
def colourCalculation(lineColourT,offset=0):
    if not(type(lineColourT) is list or type(lineColourT) is tuple):
        lineColourT = (float(lineColourT),0,0)
    a = lineColourT[0]
    if a == math.nan or a == math.inf or a == -math.inf:
        return [0,0,0]
    elif a < 0:
        a = 0
    b = c = 0
    if a > 255:
        a %= 1536
        if a >= 256 and a < 512:
            b = a-256
            a = 255
        elif a >= 512 and a < 768:
            b = 255
            a = 768-a
        elif a >= 768 and a < 1024:
            b = 255
            c = a-768
            a = 0
        elif a >= 1024 and a < 1280:
            b = 1280-a
            c = 255
            a = 0
        elif a >= 1280:
            c = 255
            a -= 1280
        else:
            c = 256-a
            a = 255
    a = a+offset
    b = b+offset
    c = c+offset
    if a > 255:
        a = 255
    if b > 255:
        b = 255
    if c > 255:
        c = 255
    if a < 0:
        a = 0
    if b < 0:
        b = 0
    if c < 0:
        c = 0
    lineColourT = [a,b,c]
    return lineColourT
def update():
    global keyCheck,fps,rpf,origTime,currTime,diffTime,avgTime,mposition,mouseCheck,flash,playing,frames,brightness,display,started,shifted,controlled,pressed,screenSize,screenSize2,changedSize
    frames = (frames+1)%65536
    if display < 3:
        display = not(frames%rpf)
    if not ((mouseCheck[0] or pressed) and shifted):
        mposition[2] = mposition[0]
    mposition[1] = mposition[0]
    mposition[0] = list(pygame.mouse.get_pos())
    for m in range(0,len(mposition[0])):
        ratio = screenSize2[m]/screenSize[m]
        mposition[0][m] = round(mposition[0][m]/ratio)
    if pygame.mouse.get_pressed()[0]:
        if not mouseCheck[0]:
            mouseCheck[0] = True
            mouseCheck[1] = True
        else:
            mouseCheck[1] = False
    else:
        mouseCheck[0] = False
        mouseCheck[1] = False
    if pygame.mouse.get_pressed()[2]:
        if not mouseCheck[2]:
            mouseCheck[2] = True
            mouseCheck[3] = True
        else:
            mouseCheck[3] = False
    else:
        mouseCheck[2] = False
        mouseCheck[3] = False

    if changedSize:
        systemVar[0] = pygame.display.set_mode(screenSize2,pygame.RESIZABLE)
        changedSize = False
    if display:
        currFPS = 1/(avgTime+.0001)
        systemVar[4].blit(systemVar[1].render("FPS: "+str(round(currFPS,2)),True,(255,255,255)),(0,0))
        pygame.transform.smoothscale(systemVar[4],screenSize2,systemVar[0])
        pygame.display.update()
        col2 = [col[0]*brightness/256,col[1]*brightness/256,col[2]*brightness/256]
        for c in range(0,len(col2)):
            if col2[c] > 255:
                for d in range(0,len(col2)):
                    col2[d] += col2[c]-256
        for e in range(0,len(col2)):
            if col2[e] > 255:
                col2[e] = 255
        if display >= 2:
            systemVar[4].fill((0,0,0,0))
        else:
            systemVar[4].fill(col2)
            
    if brightness > 0:
        brightness -= 16
    waitTime = 2/fps-diffTime
    if not playing:
        waitTime *= 3
    while time.time() < origTime+waitTime:
        time.sleep(0.0001)
    currTime = time.time()
    diffTime = currTime-origTime
    origTime = currTime
    avgTime = (diffTime+4*avgTime)/5
    for event in pygame.event.get():
        if event.type == pygame.VIDEORESIZE:
            screenSize2 = list(event.size)
            changedSize = True
            aratio = round(sqrt(screenSize2[0]/screenSize[0]*screenSize2[1]/screenSize[1])*4)/4
            if not shifted:
                for s in range(0,len(screenSize2)):
                    curr = aratio*screenSize[s]
                    screenSize2[s] = math.ceil(curr)
        elif event.type == QUIT:
            try:
                if started == False:
                    [throwException]
                returntype = pickbox("Are you sure you want to quit?",["YES","NO"])
                if returntype == "YES":
                    [throwException]
            except:
                pquit()
                return(0)
    pygame.event.clear()
    keyCheck[0] = pygame.key.get_pressed()
    for key in range(0,len(keyCheck[0])):
        keyCheck[4][key] = False
        if keyCheck[0][key]:
            if keyCheck[3][key] == 0 or keyCheck[3][key] >= 16:
                keyCheck[4][key] = True
            keyCheck[3][key] += 1
        else:
            keyCheck[3][key] = 0
        if key == 303 or key == 304:
            keyCheck[2][key] = keyCheck[0][key]
        else:
            keyCheck[2][key] = keyCheck[0][key] and (keyCheck[0][key] ^ keyCheck[1][key])
    keyCheck[1] = tuple(keyCheck[0])
    shifted = False
    controlled = False
    if keyCheck[0][K_LSHIFT] or keyCheck[0][K_RSHIFT]:
        shifted = True
def playNote(n,m,mode):
    global channels,channel,keyCheck,held,pitchD,pitchO,detune,instr,insno,unison
    if mode:
        note = table2[n]
    else:
        note = table1[n]
    if note >= 0:
        channel = round(note*8)
        if mode:
            start = str(n)
        else:
            start = chr(n+97)
        if eval("keyCheck[m][K_"+start+"]"):
            try:
                insno = 0
                if note >= 12:
                    insno = 1
                note += instr[insno][1]+pitchO-96
                for i in range(int(unison)):
                    pitchoffset = (insno*2-1)*(detune*10)*math.ceil(i/2)*((int(i)&1)*2-1)
                    fin_note = pitchD+pitchoffset
                    if fin_note > 512:
                        fin_note = 512
                    elif fin_note <= 0:
                        fin_note = 0.00000000001
                    pitch = (fin_note)*(2**(1/12))**note

                    playSound(-1,pitch,channel+i)
            except:
                raise
        elif not eval("keyCheck[0][K_"+start+"]"):
            try:
                for i in range(int(unison)):
                    stopSound(channel+i)
            except:
                pass
        if eval("keyCheck[0][K_"+start+"]"):
            held = n
        return(held)
    else:
        return(0)
def playSound(length,frequency,channel):
    global timer,tbln,fps,sampleRate,volume,channels,note
    sample = numpy.array(createWave(frequency),dtype="int32")
    pan = 0
    try:
        note = pygame.sndarray.make_sound(sample)
    except:
        pass
    try:
        if channels[channel].get_sound() != note:
            channels[channel].play(note,-1,length,0)
            channels[channel].set_volume(volume*(1+pan)/sqrt(unison),volume*(1-pan)/sqrt(unison))
    except:
        return 0
    return 1
def stopSound(channel):
    global channels
    if channels[channel].get_sound() != None:
        channels[channel].stop()
    return 1
def createWave(frequency):
    global data,xcam,sampleRate,sampleLength,part1,part2,instr,insno
    xwave = xcam
    if instr[insno][0] > 0:
        xwave = instr[insno][0]*sampleLength
    soundArray = []
    ratio = (sampleRate/frequency)
    try:
        freq_pos = 16*2**(round(log(sampleLength/ratio,2)))
    except:
        freq_pos = 256
    freq_mult = sampleLength/sampleRate*frequency
    for inc in range(0,round(ratio*freq_pos)):
        pos_offset = int(inc*freq_mult)
        part1 = int(xwave+(pos_offset%sampleLength))
        part2 = part1+1
        if part2 >= sampleLength+xwave:
            part2 -= sampleLength
        bias = ((pos_offset)*sampleLength)%1
        y1 = data[part1]
        y2 = data[part2]
        if y1 >= 128:
            y1 -= 256
        if y2 >= 128:
            y2 -= 256
        pos = (y2*bias+y1*(1-bias))*256
        soundArray.append((pos,pos))
    return(soundArray)
def init():
    global keyCheck,mposition,mouseCheck,systemVar,screenSize,test,fps,sampleRate,origTime,channels
    try:
        origTime = time.time()
        test[2] = pygame.mixer.pre_init(frequency=sampleRate,size=-16,channels=2,buffer=int(sampleRate/86))
        test[0] = pygame.init()
        test[1] = pygame.font.init()
        for t in range(0,len(test)):
            if test[t] == 0:
                [throwException]
        systemVar[0] = pygame.display.set_mode(screenSize,pygame.RESIZABLE)
        systemVar[1] = pygame.font.Font(None,32)
        systemVar[4] = pygame.Surface(screenSize)
        keyL = pygame.key.get_pressed()
        keyCheck = [list(keyL),list(keyL),list(keyL),list(keyL),list(keyL)]
        mposition = [[0,0],[0,0],[0,0]]
        mouseCheck = [0,0,0,0]
        pygame.mixer.set_num_channels(512)
        channels = [pygame.mixer.Channel(n) for n in range(0,512)]
    except:
        print("Error initializing program.")
        raise
    pygame.display.set_caption("Wave Sample Generator")
    return(1)
def linearInterpolate(array,offset):
    global data,sampleRate,sampleLength,inputValues
    frequency = inputValues[4]
    ratio = int(sampleLength/frequency)
    part1 = math.floor(offset*sampleLength)
    if part1 >= len(array):
        part1 -= len(array)
    part2 = part1+1
    if part2 >= len(array):
        part2 -= len(array)
    bias = ((offset*sampleLength)%1)
    try:
        y1 = array[part1]
        y2 = array[part2]
    except:
        y1 = 0
        y2 = 0
    if y1 >= 128:
        y1 -= 256
    if y2 >= 128:
        y2 -= 256
    if len(array) < 16:
        bias = 0
    pos = y2*bias+y1*(1-bias)
    return pos
def dataR(offset):
    global data,dataX,sampleRate,sampleLength,inputValues
    return linearInterpolate(dataX,offset)/64
def dataF(offset):
    global data,dataY,sampleRate,sampleLength,inputValues
    return linearInterpolate(dataY,offset)/64
def save():
    global col,brightness,data,istring,output
    col = (0,255,0)
    brightness = 512
    for d in range(0,len(data)):
        data[d] = int(abs(data[d]%256))
    output = bytes(data)
    file = open(istring,"wb+")
    file.write(output)
    file.close()
    return(0)
def backup():
    global data,undoing
    undoing.append(list(data))
    if len(undoing) > 256:
        del(undoing[0])
def copy():
    global cutting,cutting2,data,xcam,sampleLength,shifted,col,brightness,m
    cutting = data[xcam:xcam+sampleLength]
    cutting2 = ""
    for currbyte in range(0,sampleLength):
        currnumber = hex(cutting[currbyte]%256)
        l = len(currnumber)
        currstring = currnumber[l-2:l]
        if currstring[0] == "x":
            currstring = "0"+currstring[1]
        if (currbyte+1)%16 == 0:
            cutting2 += currstring+"\n"
        else:
            cutting2 += currstring+" "
    if shifted:
        pyperclip.copy(pyperclip.paste()+"\r\n"+cutting2)
        col = (255,0,255)
    else:
        pyperclip.copy(cutting2)
        col = (0,0,255)
    brightness = 512
    m = 0
def paste():
    global pasting,pasting2,data,xcam,sampleLength,shifted,col,brightness,m
    backup()
    getpaste()
    for currbyte in range(0,len(pasting2)):
        data[xcam+currbyte] = pasting2[currbyte]
        if data[xcam+currbyte] >= 127:
            data[xcam+currbyte] -= 256
        if data[xcam+currbyte] >= 128:
            data[xcam+currbyte] = 127
        elif data[xcam+currbyte] <= -129:
            data[xcam+currbyte] = -128
    col = (255,255,0)
    brightness = 512
    m = 0
def getpaste():
    global pasting,pasting2,data,xcam,sampleLength,shifted,col,brightness,m
    pasting = pyperclip.paste()
    pasting2 = []
    curr = 0
    while curr < len(pasting):
        index = 0
        while True:
            found = False
            for valid in range(0,len(validhex)):
                if curr+index >= len(pasting):
                    break
                elif pasting[curr+index] == validhex[valid]:
                    found = True
            if found:
                index += 1
            else:
                if index:
                    number = int(pasting[curr:curr+index],16)
                    pasting2.append(number)
                else:
                    index += 1
                break
        curr += index+1
    return(pasting2)
def undo():
    global data,undoing,redoing,col,brightness
    try:
        if len(undoing) == 0:
            [throwException]
        redoing.append(list(data))
        if len(redoing) > 256:
            del(redoing[0])
        data = list(undoing[len(undoing)-1])
        del(undoing[len(undoing)-1])
        col = (255,0,0)
        brightness = 512
    except:
        pass
def redo():
    global data,undoing,redoing,col,brightness
    try:
        if len(redoing) == 0:
            [throwException]
        backup()
        data = list(redoing[len(redoing)-1])
        del(redoing[len(redoing)-1])
        col = (255,127,0)
        brightness = 512
    except:
        pass
def settings():
    global volume,mode,transform_length,detune,instr,data,unison,sampleLength
    ins_count = int(len(data)*transform_length)/sampleLength-1
    inputvar = multenterbox("Settings",["Volume","Render Mode","Interval Length","Instrument Detune","Lower Instrument","Lower Pitch","Upper Instrument","Upper Pitch","Unison Order"],
                            [volume,mode,transform_length*256,detune,round(instr[0][0]),instr[0][1],round(instr[1][0]),instr[1][1],unison],
                            [[0,1],((0,2),('Bars','Lines','Bars+Lines')),(1,256),[0,1],(-1,ins_count),[-24,24],(-1,ins_count),[-24,24],(1,8)])
    if inputvar != None:
        try:
            scaling = list(inputvar)
            volume = float(scaling[0])
            mode = int(scaling[1])
            transform_length = float(scaling[2])/256
            detune = float(scaling[3])
            instr = [[float(scaling[4]),float(scaling[5])],[float(scaling[6]),float(scaling[7])]]
            unison = float(scaling[8])
            file = open("settings.ini","w+")
            output = str([screenSize,screenSize2,volume,mode,transform_length,detune,instr,unison])
            file.write(output)
            file.close()
        except:
            try:
                msgbox("There was an error saving the settings.","Please try again.")
            except:
                pquit()

init()

while True:
    while True:
        if end:
            pquit()
            break
        while mouseCheck[0] or mouseCheck[1]:
            update()
        if not started:
            i = pickbox("Welcome!",["Start","Settings"])
            if i == "Settings":
                settings()
                continue
        try:
            started = True
            istring = enterbox("Enter the name of the 8-bit sample file to use: ","wave100")
            if istring == None:
                started = False
                continue
            else:
                istring = str(istring)
            sampleLength = enterbox("Enter the length of each sample in bytes: ","256")
            if sampleLength == None:
                started = False
                continue
            else:
                sampleLength = int(sampleLength)
            hscale = 4*256/sampleLength
            file = open(istring,"rb+")
            try:
                data = list(file.read())
            except:
                msgbox("The specified file was not found.","Please try again.")
                continue
            filelen = len(data)
            msgbox("File successfully opened!",str(filelen/sampleLength)+" samples detected.")
            file.close()
            break
        except:
            try:
                msgbox("There was an error while opening the file.","Please try again.")
            except:
                pquit()
        if end:
            pquit()
            break

    while True:
        if end:
            pquit()
            break
        m = 2
        if keyCheck[2][K_MINUS]:
            pitchO = round((pitchO-12)/12)*12
            m = 0
        if keyCheck[2][K_EQUALS]:
            pitchO = round((pitchO+12)/12)*12
            m = 0
        if keyCheck[0][K_LEFTBRACKET]:
            pitchO -= .25
            m = 0
        if keyCheck[0][K_RIGHTBRACKET]:
            pitchO += .25
            m = 0
        if not display == 3:
            if keyCheck[4][K_RIGHT]:
                xcam += sampleLength
                if xcam > filelen-sampleLength:
                    xcam = 0
                pygame.mixer.stop()
                m = 0
                brightness = 0
            if keyCheck[4][K_LEFT]:
                xcam -= sampleLength
                if xcam < 0:
                    xcam = filelen-sampleLength
                pygame.mixer.stop()
                m = 0
                brightness = 0
            if keyCheck[0][K_TAB] and display == 1 and brightness <= 0:
                display = 2
        if keyCheck[0][K_LCTRL] or keyCheck[0][K_RCTRL]:
            controlled = True
            if keyCheck[0][K_s] and brightness <= 0:
                save()
            elif keyCheck[0][K_z] and brightness <= 0:
                undo()
            elif keyCheck[0][K_y] and brightness <= 0:
                redo()
            elif keyCheck[2][K_e] or draw_increment:
                draw_increment += 1
                if display:
                    ioutput = [0 for e in range(0,int(len(data)/sampleLength))]
                    display = 3
                    xcam = 0
                    draw_increment = 0
            elif keyCheck[m][K_c]:
                copy()
            elif keyCheck[m][K_x]:
                backup()
                copy()
                for currbyte in range(0,sampleLength):
                    data[xcam+currbyte] = 0
            elif keyCheck[m][K_v]:
                paste()
        if keyCheck[2][K_ESCAPE]:
            if frames:
                settings()
                continue
        elif not controlled:
            if changed:
                m = 0
            held = False
            for n in range(0,26):
                playNote(n,m,False)
            for o in range(0,10):
                playNote(o,m,True)
            if not held:
                pygame.mixer.stop()
        pitchO %= 192
        if keyCheck[2][K_SPACE] and not display == 3:
            inp = pickbox('Select math equation to calculate a wave: ',equations1)
            multiplier = 1
            if not (inp == "" or inp == None):
                index = 1
                for i in range(0,len(equations1)):
                    if equations1[i] == inp:
                        index = i
                origeq = str(equation)
                equation = equations2[index]
                if equation == "data":
                    interpolation = float(enterbox("Select level of interpolation to be used",7,(0,7)))
                    ic = math.ceil(8-interpolation)
                    if ic <= 0:
                        ic = 1
                    dataI = getpaste()
                    dataX = []
                    for ix in range(0,len(dataI)):
                        for iy in range(0,ic):
                            dataX.append(dataI[ix])
                    equation = "dataR(z-(1-pulse)/sampleLength)"
                    try:
                        multiplier = sampleLength/len(dataX)
                    except:
                        multiplier = 0
                if equation == "flip":
                    flip = int(enterbox("Select direction to transform wave",0,((0,3),('None','Horizontal Flip','Vertical Flip','180° Rotation'))))
                    dataY = []
                    for f in range(0,sampleLength):
                        if flip&1:
                            g = sampleLength-f
                        else:
                            g = f
                        interval = data[xcam+g]
                        if flip&2:
                            interval *= -1
                        dataY.append(interval)
                    equation = "dataF(z-(1-pulse)/sampleLength)"
                if equation == "custom":
                    equation = enterbox("Enter custom math function (With respect to x):",origeq)
                    if equation == "" or equation == None:
                        equation = "0"
                        continue
                try:
                    #              0            1           2          3          4                      5                    6              7                  8            9           10               11
                    currfields = ("Wavelength","Amplitude","X Offset","Y Offset","Frequency Multiplier","Bandpass Frequency","Pulse Length","Clipping Position","Distortion","Bit Depth","Allow Wrapping","Operation")
                    currinputValues = (str(sampleLength*transform_length/256),str(transform_length*0.25),"0.0","0.0","1.0","1.0","0.5","1.0","0.0","8","0","0")
                    dtypes = [[0,4],[0,1],[-1,1],[-1,1],[0,16],[-1,1],[0,1],[-3,3],[0,2],[0,8],((0,1),("No","Yes")),((0,len(operations[0])-1),operations[0])]
                    inputValues = multenterbox('Enter the custom stats for the wave: ',currfields,currinputValues,dtypes)
                    frames = 0
                    if inputValues == None:
                        continue
                    
                    for value in range(0,10):
                        try:
                            exec("inputValues[value] = "+str(inputValues[value]))
                        except:
                            pass

                    for i in range(0,4):
                        inputValues[i] /= transform_length
                    backup()
                    inputValues[0] *= 256*multiplier
                    inputValues[1] *= 256
                    bitcrush = 256/(2**inputValues[9])
                    lowpass = inputValues[5]
                    inputValues[11] = operations[1][int(inputValues[11])]
                    for pulse in range(0,2):
                        if not pulse:
                            c = inputValues[6]
                            b = inputValues[0]*c+1
                            a = 0
                            d = 1
                        else:
                            c = (1-inputValues[6])
                            b = inputValues[0]
                            a = inputValues[0]-inputValues[0]*c
                            d = -1
                        for s in range(math.floor(a),math.ceil(b)):
                            try:
                                if d == 1:
                                    t = s-1
                                else:
                                    t = b-s+a-1
                                #print(t)
                                t += inputValues[2]*256
                                o = inputValues[3]*256
                                if t < 0:
                                    t += sampleLength
                                elif t >= sampleLength:
                                    t -= sampleLength
                                    if not ast.literal_eval(inputValues[10]):
                                        break
                                t = int(t)
                                if d == 1:
                                    z = (s/inputValues[0]*inputValues[4])/c/2*d
                                else:
                                    z = 1-((b-s+a-1-256)/inputValues[0]*inputValues[4])/c/2*d
                                x = z*2*math.pi
                                lowp = sin(x)*min(max(1-lowpass,-1),1)
                                if lowpass == 1 or lowpass == -1 or lowpass == 0:
                                    lowmult = lowpass
                                else:
                                    lowmult = (min(abs((-(abs((z+.25)%1*2-1)-.5)/2*sqrt(3)*pi)),1/(lowpass*32))*lowpass*32)*min(max(lowpass,-1),1)
                                #print(z)

                                if inputValues[11] == "=":
                                    exec("data[t+xcam] = int(round((raisec(("+equation+")*lowmult+lowp+random.randint(-256,256)/4096*inputValues[8],1/inputValues[7])*inputValues[1]+o)/bitcrush,0)*bitcrush)")
                                elif inputValues[11] == "*" or inputValues[11] == "**" or inputValues[11] == "/":
                                    exec("data[t+xcam] = int(((data[t+xcam]/128 "+inputValues[11]+" round(raisec(("+equation+")*lowmult+lowp+random.randint(-256,256)/4096*inputValues[8],1/inputValues[7])*inputValues[1]+o))/bitcrush/128)*bitcrush*128)")
                                else:
                                    exec("data[t+xcam] = data[t+xcam] "+inputValues[11]+" int(round((raisec(("+equation+")*lowmult+lowp+random.randint(-256,256)/4096*inputValues[8],1/inputValues[7])*inputValues[1]+o)/bitcrush,0)*bitcrush)")
                                if data[t+xcam] > 256 or data[t+xcam] < -256:
                                    0/0
                                if data[t+xcam] > 127:
                                    data[t+xcam] -= 256
                                if data[t+xcam] > 127:
                                    data[t+xcam] = 127
                                elif data[t+xcam] < -128:
                                    data[t+xcam] = -128
                                data[t+xcam] %= 256
                            except ZeroDivisionError:
                                data[t+xcam] = 0
                                continue
                            except OverflowError:
                                data[t+xcam] = 0
                                continue
                            except:
                                raise
                except:
                    undo()
                    msgbox("Error!","There was an error applying the function.")
        oldposition = [0,screenSize[1]/2,""]
        if mouseCheck[0]:
            pressed = 1
        else:
            if pressed == 1:
                pressed = 2
            else:
                pressed = 0
                lastval = currval
        if not shifted:
            lastval = currval
        currval = int((screenSize[1]/2-mposition[0][1])/vscale)-1
        if currval == 128:
            currval = -128
        if mouseCheck[1]:
            backup()
        if end:
            break
        thickness = 4
        allD = True
        if display == 3:
            allD = False
            thickness = 48
        surf = [pygame.Surface(screenSize).convert_alpha(),pygame.Surface(screenSize).convert_alpha(),pygame.Surface(screenSize).convert_alpha()]
        for s in range(0,len(surf)):
            if (mode == 1 and s == 2) or allD:
                surf[s].fill((0,0,0,0))
        y = data[xcam+sampleLength-1]
        if y >= 128:
            y -= 256
        dy = int(y*vscale)
        lastpos = (hscale*-.5,screenSize[1]/2-dy)
        currCol = (y+256)*6+sampleLength
        if mode >= 1:
            pygame.draw.line(systemVar[4],(96,96,96),(0,screenSize[1]/2),(screenSize[0],screenSize[1]/2),thickness)
        changed = False
        m1 = mposition[0][0]/hscale
        m2 = mposition[2][0]/hscale
        for e in range(0,sampleLength):
            f = e+xcam
            y = data[f]
            if y >= 128:
                y -= 256
                data[f] = y
            lastCol = currCol
            currCol = (y+256)*6+sampleLength
            if mode != 1:
                lineCol = currCol
            else:
                lineCol = (currCol+lastCol)/2
            colourA = colourCalculation((lineCol,0,0))
            colourB = (colourA[0]*.75,colourA[1]*.75,colourA[2]*.75)
            colourC = (colourA[0]*.5,colourA[1]*.5,colourA[2]*.5)
            if display:
                dy = int(y*vscale)
                if mode != 1:
                    pygame.draw.rect(systemVar[4],colourA,(e*hscale,screenSize[1]/2-dy,hscale,dy))
                pos = ((e+.5)*hscale,screenSize[1]/2-dy)
                if mode >= 1:
                    if allD:
                        pygame.draw.line(surf[0],colourC,lastpos,pos,thickness+4)
                        pygame.draw.line(surf[1],colourB,lastpos,pos,thickness+2)
                    pygame.draw.line(surf[2],colourA,lastpos,pos,thickness)
                lastpos = pos
            if ((int(m1) >= int(e) and int(m2) <= int(e)) or (int(m1) <= int(e) and int(m2) >= int(e))) and not display>=2:
                if (pressed and not shifted) or pressed == 2:
                    try:
                        changeval = int((lastval-currval)*(e-m2)/(m2-m1)+lastval)
                    except:
                        changeval = currval
                    if changeval < -128:
                        changeval = -128
                    elif changeval > 127:
                        changeval = 127
                    if data[f] != changeval:
                        changed = True
                        data[f] = changeval
                        y = data[f]
                        if y >= 128:
                            y -= 256
                if display != 2:
                    dy = mposition[0][1]-y*vscale
                    if mode == 0:
                        pygame.draw.rect(surf[2],(127,127,127),(e*hscale,screenSize[1]/2-y*vscale,hscale,y*vscale))
                        pygame.draw.rect(surf[2],(223,223,223),(e*hscale,mposition[0][1],hscale,screenSize[1]/2-mposition[0][1]))
                    else:
                        pygame.draw.rect(surf[2],(223,223,223),(e*hscale,mposition[0][1],hscale,screenSize[1]/2-y*vscale-mposition[0][1]))
                    if display:
                        currposition = [e*hscale+14,screenSize[1]/2-y*vscale]
                        if currposition[0] > screenSize[0]-36:
                            currposition[0] = screenSize[0]-36
                        if currposition[1] > screenSize[1]-48:
                            currposition[1] = screenSize[1]-48
                        oldposition = list(currposition)+[y]
        if display:
            if mode != 0:
                y = data[xcam]
                dy = int(y*vscale)
                pos = (hscale*(sampleLength+.5),screenSize[1]/2-dy)
                if allD:
                    pygame.draw.line(surf[0],colourC,lastpos,pos,thickness+4)
                    pygame.draw.line(surf[1],colourB,lastpos,pos,thickness+2)
                pygame.draw.line(surf[2],colourA,lastpos,pos,thickness)
            for s in range(0,len(surf)):
                if (mode == 1 and s == 2) or allD:
                    systemVar[4].blit(surf[s],(0,0))
        if mouseCheck[0]:
            pygame.draw.line(systemVar[4],(0,0,0),mposition[0],mposition[2],12)
            pygame.draw.line(systemVar[4],(255,255,255),mposition[0],mposition[2],8)
        if display == 2:
            pygame.image.save(systemVar[4],"saves/wave"+str(int(xcam/sampleLength))+".png")
            col = (255,255,255)
            brightness = 255
            tempf = open("saves/wave"+str(int(xcam/sampleLength))+".wav","wb+")
            outA = [82,73,70,70,36,1,0,0,87,65,86,69,102,109,116,32,16,0,0,0,1,0,1,0,172,130,0,0,
                          88,5,1,0,2,0,16,0,100,97,116,97,0,1,0,0]
            outA += data[xcam:xcam+256]
            for f in range(44,len(outA)):
                if outA[f] < 0:
                    outA[f] += 256
            outF = bytes(outA)
            tempf.write(outF)
            tempf.close
        if display == 3:
            ioutput[int(xcam/sampleLength)] = systemVar[4].copy().convert_alpha()
            xcam += sampleLength
            if xcam > filelen-sampleLength:
                xcam = 0
            if xcam == 0:
                display = 1
                template = pygame.image.load("template.png").convert_alpha()
                for i in range(0,len(ioutput)):
                    if i < 100:
                        x = i%10
                        y = math.ceil((i+1)/10)-1
                        image1 = pygame.transform.smoothscale(ioutput[i],[32,32]).convert_alpha()
                        image2 = pygame.transform.scale(ioutput[i],[32,32]).convert_alpha()
                        blit_complex(image1,image2,(0,0),64,0)
                        template.blit(image1,(x*36+(x>=5)*4+8,(y*48+(y>=5)*4+16)))
                        tempf = open("saves/wave"+str(i)+".wav","wb+")
                        outA = [82,73,70,70,36,1,0,0,87,65,86,69,102,109,116,32,16,0,0,0,1,0,1,0,172,130,0,0,
                                      88,5,1,0,2,0,16,0,100,97,116,97,0,1,0,0]
                        outA += data[i*256:i*256+256]
                        for f in range(44,len(outA)):
                            if outA[f] < 0:
                                outA[f] += 256
                        outF = bytes(outA)
                        tempf.write(outF)
                        tempf.close
                pygame.image.save(template,"saves/wave100.bmp")
        if display <= 1:
            systemVar[4].blit(systemVar[1].render("Global Pitch: "+str(float(pitchO))+'000',True,(255,255,255)),(screenSize[0]-222,screenSize[1]-19))
            systemVar[4].blit(systemVar[1].render("Wave: "+str(int(xcam/sampleLength)),True,(255,255,255)),(0,screenSize[1]-19))
            crosshairwidth = 6*(2+shifted)
            pygame.draw.circle(systemVar[4],colourCalculation((frames*3,0,0)),mposition[0],crosshairwidth-4,2)
            pygame.draw.line(systemVar[4],colourCalculation((frames*3,0,0)),[mposition[0][0]-1,mposition[0][1]-1-crosshairwidth],[mposition[0][0]-1,mposition[0][1]-1+crosshairwidth],2)
            pygame.draw.line(systemVar[4],colourCalculation((frames*3,0,0)),[mposition[0][0]-1-crosshairwidth,mposition[0][1]-1],[mposition[0][0]-1+crosshairwidth,mposition[0][1]-1],2)
            currposition = [mposition[0][0]+14,mposition[0][1]]
            if currposition[0] > screenSize[0]-36:
                currposition[0] = screenSize[0]-36
            if currposition[1] > screenSize[1]-48:
                currposition[1] = screenSize[1]-48
            systemVar[4].blit(systemVar[1].render(str(oldposition[2]),True,(255,255,255)),oldposition[0:2])
            systemVar[4].blit(systemVar[1].render(str(currval),True,(127,127,127)),currposition)
        if display == 3:
            doneA = int(xcam/sampleLength)
            sampleA = int(len(data)/sampleLength)
            systemVar[4].fill(colourCalculation(doneA/sampleA*1536))
            message_display(str(doneA)+"/"+str(sampleA),48,(255,255,255),(screenSize[0]/2,screenSize[1]/2))
        if end:
            pquit()
            break
        update()
sys.exit(0)

import os
import cv2
import math
import numpy as np
from PIL import ImageTk, Image
from matplotlib import pyplot as plt

# Classe para armazenar um pico 
class Pico:
    rho = 0
    tetha = 0
# Fim da classe pico ----------
# ----------------------------------------
# Classe para armazena um segmento de reta 
class Segmento: 
    x1 = 0
    y1 = 0
    x2 = 0 
    y2 = 0
# Fim da classe Segmento ----------------

class Dot: 
    x = 0
    y = 0
# Fim da classe dot

# função para aplicar a transformada de Hough
def HoughLines (img, min_length, max_length):
    transformada = []
    hipotenusa = int(round(math.sqrt(len(img)*len(img) + len(img[0])*len(img[0]))))
    for i in range(int(hipotenusa)*2): 
        linha = []
        for j in range(0,180,1): 
            linha.append(0)
        transformada.append(linha)
    ## Matriz transformada gerada!!!

    #print('Valores da transformada: ',len(transformada), len(transformada[0]))

    ## Calculando a transformada de Hough
    for x in range(len(img)): 
        for y in range(len(img[x])): 
            if img[x][y] == 255:        # Achado um pixel branco 
                for tetha in range(0,180,1): 
                    cosseno = math.cos(tetha * math.pi / 180)
                    seno = math.sin(tetha * math.pi / 180)
                    p = int(round(x * cosseno + y * seno + hipotenusa))
                    transformada[p][tetha] += 1
    ## Fim do calculo da transformada 

    picos = []
    ## Retornando um vetor com os picos 
    for rho in range(len(transformada)): 
        for tetha in range(len(transformada[rho])):
            if transformada[rho][tetha] > min_length: 
                pico = Pico()
                pico.rho = int(round(rho - hipotenusa -2))
                pico.tetha = tetha
                picos.append(pico)
    return transformada, picos            
# ---------------------------------- Fim da função de Hough

# Funçao para verificar se na vizinhança do pixel existe um pixel com a cor color 
def VerificarVizinhaca (img, x, y, color):
    #print(x,y,len(img),len(img[0]))
    cor = color
    if img[x][y] == cor: 
        return True
    else: 
        somX = 1
        somY = 1
        subX = -1
        subY = -1 
        if x == 0: 
            subX = 0
        if y == 0: 
            subY = 0
        if x == len(img)-1: 
            somX = 0
        if y == len(img[0])-1: 
            somY = 0
        if img[x+subX][y+subY] == cor or img[x][y+subY] == cor or img[x+somX][y+subY] == cor or img[x+subX][y] == cor or img[x+somX][y] == cor or img[x+subX][y+somY] == cor or img[x][y+somY] == cor or img[x+somX][y+somY] == cor:
            return True
        else: 
            return False
# Fim da funcao de busca na vizinhanca ------------------------------

def BuscarReta (img, reta):
    ## Calculando o seno e cosseno de tetha 
    rho = reta.rho
    tetha = reta.tetha
    cosseno = math.cos(tetha * math.pi / 180)
    seno = math.sin(tetha * math.pi / 180)

    reta = []

    if abs(seno) <= 0.2: 
        for y in range(0,len(img[0]),1): 
            x = int(round(rho - y*seno)/cosseno)
            if x >= len(img): 
                x = len(img)-1
            dot = Dot()
            dot.x = x 
            dot.y = y
            reta.append(dot)
    else: 
        for x in range(0,len(img), 1): 
            y = int(round(rho - x*cosseno)/seno)
            if y >= len(img[0]):
                y = len(img[0])-1
            dot = Dot()
            dot.x = x
            dot.y = y
            reta.append(dot)
    return reta
## Fim da procura por retas 

def BuscarSegmento (img, reta, min, gap):

    isCounting = False 
    isSegment  = False 
    countingGap = False 
    count_seg = 0
    count_gap = 0
    x_inicio = 0
    x_final = 0
    y_inicio = 0
    y_final = 0
    segmentos = []
    for dot in reta: 
        x = dot.x 
        y = dot.y
        # Encontrando um pixel branco
        if(VerificarVizinhaca(img,x,y,255)): 
            # Começa a contar se não estava 
            if isCounting == False: 
                isCounting = True
                x_inicio = x
                y_inicio = y
            
            count_seg += 1  # Acrescenta 1 o contador do tamanho

            # Reseta a gap se estiver contando gap
            if countingGap == True: 
                countingGap = False
                count_gap = 0
                x_final = 0
                y_final = 0

            if count_seg >= min and isSegment == False:
                isSegment = True
        else: 
            if isCounting == True and isSegment == False: 
                isCounting = False
                count_seg = 0
                # n precisa zerar o começo 
            else: 
                if isCounting == True and isSegment == True: 
                    # Encontrado um possivel gap 
                    if countingGap == False: 
                        countingGap = True
                        x_final = x
                        y_final = y
                        # salva o final TODO
                    
                    # Acrescentando 1 no contador do gap 
                    count_gap += 1

                    if count_gap >= gap or reta.index(dot) == len(reta)-1: 
                        segmento = Segmento()
                        segmento.x1 = x_inicio
                        segmento.y1 = y_inicio
                        segmento.x2 = x_final
                        segmento.y2 = y_final
                        count_gap = 0
                        count_seg = 0
                        x_inicio = 0
                        x_final = 0
                        y_inicio = 0
                        y_final = 0
                        isSegment = False
                        isCounting = False 
                        countingGap = False
                        segmentos.append(segmento) 
    return segmentos

# Fim da busca dos segmentos 

def Rotacionar (angle, x, y, Tx, Ty): # Função para rotacionar uma coordenada
    tetha = (angle * math.pi / 180)
    x_linha = int(round(x * math.cos(tetha) - y * math.sin(tetha) + Tx))
    y_linha = int(round(x * math.sin(tetha) + y * math.cos(tetha) + Ty))
    return x_linha, y_linha
# Fim da função de rotação -----------------------------------------

def PlotarLinha(img, x1, y1, x2, y2, angulo, tx, ty, cor, line):
    xy1 = Rotacionar(angulo, x1, y1, tx, ty)
    xy2 = Rotacionar(angulo, x2, y2, tx, ty)
    cv2.line(img, (xy1), (xy2), cor, line)

# -------------------------------------------------------------------
#                     COMEÇO DO PROGRAMA PRINCIPAL
# -------------------------------------------------------------------

nome = 'im.png'

## Variaveis Globais
## ------- Manipulação do desenho
anguloRotacao = 90
TranslacaoX = 120 
TranslacaoY = 0

## Thesholds 
votacaoHough = 20
lenghtMinSeg = 8
lengthGap = 5

## Carregando imagens
img = cv2.imread(nome) 
retasImg = cv2.imread(nome) 
finalImage = cv2.imread(nome) 
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray,100,200)

retas = []
transformada, picos = HoughLines(edges, votacaoHough, 500)

# Após encontrados os picos na transformada de Hough, hora de
# Encontrar as retas, o código abaixo retorna um vetor de pontos
# aonde os pontos são coordenadas x, y
for pico in picos:
    retas.append(BuscarReta(edges,pico))

# Com as retas encontradas, é hora de encontrar os segmentos
# O vetor segmentos possui objetos com x, y final e inicial 
segmentos = []
for dots in retas:  
    reta = [dots[0], dots[-1]]
    PlotarLinha(retasImg, reta[0].x, reta[0].y, reta[1].x, reta[1].y, anguloRotacao, TranslacaoX, TranslacaoY, (0,255,0), 1)
    segmentos.append(BuscarSegmento(edges, dots, lenghtMinSeg, lengthGap))

# Desenhando na imagem 
for segs in segmentos: 
    for seg in segs:                                        # tetha, Tx, Ty,    RGB,    thick
        PlotarLinha(finalImage, seg.x1, seg.y1, seg.x2, seg.y2, anguloRotacao, TranslacaoX, TranslacaoY, (255, 0, 0), 1)

# Mostrando as imagens
plt.subplot(231),plt.imshow(img,cmap = 'gray')
plt.title('Imagem Original'), plt.xticks([]), plt.yticks([])

plt.subplot(232),plt.imshow(gray,cmap = 'gray')
plt.title('Imagem Cinza'), plt.xticks([]), plt.yticks([])

plt.subplot(233),plt.imshow(edges,cmap = 'gray')
plt.title('Aplicado o Canny'), plt.xticks([]), plt.yticks([])

plt.subplot(234),plt.imshow(transformada,cmap = 'gray')
plt.title('Transformada'), plt.xticks([]), plt.yticks([])

plt.subplot(235),plt.imshow(retasImg,cmap = 'gray')
plt.title('Retas'), plt.xticks([]), plt.yticks([])

plt.subplot(236),plt.imshow(finalImage,cmap = 'gray')
plt.title('Segmentos'), plt.xticks([]), plt.yticks([])

plt.show()
# Fim do programa
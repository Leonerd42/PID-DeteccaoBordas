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

# função para aplicar a transformada de Hough
def HoughLines (img, min_length, max_length):
    transformada = []
    hipotenusa = math.sqrt(len(img)*len(img) + len(img[0])*len(img[0]))
    for i in range(int(hipotenusa)*2+1): 
        linha = []
        for j in range(0,180,1): 
            linha.append(0)
        transformada.append(linha)
    ## Matriz transformada gerada!!!

    ## Calculando a transformada de Hough
    for x in range(len(img)): 
        for y in range(len(img[x])): 
            if img[x][y] == 255:        # Achado um pixel branco 
                for tetha in range(0,180,1): 
                    cosseno = math.cos(tetha * math.pi / 180)
                    seno = math.sin(tetha * math.pi / 180)
                    p = int(round(x * cosseno + y * seno + len(img)))
                    transformada[p][tetha] += 1
    ## Fim do calculo da transformada 

    picos = []
    ## Retornando um vetor com os picos 
    for rho in range(len(transformada)): 
        for tetha in range(len(transformada[rho])):
            if transformada[rho][tetha] > min_length: 
                pico = Pico()
                pico.rho = int(round(rho - hipotenusa))
                pico.tetha = tetha
                picos.append(pico)

    return picos            
# ---------------------------------- Fim da função de Hough

# Funçao para verificar se na vizinhança do pixel existe um pixel com a cor color 
def VerificarVizinhaca (img, x, y, color):
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

def BuscarSegmento (img, reta, min_length, gaps, line_color):
    ## Calculando o seno e cosseno de tetha 
    tetha = reta.tetha
    cosseno = int(round(math.cos(tetha * math.pi / 180)))
    seno = int(round(math.sin(tetha * math.pi / 180)))
    segmentosReta = []

    ## Seno e cosseno encontrados!!! Função y eh y = ( p - x * cos (tetha) )/ sin (tetha)
    ## Logo seno não pode ser 0 
    if seno == 0: 
        ## Tratar como uma reta vertical 
        x = reta.rho
        if reta.rho < 0: 
             x *= (-1)
             x = int(round(x/2))            
        isCounting = False 
        isSegment  = False 
        countingGap = False 
        count_seg = 0
        count_gap = 0
        y_inicio = 0
        y_final = 0
        for y in range(0,len(img[0]),1): 
            if VerificarVizinhaca(img, x, y, line_color): 
                ## Existe um segmento de linha
                if isCounting == False:  # já esta contando o segmento 
                    isCounting = True
                count_seg +=1            # Sempre sera contando quando encontrar um pixel da cor color
                ## Resetando a gap se ela for menor que o tamanho da gap: 
                if countingGap == True: 
                    countingGap = False
                    count_gap = 0
                    y_final = 0  # Zerando o final do segmento 
                ## Zerado o contador de gaps 

                ## Verificando se ja passou do comprimento minimo 
                if count_seg >= min_length and isSegment == False: 
                    # Salvando o inicio do segmento!!
                    isSegment = True
                    y_inicio = y
                # -- Fim do salvamento do segmento 
            else:
                if isCounting == True and isSegment == False: # Se estiver contando, mas ainda não é um segmento  
                    isCounting = False
                    count_seg = 0
                else: 
                    if isCounting == True and isSegment == True:
                        ## Encontrado um possivel gap 
                        if countingGap == False:  ## Primeiro pixel contrario ao color 
                            countingGap = True
                            y_final = y            # Salvando o ponto que terminou o segmento 
                        
                        count_gap += 1

                        ## Verificando se passou do tamanho da gap 
                        if count_gap >= gaps:   # Acabou o segmento aqui 
                            count_gap = 0
                            count_seg = 0
                            segmento = Segmento() 
                            segmento.x1 = x
                            segmento.y1 = y_inicio
                            segmento.x2 = x
                            segmento.y2 = y_final
                            y_final = 0
                            isSegment = False
                            isCounting = False
                            countingGap = False
                            segmentosReta.append(segmento)
                            #print('final!')
    #-- Fim do tratamento de uma reta vertical     
    else: 
        ## Tratar como uma reta normal 
        #print('Outras retas')
        x_inicio = 0
        y_inicio = 0
        x_final = 0
        y_final = 0
        isCounting = False 
        isSegment  = False 
        countingGap = False 
        count_seg = 0
        count_gap = 0
        for x in range(len(img)):
            y = int(round((reta.rho - x * cosseno) / seno ))

            if VerificarVizinhaca(img, x, y, line_color): 
                ## Existe um segmento de linha
                if isCounting == False:  # já esta contando o segmento 
                    isCounting = True
                count_seg += 1            # Sempre sera contando quando encontrar um pixel da cor color
                ## Resetando a gap se ela for menor que o tamanho da gap: 
                if countingGap == True: 
                    countingGap = False
                    count_gap = 0
                    x_final = 0
                    y_final = 0  # Zerando o final do segmento 
                ## Zerado o contador de gaps 

                ## Verificando se ja passou do comprimento minimo 
                if count_seg >= min_length and isSegment == False: 
                    # Salvando o inicio do segmento!!
                    isSegment = True
                    x_inicio = x
                    y_inicio = y
                # -- Fim do salvamento do segmento 
            else:
                if isCounting == True and isSegment == False: # Se estiver contando, mas ainda não é um segmento  
                    isCounting = False
                    count_seg = 0
                else: 
                    if isCounting == True and isSegment == True:
                        ## Encontrado um possivel gap 
                        if countingGap == False:  ## Primeiro pixel contrario ao color 
                            countingGap = True
                            x_final = x
                            y_final = y            # Salvando o ponto que terminou o segmento 
                        
                        count_gap += 1

                        ## Verificando se passou do tamanho da gap 
                        if count_gap >= gaps:   # Acabou o segmento aqui 
                            count_gap = 0
                            count_seg = 0
                            segmento = Segmento() 
                            segmento.x1 = x_inicio
                            segmento.y1 = y_inicio
                            segmento.x2 = x_final
                            segmento.y2 = y_final
                            segmentosReta.append(segmento)
                            x_final = 0
                            y_final = 0
                            isSegment = False
                            isCounting = False
                            countingGap = False
                            print('Salvo um segmento não vertical!', x_inicio, y_inicio, x_final, y_final)
    return segmentosReta            

# Fim da função Buscar Segmento -----------------

def Rotacionar (angle, x, y): # Função para rotacionar uma coordenada
    tetha = (angle * math.pi / 180)
    transl_x = 0
    transl_y = 0
    x_linha = int(round(x * math.cos(tetha) - y * math.sin(tetha) + transl_x))
    y_linha = int(round(x * math.sin(tetha) + y * math.cos(tetha) + transl_y))
    return x_linha, y_linha
# Fim da função de rotação -----------------------------------------

# -------------------------------------------------------------------
#                     COMEÇO DO PROGRAMA PRINCIPAL
# -------------------------------------------------------------------

img = cv2.imread('square.png') 
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray,100,200)
output = edges

segmentos = []
picos =  HoughLines(edges, 0, 200)

anguloRotacao = 0

# for pico in picos: 
#     print (pico.rho, pico.tetha)

for pico in picos:
    auxiliar = BuscarSegmento(edges,pico,20,5,255)
    for seg in auxiliar: 
        print(seg.x1, seg.y1, seg.x2, seg.y2)
    segmentos.append(auxiliar)

print('Desenhando na imagem!')
for segmento in segmentos: 
    for seg in segmento: 
        #print('here')
        cv2.line(img, (Rotacionar(anguloRotacao, seg.x1, seg.y1)),(Rotacionar(anguloRotacao,seg.x2, seg.y2)),(0,255,0),2)

# testes = BuscarSegmento(output, picos[2], 10, 5, 255)
# for teste in testes: 
#     print ('Segmento de reta: '), 
#     print (teste.x1, teste.y1, teste.x2, teste.y2)
#     cv2.line(img, (teste.x1, teste.y1), (teste.x2, teste.y2), (255,0,0), 1)

finalImage = output

# Mostrando a imagem 
plt.subplot(231),plt.imshow(img,cmap = 'gray')
plt.title('Original Image'), plt.xticks([]), plt.yticks([])
plt.subplot(232),plt.imshow(gray,cmap = 'gray')
plt.title('Gray Image'), plt.xticks([]), plt.yticks([])
plt.subplot(233),plt.imshow(edges,cmap = 'gray')
plt.title('Bordas'), plt.xticks([]), plt.yticks([])
plt.subplot(234),plt.imshow(finalImage,cmap = 'gray')
plt.title('Segmentos'), plt.xticks([]), plt.yticks([])

plt.show()
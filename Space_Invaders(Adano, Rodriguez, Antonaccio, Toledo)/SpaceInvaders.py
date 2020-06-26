#--- INTEGRANTES ------------
#--- Ana Adano
#--- Felipe Rodriguez
#--- Magdalena Antonaccio
#--- Pedro Toledo
#-----------------------------

#importamos las librerias
import pygame
import time
import random
import os
import sys

pygame.font.init()
pygame.init()


largo_vent = 600                                                    #dimensiones de la ventana
ancho_vent = 600

VENTANA = pygame.display.set_mode((largo_vent, ancho_vent))         #se crea la ventana
pygame.display.set_caption("Space Invaders")                         #titulo de la ventana

NAVE1 = pygame.image.load(os.path.join('complementos', 'nave1.png'))        #imagen de la nave para el jugador

NAVE2 = pygame.image.load(os.path.join('complementos', 'invasor.png'))     #imagen de la nave para el enemigo

BALA_AZUL = pygame.image.load(os.path.join('complementos', 'bala1.png'))  #imagen bala del jugador

FONDO = pygame.transform.scale(pygame.image.load(os.path.join('complementos', 'fondo.jpg')),(largo_vent, ancho_vent))     #imagen escalada del fondo para que se ajuste al tamaño de la ventana

LaserSonido = pygame.mixer.Sound(os.path.join('complementos', 'Laser.wav'))     #Se carga el sonido laser

MusicaFondo = pygame.mixer.music.load(os.path.join('complementos', 'Sonido_Fondo.wav'))     #Se carga la musica de fondo

ExplosionSonido = pygame.mixer.Sound(os.path.join('complementos', 'Explosion.wav'))     #Se carga el sonido explosion

GameOverSonido = pygame.mixer.Sound(os.path.join('complementos', 'Game_Over.wav'))      #Se carga el sonido al perder el juego

VidaMenosSonido = pygame.mixer.Sound(os.path.join('complementos', 'Vida_Menos.wav'))    #Se carga el sonido al perder una vida



class Bala:                                                #se crea la clase para las balas
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def dibujo(self, ventana):                              #funcion para dibujar dentro de la ventana las balas
        ventana.blit(self.img, (self.x, self.y))

    def mov(self, vel):                                     #movimiento de la bala
        self.y += vel

    def off_screen(self, largo):                            #funcion para determinar si se va de la pantalla
        return not(self.y <= largo and self.y >= 0)

    def colision(self, obj):                                #funcion para determinar si colisiona
        return colisiona(self, obj)


class NAVE:                                                 #se crea la clase para las naves  
    ESPERA = 15                                             #hay una pequeña espera entre disparo y disparo

    def __init__(self, x, y):                               
        self.x = x
        self.y = y
        self.nave_img = None
        self.bala_img = None
        self.balas = []
        self.contador_espera = 0                            #contador para la espera entre disparo y disparo

    def dibujo(self, ventana):                              #funcion para dibujar dentro de la ventana la nave en posicion inical
        ventana.blit(self.nave_img, (self.x, self.y))       
        for bala in self.balas:        
            bala.dibujo(ventana)                            #dibujamos las balas

    def mov_balas(self, vel, obj):                         #funcion para el movimiento de las balas
        self.espera()
        for bala in self.balas:
            bala.mov(vel)
            if bala.off_screen(largo_vent):                 
                self.balas.remove(bala)                     #se eliminan las balas de la lista si se salen de la pantalla
            elif bala.colision(obj):
                self.balas.remove(bala)                     #se eliminan las balas de la lista al colicionar con los enemigos

    def espera(self):                                       #función para que espere entre disparos
        if self.contador_espera >= self.ESPERA:
            self.contador_espera = 0
        elif self.contador_espera > 0:                      #espera de 15 seg
            self.contador_espera += 1


    def dispara(self):                                     #funcion para disparar las balas
        if self.contador_espera == 0:                      # si el contador esta en 0 dispara
           bala = Bala(self.x, self.y, self.bala_img)         #creamos una nueva bala 
           self.balas.append(bala)                            #agregamos la bala a la lista de balas
           self.contador_espera = 1                        #el contador es 1, para que cuente hasta 15


    def get_width(self):                                    #funcion que calcula el ancho de la imagen .png de la nave
        return self.nave_img.get_width()

    def get_height(self):                                   #funcion que calcula el largo de la imagen .png de la nave
        return self.nave_img.get_height()


class JUGADOR(NAVE):                                        #se crea la clase del jugador
    def __init__(self, x, y, puntos, vidas):
        super().__init__(x, y)                              #el jugador toma todos los parametros de la nave
        self.nave_img = NAVE1                               #se le atribuye la imagen correspondiente a la nave del jugador
        self.bala_img = BALA_AZUL                           #se le atribuye la imagen correspondiente a la bala que lanza el jugador
        self.puntos = puntos                                #puntos del jugador
        self.vidas = vidas                                  #vidas del jugador
        self.mask = pygame.mask.from_surface(self.nave_img) #mascara de la imagen de la nave del jugador, para usar al hacer la colision con el enemigo


    def mov_balas(self, vel, objs):                        #funcion para el movimiento de las balas
        self.espera()                                        #llamamos a la funcion espera
        for bala in self.balas:
            bala.mov(vel)
            if bala.off_screen(largo_vent):                #si la bala se va de la pantalla, la removemos del listado
                self.balas.remove(bala)
            else:
                for obj in objs:
                    if bala.colision(obj):
                        self.puntos += 5                    #se le suman 5 puntos al jugador al colisionar su bala con el enemigo
                        objs.remove(obj)                   #si colisionamos con un objeto removemos el obj
                        if bala in self.balas:             # y removemos la bala
                            ExplosionSonido.play()          #se reproduce el sonido de explosion al colicionar la bala del jugador con el enemigo
                            self.balas.remove(bala)
        

class ENEMIGO(NAVE):
    def __init__(self, x, y):
        super().__init__(x, y)                              #el jugador toma todos los parametros de la nave
        self.nave_img = NAVE2                               #se le atribuye la imagen correspondiente a la nave del enemigo
        self.mask = pygame.mask.from_surface(self.nave_img) #mascara de la imagen de la nave del enemigo, para usar al hacer la colision con el enemigo


    def mov(self, vel):                                     #movimiento del enemigo
        self.y += vel

   
def colisiona(obj1, obj2):                                    #calculamos si hubo una colision
    offset_x = obj2.x - obj1.x                                #corroboramos si hay una colision, al superponerse las superficies de las imagenes
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None #si no hay colision nos devuelve el valor none

    

def Principal():                                                           #funcion principal
    Corre = True                                            
    FPS = 60
    jug = JUGADOR(300, 500, -10, 3)                                        #inicio del jugador, posición, puntos y vidas 
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('gw6mb8k8gidoleregularotf', 30, True)       #tipo de fuente (estilo, tamaño, negrita)
    font_perdi = pygame.font.SysFont('gw6mb8k8gidoleregularotf', 60, True)
    pygame.mixer.music.play(-1)                                            #reproductor de musica
    
    nivel = 0

    invasores=[]                                            #lista para los enemigos
    ing_nuevos = 5                                          #ingresan 5 enemigos
    vel_enemigo = 1                                         #velocidad de los invasores
    vel_jug = 5                                             #velocidad del jugador
    vel_bala_azul = 4                                       #velocidad de la bala

    perdi = False                                           # inicializo con perdi false, cuando sea true se finaliza el juego
    tiempo_perdi = 0                                        # inicio el contador para que PERDI aparezca 3seg
    
    def VentJuego():                                        #funcion de re-dibujar el fondo y los objetos
        VENTANA.blit(FONDO, (0,0))                          #se inserta el fondo
        jug.dibujo(VENTANA)                                 #se inserta la nave del jugador

        PUNTOS = font.render(f"Puntos: {jug.puntos}", 1, (255,255,255))         #se le atribuyen las caracteristicas a los textos 
        NIVEL = font.render(f"Nivel: {nivel}", 1, (255,255,255))    
        VIDAS = font.render(f"Vidas: {jug.vidas}", 1, (255,255,255))
        VENTANA.blit(PUNTOS, (10,10))                                           #se insertan los textos en la pantalla y se posicionan en sus respectivos lugares
        VENTANA.blit(VIDAS, (470,10))       
        VENTANA.blit(NIVEL, (10,45))

        for enemigo in invasores:                                               #se dibujan los enemigos
            enemigo.dibujo(VENTANA)

        if perdi:                                                               #se dibuja el texto al perder 
            PERDI = font_perdi.render("GAME OVER", 1, (255,0,0))
            VENTANA.blit(PERDI, (130, 250))

        pygame.display.update()

    while Corre:
        clock.tick(FPS)
        VentJuego()

        if jug.vidas <= 0 :                                 #si no tenga mas vidas, pierdo
            perdi = True
            tiempo_perdi += 1                               #contador, para que el cartel de perdi este 3 seg

        if perdi:
            GameOverSonido.play()                           #se reproduce el sonido al perder
            pygame.mixer.music.pause()                      #se pausa la musca al momento de perder
            if tiempo_perdi > FPS * 3:                      #despues de 3 segundos que perdi, se finaliza el juego
                Corre = False                               #el cartel de perdi aparece durante 3 segundos, antes de que se finalice
            else:
                continue

        if len(invasores) == 0:                             #si ya no hay mas enemigos en pantalla:
            nivel += 1                                      #se suma 1 al contador de niveles
            jug.puntos += 10                                #se suman 10 al contador de puntos
            ing_nuevos += 5                                 #se suman 5 nuevos enemigos para la siguiente oleada
            for i in range(ing_nuevos):                     #nueva oleada
                enemigo = ENEMIGO(random.randrange(50, ancho_vent-100), random.randrange(-1500, -100),)     #aparaecen aleatoreamente nuevos enemigos entre esas coordenadas, de modo que en la pantalla aparezcan en diferente altura
                invasores.append(enemigo)
        

        for evento in pygame.event.get():                   #para cerrar la ventana apretando la X
            if evento.type == pygame.QUIT:
                pygame.quit()                               
                sys.exit(0)                                 #al hacer clic para cerrar la ventana del juego se cierra

        keys = pygame.key.get_pressed()                     #se mantiene apretada la tecla al mover

        if keys[pygame.K_LEFT] and jug.x - vel_jug > 0:                                             #movimiento a la izquierda y bordes
            jug.x -= vel_jug
        if keys[pygame.K_RIGHT] and jug.x + vel_jug + jug.get_width() < ancho_vent:                 #movimiento a la derecha y bordes
            jug.x+= vel_jug
        if keys[pygame.K_UP] and jug.y - vel_jug > 0:                                               #movimiento hacia arriba y bordes
            jug.y-= vel_jug
        if keys[pygame.K_DOWN] and jug.y + vel_jug + jug.get_height() < largo_vent:                 #moviemiento hacia abajo y bordes
           jug.y+= vel_jug
        if keys[pygame.K_SPACE]:                                                                    #movimiento para disparar. Se reproduce el sonido de disparo 
            jug.dispara()
            LaserSonido.play()
            

        for enemigo in invasores[:]:                #movimiento del enemigo
            enemigo.mov(vel_enemigo)

            if colisiona(enemigo, jug):         #si existe colision entre el jugador y el enemigo
                jug.puntos -= 10                #se restan 10 del contador de puntos
                jug.vidas -= 1                  #se resta 1 del contador de vidas
                VidaMenosSonido.play()          #se reproduce el sonido al perder vidas
                invasores.remove(enemigo)       #se remueve dicho enemigo
            elif enemigo.y + enemigo.get_height() > largo_vent :    #si un enemigo se va de la pantalla
                jug.vidas -= 1                  #se resta 1 del contador de vidas
                jug.puntos -= 15                #se restan 15 del contador de puntos
                VidaMenosSonido.play()          #se reproduce el sonido al perder vidas
                invasores.remove(enemigo)       #se remueve dicho enemigo
                
        jug.mov_balas(-vel_bala_azul, invasores)    #movimiento vertical hacia arriba de las balas

def menuInicio():                               #menu inicial
    titulo = pygame.font.SysFont('gw6mb8k8gidoleregularotf', 35, True)
    Corre = True

    while Corre:
        VENTANA.blit(FONDO, (0,0))
        TITULO = titulo.render("Presiona una tecla para comenzar...", 1, (255,255,255))
        VENTANA.blit(TITULO, (30, 270))         #se imprime el texto en la pantalla
        pygame.display.update()

        for evento in pygame.event.get():       
            if evento.type == pygame.QUIT:      #si se aprieta la cruz se sale del juego
                run = False
            elif evento.type == pygame.KEYUP:   #si se aprieta cualquier tecla comienza el juego
                Principal()

    pygame.quit()                               #para salir de la ventana                     
    sys.exit(0)

menuInicio()

import pyxel, random, math
from stopwatch import Stopwatch

WIDTH = 150
HEIGHT = 300

class Jeu:
    ennemiesArray=[]
    effectArray=[]
    bossArray=[]
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Space Invaders")
        pyxel.load(r"sprites.pyxres")
        self.ship = Player(WIDTH//2-7, HEIGHT)

        self.scale=1
        self.decal=0

        self.nb_etoiles = 40
        self.etoiles = []
        self.eSpawner=0
        self.eSpawnLatence=10
        self.map=0
        self.finalCameraY=0
        self.cameraY=0
        Jeu.bossArray.append(Boss(10, -HEIGHT+10, "guardian"))
        self.cheats=KeyLogger()
        self.statut="start"
        self.easterDiscovered=False
        self.easterDiscovered2=False
        self.door=-13
        self.chronoStart=Stopwatch()
        self.evolvStart=3

        for _ in range(self.nb_etoiles):
            self.etoiles.append([
                random.randint(0, WIDTH - 1),
                random.randint(-HEIGHT, HEIGHT - 1),
                random.randint(1, 2)
            ])

        self.level=0
        pyxel.run(self.update, self.draw)

    def update(self):
        if not self.ship.isDead():
            #musique
            if pyxel.play_pos(0) == None and self.statut=="play":
                pyxel.playm(0, True)
            self.eSpawner+=1

            #vaisseau
            if self.statut=="play" or self.statut=="won":
                self.ship.UPDATE(self.map, self.statut)
                if self.statut=="play":
                    self.ship.fire()
            elif self.statut=="start" and self.ship.y>HEIGHT-50:
                self.ship.y-=1

            #étoiles
            if self.statut=="play" or self.statut=="start":
                for e in self.etoiles:
                    e[1] += e[2]
                    if e[1] > HEIGHT:
                        e[0] = random.randint(0, WIDTH - 1)
                        e[1] = -HEIGHT-1

            #freeze ennemies
            effet=self.ship.reactEffect()
            if effet=="freeze":
                for e in Jeu.ennemiesArray:
                    if e.y>0 or self.ship.y<0:
                        e.malusSpeed+=1
            elif effet=="reset":
                for e in Jeu.ennemiesArray:
                    if e.y>0 or self.ship.y<0:
                        e.statut="dead"


            #load tankers
            if self.eSpawner%self.eSpawnLatence==0:
                for boss in Jeu.bossArray:
                    if boss.name=="guardian":
                        boss.generateTanker()
                if self.statut=="start":
                    self.eSpawnLatence=random.randint(15, 50)
                else:
                    self.eSpawnLatence=random.randint(30, 100)

            for effect in Jeu.effectArray:
                effect.UPDATE()

            for e in Jeu.ennemiesArray:
                e.UPDATE(self.level, self.statut)

            #tirs
            suprTir=[]
            if not self.easterDiscovered or self.ship.y>0:
                for tir in self.ship.tirArray:
                    if tir.y<=-8:
                        suprTir.append(tir)
                for tir in suprTir:
                    self.ship.tirArray.remove(tir)

            self.level=math.floor(self.ship.score/100)

            #Guardian
            suprboss=[]
            for boss in Jeu.bossArray:
                if boss.pv<=0 and boss.statut=="alive":
                    boss.statut = "dead"
                    boss.animDead = 0

                if boss.statut == "dead":
                    boss.animDead += 1
                    if boss.animDead >= 14:
                        suprboss.append(boss)
                        pyxel.stop()
                        pyxel.playm(1, 0)
                        self.statut="won"
                        suprE=[]
                        for e in Jeu.ennemiesArray:
                            suprE.append(e)
                        for e in suprE:
                            Jeu.ennemiesArray.remove(e)
                        print("Sometimes, going back helps you see further ahead...")
                        print("\n" * 100)

                if boss.statut == "alive":
                    boss.UPDATE()

            for boss in suprboss:
                Jeu.bossArray.remove(boss)

            #camera
            self.manageCamera()

            #keylogger
            action=self.cheats.detecter()
            if action=="bpv3":
                self.ship.pv+=3
                if self.ship.pv>10:
                    self.ship.pv=10
            elif action=="maxheal":
                self.ship.pv=10
            elif action=="killguardian":
                for b in Jeu.bossArray:
                    if b.name=="guardian":
                        b.pv=0

            #gagné
            if self.statut=="won" and pyxel.btn(pyxel.KEY_R):
                self.reboot()

        elif pyxel.btn(pyxel.KEY_R):
            self.reboot()


    def draw(self):
        pyxel.cls(0)
        if not self.ship.isDead():
            #chronoStart
            if self.chronoStart.duration<=4:
                pyxel.blt(int(WIDTH//2.5), HEIGHT//3, 0, 72+math.floor(self.chronoStart.duration)*40, 185, 36, 50, 0, scale=2)
                if self.evolvStart!=math.floor(self.chronoStart.duration):
                    if math.floor(self.chronoStart.duration)!=3:
                        pyxel.play(2, 22)
                    else:
                        pyxel.play(2, 23)
                    self.evolvStart=math.floor(self.chronoStart.duration)

            #tires
            for tir in self.ship.tirArray:
                pyxel.blt(tir.x, tir.y, 0, 8, 0, 8, 8, 0)

            #vaisseau
            pyxel.blt(self.ship.x, self.ship.y, 0, 0, 0, 8, 8, 0)
            if self.ship.shuffle:
                dic={"right": (64, 8), "left": (56, 8), "down": (56, 16), "up": (64, 16)}
                pyxel.blt(self.ship.x+self.ship.sizeX, self.ship.y, 0, *dic[self.ship.directions[0]], 8, 8, 0) #right
                pyxel.blt(self.ship.x-self.ship.sizeX, self.ship.y, 0, *dic[self.ship.directions[1]], 8, 8, 0) #left
                pyxel.blt(self.ship.x, self.ship.y+self.ship.sizeY, 0, *dic[self.ship.directions[2]], 8, 8, 0) #down
                pyxel.blt(self.ship.x, self.ship.y-self.ship.sizeY, 0, *dic[self.ship.directions[3]], 8, 8, 0) #up

            #coeurs
            self.ship.displayCoeur(self.cameraY)

            #ennemies
            for e in Jeu.ennemiesArray:
                e.display()

            #guardian
            for boss in Jeu.bossArray:
                if boss.statut == "alive":
                    boss.display()
                elif boss.statut == "dead" and boss.animDead < 14:
                    # Afficher l'animation de mort
                    frame = boss.animDead
                    if frame % 2 == 0:
                        pyxel.blt(boss.x+boss.sizeX//2, boss.y+boss.sizeY//2, 0, 0, 48 + 24 * (frame // 2), 24, 24, 0, scale=10)
                    else:
                        pyxel.blt(boss.x+boss.sizeX//2, boss.y+boss.sizeY//2, 0, 0, 48 + 24 * ((frame - 1) // 2), 24, 24, 0, scale=10)

            #étoiles
            for e in self.etoiles:
                pyxel.pset(e[0], e[1], 7)

            #score
            pyxel.text(WIDTH-20, 10+self.cameraY, str(self.ship.getScore()), 7)

            #base
            pyxel.blt(10, HEIGHT-30, 0, 72, 120, 123, 27, 0, scale=1.5)
            pyxel.blt(int(WIDTH//2-12+self.door), HEIGHT-10, 0, 126, 105, 13, 11, 0, scale=1.5)
            if self.door<0 and self.statut=="start":
                self.door+=0.15
            elif self.statut=="won":
                self.door=-13
            elif self.door>=0 and self.statut=="start":
                self.statut="play"

            #winning
            if self.statut=="won":
                pyxel.blt(WIDTH//2-30, -HEIGHT//2-10, 0, 72, 0, 64, 8, 0, scale=2)
                pyxel.text(WIDTH//2-25, -HEIGHT//2+20, f"YOUR SCORE: {str(self.ship.getScore())}", 7)
                pyxel.text(WIDTH//2-30, -HEIGHT//2+30, "Press R to retry", 7)

            #contours
            for i in range((-HEIGHT//8)-1, HEIGHT//8+1):
                pyxel.blt(0, 8*i+self.decal, 0, 8, 8, 8, 8, 0)
                pyxel.blt(WIDTH-8, 8*i+self.decal, 0, 8, 16, 8, 8, 0)
            if  self.statut=="play" or self.statut=="start":
                if self.decal<8:
                    self.decal+=1
                else:
                    self.decal=0

            #effets
            for effect in Jeu.effectArray:
                effect.display()

            #crédits
            pyxel.text(20, HEIGHT+20, "Game made by MagnusGabinus", 7)
            pyxel.text(25, HEIGHT+30, "with the help of Nico", 7)
            pyxel.blt(20, HEIGHT*1.5, 0, 72, 8, 150, 24, 0, scale=1.2)
            pyxel.text(25, HEIGHT*1.65, "(Please, just press R...)", 8)
            pyxel.blt(WIDTH*0.3, HEIGHT*2.1, 0, 72, 152, 59, 32, 0, scale=2)
            pyxel.text(5, HEIGHT*2.3, "ADMIN COMMANDS:", 10)
            pyxel.text(5, HEIGHT*2.33, "Left, Left, Down, Up, Right, Right:", 11)
            pyxel.text(5, HEIGHT*2.35, "Active admin mode", 11)
            pyxel.text(5, HEIGHT*2.39, "K.I.L.L.G.U.A.R.D.I.A.N:", 11)
            pyxel.text(5, HEIGHT*2.41, "Kill the guardian", 11)
            pyxel.text(5, HEIGHT*2.45, "R.E.B.O.O.T:", 11)
            pyxel.text(5, HEIGHT*2.47, "Reboot of tankers", 11)
            pyxel.text(5, HEIGHT*2.49, "F.R.E.E.Z.E:", 11)
            pyxel.text(5, HEIGHT*2.51, "Freeze effect", 11)

        elif self.ship.animDead==0:
            pyxel.stop()
            pyxel.play(1, 4)
            pyxel.blt(self.ship.x, self.ship.y, 0, 0, 48, 24, 24, 0)
            self.ship.animDead+=1

        elif self.ship.animDead<14:
            frame = self.ship.animDead
            if frame % 2 == 0:
                pyxel.blt(self.ship.x, self.ship.y, 0, 0, 48 + 24 * (frame // 2), 24, 24, 0)
            else:
                pyxel.blt(self.ship.x, self.ship.y, 0, 0, 48 + 24 * ((frame - 1) // 2), 24, 24, 0)
            self.ship.animDead+=1

        else:
            # Écran GAME OVER
            pyxel.camera(0, 0)
            self.map=0
            self.cameraY=0
            self.finalCameraY=0
            pyxel.blt(WIDTH//2-24, HEIGHT//2-4, 0, 24, 0, 48, 8, 0, scale=self.scale)
            if self.scale==1:
                pyxel.play(0, 2)
            if self.scale<2.8:
                self.scale+=0.015
            else:
                pyxel.text(WIDTH//2-25, HEIGHT//2+20, f"YOUR SCORE: {str(self.ship.getScore())}", 7)
                pyxel.text(WIDTH//2-30, HEIGHT//2+30, "Press R to retry", 7)

    def getLevel(self):
        return self.level

    def reboot(self):
        pyxel.stop()
        self.ship.reboot()
        Jeu.ennemiesArray=[]
        Jeu.effectArray=[]
        self.level=0
        self.scale=1
        self.decal=0
        self.map=0
        self.statut="start"
        self.door=-13
        self.easterDiscovered2=False
        self.easterDiscovered=False
        self.chronoStart.restart()
        suprboss=[]
        for boss in Jeu.bossArray:
            suprboss.append(boss)
        for boss in suprboss:
            Jeu.bossArray.remove(boss)
        Jeu.bossArray.append(Boss(10, -HEIGHT+10, "guardian"))

    def manageCamera(self):
        #maps
        if self.ship.y<-5 and self.ship.y>-HEIGHT:
            self.map=-1
            if not self.easterDiscovered:
                pyxel.play(1, 18)
                self.easterDiscovered=True
        elif self.ship.y>HEIGHT+5:
            self.map=1
            if not self.easterDiscovered2:
                pyxel.play(1, 18)
                self.easterDiscovered2=True
        elif self.ship.y>0 and self.ship.y<HEIGHT:
            self.map=0

        #animation
        if self.ship.y<HEIGHT*1.5:
            self.finalCameraY=HEIGHT*self.map
        else:
            self.finalCameraY=self.ship.y-HEIGHT//2

        if self.cameraY>self.finalCameraY:
            if self.cameraY-self.finalCameraY>=6:
                self.cameraY-=6
            else:
                self.cameraY=self.finalCameraY
        elif self.cameraY<self.finalCameraY:
            if self.finalCameraY-self.cameraY>=6:
                self.cameraY+=6
            else:
                self.cameraY=self.finalCameraY

        pyxel.camera(0, self.cameraY)

class Player:
    def __init__(self, x, y):
        self.startX=x
        self.startY=y
        self.x = x
        self.y = y
        self.sizeX = 8
        self.sizeY = 8
        self.latence=0
        self.tirArray=[]
        self.speed=3
        self.pv=3
        self.score=0
        self.animDead=0
        self.shuffleLatence=0
        self.directions=["right", "left", "down", "up"]
        self.currentDirection=[]
        self.shuffle=False

    def reboot(self):
        self.x = self.startX
        self.y = self.startY
        self.sizeX = 8
        self.sizeY = 8
        self.latence=0
        self.tirArray=[]
        self.speed=3
        self.pv=3
        self.score=0
        self.animDead=0
        self.shuffleLatence=0

    def UPDATE(self, map, statut):
        # Déplacements
        if self.score>500:
            self.speed=4

        self.currentDirection = []  # Réinitialiser à chaque frame

        if pyxel.btn(pyxel.KEY_RIGHT):
            self.currentDirection.append(self.directions[0])
        if pyxel.btn(pyxel.KEY_LEFT):
            self.currentDirection.append(self.directions[1])
        if pyxel.btn(pyxel.KEY_DOWN):
            self.currentDirection.append(self.directions[2])
        if pyxel.btn(pyxel.KEY_UP):
            self.currentDirection.append(self.directions[3])

        # Appliquer tous les déplacements demandés
        if "right" in self.currentDirection and self.x <= WIDTH - self.sizeX:
            self.x += self.speed
        if "left" in self.currentDirection and self.x >= 0:
            self.x -= self.speed
        if "down" in self.currentDirection and (self.y <= HEIGHT - self.sizeY or (statut=="won" and (self.y>WIDTH//2-5 or self.y<WIDTH//2+5))):
            self.y += self.speed
        #if "up" in self.currentDirection and self.y >= 0:
        if "up" in self.currentDirection:
            self.y -= self.speed

        if self.shuffleLatence<=0:
            self.directions=["right", "left", "down", "up"]
            self.shuffle=False
        else:
            self.shuffleLatence-=1

        # Collisions avec les ennemis
        for ennemie in Jeu.ennemiesArray:
            # Ennemi qui atteint le bas
            if ennemie.y >= HEIGHT-20 and ennemie.statut=="alive":
                ennemie.statut="dead"
                self.pv -= 1
                #Ennemies.suprEnnemies.append(ennemie)

            # Collision joueur <-> ennemi
            if ennemie.verifHitbox(self.x, self.x+self.sizeX, self.y, self.y+self.sizeY):
                self.pv = 0
                Ennemies.suprEnnemies.append(ennemie)

        # Suppression des ennemis touchés
        for ennemie in Ennemies.suprEnnemies:
            if ennemie in Jeu.ennemiesArray:
                Jeu.ennemiesArray.remove(ennemie)

        if self.x<2 or self.x>WIDTH-9 or (self.y>HEIGHT-15 and statut=="play"):
            self.pv=0


    def fire(self):
        # Cadence de tir
        if self.latence == 0:
            if pyxel.btn(pyxel.KEY_SPACE):
                pyxel.play(1, 19)
                self.tirArray.append(Tir(self.x, self.y))
                self.latence = 1
        elif self.latence >= 10:
            self.latence = 0
        else:
            self.latence += 1

        suprTir = []

        # Mise à jour des tirs
        for tir in self.tirArray:
            tir.UPDATE()

            # Vérif collisions tirs <-> ennemis
            tir_hit = False

            for ennemie in Jeu.ennemiesArray:

                if ennemie.verifHitbox(tir.x, tir.x+8, tir.y, tir.y+8) and ennemie.statut=="alive":
                    suprTir.append(tir)
                    ennemie.statut="dead"
                    pyxel.play(1, 1)
                    self.score+=10
                    tir_hit = True

            # Vérification boss
            for boss in Jeu.bossArray:
                if boss.verifHitbox(tir.x, tir.y) and not tir_hit:
                    suprTir.append(tir)
                    boss.pv -= 1  # Un seul point de dégât par tir
                    tir_hit = True

        # Suppression tirs
        for tir in suprTir:
            if tir in self.tirArray:
                self.tirArray.remove(tir)

        # Suppression ennemis
        for ennemie in Ennemies.suprEnnemies:
            if ennemie in Jeu.ennemiesArray:
                Jeu.ennemiesArray.remove(ennemie)

    def displayCoeur(self, cameraY):
        for i in range(self.pv):
            pyxel.blt(5 + 14*i, 5+cameraY, 0, 24, 8, 13, 13, 0)

    def isDead(self):
        if self.pv<=0:
            return True
        else:
            return False

    def getScore(self):
        return self.score

    def reactEffect(self):
        # Collision avec les effets
        deletEffect = []
        effectType=None

        for effect in Jeu.effectArray:
            touched = False

            # Vérification pixel par pixel
            for px in range(self.x, self.x + self.sizeX):
                for py in range(self.y, self.y + self.sizeY):
                    if effect.verifHitbox(px, py):
                        touched = True
                        break
                if touched:
                    break

            if touched:
                if effect.type == "heal" and self.pv<10:
                    self.pv += 1

                if effect.type=="meteor":
                    self.pv-=5

                if effect.type=="shuffle":
                    self.shuffleLatence=100
                    self.shuffle=True
                    random.shuffle(self.directions)

                if effect.type=="bigup":
                    self.pv+=3
                    if self.pv>10:
                        self.pv=10

                effectType=effect.type
                deletEffect.append(effect)

        # Suppression des effets ramassés
        for effect in deletEffect:
            if effect in Jeu.effectArray:
                Jeu.effectArray.remove(effect)

        return effectType

class Ennemies:
    suprEnnemies=[]
    def __init__(self, x, y, typeShip):
        self.x=x
        self.y=y
        self.size=8
        self.animDead=24
        self.statut="alive"
        self.malusSpeed=1
        self.type=typeShip

    def UPDATE(self, level, mode):
        if self.statut=="alive":
            if mode=="start":
                self.y+=((level/2+1)/self.malusSpeed)*2.5
            else:
                self.y+=(level/2+1)/self.malusSpeed

    def display(self):
        if self.statut=="alive":
            if self.malusSpeed>1:
                pyxel.blt(self.x, self.y, 0, 0, 32, 8, 8, 0)
            else:
                pyxel.blt(self.x, self.y, 0, 0, 8, 8, 8, 0)
        elif self.animDead<=40:
            if self.animDead==40:
                if random.randint(1, 100)>=50:
                    a=random.randint(1, 100)
                    if a>=75:
                        Jeu.effectArray.append(Effect(self.x, self.y, "heal"))
                    elif a>=50:
                        Jeu.effectArray.append(Effect(self.x, self.y, "freeze"))
                    elif a>=30:
                        Jeu.effectArray.append(Effect(self.x, self.y, "meteor"))
                    elif a>=20:
                        Jeu.effectArray.append(Effect(self.x, self.y, "reset"))
                    elif a>=10:
                        Jeu.effectArray.append(Effect(self.x, self.y, "shuffle"))
                    elif a>=0:
                        Jeu.effectArray.append(Effect(self.x, self.y, "bigup"))
            pyxel.blt(self.x, self.y, 0, 8, self.animDead, 8, 8, 0)
            self.animDead+=8
        elif self.animDead>40:
            Ennemies.suprEnnemies.append(self)


    def verifHitbox(self, x, x2, y, y2):
        for u in range(x, x2):
            for v in range(y, y2):
                if (self.x <= u <= self.x+self.size) and (self.y <= v <= self.y+self.size):
                    return True

        return False

class Tir:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size=8

    def UPDATE(self):
        self.y -= 4

class Effect:
    def __init__(self, x, y, type):
        self.y=y
        self.x=x
        self.type=type
        self.direction=0
        if self.type=="meteor":
            self.direction=random.randint(-2, 2)

    def UPDATE(self):
        self.y+=3
        self.x+=self.direction

    def display(self):
        if self.type=="heal":
            pyxel.blt(self.x, self.y, 0, 16, 16, 8, 8, 0)

        elif self.type=="freeze":
            pyxel.blt(self.x, self.y, 0, 16, 8, 8, 8, 0)

        elif self.type=="meteor":
            pyxel.blt(self.x, self.y, 0, 16, 0, 8, 8, 0)

        elif self.type=="shuffle":
            pyxel.blt(self.x, self.y, 0, 24, 40, 8, 8, 0)

        elif self.type=="bigup":
            pyxel.blt(self.x, self.y, 0, 16, 32, 8, 8, 0)

        elif self.type=="reset":
            pyxel.blt(self.x, self.y, 0, 16, 40, 8, 8, 0)

    def verifHitbox(self, x, y):
        if (self.x <= x <= self.x+8) and (self.y <= y <= self.y+8):
            pyxel.play(1, 3)
            return True
        else:
            return False

class Boss:
    def __init__(self, x, y, name):
        self.x=x
        self.y=y
        self.name=name
        self.sizeX=0
        self.sizeY=0
        self.pv=20
        self.direction="right"
        self.animDead=0
        self.statut="alive"
        if name=="guardian":
            self.sizeX=127
            self.sizeY=56

    def display(self):
        if self.name=="guardian":
            pyxel.blt(int(self.x), int(self.y), 0, 64, 32, 128, 56, 0)

    def generateTanker(self):
        Jeu.ennemiesArray.append(Ennemies(random.randint(int(self.x+5), int(self.x+self.sizeX-5)), int(self.y+self.sizeY//2), "tanker"))

    def verifHitbox(self, x, y):
        if (self.x <= x <= self.x+self.sizeX) and (self.y <= y <= self.y+self.sizeY):
            return True
        else:
            return False

    def UPDATE(self):
        if self.direction=="right":
            self.x+=0.5
            if self.x+self.sizeX>=WIDTH:
                self.direction="left"
        elif self.direction=="left":
            self.x-=0.5
            if self.x<=0:
                self.direction="right"

class KeyLogger:
    def __init__(self):
        self.data=[]
        self.admin=False
        self.code1= [pyxel.KEY_R, pyxel.KEY_E, pyxel.KEY_B, pyxel.KEY_O, pyxel.KEY_O, pyxel.KEY_T]
        self.code2 = [pyxel.KEY_C, pyxel.KEY_L, pyxel.KEY_E, pyxel.KEY_M, pyxel.KEY_E, pyxel.KEY_N, pyxel.KEY_T, pyxel.KEY_I, pyxel.KEY_N, pyxel.KEY_E]
        self.code2Used=False
        self.code3=[pyxel.KEY_M, pyxel.KEY_A, pyxel.KEY_X, pyxel.KEY_H, pyxel.KEY_E, pyxel.KEY_A, pyxel.KEY_L]
        self.code4= [pyxel.KEY_LEFT, pyxel.KEY_LEFT, pyxel.KEY_DOWN, pyxel.KEY_UP, pyxel.KEY_RIGHT, pyxel.KEY_RIGHT]
        self.code5=[pyxel.KEY_F, pyxel.KEY_R, pyxel.KEY_E, pyxel.KEY_E, pyxel.KEY_Z, pyxel.KEY_E]
        self.code6=[pyxel.KEY_K, pyxel.KEY_I, pyxel.KEY_L, pyxel.KEY_L, pyxel.KEY_G, pyxel.KEY_U, pyxel.KEY_A, pyxel.KEY_R, pyxel.KEY_D, pyxel.KEY_I, pyxel.KEY_A, pyxel.KEY_N]

    def detecter(self):
        if pyxel.btnr(pyxel.KEY_LEFT):
            self.data.append(pyxel.KEY_LEFT)
        elif pyxel.btnr(pyxel.KEY_RIGHT):
            self.data.append(pyxel.KEY_RIGHT)
        elif pyxel.btnr(pyxel.KEY_UP):
            self.data.append(pyxel.KEY_UP)
        elif pyxel.btnr(pyxel.KEY_DOWN):
            self.data.append(pyxel.KEY_DOWN)
        elif pyxel.btnr(pyxel.KEY_A):
            self.data.append(pyxel.KEY_A)
        elif pyxel.btnr(pyxel.KEY_B):
            self.data.append(pyxel.KEY_B)
        elif pyxel.btnr(pyxel.KEY_C):
            self.data.append(pyxel.KEY_C)
        elif pyxel.btnr(pyxel.KEY_D):
            self.data.append(pyxel.KEY_D)
        elif pyxel.btnr(pyxel.KEY_E):
            self.data.append(pyxel.KEY_E)
        elif pyxel.btnr(pyxel.KEY_F):
            self.data.append(pyxel.KEY_F)
        elif pyxel.btnr(pyxel.KEY_G):
            self.data.append(pyxel.KEY_G)
        elif pyxel.btnr(pyxel.KEY_H):
            self.data.append(pyxel.KEY_H)
        elif pyxel.btnr(pyxel.KEY_I):
            self.data.append(pyxel.KEY_I)
        elif pyxel.btnr(pyxel.KEY_J):
            self.data.append(pyxel.KEY_J)
        elif pyxel.btnr(pyxel.KEY_K):
            self.data.append(pyxel.KEY_K)
        elif pyxel.btnr(pyxel.KEY_L):
            self.data.append(pyxel.KEY_L)
        elif pyxel.btnr(pyxel.KEY_M):
            self.data.append(pyxel.KEY_M)
        elif pyxel.btnr(pyxel.KEY_N):
            self.data.append(pyxel.KEY_N)
        elif pyxel.btnr(pyxel.KEY_O):
            self.data.append(pyxel.KEY_O)
        elif pyxel.btnr(pyxel.KEY_P):
            self.data.append(pyxel.KEY_P)
        elif pyxel.btnr(pyxel.KEY_Q):
            self.data.append(pyxel.KEY_Q)
        elif pyxel.btnr(pyxel.KEY_R):
            self.data.append(pyxel.KEY_R)
        elif pyxel.btnr(pyxel.KEY_S):
            self.data.append(pyxel.KEY_S)
        elif pyxel.btnr(pyxel.KEY_T):
            self.data.append(pyxel.KEY_T)
        elif pyxel.btnr(pyxel.KEY_U):
            self.data.append(pyxel.KEY_U)
        elif pyxel.btnr(pyxel.KEY_V):
            self.data.append(pyxel.KEY_V)
        elif pyxel.btnr(pyxel.KEY_W):
            self.data.append(pyxel.KEY_W)
        elif pyxel.btnr(pyxel.KEY_X):
            self.data.append(pyxel.KEY_X)
        elif pyxel.btnr(pyxel.KEY_Y):
            self.data.append(pyxel.KEY_Y)
        elif pyxel.btnr(pyxel.KEY_Z):
            self.data.append(pyxel.KEY_Z)

        if len(self.data) >= len(self.code4) and self.data[-len(self.code4):] == self.code4:
            self.data=[]
            print("Admin mode activated")
            self.admin=True

        if self.admin:
            if len(self.data) >= len(self.code1) and self.data[-len(self.code1):] == self.code1:
                suprE=[]
                for e in Jeu.ennemiesArray:
                    suprE.append(e)
                for e in suprE:
                    Jeu.ennemiesArray.remove(e)

                print("Admin command: Reboot of tankers")
                self.data = []

            if len(self.data) >= len(self.code3) and self.data[-len(self.code3):] == self.code3:
                self.data=[]
                print("Admin command: max heal")
                return "maxheal"

            if len(self.data) >= len(self.code5) and self.data[-len(self.code5):] == self.code5:
                self.data=[]
                print("Admin command: freeze")
                for e in Jeu.ennemiesArray:
                    e.malusSpeed+=1

            if len(self.data) >= len(self.code6) and self.data[-len(self.code6):] == self.code6:
                self.data=[]
                print("Admin command: Guardian killed")
                return "killguardian"

        if len(self.data) >= len(self.code2) and self.data[-len(self.code2):] == self.code2:
            self.data=[]
            if not self.code2Used:
                print("Coupon: more 3 hp")
                self.code2Used=True
                return "bpv3"
            else:
                print("Coupon already used")


game = Jeu()
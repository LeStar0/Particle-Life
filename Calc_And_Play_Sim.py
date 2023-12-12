import pygame
import numpy as np
from random import randint, shuffle
import pickle
from time import sleep
import sys
pygame.init()

FONT = pygame.font.SysFont("Arial", 20)
WIDTH, HEIGHT = 1200, 1000
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Window")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (235, 0, 0)
GREEN = (0, 220, 0)
BLUE = (0, 40, 210)

def checkPointsInRange_V2(h, k, r, points):
    x = points[0]
    y = points[1]   
    inside = np.where(((x > h - r) & (x < h + r)) & ((y > k - r) & (y < k + r)), ((x - h)**2 + (y - k)**2 < r**2) & ((x - h)**2 + (y - k)**2 != 0), False)
    return inside

def checkPointsInRange(h, k, r, points):
    x = points[0]
    y = points[1]
    inside = ((x - h)**2 + (y - k)**2 < r**2) & ((x - h)**2 + (y - k)**2 != 0)
    return inside

def drawParticles(particleGroup):
    for n in range(particleGroup["particleNumber"]):
            x, y = particleGroup["particles"][0,n], particleGroup["particles"][1,n]
            pygame.draw.circle(WIN, particleGroup["particleColor"], (int(x), int(y)), 3)


def createParticleGroup(number, color): 
    particleGroup = {
    "particles": np.array([[randint(0, WIDTH) for x in range(number)],[randint(0, HEIGHT) for y in range(number)],
                           [0 for xV in range(number)], [0 for yV in range(number)]], dtype="f"),
    "particleColor": color,
    "particleNumber": number
    }

    return particleGroup

def rule(particle1, particle2, g):
    loopCount = 0
    for n in particle1[0]:
        xDirectionForce, yDirectionForce = 0, 0

        p1xPos = particle1[0, loopCount]
        p1yPos = particle1[1, loopCount]
        p1xVel = particle1[2, loopCount]
        p1yVel = particle1[3, loopCount]

        distanceFilter = checkPointsInRange_V2(p1xPos, p1yPos, 70, particle2)
        

        particle2X = particle2[0]
        particle2Y = particle2[1]

        xDelta = p1xPos - particle2X[distanceFilter]
        yDelta = p1yPos - particle2Y[distanceFilter]

        distance = np.hypot(xDelta, yDelta)
        
        force = np.divide(1, distance)
        force = np.multiply(g, force)

        xDirectionForce = np.multiply(force, xDelta)
        yDirectionForce = np.multiply(force, yDelta)

        xDirectionForce = np.sum(xDirectionForce)
        yDirectionForce = np.sum(yDirectionForce)

        p1xVel = (p1xVel + xDirectionForce) * 0.5
        p1yVel = (p1yVel + yDirectionForce) * 0.5

        p1xPos += p1xVel
        p1yPos += p1yVel

        if p1xPos <= 5 or p1xPos >= WIDTH - 5: p1xVel *= -1
        if p1yPos <= 5 or p1yPos >= HEIGHT - 5: p1yVel *= -1

        if p1xPos <= 5: p1xPos = 5
        if p1xPos >= WIDTH - 5: p1xPos = WIDTH - 5
        if p1yPos <= 5: p1yPos = 5
        if p1yPos >= HEIGHT - 5: p1yPos = HEIGHT - 5

        

        particle1[0, loopCount] = p1xPos
        particle1[1, loopCount] = p1yPos
        particle1[2, loopCount] = p1xVel
        particle1[3, loopCount] = p1yVel
        
 
        loopCount += 1

def saveArr(listOfArr, f):
    for arr in listOfArr:
        np.save(f, arr, allow_pickle=True)

def loadArr(listOfArr, loadArrFromFile):
    tmpArrList = []
    
    for arr in listOfArr:
        tmpArr = np.load(loadArrFromFile, allow_pickle=True)
        tmpArrList.append(tmpArr)
    
    return tmpArrList

#----------------------------------------------------------------------------------------------------------

def recordAndPlay(recordLen):
    
    #Set Parameters
    

    #LoadingBarInit
    finishedLoad = FONT.render("Press any Key to play Simulation!", True, BLACK)
    MAXloadingBarWidth = 300
    loadingBarWidth = 0
    loadingBarHeight = 50
    loadingBarPosition = (WIDTH / 2 -MAXloadingBarWidth / 2, HEIGHT / 2 -loadingBarHeight / 2) 
    loadingBar = pygame.Rect(loadingBarPosition, (loadingBarWidth, loadingBarHeight))
    loadingBarFrame = pygame.Rect(loadingBarPosition, (MAXloadingBarWidth, loadingBarHeight))
        
    run = True
    clock = pygame.time.Clock()
    tick = 120
    maxCount = 0

    testGroup01 = createParticleGroup(300, RED)
    testGroup02 = createParticleGroup(300, GREEN)
    testGroup03 = createParticleGroup(300, BLUE)

    redParticles = testGroup01["particles"].view()
    greenParticles = testGroup02["particles"].view()
    blueParticles = testGroup03["particles"].view()

    allParticles = [redParticles, greenParticles, blueParticles]
    allParticlesRepGroup = np.concatenate((redParticles, greenParticles, blueParticles))

    saveArrToFile = open("recording.npy", "wb")

    for n in range(recordLen):
        
        #Loading Bar
        clock.tick(tick)
        WIN.fill(WHITE)
        loadingBar = pygame.Rect(loadingBarPosition, (loadingBarWidth, loadingBarHeight))

        if loadingBarWidth < MAXloadingBarWidth:
            loadingBarWidth = n / recordLen * MAXloadingBarWidth
            pygame.draw.rect(WIN, BLACK, loadingBarFrame, 2, 1)
            pygame.draw.rect(WIN, BLACK, loadingBar)
        
    
        pygame.display.update()

        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()        
                
    
        saveArr(allParticles, saveArrToFile)
        
        rule(allParticlesRepGroup, allParticlesRepGroup, 0.1)
        rule(redParticles, redParticles, -0.02)
        rule(redParticles, greenParticles,0.1)
        rule(greenParticles, redParticles,-0.3)
        rule(blueParticles, greenParticles, -0.2)
        rule(redParticles, blueParticles, 0.25)
    
    saveArrToFile.close()

    pause = True
    while pause:
        clock.tick(tick)
        WIN.fill(WHITE)
        WIN.blit(finishedLoad, loadingBar)

        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

        # This may not work in newer Versions of pygame
        for key in pygame.key.get_pressed():
                    if key == True:
                        pause = False 
                    else:
                        pass
        pygame.display.update()
    
    loadArrFromFile = open("recording.npy", "rb")

    everyParticleAcrossTime = []

    for record in range(recordLen):
        allParticles = loadArr(allParticles, loadArrFromFile)
        everyParticleAcrossTime.append(allParticles)

    

    while run:
        maxCount = 0
        while run:
            clock.tick(tick)
            WIN.fill(WHITE)

            allParticles = everyParticleAcrossTime[maxCount]

            testGroup01["particles"] = allParticles[0]
            testGroup02["particles"] = allParticles[1]
            testGroup03["particles"] = allParticles[2]

            maxCount += 1
            if maxCount == recordLen:
                break
            
            # Exit Window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            drawParticles(testGroup01)
            drawParticles(testGroup02)
            drawParticles(testGroup03)
            
            pygame.display.update()
            sleep(0.01)

        loadArrFromFile.close()
        
    #pygame.quit()



def runGame(maxLen=0):
    run = True
    clock = pygame.time.Clock()
    tick = 120
    
    testGroup01 = createParticleGroup(100, RED)
    testGroup02 = createParticleGroup(400, GREEN)
    testGroup03 = createParticleGroup(400, BLUE)

    redParticles = testGroup01["particles"].view()
    greenParticles = testGroup02["particles"].view()
    blueParticles = testGroup03["particles"].view()

    maxCount = 0
            
    while run:
        clock.tick(tick)
        WIN.fill(WHITE)

        if maxLen != 0 :
            maxCount += 1
            if maxCount == maxLen:
                run = False
        else:
            pass
               
        # Exit Window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False    
       
        rule(redParticles, redParticles, -0.02)
        rule(greenParticles, redParticles,-0.3)
        rule(blueParticles, greenParticles, -0.2)
        rule(redParticles, blueParticles, 0.25)

        drawParticles(testGroup01)
        drawParticles(testGroup02)
        drawParticles(testGroup03)
        
        pygame.display.update()
         
    pygame.quit()


def mainProfile():
    import cProfile
    import pstats

    with cProfile.Profile() as pr:
        recordAndPlay(100)

    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.dump_stats(filename='pyGameParticlesV2.prof')
    #stats.print_stats()

def main():
    recordAndPlay(1000)
    

main()
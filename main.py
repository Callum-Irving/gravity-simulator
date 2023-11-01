##########################################################
####### Simple Gravity Simulation by Callum Irving #######
#######              October 30, 2020              #######
##########################################################

import numpy as np
from math import sqrt, pi, sin, cos
from random import randint, uniform
from time import sleep, perf_counter
from tkinter import *

####### GLOBAL VARIABLES #######
WIDTH = 1280
HEIGHT = 830
FRAMERATE = 60
FRAMETIME = 1/FRAMERATE
G = 2.5
running = True
sunEnabled = True


def toHex(rgb):
    # Function to convert an rgb tuple to a hex colour value, for tkinter
    # I used RGB so that I could generate random colours without a massive array of preset colours
    return "#%02x%02x%02x" % rgb


class Planet:
    def __init__(self, x, y, velX, velY, mass, radius, colour):
        # Row vectors for position and velocity
        self.pos = np.array([x, y])
        self.vel = np.array([velX, velY])

        self.mass = mass
        self.radius = radius
        self.colour = toHex(colour)
        # Variable to store the drawing, so it can be deleted
        self.drawing = False

    def gravity(self, objects):
        for o in objects:
            if o == self or not o:
                continue

            dist = self.pos - o.pos
            dist = dist.dot(dist)

            # Gravity formula, the key to the simulation
            mag = G * o.mass / dist  # Never sqrted dist, no **2 needed
            toObject = o.pos - self.pos
            # Convert toObject to a unit vector and multiply by mag
            gravity = toObject / np.linalg.norm(toObject) * mag

            self.vel += gravity

    def checkColliding(self, objects):
        # Check if colliding with objects
        for o in objects:
            if o == self:
                continue
            dist = self.pos - o.pos
            dist = sqrt(dist.dot(dist))
            if dist < (self.radius + o.radius):
                return True

        return False

    def move(self):
        self.pos += self.vel

    def draw(self):
        self.drawing = screen.create_oval(self.pos[0] - self.radius, self.pos[1] - self.radius,
                                          self.pos[0] + self.radius, self.pos[1] + self.radius, fill=self.colour)


class Particle:
    def __init__(self, cX, cY, speed, angle):
        self.x = cX
        self.y = cY
        self.speed = speed
        self.angle = angle

    def move(self):
        self.x += self.speed * cos(self.angle)
        self.y += self.speed * sin(self.angle)


class Explosion:
    def __init__(self, centerX, centerY, colour, numParticles):
        self.centerX = centerX
        self.centerY = centerY
        self.colour = colour
        self.particles = []
        self.drawings = []

        for i in range(numParticles):
            speed = uniform(0.5, 8)
            angle = uniform(0, 2*pi)
            particle = Particle(centerX, centerY, speed, angle)
            self.particles.append(particle)
            self.drawings.append(0)

        self.delete = False
        self.tick = 0

    def update(self):
        for particle in self.particles:
            particle.move()

        self.tick += 1
        if self.tick % 3 == 0:
            # Remove a particle every 3 frames
            if len(self.particles) > 0:
                self.particles.remove(self.particles[0])
            else:
                # Delete explosion when all particles are gone
                self.delete = True

    def draw(self):
        for i in range(len(self.particles)):
            self.drawings[i] = screen.create_rectangle(
                self.particles[i].x-2, self.particles[i].y-2, self.particles[i].x+2, self.particles[i].y+2, fill=self.colour, outline="")


####### CREATE WINDOW #######
root = Tk()
root.title("Gravity Simulation")
screen = Canvas(root, width=WIDTH, height=HEIGHT, background="black")
screen.pack()
screen.focus_set()

####### IMPLEMENTING DRAG TO CREATE PLANET #######
lineCoords = [0, 0, 0, 0]  # coordinates for line, in form x1, y1, x2, y2
planetLine = None


####### INPUT PROCEDURES #######
def click(location):
    # Pause
    global running  # global is how you access global variables inside python functions/procedures
    running = False

    lineCoords[0] = location.x
    lineCoords[1] = location.y
    lineCoords[2] = location.x
    lineCoords[3] = location.y
    global planetLine
    planetLine = screen.create_line(
        lineCoords[0], lineCoords[1], lineCoords[2], lineCoords[3], fill="white")


def drag(location):
    lineCoords[2] = location.x
    lineCoords[3] = location.y
    screen.coords(planetLine, lineCoords[0],
                  lineCoords[1], lineCoords[2], lineCoords[3])


def release(e=None):
    # Unpause
    global running
    running = True

    screen.delete(planetLine)
    vX = float(lineCoords[2] - lineCoords[0]) / 20
    vY = float(lineCoords[3] - lineCoords[1]) / 20
    mass = randint(10, 30)
    size = randint(7, 12)
    colour = (randint(0, 255), randint(0, 255), randint(0, 255))

    planets.append(Planet(float(lineCoords[0]), float(lineCoords[1]),
                          vX, vY, mass, size, colour))


def raiseG(e=None):
    global G
    G += 0.1


def lowerG(e=None):
    # I was going to stop G at 0, but it's actually more fun if it can be negative
    global G
    G -= 0.1


def toggleSun(e=None):
    global sunEnabled
    sunEnabled = not sunEnabled


####### DISPLAY INTRO SCREEN #######
screen.create_text(WIDTH/2, HEIGHT/2-100,
                   text="Gravity Simulation", font=("Ubuntu", "48", "bold"), fill="white", anchor=CENTER)
screen.create_text(WIDTH/2, HEIGHT/2+45,
                   text="Click and drag to create new object", font=("Ubuntu", "16"), fill="white", anchor=CENTER)
screen.create_text(WIDTH/2, HEIGHT/2+75,
                   text="Use arrows to adjust gravitational constant G", font=("Ubuntu", "16"), fill="white", anchor=CENTER)
screen.create_text(WIDTH/2, HEIGHT/2+105,
                   text="Press the spacebar to toggle the sun", font=("Ubuntu", "16"), fill="white", anchor=CENTER)
screen.update()
sleep(4)
screen.delete("all")


####### SIMULATION #######

# Draw stars, no animation loop needed because they are static
numStars = 200
starsX = []
starsY = []
starDrawings = []
for i in range(numStars):
    starsX.append(randint(0, WIDTH))
    starsY.append(randint(0, HEIGHT))
    starDrawings.append(screen.create_oval(starsX[i]-2, starsY[i]-2,
                                           starsX[i]+2, starsY[i]+2, fill="white"))
screen.update()


####### RANDOMLY GENERATE PLANETS #######
numPlanets = 50
planets = []  # This includes the "sun"
explosions = []

# Create "sun"
planets.append(Planet(WIDTH/2, HEIGHT/2, 0.0, 0.0,
                      10000, 30, (255, 255, 0)))  # 0.0 means float instead of int

# Create other planets
for i in range(numPlanets):
    pX = uniform(0, WIDTH)
    pY = uniform(0, HEIGHT)
    pRadius = randint(7, 12)
    pMass = randint(10, 30)
    pColour = (randint(0, 255), randint(0, 255), randint(0, 255))
    pVelX = uniform(-5, 5)

    if pY > planets[0].pos[0]:
        pVelY = uniform(3, 5)
    else:
        pVelY = uniform(-5, -3)

    planets.append(Planet(pX, pY, pVelX, pVelY, pMass, pRadius, pColour))


####### BINDING INPUT PROCEDURES #######
screen.bind("<Up>", raiseG)
screen.bind("<Down>", lowerG)
screen.bind("<space>", toggleSun)
screen.bind("<ButtonPress-1>", click)
screen.bind("<B1-Motion>", drag)
screen.bind("<ButtonRelease-1>", release)


####### MAIN LOOP #######
while True:
    frameStart = perf_counter()

    GText = screen.create_text(
        20, 20, font=("Ubuntu"), text="G = "+str(round(G, 2)), fill="white", anchor=NW)

    # Only run logic if running is true, otherwise only draw
    if running == True:
        # Check collisions
        colliding = []
        # Using slice notation to skip the first planet (the sun)
        for planet in planets[1:]:
            # Since booleans are just ints, this is normal slice notation
            # this means if the sun is NOT enabled, it will skip the first element
            if planet.checkColliding(planets[not sunEnabled:]):
                colliding.append(planet)
            elif planet.pos[0] < -150 or planet.pos[0] > WIDTH+150 or planet.pos[1] < -150 or planet.pos[1] > HEIGHT+150:
                # Remove planets out of bounds, to make program run faster
                colliding.append(planet)

        # Remove colliding planets
        i = 1
        while i < len(planets):
            if not colliding:
                break
            # We only need to check colliding[0] because it will always be sorted,
            # relative to how the planets list is sorted and we pop the first element when we detect collision
            if planets[i] == colliding[0]:
                explosions.append(
                    Explosion(planets[i].pos[0], planets[i].pos[1], planets[i].colour, 20))
                planets.remove(planets[i])
                colliding.pop(0)
            else:
                i += 1

        # Calculate gravity
        for planet in planets[1:]:
            planet.gravity(planets[not sunEnabled:])

        # Move planets
        for planet in planets[1:]:
            planet.move()

        # Update explosions
        for explosion in explosions:
            explosion.update()

    # Draw planets
    for planet in planets[not sunEnabled:]:
        planet.draw()

    # Draw explosions
    for explosion in explosions:
        explosion.draw()

    physicsTime = perf_counter() - frameStart
    # Update, sleep, delete
    screen.update()
    # Trying to keep the frametimes relatively similar
    sleep(max(0, FRAMETIME-physicsTime))

    screen.delete(GText)

    for planet in planets:
        screen.delete(planet.drawing)

    # A while loop is used instead of a for loop because
    # if you pop() inside a for loop, it will skip the next element
    i = 0
    while i < len(explosions):
        for particle in explosions[i].drawings:
            screen.delete(particle)

        if explosions[i].delete:
            explosions.pop(i)
            # Notice that i is not incremented if an explosion is removed
        else:
            i += 1

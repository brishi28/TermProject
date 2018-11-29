import flaskHelper
import cozmo
import time
import asyncio
import sys
from tkinter import *
from pathPlanning import Cell, PathPlan
from TKMapViewer import CozmoView
import threading

from flask import Flask, redirect, url_for, request, render_template
from cozmo.util import degrees, distance_mm, speed_mmps, Angle

currentState = None
coz = None
cube = None
#tkin = None

'''
def init(data):
    data.cellWidth = data.width / (coz.maxX + 1)
    data.cellHeight = data.height / (coz.maxY + 1)
    

def redrawAll(canvas, data):
    for y in range(height+1):
        for x in range(width+1):
            if (x, y) == (coz.currentX, coz.currentY):
                color = 'blue'
            elif (x, y) in coz.safeSpaces:
                color = 'green'
            elif (x, y) in coz.currentMovement:
                color = 'red'
            else:
                color = 'black'
            x0 = x * data.cellWidth
            y0 = y * data.cellHeight
            x1 = x0 + data.cellWidth
            y1 = y0 + data.cellHeight
            canvas.create_rectangle(x0, y0, x1, y1, color)

def timerFired(data):
    pass

class App(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def callback(self):
        self.root.quit()

    def run(self):
        #self.root.protocol("WM_DELETE_WINDOW", self.callback)
        def redrawAllWrapper(canvas, data):
            canvas.delete(ALL)
            canvas.create_rectangle(0, 0, data.width, data.height,
                                    fill='white', width=0)
            redrawAll(canvas, data)
            canvas.update()    

        def timerFiredWrapper(canvas, data):
            timerFired(data)
            redrawAllWrapper(canvas, data)
            # pause, then call timerFired again
            canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
            # Set up data and call init


        class Struct(object): pass
        data = Struct()
        data.width = 400
        data.height = 400
        data.timerDelay = 100 # milliseconds
        self.root = Tk()
        self.root.resizable(width=False, height=False) # prevents resizing window
        init(data)
        # create the root and the canvas
        canvas = Canvas(self.root, width=data.width, height=data.height)
        canvas.configure(bd=0, highlightthickness=0)
        canvas.pack()
        # set up events
        timerFiredWrapper(canvas, data)
        # and launch the app
        self.root.mainloop()  # blocks until window is closed
'''

'''
Records the information about the robot
'''
class cozmoRobot(object):
    def __init__(self, robot = cozmo.robot.Robot):
        self.directionList = {'N': [0, 1], 'S': [0, -1], 'W': [1, 0], 'E': [-1, 0]}
        self.searchingOrder = ['N', 'W', 'S', 'W']
        self.searchingInt = 1
        self.currentDirection = 'N'
        self.safeSpaces = []
        self.maxX = 0
        self.maxY = 0
        self.minX = 0
        self.minY = 0
        self.robot = robot
        self.currentX = 0
        self.currentY = 0
        self.state = 'mapping'
        self.cubes = [None, None, None]
        self.currentMovement = None
    '''
    Move 30 millimeters and record information about the coordinate that the Cozmo is on
        within the map
    '''
    def moveASpace(self):
        current_action = self.robot.drive_straight(distance_mm(30.0), speed_mmps(40.0))
        current_action.wait_for_completed()
        self.currentX += self.directionList[self.currentDirection][0]
        self.currentY += self.directionList[self.currentDirection][1]
        #Cliff detected
        if current_action.has_failed:
            code, reason = current_action.failure_reason
            result = current_action.result
            print("Drive failed: code=%s reason='%s' result=%s" % (code, reason, result))
            if self.state == 'mapping':
                self.mapSpace("cliff")
            current_action = self.robot.drive_straight(distance_mm(-30.0), speed_mmps(15.0))
            current_action.wait_for_completed()
            self.currentX -= self.directionList[self.currentDirection][0]
            self.currentY -= self.directionList[self.currentDirection][1]
            return False
        else:
            #get the position of each of the cubes. Highly variable
            if self.state == 'mapping':
                cube1 = self.robot.world.get_light_cube(cozmo.objects.LightCube1Id)
                cube2 = self.robot.world.get_light_cube(cozmo.objects.LightCube2Id)
                cube3 = self.robot.world.get_light_cube(cozmo.objects.LightCube3Id)
                print(cube1)
                print(cube2)
                print(cube3)
                if cube1 != None and cube1._is_visible and abs(cube1._pose._position._y) < 30:
                    if cube1._pose._position._x <= 100:
                        self.avoidCube(1)
                if cube2 != None and cube2._is_visible and abs(cube2._pose._position._y) < 30:
                    if cube2._pose._position._x <= 100:
                        self.avoidCube(2)
                if cube3 != None and cube3._is_visible and abs(cube3._pose._position._y) < 30:
                    if cube3._pose._position._x <= 100:
                        self.avoidCube(3)
                self.mapSpace("safe")
            return True

        def avoidCube(self, cubeNumber):
            initialDirection = self.currentDirection
            self.changeDirection('E')
            current_action = self.robot.drive_straight(distance_mm(30.0), speed_mmps(15.0))
            current_action.wait_for_completed()
            self.changeDirection(initialDirection)
            current_action = self.robot.drive_straight(distance_mm(90.0), speed_mmps(15.0))
            current_action.wait_for_completed()
            self.changeDirection('W')
            current_action = self.robot.drive_straight(distance_mm(30.0), speed_mmps(15.0))
            current_action.wait_for_completed()
            self.currentX += 3*self.directionList[self.currentDirection][0]
            self.currentY += 3*self.directionList[self.currentDirection][1]
            self.cubes[cubeNumber-1] = (self.currentX - 2*self.directionList[self.currentDirection][0],
                self.currentY - 2*self.directionList[self.currentDirection][1])            

    '''
    Record map information
    '''
    def mapSpace(self, info):
        if len(self.safeSpaces) - 1 <= self.currentY:
            if info == 'safe':
                self.safeSpaces.append([True])
            else:
                self.safeSpaces.append([False])
        elif len(self.safeSpaces[self.currentY]) - 1 <= self.currentX:
            if info == 'safe':
                self.safeSpaces[self.currentY].append(True)
            else:
                self.safeSpaces[self.currentY].append(False)
        else:
            if info == 'safe':
                self.safeSpaces[self.currentY][self.currentX] = True
            else:
                self.safeSpaces[self.currentY][self.currentX] = True
    '''
    Rotate to a specific direction
    '''
    def changeDirection(self, newDirection):
        direction = ['N', 'NW', 'W', 'SW', 'S', 'SE', 'E', 'NE']
        curr = direction.index(self.currentDirection)
        while self.currentDirection != newDirection:
            angle = degrees(45)
            action = self.robot.turn_in_place(angle)
            action.wait_for_completed()
            curr += 1
            curr %= 8
            self.currentDirection = direction[curr]

    '''
    Angles the robot 45 degrees in any direction based on where it is relative to the new cell
    '''
    def moveToCell(self, x, y):
        if x > self.currentX and y > self.currentY:
            self.changeDirection('NW')
            current_action = self.robot.drive_straight(distance_mm(30.0 * 2**0.5), speed_mmps(15.0))
            current_action.wait_for_completed()
            self.currentX = x
            self.currentY = y
        elif x > self.currentX and y == self.currentY:
            self.changeDirection('W')
            self.moveASpace()
        elif x > self.currentX and y < self.currentY:
            self.changeDirection('SW')
            current_action = self.robot.drive_straight(distance_mm(30.0 * 2**0.5), speed_mmps(15.0))
            current_action.wait_for_completed()
            self.currentX = x
            self.currentY = y
        elif x == self.currentX and y > self.currentY:
            self.changeDirection('N')
            self.moveASpace()
        elif x == self.currentX and y < self.currentY:
            self.changeDirection('S')
            self.moveASpace()
        elif x < self.currentX and y > self.currentY:
            self.changeDirection('NE')
            current_action = self.robot.drive_straight(distance_mm(30.0 * 2**0.5), speed_mmps(15.0))
            current_action.wait_for_completed()
            self.currentX = x
            self.currentY = y
        elif x < self.currentX and y == self.currentY:
            self.changeDirection('E')
            self.moveASpace()
        elif x < self.currentX and y < self.currentY:
            self.changeDirection('SE')
            current_action = self.robot.drive_straight(distance_mm(30.0 * 2**0.5), speed_mmps(15.0))
            current_action.wait_for_completed()
            self.currentX = x
            self.currentY = y

    '''
    Find and pick up a block
    '''
    def grabBlock(self):
        lookaround = self.robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
        cubes = self.robot.world.wait_until_observe_num_objects(num=1, object_type=cozmo.objects.LightCube, timeout=60)
        lookaround.stop()

        current_action = self.robot.pickup_object(cubes[0], num_retries=3)
        current_action.wait_for_completed()
        if current_action.has_failed:
            code, reason = current_action.failure_reason
            result = current_action.result
            print("Pickup Cube failed: code=%s reason='%s' result=%s" % (code, reason, result))

    def drawMap(self):
        if self.safeSpaces:
            for y in range(len(self.safeSpaces)):
                print()
                for x in range(len(self.safeSpaces[y])):
                    if (x, y) == (self.currentX, self.currentY):
                        print("C", end = "    ")
                    elif self.currentMovement and (x, y) in self.currentMovement:
                        print("P", end = "    ")
                    elif self.safeSpaces[y][x]:
                        print("S", end = "    ")
                    else:
                        print("U", end = "    ")



app = Flask(__name__)

'''
Call a function based on a post request ending with a given url
'''
@app.route('/state',methods = ['POST', 'GET'])
def buttonsWebpage():
    global currentState
    global cube
    if request.method == 'POST':
        value = request.form['action']
        if value == 'Stop':
            currentState = 'paused'
        elif value == 'Map':
            currentState = 'mapping'
            cozmo.run_program(startMapping)
        elif value == 'Block1':
            cube = 1
            currentState = 'pathing'
            cozmo.run_program(startPathing)
        elif value == 'Block2':
            cube = 2
            currentState = 'pathing'
            cozmo.run_program(startPathing)
        elif value == 'Block3':
            cube = 3
            currentState = 'pathing'
            cozmo.run_program(startPathing)
        return render_template('buttonsWebpage.html',**locals())
    else:
        value = request.form['action']
        return render_template('buttonsWebpage.html',**locals())


'''
maps a table using the cliff sensor
'''
def startMapping(robot: cozmo.robot.Robot):
    global coz
    #global tkin
    #tkin = CozmoView()
    robot.enable_stop_on_cliff(True)
    if coz == None:
        coz = cozmoRobot(robot)
    while currentState == 'mapping':
        #add a base case
        test = coz.moveASpace()
        #tkin.updateMap(coz.safeSpaces)
        #tkin.updateLoc((coz.currentX, coz.currentY))
        coz.drawMap()
        if not test:
            coz.changeDirection(coz.searchingOrder[coz.searchingInt])
            coz.searchingInt += 1
            coz.searchingInt %= 4
            coz.moveASpace()
            #tkin.updateMap(coz.safeSpaces)
            #tkin.updateLoc((coz.currentX, coz.currentY))
            coz.drawMap()
            coz.changeDirection(coz.searchingOrder[coz.searchingInt])
            coz.searchingInt += 1
            coz.searchingInt %= 4

    return

'''
plans a path to a given location based on a map
uses a*
TODO: have the robot consistently identify a block while mapping and chose coordinates
    using a lightblock
'''
def startPathing(robot: cozmo.robot.Robot):
    global cube
    global coz
    #global tkin
    coz.robot = robot
    if currentState == 'pathing':
        coz.state = 'pathing'
        x, y = (0, 3)
        pathing = PathPlan()
        pathing.initMap(coz.safeSpaces, (coz.currentX, coz.currentY), (x, y))
        solution = pathing.solve()
        coz.currentMovement = set(solution)
        #tkin.updatePath(coz.currentMovement)
        coz.drawMap()
        #app = App()
        if solution != None:
            for cell in solution[:-1]:
                x, y = cell
                coz.moveToCell(x, y)
                coz.currentMovement.discard(x, y)
                #tkin.updatePath(coz.currentMovement)
                #tkin.updateLoc((coz.currentX, coz.currentY))
                coz.drawMap()
            coz.grabBlock()
            solution.reverse()
            coz.currentMovement = set(solution)
            for cell in solution[:-1]:
                x, y = cell
                coz.moveToCell(x, y)
                coz.currentMovement.discard(x, y)
                #tkin.updatePath(coz.currentMovement)
                #tkin.updateLoc((coz.currentX, coz.currentY))
                coz.drawMap()

        ######## taken from cozmo tutorials #########
        # Tell Cozmo to look around for the charger
        look_around = coz.robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
        charger = None
        try:
            charger = coz.robot.world.wait_for_observed_charger(timeout=10)
            print("Found charger: %s" % charger)
        except asyncio.TimeoutError:
            print("Didn't see the charger")
        finally:
            # whether we find it or not, we want to stop the behavior
            look_around.stop()
        if charger:
            # Attempt to drive near to the charger, and then stop.
            action = coz.robot.go_to_object(charger, distance_mm(65.0))
            action.wait_for_completed()
            print("Completed action: result = %s" % action)
            print("Done.")
        return
        ######## taken from cozmo tutorials #########


def run():
    flaskHelper.runFlask(app)


if __name__ == '__main__':
    cozmo.setup_basic_logging()
    run()

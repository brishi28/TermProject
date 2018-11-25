import flaskHelper
import cozmo
import time
import asyncio
import sys

from flask import Flask, redirect, url_for, request, render_template
from cozmo.util import degrees, distance_mm, speed_mmps, Angle

paused = False
coz = None

'''
Records the information about the robot
'''
class cozmoRobot(object):
    def __init__(self, robot = cozmo.robot.Robot):
        self.directionList = {'N': [0, 1], 'S': [0, -1], 'W': [1, 0]}
        self.searchingOrder = ['N', 'W', 'S', 'W']
        self.searchingInt = 1
        self.currentDirection = 'N'
        self.currentMap = []
        self.visited = set()
        self.robot = robot
        self.currentX = 0
        self.currentY = 0

    def getCurrentMap(self):
        return self.currentMap

    '''
    Move 30 millimeters and record information about the coordinate that the Cozmo is on
        within the map
    '''
    def moveASpace(self):
        current_action = self.robot.drive_straight(distance_mm(30.0), speed_mmps(15.0))
        current_action.wait_for_completed()
        self.currentX += self.directionList[self.currentDirection][0]
        self.currentY += self.directionList[self.currentDirection][1]
        #Cliff detected
        if current_action.has_failed:
            code, reason = current_action.failure_reason
            result = current_action.result
            print("Drive failed: code=%s reason='%s' result=%s" % (code, reason, result))

            self.mapSpace("cliff")
            current_action = self.robot.drive_straight(distance_mm(-30.0), speed_mmps(15.0))
            current_action.wait_for_completed()
            self.currentX -= self.directionList[self.currentDirection][0]
            self.currentY -= self.directionList[self.currentDirection][1]
            return False
        else:
            self.mapSpace("safe")
            return True

    '''
    Record map information
    '''
    def mapSpace(self, type):
        self.currentMap += [gridNode(self.currentX, self.currentY, type)]
        print(self.currentMap)

    '''
    Inlude a visited list to exit out of the mapping loop
    '''
    def addToVisited(self):
        self.visited.add((self.currentX, self.currentY))

    '''
    Rotate to a specific direction
    '''
    def changeDirection(self, newDirection):
        print(newDirection)
        direction = ['N', 'W', 'S', 'E']
        curr = direction.index(self.currentDirection)
        while self.currentDirection != newDirection:
            print(self.currentDirection)
            angle = degrees(90)
            action = self.robot.turn_in_place(angle)
            action.wait_for_completed()
            curr += 1
            curr %= 4
            self.currentDirection = direction[curr]

class gridNode(object):
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value

    def __repr__(self):
        return str((self.x, self.y, self.value))

app = Flask(__name__)

'''
Call a function based on a post request ending with a given url
'''
@app.route('/state',methods = ['POST', 'GET'])
def buttonsWebpage():
    global paused
    if request.method == 'POST':
        value = request.form['action']
        if value == 'Stop':
            pasued = True
            sys.exit()
        elif value == 'Map':
            paused = False
            cozmo.run_program(beginMapping)
        elif value == 'FindBlock':
            paused = False
            cozmo.run_program(grabBlock)
        return render_template('buttonsWebpage.html',**locals())
    else:
        value = request.form['action']
        return render_template('buttonsWebpage.html',**locals())


def beginMapping(robot: cozmo.robot.Robot):
    robot.enable_stop_on_cliff(True)
    coz = cozmoRobot(robot)
    while not paused:
        test = coz.moveASpace()
        if not test:
            coz.changeDirection(coz.searchingOrder[coz.searchingInt])
            coz.searchingInt += 1
            coz.searchingInt %= 4
            coz.moveASpace()
            coz.changeDirection(coz.searchingOrder[coz.searchingInt])
            coz.searchingInt += 1
            coz.searchingInt %= 4
        if (coz.currentX, coz.currentY) in coz.visited:
            break
        else:
            coz.addToVisited()

'''
Find and pick up a block
'''
def grabBlock(robot: cozmo.robot.Robot):
    if not paused:
        lookaround = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
        cubes = robot.world.wait_until_observe_num_objects(num=1, object_type=cozmo.objects.LightCube, timeout=60)
        lookaround.stop()

        current_action = robot.pickup_object(cubes[0], num_retries=3)
        current_action.wait_for_completed()
        if current_action.has_failed:
            code, reason = current_action.failure_reason
            result = current_action.result
            print("Pickup Cube failed: code=%s reason='%s' result=%s" % (code, reason, result))
            return

        current_action = robot.place_object_on_ground_here(cubes[0], num_retries = 3)
        current_action.wait_for_completed()
        if current_action.has_failed:
            code, reason = current_action.failure_reason
            result = current_action.result
            print("Place Cube failed: code=%s reason='%s' result=%s" % (code, reason, result))
            return

def run():
    flaskHelper.runFlask(app)


if __name__ == '__main__':
    paused = False
    cozmo.setup_basic_logging()
    run()

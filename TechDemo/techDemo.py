import flaskHelper
import cozmo

from flask import Flask, redirect, url_for, request, render_template
from cozmo.util import degrees, distance_mm
global paused

app = Flask(__name__)

@app.route('/state',methods = ['POST', 'GET'])
def buttonsWebpage():
    if request.method == 'POST':
        value = request.form['action']
        if value == 'Stop':
            pasued = True
        else:
            paused = False
            cozmo.run_program(goToObject)

        return render_template('buttonsWebpage.html',**locals())
    else:
        value = request.form['action']
        return render_template('buttonsWebpage.html',**locals())

def run():
    flaskHelper.runFlask(app)

def stop(robot: cozmo.robot.Robot):
    robot.stop_all_motors()

def goToObject(robot: cozmo.robot.Robot):

    while not paused:
        robot.move_lift(-3)
        robot.set_head_angle(degrees(0)).wait_for_completed()

        lookAround = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)

        cube = None

        try:
            cube = robot.world.wait_for_observed_light_cube()
        except e:
            print("Didn't find a cube")
        finally:
            lookAround.stop()

        if cube:
            action = robot.go_to_object(cube, distance_mm(70.0))
            action.wait_for_completed()
            action = robot.pickup_object(cube, num_retries=3)
            action.wait_for_completed()
            if action.has_failed:
                code, reason = action.failure_reason
                result = action.result
                print("Pickup Cube failed: code=%s reason='%s' result=%s" % (code, reason, result))

            

if __name__ == '__main__':
    paused = False
    cozmo.setup_basic_logging()
    run()

    

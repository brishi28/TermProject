import cozmo

def simple(robot: cozmo.robot.Robot):
    #print(robot.world.light_cubes[cozmo.objects.LightCube1Id])
    #print(robot.world.get_light_cube(cozmo.objects.LightCube1Id)._is_visible)
    cube1 = robot.world.get_light_cube(cozmo.objects.LightCube1Id)
    cube2 = robot.world.get_light_cube(cozmo.objects.LightCube2Id)
    cube3 = robot.world.get_light_cube(cozmo.objects.LightCube3Id)
    print(cube1)
    print(cube2)
    print(cube3)

cozmo.run_program(simple)

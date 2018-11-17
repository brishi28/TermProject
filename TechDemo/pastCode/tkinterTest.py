# Basic Animation Framework

from tkinter import *
import cozmo
import threading

def runCozmo(data):
    print(data.paused)

def init(data):
    data.paused = False
    buttonWidth = 80
    buttonHeight = 40
    data.button = (data.width/2 - buttonWidth, data.height/2 - buttonHeight, data.width/2 + buttonWidth, data.height/2 + buttonHeight)

def mousePressed(event, data):
    if data.button[0] <= event.x and event.x <= data.button[2] and data.button[1] <= event.y and event.y <= data.button[3]:
        if data.paused:
            data.paused = False
        else:
            data.paused = True

def keyPressed(event, data):
    pass

def redrawAll(canvas, data):
    x0, y0, x1, y1 = data.button
    if data.paused:
        color = 'green'
        command = 'Start'
    else:
        color = 'red'
        command = 'Stop'
    canvas.create_rectangle(x0, y0, x1, y1, fill = color)
    canvas.create_text(data.width/2, data.height/2, text = command)

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height, fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    root = Tk()
    root.resizable(width=False, height=False) # prevents resizing window
    init(data)
    # create the root and the canvas
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    redrawAll(canvas, data)
    
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")
    t.stop()

run(400, 200)

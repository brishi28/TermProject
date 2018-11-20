import webbrowser, os
from time import sleep
from threading import Thread


def openBrowser():
    path = 'file://' + os.path.realpath("buttonsWebpage.html")

    def delayedOpen():
        sleep(1.0)
        webbrowser.open(path, new=0, autoraise=True)

    thread = Thread(target=delayedOpen)
    thread.daemon = True # Force to quit on main quitting
    thread.start()

def runFlask(app):
    openBrowser()
    app.run(debug = True, threaded = True, use_evalex = False)

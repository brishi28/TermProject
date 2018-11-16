import asyncio
import io
import json
import math
import sys
import cozmo

import logging
from threading import Thread
import webbrowser
from time import sleep
from io import BytesIO

from flask import Flask, request, make_response, Response, send_file

#CONTINUE READING THE FLASK DOCUMENTATION ABOUT SHUTDOWNFLASK. ALSO LOOK AS TO HOW THIS SHIT IS USED

'''
@PARAM:
    url - url location
    delay - time delay before opening the browser
        prevents someone from requesting data from the browser before it is available
    new -
    autoRaise - make the window pop up
    specificBrowser - whether a specific browser should be used
@RETURN: None

SUMMARY: open a web browser and create a thread to monitor it while main is running
'''
def openWebBrowser(url, delay, new = 0, autoraise = True, specificBrowser = None):
    def browserThread(url, delay, new, autoraise, specificBrowser):
        sleep(delay)
        browser = webbrowser
        browser.open(url, new = new, autoraise = autoraise)

    thread = Thread(target = browserThread, kwargs = dict(url = url, new = new, delay = delay, autoraise = autoraise, specifcBrowser = specificBrowser))
    thread.daemon = True #When main ends, so will the thread
    thread.start()

def runFlask(flask_app, hostIP = "127.0.0.1", hostPort = 5000, enableFlaskLogging = False, openPage = True, delay = 1.0):
    if not enableFlaskLogging:
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

    if openPage:
        openWebBrowser("http://" + hostIP + : + str(hostPort), delay = delay)

    flask_app.run(host = hostIP, port = hostPort, use_evalex = False, threaded = True)


def shutdownFlask(request):
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        sys.exit('SDK Shutdown')
    func()

import webbrowser, os

from flask import Flask, redirect, url_for, request, render_template
app = Flask(__name__)

@app.route('/state',methods = ['POST', 'GET'])
def buttonsWebpage():
    if request.method == 'POST':
        value = request.form['action']
        return render_template('buttonsWebpage.html',**locals())
    else:
        value = request.form['action']
        return render_template('buttonsWebpage.html',**locals())

if __name__ == '__main__':
    path = 'file://' + os.path.realpath("buttonsWebpage.html")
    webbrowser.open(path)
    app.run(debug = True)

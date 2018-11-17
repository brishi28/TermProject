import webbrowser, os

from flask import Flask, redirect, url_for, request, render_template
app = Flask(__name__)
path = 'file://' + os.path.realpath("buttonsWebpage.html")

@app.route('/success/<name>')
def success(name):
       return 'welcome %s' % name

@app.route('/state',methods = ['POST', 'GET'])
def buttonsWebpage():
    if request.method == 'POST':
        user = request.form['action']
        print(user)
        return render_template('buttonsWebpage.html',**locals())
    else:
        user = request.args.get('nm')
        return redirect(url_for('success',name = user))

if __name__ == '__main__':
    webbrowser.open(path)
    app.run(debug = True)
    print('a')

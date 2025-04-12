from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
@app.route("/<user>")
def ddp(user=None):
    return render_template('index.html', user=user)
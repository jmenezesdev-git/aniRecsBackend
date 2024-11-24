from flask import Flask, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/", methods=['POST', 'GET'])
def hello_world():
    return "<p>Hello, CHAT!</p>"

@app.route("/hello", methods=['POST', 'GET'])
def testRequestContextStuff():
    return "<p>Hello, CHAT!</p>"

@app.route("/getGenres", methods=['GET'])
def getGenresRequest():
    return "<p>This is Get Genres!</p>"

@app.route("/aniRequest", methods=['GET'])
def getRecRequest():
    malAccount=request.args.get('malAccount', '')
    print (malAccount)
    print(request.args)

    return {'requestArgs':request.args}

if __name__ == '__main__':
    app.run()
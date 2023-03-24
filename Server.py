from flask import Flask, request
from flask_cors import CORS
from flask_restful import Resource, Api
import requests

app = Flask(__name__)
CORS(app)
api = Api(app)


class Users(Resource):
  @app.route('/home', methods = ['GET', 'POST'])
  def json_example():
    return "Hello World"
  pass


if __name__ == '__main__':
  app.run()
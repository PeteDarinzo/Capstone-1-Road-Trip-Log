from flask import Flask, render_template, request
import requests

from models import connect_db

app = Flask(__name__)

app.config['SECRET_KEY'] = "CanadianGeese1195432"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///greenflash'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)




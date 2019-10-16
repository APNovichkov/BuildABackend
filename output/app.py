from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

client = MongoClient()
test = client['test']
hi = test['hi']


@app.route('test')
def test_function():
	"""test."""

	pass

@app.route('test')
def test_function():
	"""test."""

	pass


if __name__ == "__main__":
	app.run(debug=True)
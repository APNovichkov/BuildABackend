from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/builder/add-route', methods=['POST'])
def new_function():
	"""Creates new route."""

	pass

@app.route('/builder/detele-route/<route_id>')
def delete_function(route_id):
	"""Deletes route by route_id."""

	pass


if __name__ == "__main__":
	app.run(debug=True)
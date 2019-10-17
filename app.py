import flask as fl
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from web_services import DataProvider
from datetime import datetime
import os

# bcrypt
# string.replace() for time

app = Flask(__name__)

# client = MongoClient()
# db = client['BuildABackend']
host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/BuildABackend')
client = MongoClient(host=f'{host}?retryWrites=false')
db = client.get_default_database()

dp = DataProvider()

# collections
html_pages = db['html_pages']
routes = db['routes']
databases = db['databases']
projects = db['projects']
users = db['users']


@app.route("/")
def index():
    return redirect(url_for("show_login"))

@app.route("/login")
def show_login():
    return render_template('login.html')

@app.route("/login/authorize", methods=['POST'])
def login_user():
    user = {'username': request.form.get('username')}

    user_id = None

    if users.find_one({'username': user['username']}) is not None:
        print("Username exists")
        user_id = str(users.find_one({'username': user['username']})['_id'])
    else:
        print("Username does not exist")
        print("Adding username: {}".format(user['username']))
        user_id = str(users.insert_one(user).inserted_id)

    return redirect(url_for("show_choose_project_page", user_id=user_id))


@app.route("/builder/<user_id>/<project_id>")
def show_builder(user_id, project_id):
    """Show the builder template."""

    return render_template(
        "builder.html",
        user_id=user_id,
        html_pages=html_pages.find({'project_id': project_id}),
        databases=databases.find({'project_id': project_id}),
        routes=routes.find({'project_id': project_id}),
        project=projects.find_one({'_id': ObjectId(project_id)}),
        num_html_pages=html_pages.find({'project_id': project_id}).count(),
        num_databases=databases.find({'project_id': project_id}).count(),
        num_routes=routes.find({'project_id': project_id}).count())

@app.route("/choose-project/<user_id>")
def show_choose_project_page(user_id):
    """Show choose project page or create new project."""

    print("This is the user_id from show_choose_project_page: {}".format(user_id))

    return render_template(
        "choose_project.html",
        projects=projects.find({'user_id': user_id}),
        user_id=user_id)

@app.route("/builder/delete/<user_id>/<project_id>")
def remove_project(user_id, project_id):
    """Delete project based on project_id thats passted in."""

    html_pages.delete_many({'project_id': project_id})
    databases.delete_many({'project_id': project_id})
    routes.delete_many({'project_id': project_id})

    projects.delete_one({'_id': ObjectId(project_id)})

    return redirect(url_for("show_choose_project_page", user_id=user_id))

@app.route("/builder/<user_id>/new")
def show_new_project_page(user_id):
    """Show the NEW PROJECT form/page."""

    return render_template("new_project.html", user_id=user_id)

@app.route("/builder/<user_id>/new", methods=['POST'])
def create_new_project(user_id):
    """Create NEW PROJECT."""

    print("This is the user_id from create_new_project: {}".format(user_id))

    project = {
        'name': request.form.get("project-name"),
        'user_id': user_id,
        'time_created': datetime.now().strftime("%c"),
        'last_modified': datetime.now().strftime("%c")
    }

    project_id = projects.insert_one(project).inserted_id

    return redirect(url_for("show_builder", user_id=user_id, project_id=project_id))

# CRUD for HTML pages
@app.route("/builder/<user_id>/add-html", methods=['POST'])
def add_html_page(user_id):
    """Add new HTML page to builder."""

    html_page = {
        'project_id': request.form.get('project-id'),
        'name': request.form.get("name"),
        'url': request.form.get('url'),
        'http_verb': request.form.get("http-verb"),
        'action': request.form.get("action"),
        'description': request.form.get("description")
    }

    projects.find_one_and_update({'_id': ObjectId(html_page['project_id'])}, {'$set': {'last_modified': datetime.now().strftime("%c")}})

    html_pages.insert_one(html_page)
    return redirect(url_for("show_builder", user_id=user_id, project_id=html_page['project_id']))


@app.route("/builder/<user_id>/delete-html-page/<html_page_id>")
def remove_html_page(user_id, html_page_id):
    """Remove HTML page from builder by the page_id given."""

    project_id = html_pages.find_one({'_id': ObjectId(html_page_id)})['project_id']

    html_pages.delete_one({'_id': ObjectId(html_page_id)})

    projects.find_one_and_update({'_id': ObjectId(project_id)}, {'$set': {'last_modified': datetime.now().strftime("%c")}})

    return redirect(url_for("show_builder", user_id=user_id, project_id=project_id))

# CRUD for DATABASES
@app.route("/builder/<user_id>/add-database", methods=['POST'])
def add_database(user_id):
    """Add new database to builder."""

    collections = request.form.get('collections').split()

    database = {
        'project_id': request.form.get("project-id"),
        'framework': request.form.get("database-framework"),
        'name': request.form.get("name"),
        'collections': collections}

    projects.find_one_and_update({'_id': ObjectId(database['project_id'])}, {'$set': {'last_modified': datetime.now().strftime("%c")}})

    databases.insert_one(database)

    return redirect(url_for("show_builder", user_id=user_id, project_id=database['project_id']))

@app.route("/builder/<user_id>/delete-database/<database_id>")
def remove_database(user_id, database_id):
    """Remove Database from builder by the database_id given."""

    project_id = databases.find_one({'_id': ObjectId(database_id)})['project_id']

    projects.find_one_and_update({'_id': ObjectId(project_id)}, {'$set': {'last_modified': datetime.now().strftime("%c")}})

    databases.delete_one({'_id': ObjectId(database_id)})

    return redirect(url_for("show_builder", user_id=user_id, project_id=project_id))


# CRUD for ROUTES
@app.route("/builder/<user_id>/add-route", methods=['POST'])
def add_route(user_id):
    """Add new route to builder."""

    route = {
        'project_id': request.form.get('project-id'),
        'url': request.form.get('url'),
        'name': request.form.get('name'),
        'http_verb': request.form.get("http-verb"),
        'action': request.form.get("action"),
        'description': request.form.get("description")
    }

    projects.find_one_and_update({'_id': ObjectId(route['project_id'])}, {'$set': {'last_modified': datetime.now().strftime("%c")}})

    routes.insert_one(route)

    return redirect(url_for("show_builder", user_id=user_id, project_id=route['project_id']))

@app.route("/builder/<user_id>/delete_route/<route_id>", methods=['POST'])
def remove_route(user_id, route_id):

    project_id = routes.find_one({'_id': ObjectId(route_id)})['project_id']

    projects.find_one_and_update({'_id': ObjectId(project_id)}, {'$set': {'last_modified': datetime.now().strftime("%c")}})

    routes.delete_one({'_id': ObjectId(route_id)})

    return redirect(url_for("show_builder", user_id=user_id, project_id=project_id))


@app.route("/builder/download/<project_id>")
def download_project(project_id):
    """Use the DataProvider to call the download method giving it the project_id."""

    zip_file, zip_filename = dp.create_project_downloadable(project_id)

    print("This is the filename in flask: {}".format(zip_filename))

    return fl.send_file(
        zip_file,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename='downloadable_output.zip'
    )


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))

import flask as fl
from flask import Flask, Response, render_template, request, redirect, url_for, send_file
from pymongo import MongoClient
from bson.objectid import ObjectId
from web_services import DataProvider
from datetime import datetime
from io import BytesIO

# bcrypt
# string.replace() for time

app = Flask(__name__)

client = MongoClient()
db = client['BuildABackend']
dp = DataProvider()

# collections
html_pages = db['html_pages']
routes = db['routes']
databases = db['databases']
projects = db['projects']


@app.route("/")
def index():
    return redirect(url_for("show_choose_project_page"))

@app.route("/builder/<project_id>")
def show_builder(project_id):
    """Show the builder template."""

    return render_template(
        "builder.html",
        html_pages=html_pages.find({'project_id': project_id}),
        databases=databases.find({'project_id': project_id}),
        routes=routes.find({'project_id': project_id}),
        project=projects.find_one({'_id': ObjectId(project_id)}),
        num_html_pages=html_pages.find({'project_id': project_id}).count(),
        num_databases=databases.find({'project_id': project_id}).count(),
        num_routes=routes.find({'project_id': project_id}).count())

@app.route("/choose-project")
def show_choose_project_page():
    """Show choose project page or create new project."""

    return render_template(
        "choose_project.html",
        projects=projects.find())

@app.route("/builder/delete/<project_id>")
def remove_project(project_id):
    """Delete project based on project_id thats passted in."""

    html_pages.delete_many({'project_id': project_id})
    projects.delete_one({'_id': ObjectId(project_id)})

    return redirect(url_for("show_choose_project_page"))

@app.route("/builder/new")
def show_new_project_page():
    """Show the NEW PROJECT form/page."""

    return render_template("new_project.html")

@app.route("/builder/new", methods=['POST'])
def create_new_project():
    """Create NEW PROJECT."""

    project = {
        'name': request.form.get("project-name"),
        'time_created': datetime.now().strftime("%c"),
        'last_modified': datetime.now().strftime("%c")
    }

    project_id = projects.insert_one(project).inserted_id

    return redirect(url_for("show_builder", project_id=project_id))

# CRUD for HTML pages
@app.route("/builder/add-html", methods=['POST'])
def add_html_page():
    """Add new HTML page to builder."""

    html_page = {
        'project_id': request.form.get('project-id'),
        'name': request.form.get("name"),
        'url': request.form.get('url'),
        'http_verb': request.form.get("http-verb"),
        'action': request.form.get("action"),
        'description': request.form.get("description")
    }

    html_pages.insert_one(html_page)
    return redirect(url_for("show_builder", project_id=html_page['project_id']))


@app.route("/builder/delete-html-page/<html_page_id>")
def remove_html_page(html_page_id):
    """Remove HTML page from builder by the page_id given."""

    project_id = html_pages.find_one({'_id': ObjectId(html_page_id)})['project_id']

    html_pages.delete_one({'_id': ObjectId(html_page_id)})

    return redirect(url_for("show_builder", project_id=project_id))

# CRUD for DATABASES
@app.route("/builder/add-database", methods=['POST'])
def add_database():
    """Add new database to builder."""

    collections = request.form.get('collections').split()

    database = {
        'project_id': request.form.get("project-id"),
        'framework': request.form.get("database-framework"),
        'name': request.form.get("name"),
        'collections': collections}

    databases.insert_one(database)

    return redirect(url_for("show_builder", project_id=database['project_id']))

@app.route("/builder/delete-database/<database_id>")
def remove_database(database_id):
    """Remove Database from builder by the database_id given."""

    project_id = databases.find_one({'_id': ObjectId(database_id)})['project_id']

    databases.delete_one({'_id': ObjectId(database_id)})

    return redirect(url_for("show_builder", project_id=project_id))


# CRUD for ROUTES
@app.route("/builder/add-route", methods=['POST'])
def add_route():
    """Add new route to builder."""

    route = {
        'project_id': request.form.get('project-id'),
        'url': request.form.get('url'),
        'name': request.form.get('name'),
        'http_verb': request.form.get("http-verb"),
        'action': request.form.get("action"),
        'description': request.form.get("description")
    }

    routes.insert_one(route)

    return redirect(url_for("show_builder", project_id=route['project_id']))

@app.route("/builder/delete_route/<route_id>", methods=['POST'])
def remove_route(route_id):

    project_id = routes.find_one({'_id': ObjectId(route_id)})['project_id']

    routes.delete_one({'_id': ObjectId(route_id)})

    return redirect(url_for("show_builder", project_id=project_id))


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
    app.run(debug=True)

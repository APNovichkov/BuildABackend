from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

client = MongoClient()
db = client['BuildABackend']

# collections
html_pages = db['html_pages']
projects = db['projects']


@app.route("/")
def index():
    return redirect(url_for("show_choose_project_page"))

@app.route("/builder/<project_id>")
def show_builder(project_id):
    """Show the builder template."""

    print("This is id of the product: {}".format(project_id))
    print("This is the name of that project: {}".format(projects.find_one({'_id': ObjectId(project_id)})['name']))

    return render_template(
        "builder.html",
        html_pages=html_pages.find({'project_id': project_id}),
        project=projects.find_one({'_id': ObjectId(project_id)}),
        num_html_pages=html_pages.find({'project_id': project_id}).count())

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

    project = {'name': request.form.get("project-name")}
    project_id = projects.insert_one(project).inserted_id

    return redirect(url_for("show_builder", project_id=project_id))

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


if __name__ == "__main__":
    app.run(debug=True)

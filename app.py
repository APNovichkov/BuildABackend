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
    return redirect(url_for("show_builder"))

@app.route("/builder")
def show_builder():
    """Show the builder template."""

    return render_template(
        "builder.html",
        html_pages=html_pages.find(),
        projects=projects.find())

@app.route("/builder/new")
def show_new_project_page():
    """Show the NEW PROJECT form/page."""
    pass

@app.route("/builder/new", methods=['POST'])
def create_new_project():
    """Create NEW PROJECT."""
    pass

@app.route("/builder/add-html", methods=['POST'])
def add_html_page():
    """Add new HTML page to builder."""
    pass

@app.route("/builder/delete-html-page/<html_page_id>")
def remove_html_page():
    """Remove HTML page from builder by the page_id given."""
    pass


if __name__ == "__main__":
    app.run(debug=True)

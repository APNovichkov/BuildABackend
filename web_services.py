from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os
import zipfile
import shutil
import io


class DataProvider():
    def __init__(self):
        self.host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/BuildABackend')
        self.client = MongoClient(host=f'{self.host}?retryWrites=false')
        self.db = self.client.get_default_database()
        # self.client = MongoClient()
        # self.db = self.client['BuildABackend']
        self.projects = self.db['projects']
        self.html_pages = self.db['html_pages']
        self.databases = self.db['databases']
        self.routes = self.db['routes']

    def create_project_downloadable(self, project_id):
        project = self.projects.find_one({'_id': ObjectId(project_id)})

        # Get html files
        html_files_to_create = []
        for html_file in self.html_pages.find({'project_id': project_id}):
            html_files_to_create.append(html_file)
        print("HTML files to create:")
        print(html_files_to_create)

        # Get routes
        routes_to_create = []
        for route in self.routes.find({'project_id': project_id}):
            routes_to_create.append(route)
        print("Routes to create:")
        print(routes_to_create)

        # Get databases
        databases_to_create = []
        for database in self.databases.find({'project_id': project_id}):
            databases_to_create.append(database)
        print("Databases to create:")
        print(databases_to_create)

        # Directory creation
        print("\nCurrent working directory: {}".format(os.getcwd()))
        output_dir = os.getcwd() + "/output"
        print("Creating directory while on flask: {}".format(output_dir))
        os.mkdir(output_dir)

        # Create html files
        self.create_html_files(html_files_to_create, project, output_dir)

        # Write app.py
        self.write_app_dot_py(output_dir, html_files_to_create, databases_to_create, routes_to_create, project['name'])

        zip_file, zip_filepath = self.zip_directory(output_dir)

        return zip_file, zip_filepath

    def create_html_files(self, html_files_to_create, project, output_dir):
        # Create directory
        html_files_path = output_dir + "/templates"
        os.mkdir(html_files_path)

        # Write base.html
        self.write_base_file(html_files_path, project['name'])

        # Write html files
        for html_file in html_files_to_create:
            self.write_html_file(html_files_path, html_file['name'])

    def write_app_dot_py(self, output_dir, html_files, databases, routes, project_name):
        f = open("{}/app.py".format(output_dir), "w+", encoding="utf-8")

        # import statements
        f.write("from flask import Flask, render_template, request, redirect, url_for\n")

        if len(databases) != 0:
            f.write("from pymongo import MongoClient\nfrom bson.objectid import ObjectId\n")

        # general initialization statements
        f.write("\napp = Flask(__name__)\n\n")

        # database initialization
        if len(databases) != 0:
            f.write("client = MongoClient()\n")
            for database in databases:
                f.write("{} = client[\'{}\']\n".format(database['name'].lower(), database['name']))
                for collection in database['collections']:
                    f.write("{} = {}[\'{}\']\n".format(collection, database['name'].lower(), collection))
            f.write('\n\n')

        # app.route statements for html files
        for html_file in html_files:
            if html_file['http_verb'].lower() != 'post':
                f.write("@app.route(\'{}\')\n".format(html_file['url']))
            else:
                f.write("@app.route(\'{}\', methods=['POST'])\n".format(html_file['url']))

            f.write("def {}_function():\n".format(html_file['name']))
            f.write("\t\"\"\"{}.\"\"\"\n\n".format(html_file['description']))
            f.write("\tpass\n\n")

        # app.route statements for routes
        for route in routes:
            if route['http_verb'].lower() != 'post':
                f.write("@app.route(\'{}\')\n".format(route['url']))
                if "<" in route['url']:
                    start_index = route['url'].index("<") + 1
                    end_index = route['url'].index(">")

                    f.write("def {}_function({}):\n".format(route['name'], route['url'][start_index:end_index]))
                else:
                    f.write("def {}_function():\n".format(route['name']))
            else:
                f.write("@app.route(\'{}\', methods=['POST'])\n".format(route['url']))
                f.write("def {}_function():\n".format(route['name']))

            f.write("\t\"\"\"{}.\"\"\"\n\n".format(route['description']))
            f.write("\tpass\n\n")

        # if main statement
        f.write("\nif __name__ == \"__main__\":\n\tapp.run(debug=True)")

        f.close()

    def write_base_file(self, html_files_path, project_name):
        f = open("{}/base.html".format(html_files_path), "w+", encoding="utf-8")

        f.write("<!DOCTYPE html>\n\n")
        f.write("<html>\n")

        f.write("<head>\n")
        f.write("\t<title>{}</title>\n".format(project_name))
        f.write("</head>\n\n")

        f.write("<body>\n")
        f.write("\t{% block content %} {% endblock %}\n")
        f.write("</body>\n\n")

        f.write("</html>")

        f.close()

    def write_html_file(self, html_files_path, html_filename):
        f = open("{}/{}.html".format(html_files_path, html_filename), "w+", encoding="utf-8")

        f.write("{% extends \"base.html\" %}\n\n")
        f.write("{% block content %}\n\n")
        f.write("<h1>This is {}.html!</h1>\n\n".format(html_filename))
        f.write("{% endblock %}")

    def zip_directory(self, output_path):
        # Assign the name of the directory to zip
        dir_name = output_path

        # Call the function to retrieve all files and folders of the assigned directory
        filePaths = self.retrieve_file_paths(dir_name)

        # printing the list of all files to be zipped
        print('The following list of files will be zipped:')
        for fileName in filePaths:
            print(fileName)

        zip_filepath = '{}_{}.zip'.format(dir_name, str(datetime.now()).split()[1].replace(':', '_').replace('.', '_'))

        zip_file = io.BytesIO()
        with zipfile.ZipFile(zip_file, mode='w') as z:
            for file in filePaths:
                z.write(file)

        zip_file.seek(0)

        print('{} file is created successfully!'.format(zip_filepath))

        self.remove_output_dir(output_path)

        return zip_file, zip_filepath

    def retrieve_file_paths(self, dir_name):
        # setup file paths variable
        file_paths = []

        # Read all directory, subdirectories and file lists
        for root, directories, files in os.walk(dir_name):
            for filename in files:
                # Create the full filepath by using os module.
                file_path = os.path.join(root, filename)
                file_paths.append(file_path)

        print("Filepaths:")
        print(file_paths)

        # return all paths
        return file_paths

    def remove_output_dir(self, output_path):
        shutil.rmtree(output_path)

    def remove_zip_file(self, zip_filepath, output_dir):
        os.remove(zip_filepath)
        pass

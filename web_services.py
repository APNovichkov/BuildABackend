from pymongo import MongoClient
from bson.objectid import ObjectId
import os


class DataProvider():
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client['BuildABackend']
        self.projects = self.db['projects']
        self.html_pages = self.db['html_pages']
        self.databases = self.db['databases']

    def create_project_downloadable(self, project_id):
        html_files_to_create = []

        for html_file in self.html_pages.find({'project_id': project_id}):
            html_files_to_create.append(html_file)

        print("HTML files to create:")
        print(html_files_to_create)

        databases_to_create = []

        for database in self.databases.find({'project_id': project_id}):
            databases_to_create.append(database)

        print("Databases to create:")
        print(databases_to_create)

        print("\nCurrent working directory: {}".format(os.getcwd()))

        print("Creating tmp directory while on flask")

        os.mkdir("/Users/andreynovichkov/Desktop/Make-School/Term-1/Intensive/BuildABackend/tmp")

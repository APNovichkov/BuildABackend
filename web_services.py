from pymongo import MongoClient
from bson.objectid import ObjectId


class DataProvider():
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client['BuildABackend']
        self.projects = self.db['projects']
        self.html_pages = self.db['html_pages']
        self.databases = self.db['databases']

    def create_project_downloadable(self, project_id):
        html_files_to_create = []

        print("Successfully called this function!")

        print("The project id is: {}".format(project_id))

        for html_file in self.html_pages.find({'project_id': project_id}):
            html_files_to_create.append(html_file)

        print(html_files_to_create)

# Standard library imports
import os

# Third party imports
from flask import Flask
from flask_cors import CORS


from flask_restx import Api


# Local application imports
from endpoints import api as _api
from endpoints.pdf import api as pdf
from extensions import api_list


app = Flask("api")
CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)
api.add_namespace(_api)
api.add_namespace(pdf)

for extension in api_list:
	api.add_namespace(extension)

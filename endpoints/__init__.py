# Standard library imports
import os
from datetime import datetime

# Third party imports
from flask import Flask
from flask import request
from flask import g
from flask_restx import Namespace
from flask_restx import Resource as _Resource
from flask_restx.fields import DateTime
from flask_restx.fields import Float
from flask_restx.fields import Integer
from flask_restx.fields import List
from flask_restx.fields import Nested
from flask_restx.fields import String
from flask_restx.fields import Boolean
from flask_restx.fields import Raw

# Local application imports
import models


class Resource(_Resource):
    dispatch_requests = []

    def __init__(self, api=None, *args, **kwargs):
        super(Resource, self).__init__(api, args, kwargs)

    def dispatch_request(self, *args, **kwargs):
        tmp = request.args.to_dict()
        request.args = tmp

        for method in self.dispatch_requests:
            method(self, args, kwargs)

        return super(Resource, self).dispatch_request(*args, **kwargs)


api = Namespace("api", description="")
program_base = api.model("program_base", models.Program.base())
program_reference = api.model("program_reference", models.Program.reference())
program_full = api.model("program", models.Program.model(api))
student_personal_data_base = api.model(
    "student_personal_data_base", models.StudentPersonalData.base()
)
student_personal_data_reference = api.model(
    "student_personal_data_reference", models.StudentPersonalData.reference()
)
student_personal_data_full = api.model(
    "student_personal_data", models.StudentPersonalData.model(api)
)


@api.route("/program")
class ProgramController(Resource):
    @api.marshal_list_with(api.models.get("program"))
    def get(self):
        return models.Program.fetch(request.args)

    @api.marshal_with(api.models.get("program"))
    def post(self):
        return models.Program(**request.get_json()).to_json()

    @api.marshal_with(api.models.get("program"))
    def put(self):
        data = models.Program(**request.get_json()).save()
        return data.to_json()

    @api.marshal_with(api.models.get("program"))
    def patch(self):
        return models.Program.set(**request.get_json()).to_json()


@api.route("/program/<program_id>")
class BaseProgramController(Resource):
    def delete(self, program_id):
        return models.Program.get(id=program_id).delete()


@api.route("/program/base")
class BaseProgramController(Resource):
    @api.marshal_list_with(api.models.get("program_reference"))
    def get(self):
        return [x.to_json(False) for x in models.Program.get(**request.args)]


@api.route("/student_personal_data")
class StudentPersonalDataController(Resource):
    @api.marshal_list_with(api.models.get("student_personal_data"))
    def get(self):
        from pprint import pprint

        pprint(models.StudentPersonalData.fetch(request.args))
        return models.StudentPersonalData.fetch(request.args)

    @api.marshal_with(api.models.get("student_personal_data"))
    def post(self):
        return models.StudentPersonalData(**request.get_json()).to_json()

    @api.marshal_with(api.models.get("student_personal_data"))
    def put(self):
        data = models.StudentPersonalData(**request.get_json()).save()
        return data.to_json()

    @api.marshal_with(api.models.get("student_personal_data"))
    def patch(self):
        return models.StudentPersonalData.set(**request.get_json()).to_json()


@api.route("/student_personal_data/<student_personal_data_id>")
class BaseStudentPersonalDataController(Resource):
    def delete(self, student_personal_data_id):
        return models.StudentPersonalData.get(id=student_personal_data_id).delete()


@api.route("/student_personal_data/base")
class BaseStudentPersonalDataController(Resource):
    @api.marshal_list_with(api.models.get("student_personal_data_reference"))
    def get(self):
        return [
            x.to_json(False) for x in models.StudentPersonalData.get(**request.args)
        ]

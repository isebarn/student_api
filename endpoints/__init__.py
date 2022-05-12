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
program_base = api.model('program_base', models.Program.base())
program_reference = api.model('program_reference', models.Program.reference())
program_full = api.model('program', models.Program.model(api))
airport_code_base = api.model('airport_code_base', models.AirportCode.base())
airport_code_reference = api.model('airport_code_reference', models.AirportCode.reference())
airport_code_full = api.model('airport_code', models.AirportCode.model(api))
host_family_base = api.model('host_family_base', models.HostFamily.base())
host_family_reference = api.model('host_family_reference', models.HostFamily.reference())
host_family_full = api.model('host_family', models.HostFamily.model(api))
account_base = api.model('account_base', models.Account.base())
account_reference = api.model('account_reference', models.Account.reference())
account_full = api.model('account', models.Account.model(api))
student_personal_data_base = api.model('student_personal_data_base', models.StudentPersonalData.base())
student_personal_data_reference = api.model('student_personal_data_reference', models.StudentPersonalData.reference())
student_personal_data_full = api.model('student_personal_data', models.StudentPersonalData.model(api))


@api.route("/program")
class ProgramController(Resource):

    @api.marshal_list_with(api.models.get('program'))
    def get(self):
        return models.Program.fetch(request.args)

    @api.marshal_with(api.models.get('program'))
    def post(self):
        return models.Program(**request.get_json()).to_json()

    @api.marshal_with(api.models.get('program'))
    def put(self):
        data = models.Program(**request.get_json()).save()
        return data.to_json()

    @api.marshal_with(api.models.get('program'))
    def patch(self):
        return models.Program.set(**request.get_json()).to_json()


@api.route("/program/<program_id>")
class BaseProgramController(Resource):

    def delete(self, program_id):
        return models.Program.get(id=program_id).delete()


@api.route("/program/base")
class BaseProgramController(Resource):

    @api.marshal_list_with(api.models.get('program_reference'))
    def get(self):
        return [x.to_json(False) for x in models.Program.get(**request.args)]

@api.route("/airport_code")
class AirportCodeController(Resource):

    @api.marshal_list_with(api.models.get('airport_code'))
    def get(self):
        return models.AirportCode.fetch(request.args)

    @api.marshal_with(api.models.get('airport_code'))
    def post(self):
        return models.AirportCode(**request.get_json()).to_json()

    @api.marshal_with(api.models.get('airport_code'))
    def put(self):
        data = models.AirportCode(**request.get_json()).save()
        return data.to_json()

    @api.marshal_with(api.models.get('airport_code'))
    def patch(self):
        return models.AirportCode.set(**request.get_json()).to_json()


@api.route("/airport_code/<airport_code_id>")
class BaseAirportCodeController(Resource):

    def delete(self, airport_code_id):
        return models.AirportCode.get(id=airport_code_id).delete()


@api.route("/airport_code/base")
class BaseAirportCodeController(Resource):

    @api.marshal_list_with(api.models.get('airport_code_reference'))
    def get(self):
        return [x.to_json(False) for x in models.AirportCode.get(**request.args)]

@api.route("/host_family")
class HostFamilyController(Resource):

    @api.marshal_list_with(api.models.get('host_family'))
    def get(self):
        return models.HostFamily.fetch(request.args)

    @api.marshal_with(api.models.get('host_family'))
    def post(self):
        return models.HostFamily(**request.get_json()).to_json()

    @api.marshal_with(api.models.get('host_family'))
    def put(self):
        data = models.HostFamily(**request.get_json()).save()
        return data.to_json()

    @api.marshal_with(api.models.get('host_family'))
    def patch(self):
        return models.HostFamily.set(**request.get_json()).to_json()


@api.route("/host_family/<host_family_id>")
class BaseHostFamilyController(Resource):

    def delete(self, host_family_id):
        return models.HostFamily.get(id=host_family_id).delete()


@api.route("/host_family/base")
class BaseHostFamilyController(Resource):

    @api.marshal_list_with(api.models.get('host_family_reference'))
    def get(self):
        return [x.to_json(False) for x in models.HostFamily.get(**request.args)]

@api.route("/account")
class AccountController(Resource):

    @api.marshal_list_with(api.models.get('account'))
    def get(self):
        return models.Account.fetch(request.args)

    @api.marshal_with(api.models.get('account'))
    def post(self):
        return models.Account(**request.get_json()).to_json()

    @api.marshal_with(api.models.get('account'))
    def put(self):
        data = models.Account(**request.get_json()).save()
        return data.to_json()

    @api.marshal_with(api.models.get('account'))
    def patch(self):
        return models.Account.set(**request.get_json()).to_json()


@api.route("/account/<account_id>")
class BaseAccountController(Resource):

    def delete(self, account_id):
        return models.Account.get(id=account_id).delete()


@api.route("/account/base")
class BaseAccountController(Resource):

    @api.marshal_list_with(api.models.get('account_reference'))
    def get(self):
        return [x.to_json(False) for x in models.Account.get(**request.args)]

@api.route("/student_personal_data")
class StudentPersonalDataController(Resource):

    @api.marshal_list_with(api.models.get('student_personal_data'))
    def get(self):
        return models.StudentPersonalData.fetch(request.args)

    @api.marshal_with(api.models.get('student_personal_data'))
    def post(self):
        return models.StudentPersonalData(**request.get_json()).to_json()

    @api.marshal_with(api.models.get('student_personal_data'))
    def put(self):
        data = models.StudentPersonalData(**request.get_json()).save()
        return data.to_json()

    @api.marshal_with(api.models.get('student_personal_data'))
    def patch(self):
        return models.StudentPersonalData.set(**request.get_json()).to_json()


@api.route("/student_personal_data/<student_personal_data_id>")
class BaseStudentPersonalDataController(Resource):

    def delete(self, student_personal_data_id):
        return models.StudentPersonalData.get(id=student_personal_data_id).delete()


@api.route("/student_personal_data/base")
class BaseStudentPersonalDataController(Resource):

    @api.marshal_list_with(api.models.get('student_personal_data_reference'))
    def get(self):
        return [x.to_json(False) for x in models.StudentPersonalData.get(**request.args)]


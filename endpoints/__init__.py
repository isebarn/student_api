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
airport_base = api.model('airport_base', models.Airport.base())
airport_reference = api.model('airport_reference', models.Airport.reference())
airport_full = api.model('airport', models.Airport.model(api))
flight_info_base = api.model('flight_info_base', models.FlightInfo.base())
flight_info_reference = api.model('flight_info_reference', models.FlightInfo.reference())
flight_info_full = api.model('flight_info', models.FlightInfo.model(api))
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

    @api.marshal_list_with(api.models.get('program'), skip_none=True)
    def get(self):
        return models.Program.fetch(request.args)

    @api.marshal_with(api.models.get('program'), skip_none=True)
    def post(self):
        return models.Program(**request.get_json()).to_json()

    @api.marshal_with(api.models.get('program'), skip_none=True)
    def put(self):
        data = models.Program(**request.get_json()).save()
        return data.to_json()

    @api.marshal_with(api.models.get('program'), skip_none=True)
    def patch(self):
        return models.Program.set(**request.get_json()).to_json()


@api.route("/program/<program_id>")
class BaseProgramController(Resource):
    @api.marshal_with(api.models.get("program"), skip_none=True)
    def get(self, program_id):
        return models.Program.objects.get(id=program_id)

    def delete(self, program_id):
        return models.Program.get(id=program_id).delete()


@api.route("/program/base")
class BaseProgramController(Resource):

    @api.marshal_list_with(api.models.get('program_reference'))
    def get(self):
        return [x.to_json(False) for x in models.Program.get(**request.args)]

@api.route("/airport")
class AirportController(Resource):

    @api.marshal_list_with(api.models.get('airport'), skip_none=True)
    def get(self):
        return models.Airport.fetch(request.args)

    @api.marshal_with(api.models.get('airport'), skip_none=True)
    def post(self):
        return models.Airport(**request.get_json()).to_json()

    @api.marshal_with(api.models.get('airport'), skip_none=True)
    def put(self):
        data = models.Airport(**request.get_json()).save()
        return data.to_json()

    @api.marshal_with(api.models.get('airport'), skip_none=True)
    def patch(self):
        return models.Airport.set(**request.get_json()).to_json()


@api.route("/airport/<airport_id>")
class BaseAirportController(Resource):
    @api.marshal_with(api.models.get("airport"), skip_none=True)
    def get(self, airport_id):
        return models.Airport.objects.get(id=airport_id)

    def delete(self, airport_id):
        return models.Airport.get(id=airport_id).delete()


@api.route("/airport/base")
class BaseAirportController(Resource):

    @api.marshal_list_with(api.models.get('airport_reference'))
    def get(self):
        return [x.to_json(False) for x in models.Airport.get(**request.args)]

@api.route("/flight_info")
class FlightInfoController(Resource):

    @api.marshal_list_with(api.models.get('flight_info'), skip_none=True)
    def get(self):
        return models.FlightInfo.fetch(request.args)

    @api.marshal_with(api.models.get('flight_info'), skip_none=True)
    def post(self):
        return models.FlightInfo(**request.get_json()).to_json()

    @api.marshal_with(api.models.get('flight_info'), skip_none=True)
    def put(self):
        data = models.FlightInfo(**request.get_json()).save()
        return data.to_json()

    @api.marshal_with(api.models.get('flight_info'), skip_none=True)
    def patch(self):
        return models.FlightInfo.set(**request.get_json()).to_json()


@api.route("/flight_info/<flight_info_id>")
class BaseFlightInfoController(Resource):
    @api.marshal_with(api.models.get("flight_info"), skip_none=True)
    def get(self, flight_info_id):
        return models.FlightInfo.objects.get(id=flight_info_id)

    def delete(self, flight_info_id):
        return models.FlightInfo.get(id=flight_info_id).delete()


@api.route("/flight_info/base")
class BaseFlightInfoController(Resource):

    @api.marshal_list_with(api.models.get('flight_info_reference'))
    def get(self):
        return [x.to_json(False) for x in models.FlightInfo.get(**request.args)]

@api.route("/host_family")
class HostFamilyController(Resource):

    @api.marshal_list_with(api.models.get('host_family'), skip_none=True)
    def get(self):
        return models.HostFamily.fetch(request.args)

    @api.marshal_with(api.models.get('host_family'), skip_none=True)
    def post(self):
        return models.HostFamily(**request.get_json()).to_json()

    @api.marshal_with(api.models.get('host_family'), skip_none=True)
    def put(self):
        data = models.HostFamily(**request.get_json()).save()
        return data.to_json()

    @api.marshal_with(api.models.get('host_family'), skip_none=True)
    def patch(self):
        return models.HostFamily.set(**request.get_json()).to_json()


@api.route("/host_family/<host_family_id>")
class BaseHostFamilyController(Resource):
    @api.marshal_with(api.models.get("host_family"), skip_none=True)
    def get(self, host_family_id):
        return models.HostFamily.objects.get(id=host_family_id)

    def delete(self, host_family_id):
        return models.HostFamily.get(id=host_family_id).delete()


@api.route("/host_family/base")
class BaseHostFamilyController(Resource):

    @api.marshal_list_with(api.models.get('host_family_reference'))
    def get(self):
        return [x.to_json(False) for x in models.HostFamily.get(**request.args)]

@api.route("/account")
class AccountController(Resource):

    @api.marshal_list_with(api.models.get('account'), skip_none=True)
    def get(self):
        return models.Account.fetch(request.args)

    @api.marshal_with(api.models.get('account'), skip_none=True)
    def post(self):
        return models.Account(**request.get_json()).to_json()

    @api.marshal_with(api.models.get('account'), skip_none=True)
    def put(self):
        data = models.Account(**request.get_json()).save()
        return data.to_json()

    @api.marshal_with(api.models.get('account'), skip_none=True)
    def patch(self):
        return models.Account.set(**request.get_json()).to_json()


@api.route("/account/<account_id>")
class BaseAccountController(Resource):
    @api.marshal_with(api.models.get("account"), skip_none=True)
    def get(self, account_id):
        return models.Account.objects.get(id=account_id)

    def delete(self, account_id):
        return models.Account.get(id=account_id).delete()


@api.route("/account/base")
class BaseAccountController(Resource):

    @api.marshal_list_with(api.models.get('account_reference'))
    def get(self):
        return [x.to_json(False) for x in models.Account.get(**request.args)]

@api.route("/student_personal_data")
class StudentPersonalDataController(Resource):

    @api.marshal_list_with(api.models.get('student_personal_data'), skip_none=True)
    def get(self):
        return models.StudentPersonalData.fetch(request.args)

    @api.marshal_with(api.models.get('student_personal_data'), skip_none=True)
    def post(self):
        return models.StudentPersonalData(**request.get_json()).to_json()

    @api.marshal_with(api.models.get('student_personal_data'), skip_none=True)
    def put(self):
        data = models.StudentPersonalData(**request.get_json()).save()
        return data.to_json()

    @api.marshal_with(api.models.get('student_personal_data'), skip_none=True)
    def patch(self):
        return models.StudentPersonalData.set(**request.get_json()).to_json()


@api.route("/student_personal_data/<student_personal_data_id>")
class BaseStudentPersonalDataController(Resource):
    @api.marshal_with(api.models.get("student_personal_data"), skip_none=True)
    def get(self, student_personal_data_id):
        return models.StudentPersonalData.objects.get(id=student_personal_data_id)

    def delete(self, student_personal_data_id):
        return models.StudentPersonalData.get(id=student_personal_data_id).delete()


@api.route("/student_personal_data/base")
class BaseStudentPersonalDataController(Resource):

    @api.marshal_list_with(api.models.get('student_personal_data_reference'))
    def get(self):
        return [x.to_json(False) for x in models.StudentPersonalData.get(**request.args)]


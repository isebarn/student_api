# Standard library imports
import os
from datetime import datetime
from requests import post
from requests import get

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

        if request.method == "POST":
            json = request.get_json()

            for key, value in json.items():
                if isinstance(value, dict) and key in routes:
                    if "id" in value:
                        json[key] = value["id"]

                    else:
                        item = post(
                            "http://localhost:5000/api/{}".format(key), json=value
                        )
                        json[key] = item.json()["id"]

        for method in self.dispatch_requests:
            method(self, args, kwargs)

        return super(Resource, self).dispatch_request(*args, **kwargs)

api = Namespace("api", description="")
airport_base = api.model('airport_base', models.Airport.base())
airport_reference = api.model('airport_reference', models.Airport.reference())
airport_full = api.model('airport', models.Airport.model(api))
flight_base = api.model('flight_base', models.Flight.base())
flight_reference = api.model('flight_reference', models.Flight.reference())
flight_full = api.model('flight', models.Flight.model(api))
flight_info_base = api.model('flight_info_base', models.FlightInfo.base())
flight_info_reference = api.model('flight_info_reference', models.FlightInfo.reference())
flight_info_full = api.model('flight_info', models.FlightInfo.model(api))
child_base = api.model('child_base', models.Child.base())
child_reference = api.model('child_reference', models.Child.reference())
child_full = api.model('child', models.Child.model(api))
pet_base = api.model('pet_base', models.Pet.base())
pet_reference = api.model('pet_reference', models.Pet.reference())
pet_full = api.model('pet', models.Pet.model(api))
host_parent_base = api.model('host_parent_base', models.HostParent.base())
host_parent_reference = api.model('host_parent_reference', models.HostParent.reference())
host_parent_full = api.model('host_parent', models.HostParent.model(api))
address_base = api.model('address_base', models.Address.base())
address_reference = api.model('address_reference', models.Address.reference())
address_full = api.model('address', models.Address.model(api))
phone_base = api.model('phone_base', models.Phone.base())
phone_reference = api.model('phone_reference', models.Phone.reference())
phone_full = api.model('phone', models.Phone.model(api))
school_base = api.model('school_base', models.School.base())
school_reference = api.model('school_reference', models.School.reference())
school_full = api.model('school', models.School.model(api))
host_family_base = api.model('host_family_base', models.HostFamily.base())
host_family_reference = api.model('host_family_reference', models.HostFamily.reference())
host_family_full = api.model('host_family', models.HostFamily.model(api))
account_base = api.model('account_base', models.Account.base())
account_reference = api.model('account_reference', models.Account.reference())
account_full = api.model('account', models.Account.model(api))
parent_base = api.model('parent_base', models.Parent.base())
parent_reference = api.model('parent_reference', models.Parent.reference())
parent_full = api.model('parent', models.Parent.model(api))
program_base = api.model('program_base', models.Program.base())
program_reference = api.model('program_reference', models.Program.reference())
program_full = api.model('program', models.Program.model(api))
student_profile_base = api.model('student_profile_base', models.StudentProfile.base())
student_profile_reference = api.model('student_profile_reference', models.StudentProfile.reference())
student_profile_full = api.model('student_profile', models.StudentProfile.model(api))
student_personal_data_base = api.model('student_personal_data_base', models.StudentPersonalData.base())
student_personal_data_reference = api.model('student_personal_data_reference', models.StudentPersonalData.reference())
student_personal_data_full = api.model('student_personal_data', models.StudentPersonalData.model(api))


@api.route("/program")
class ProgramController(Resource):

    # @api.marshal_list_with(api.models.get('program'), skip_none=True)
    def get(self):
        return models.Program.fetch(request.args)

    # @api.marshal_with(api.models.get('program'), skip_none=True)
    def post(self):
        return models.Program.post(request.get_json())

    # @api.marshal_with(api.models.get('program'), skip_none=True)
    def put(self):
        return models.Program.put(request.get_json())

    # @api.marshal_with(api.models.get('program'), skip_none=True)
    def patch(self):
        return models.Program.patch(request.get_json())


@api.route("/program/<program_id>")
class BaseProgramController(Resource):
    # @api.marshal_with(api.models.get("program"), skip_none=True)
    def get(self, program_id):
        return models.Program.objects.get(id=program_id).to_json()

    def delete(self, program_id):
        return models.Program.get(id=program_id).delete()

@api.route("/student_profile")
class StudentProfileController(Resource):

    # @api.marshal_list_with(api.models.get('student_profile'), skip_none=True)
    def get(self):
        return models.StudentProfile.fetch(request.args)

    # @api.marshal_with(api.models.get('student_profile'), skip_none=True)
    def post(self):
        return models.StudentProfile.post(request.get_json())

    # @api.marshal_with(api.models.get('student_profile'), skip_none=True)
    def put(self):
        return models.StudentProfile.put(request.get_json())

    # @api.marshal_with(api.models.get('student_profile'), skip_none=True)
    def patch(self):
        return models.StudentProfile.patch(request.get_json())


@api.route("/student_profile/<student_profile_id>")
class BaseStudentProfileController(Resource):
    # @api.marshal_with(api.models.get("student_profile"), skip_none=True)
    def get(self, student_profile_id):
        return models.StudentProfile.objects.get(id=student_profile_id).to_json()

    def delete(self, student_profile_id):
        return models.StudentProfile.get(id=student_profile_id).delete()

@api.route("/student_personal_data")
class StudentPersonalDataController(Resource):

    # @api.marshal_list_with(api.models.get('student_personal_data'), skip_none=True)
    def get(self):
        return models.StudentPersonalData.fetch(request.args)

    # @api.marshal_with(api.models.get('student_personal_data'), skip_none=True)
    def post(self):
        return models.StudentPersonalData.post(request.get_json())

    # @api.marshal_with(api.models.get('student_personal_data'), skip_none=True)
    def put(self):
        return models.StudentPersonalData.put(request.get_json())

    # @api.marshal_with(api.models.get('student_personal_data'), skip_none=True)
    def patch(self):
        return models.StudentPersonalData.patch(request.get_json())


@api.route("/student_personal_data/<student_personal_data_id>")
class BaseStudentPersonalDataController(Resource):
    # @api.marshal_with(api.models.get("student_personal_data"), skip_none=True)
    def get(self, student_personal_data_id):
        return models.StudentPersonalData.objects.get(id=student_personal_data_id).to_json()

    def delete(self, student_personal_data_id):
        return models.StudentPersonalData.get(id=student_personal_data_id).delete()



routes = list(set([x.urls[0].split('/')[1] for x in api.resources]))
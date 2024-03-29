# Standard library imports
from json import loads
from json import load
from os import _exists
from os import environ
from datetime import datetime

# Third party imports
from bson import json_util
from bson.objectid import ObjectId
from mongoengine import connect
from mongoengine import Document
from mongoengine import ReferenceField
from mongoengine import DictField
from mongoengine import ListField
from mongoengine import MapField
from mongoengine import EmbeddedDocument as _EmbeddedDocument
from mongoengine import EmbeddedDocumentField
from mongoengine import EmbeddedDocumentListField
from mongoengine import DictField
from mongoengine import signals
from mongoengine import NULLIFY
from mongoengine import DateTimeField as _DateTimeField
from mongoengine import FloatField as _FloatField
from mongoengine import IntField as _IntField
from mongoengine import BooleanField as _BooleanField
from mongoengine import StringField as _StringField
from flask_restx.fields import DateTime
from flask_restx.fields import Float
from flask_restx.fields import Integer
from flask_restx.fields import List
from flask_restx.fields import Nested
from flask_restx.fields import String
from flask_restx.fields import Boolean
from flask_restx.fields import Raw


class DateTimeField(_DateTimeField):
    class ISOFormat(DateTime):
        def format(self, value):
            try:
                if isinstance(value, datetime):
                    return value.isoformat()
                return value.get("$date")
            except ValueError as ve:
                raise MarshallingError(ve)

    marshal = ISOFormat


class ImageField(_StringField):
    class AWSImage(String):
        def format(self, value):
            try:
                return get_presigned_url(value)
            except ValueError as ve:
                raise MarshallingError(ve)

    marshal = AWSImage


class FloatField(_FloatField):
    marshal = Float


class IntField(_IntField):
    marshal = Integer


class BooleanField(_BooleanField):
    marshal = Boolean


class StringField(_StringField):
    marshal = String


user = environ.get("username", "root")
password = environ.get("password", "root")
host = environ.get("host", "127.0.0.1")
database_name = environ.get("DB_NAME", "data")

if _exists("rds-combined-ca-bundle.pem"):
    db = connect(
        database_name,
        username=user,
        password=password,
        host=host,
        retryWrites=False,
        ssl_ca_certs="rds-combined-ca-bundle.pem",
    )

else:
    db = connect(
        database_name,
        username=user,
        password=password,
        host=host,
        authentication_source="admin",
    )


def convert(value):
    return ObjectId(value) if ObjectId.is_valid(value) else value


class Extended(Document):
    meta = {"abstract": True, "allow_inheritance": True}

    @classmethod
    def fix_data(cls, key, value):
        if isinstance(value, list):
            return [cls.fix_data(key, x) for x in value]

        if isinstance(value, str):
            return convert(value)
        elif isinstance(value, dict):
            if "id" in value:
                return convert(value["id"])
            elif isinstance(getattr(cls, key), EmbeddedDocumentField):
                return getattr(cls, key).document_type_obj(**value)
            elif isinstance(getattr(cls, key), EmbeddedDocumentListField):
                return getattr(cls, key).field.document_type_obj(**value)

        else:
            return value

    def to_json(self):
        def f(v):
            if isinstance(v, dict) and "$oid" in v:
                return v["$oid"]

            elif isinstance(v, dict) and "$date" in v:
                return v["$date"]
            elif isinstance(v, list):
                return list(map(lambda x: f(x), v))
            else:
                return v

        data = {**{k: f(v) for k, v in loads(json_util.dumps(self.to_mongo())).items()}}
        data.update({"id": data.pop("_id")})

        return data

    @classmethod
    def post(cls, data):
        item = cls(**data)
        item.save()
        return item.to_json()

    @classmethod
    def put(cls, data):
        item = cls.objects.get(id=data.pop("id"))

        [delattr(item, k) for k, v in cls._fields.items() if k not in ["_cls", "id"]]
        for key, value in data.items():
            setattr(item, key, cls.fix_data(key, value))

        item.save()

        return item.to_json()

    @classmethod
    def patch(cls, data):
        item = cls.objects.get(id=data.pop("id"))

        for key, value in data.items():
            setattr(item, key, cls.fix_data(key, value))

        item.save()

        return item.to_json()

    @classmethod
    def get(cls, *args, **kwargs):
        def recursively_query(model, fields, search, root=False):

            if fields == "id__in":
                return {fields: search}

            if "__" not in fields:
                if root:
                    return {fields: search}

                return [x.id for x in model.objects(**{fields: search})]

            prop, fields = fields.split("__", 1)

            result = recursively_query(
                model._fields[prop].field.document_type_obj
                if isinstance(model._fields[prop], ListField)
                else model._fields[prop].document_type_obj,
                fields,
                search,
            )

            if not root:
                return [x.id for x in model.objects(**{"{}__in".format(prop): result})]
            else:
                return {"{}__in".format(prop): result}

        filters = {}
        for query, search in kwargs.items():

            if query.startswith("$"):
                continue

            elif query.split("__")[0] not in cls._reference_fields():
                filters.update({query: search})

            else:
                filters.update(
                    {
                        key: list(set(value) & set(filters.get(key, value)))
                        if isinstance(value, list)
                        else value
                        for key, value in recursively_query(
                            cls, query, search, True
                        ).items()
                    }
                )

        return (
            cls.objects(**filters)
            .skip(int(kwargs.get("$skip", 0)))
            .limit(int(kwargs.get("$limit", 0)))
        )

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        if kwargs.get("created"):
            pass

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        if (
            document.to_json().get("_id")
            and next(cls.objects(id=document.id)).status is not document.status
        ):
            pass

    @classmethod
    def base(cls):
        return {
            **{
                key: getattr(cls, key).marshal
                for key, value in list(cls._fields.items())
                if hasattr(getattr(cls, key), "marshal")
            },
            "id": String(),
        }

    @classmethod
    def reference(cls):
        return {
            **cls.base(),
            **{
                field: String()
                for field, instance in cls._fields.items()
                if isinstance(instance, ReferenceField)
            },
        }

    @classmethod
    def model(cls, api):
        return {
            **cls.base(),
            **{
                field: Nested(api.models.get(field), skip_none=True)
                for field, instance in cls._fields.items()
                if isinstance(instance, ReferenceField)
                or isinstance(instance, DictField)
                or isinstance(instance, EmbeddedDocumentField)
            },
            **{
                field: List(
                    Nested(
                        api.models.get(field),
                        skip_none=True,
                    ),
                )
                for field, instance in cls._fields.items()
                if isinstance(instance, ListField)
            },
        }

    @classmethod
    def _reference_fields(cls):
        return {
            key: value
            for key, value in cls._fields.items()
            if isinstance(value, ReferenceField)
        }

    @classmethod
    def _list_reference_fields(cls):
        return {
            key: value
            for key, value in cls._fields.items()
            if isinstance(value, ListField)
            and isinstance(cls._fields[key].field, ReferenceField)
        }

    @classmethod
    def fetch(cls, filters):
        include = filters.pop("$include", "").split(",")
        data = [x.to_json() for x in list(cls.get(**filters))]

        for key, value in cls._list_reference_fields().items():
            if key in include:
                id_lists = list(map(lambda x: x[key], data))
                ids = list(set([item for sublist in id_lists for item in sublist]))

                values = value.field.document_type_obj.fetch(
                    {
                        "$include": ",".join(
                            [
                                x.replace("{}__".format(key), "")
                                for x in include
                                if x.startswith(key)
                            ]
                        ),
                        "id__in": ids,
                    },
                )

                values = {x["id"]: x for x in values}

                for item in data:
                    item.update({key: [values[x] for x in item[key]]})

            else:
                for item in data:
                    item.update({key: [{"id": x} for x in item[key]]})

        for key, value in cls._reference_fields().items():
            if key in include:
                ids = [x.get(key) for x in data if key in x]
                values = value.document_type_obj.fetch(
                    {
                        "$include": ",".join(
                            [
                                x.replace("{}__".format(key), "")
                                for x in include
                                if x.startswith(key)
                            ]
                        ),
                        "id__in": ids,
                    },
                )

                values = {x["id"]: x for x in values}

                for item in data:
                    if key in item and item[key] in values:
                        item[key] = values[item[key]]

            else:
                list(
                    map(
                        lambda x: x.update(
                            {key: ({"id": x.get(key)} if key in x else None)}
                        ),
                        data,
                    )
                )

        return data


class EmbeddedDocument(_EmbeddedDocument):
    meta = {"abstract": True, "allow_inheritance": True}

    @classmethod
    def base(cls):
        return {
            **{
                key: getattr(cls, key).marshal
                for key, value in list(cls._fields.items())
                if hasattr(getattr(cls, key), "marshal")
            }
        }

    @classmethod
    def reference(cls):
        return {
            **cls.base(),
        }

    @classmethod
    def model(cls, api):
        return {
            **cls.base(),
        }


class Airport(EmbeddedDocument):
    name = StringField()
    code = StringField()


class Flight(EmbeddedDocument):
    date = DateTimeField()
    time = StringField()
    flight_number = StringField()
    airline = StringField()


class FlightInfo(EmbeddedDocument):
    airport = EmbeddedDocumentField(Airport)
    depart_flight = EmbeddedDocumentField(Flight)
    return_flight = EmbeddedDocumentField(Flight)


class Child(EmbeddedDocument):
    name = StringField()
    gender = StringField()


class Pet(EmbeddedDocument):
    name = StringField()
    type = StringField()
    inside = BooleanField(default=False)


class HostParent(EmbeddedDocument):
    first_name = StringField()
    last_name = StringField()
    age = IntField()
    occupation = StringField()
    email = StringField()
    phone = StringField()


class Address(EmbeddedDocument):
    line_1 = StringField()
    line_2 = StringField()
    city = StringField()
    postal_code = StringField()
    country = StringField()


class Phone(EmbeddedDocument):
    extension = StringField()
    number = StringField()


class School(EmbeddedDocument):
    name = StringField()
    contact = StringField()
    email = StringField()
    address = EmbeddedDocumentField(Address)
    phone = StringField()
    url = StringField()


class HostFamily(EmbeddedDocument):
    number = StringField()
    family_name = StringField()
    hobbies_activities = StringField()
    father = EmbeddedDocumentField(HostParent)
    mother = EmbeddedDocumentField(HostParent)
    address = EmbeddedDocumentField(Address)
    phone = EmbeddedDocumentField(Phone)
    child = EmbeddedDocumentListField(Child)
    pet = EmbeddedDocumentListField(Pet)
    smoking = BooleanField(default=False)
    profile_link = StringField()
    airport = EmbeddedDocumentField(Airport)
    distance_from_school = StringField()
    bank_details = StringField()


class Account(EmbeddedDocument):
    diet = FloatField()
    region = FloatField()
    other_reason = StringField()
    other = FloatField()
    credits_reason = StringField()
    credits = FloatField()
    deposit = FloatField()
    second_installment = FloatField()
    third_installment = FloatField()
    final_installment = FloatField()


class Parent(EmbeddedDocument):
    first_name = StringField()
    last_name = StringField()
    email = StringField()
    address = EmbeddedDocumentField(Address)


class Program(Extended):
    country = StringField()
    description = StringField()
    code = StringField()
    program_price = FloatField()
    price = FloatField()


class StudentProfile(Extended):
    first_name = StringField()
    last_name = StringField()
    age_on_arrival = IntField()
    gender = StringField()
    email = StringField()
    nationality = StringField()
    hobbies_interests = StringField()
    length_of_stay = StringField()
    passport_country = StringField()
    passport_number = StringField()
    mother_name = StringField()
    father_name = StringField()
    language = StringField()
    region_requested = StringField()
    letter = StringField()
    description = StringField()
    imagine = StringField()
    submitted = BooleanField(default=False)
    can_live_with_animals = BooleanField(default=False)
    why_cannot_live_with_animals = StringField()
    interview = DateTimeField()
    special_dietary_needs = BooleanField(default=False)
    what_special_dietary_needs = StringField()
    subjects = StringField()
    present_class = StringField()
    what_do_when_leave_school = StringField()
    allergies = IntField()
    allergies_explain = StringField()
    eating_disorder = BooleanField(default=False)
    what_eating_disorder = StringField()
    medication = BooleanField(default=False)
    what_medication = StringField()
    family_school_medical_issues = BooleanField(default=False)
    what_family_school_medical_issues = StringField()
    agreement_study = BooleanField(default=False)
    agreement_rural = BooleanField(default=False)
    agreement_another_student = BooleanField(default=False)
    agreement_contact_school = BooleanField(default=False)
    agreement_cannot_change_family = BooleanField(default=False)
    agreement_change_family_region = BooleanField(default=False)
    agreement_town_of_placement = BooleanField(default=False)
    agreement_borrow_lend_money = BooleanField(default=False)
    agreement_unauthorized_visits = BooleanField(default=False)
    program = ReferenceField(Program, reverse_delete_rule=NULLIFY)


class StudentPersonalData(Extended):
    allergies = StringField()
    average_grades = StringField()
    date_of_application = DateTimeField()
    date_of_birth = DateTimeField()
    nationality = StringField()
    school_name = StringField()
    school_type = StringField()
    student_profile = ReferenceField(StudentProfile, reverse_delete_rule=NULLIFY)
    account = EmbeddedDocumentField(Account)
    address = EmbeddedDocumentField(Address)
    airport = EmbeddedDocumentField(Airport)
    host_airport = EmbeddedDocumentField(Airport)
    flight_info = EmbeddedDocumentField(FlightInfo)
    father = EmbeddedDocumentField(Parent)
    mother = EmbeddedDocumentField(Parent)
    host_family = EmbeddedDocumentField(HostFamily)
    phone = EmbeddedDocumentField(Phone)
    host_school = EmbeddedDocumentField(School)



# def config():
    # signals.pre_save.connect(Class.pre_save, sender=Class)
    # signals.post_save.connect(Class.post_save, sender=Class)

    # seed
    # logging.info("Seeding database")
    # seed = load(open("models/seed.json"))

    # helper method to remove "_id" and "_cls" so I can compare json objects
    # from the db
    # def remove_meta_from_dict_item(item):
    #     item.pop("_cls")
    #     item.pop("_id")
    #     for key, value in item.items():
    #         if isinstance(value, dict):
    #             remove_meta_from_dict_item(value)


# config()
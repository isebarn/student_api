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
from mongoengine import ListField
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
                return datetime.fromtimestamp(value.get("$date") / 1e3).isoformat()
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


class Extended(Document):
    meta = {"abstract": True, "allow_inheritance": True}

    def __init__(self, *args, **kwargs):
        if "id" in kwargs:
            super(Document, self).__init__(*args, **kwargs)

        else:  # Create new document and recursively create or link to existing ReferenceField docs
            super(Document, self).__init__(
                *args, **{k: v for k, v in kwargs.items() if not isinstance(v, dict)}
            )
            for key, value in self._fields.items():
                if isinstance(value, ReferenceField) and key in kwargs:
                    # link to existing
                    if isinstance(kwargs[key], Document):
                        setattr(self, key, kwargs[key])

                    # pass entire object
                    elif "_id" in kwargs[key]:
                        setattr(
                            self,
                            key,
                            value.document_type_obj.objects.get(id=kwargs[key]["_id"]),
                        )

                    # pass ObjectId string of object
                    elif ObjectId.is_valid(kwargs.get(key, "")):
                        setattr(
                            self,
                            key,
                            value.document_type_obj.objects.get(id=kwargs[key]),
                        )

                    # create new ReferenceField
                    else:
                        setattr(
                            self,
                            key,
                            value.document_type_obj(**{key: {"_id": kwargs[key]}}),
                        )

                # special for Raw fields that are wildcards
                elif isinstance(value, DictField) and isinstance(kwargs.get(key), dict):
                    setattr(self, key, kwargs.get(key))

            self.save()

    def to_json(self):
        def f(v):
            if isinstance(v, dict) and "$oid" in v:
                return v["$oid"]
            elif isinstance(v, list):
                return list(map(lambda x: f(x), v))
            else:
                return v

        return {**{k: f(v) for k, v in loads(json_util.dumps(self.to_mongo())).items()}}

    @classmethod
    def set(cls, *args, **kwargs):
        _id = kwargs.pop("id")
        item = cls.objects.get(id=_id)

        # ???
        for key, value in kwargs.items():
            if isinstance(value, list) and any(value):
                string_object_ids = [x.get("_id", {}).get("$oid") for x in value]
                if all(map(lambda x: ObjectId.is_valid(x), string_object_ids)):
                    value = [ObjectId(x) for x in string_object_ids]

        cls.objects(id=_id).update_one(
            **{
                key.replace("$", "")
                if key.startswith("$")
                else "set__{}".format(key): (
                    ObjectId(value) if ObjectId.is_valid(value) else value
                )
                for key, value in kwargs.items()
            }
        )

        return cls.objects.get(id=_id)

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
            "_id": String(),
        }

    @classmethod
    def reference(cls):
        return {
            **cls.base(),
            **{
                field: String(attribute=lambda x: x["_id"])
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
            },
            **{
                field: List(
                    Nested(
                        api.models.get(
                            instance.field.document_type_obj._class_name.lower()
                        ),
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
                values = {x["_id"]: x for x in values}

                for item in data:
                    item.update({key: [values[x] for x in item[key]]})

            else:
                for item in data:
                    item.update({key: [{"_id": x} for x in item[key]]})

        for key, value in cls._reference_fields().items():
            if key in include:
                ids = list(map(lambda x: x[key], data))
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
                values = {x["_id"]: x for x in values}

                list(map(lambda x: x.update({key: values[x[key]]}), data))

            else:
                list(map(lambda x: x.update({key: {"_id": x[key]}}), data))

        return data


class Program(Extended):
    country = StringField()
    description = StringField()
    code = StringField()
    program_price = FloatField()
    price = FloatField()


class AirportCode(Extended):
    airport = StringField()
    code = StringField()


class HostFamily(Extended):
    number = IntField()
    first_name = StringField()
    last_name = StringField()
    address_line_1 = StringField()
    address_line_2 = StringField()
    address_city = StringField()
    address_postal_code = StringField()
    address_country = StringField()
    email = StringField()
    phone_extension = StringField()
    phone_number = StringField()
    airport_code = ReferenceField(AirportCode, reverse_delete_rule=NULLIFY)
    profile_link = StringField()


class Account(Extended):
    program = ReferenceField(Program, reverse_delete_rule=NULLIFY)
    deposit_prog = FloatField()
    second_installment = FloatField()
    third_installment = FloatField()
    final_installment = FloatField()
    total_prog = FloatField()
    credit_1 = FloatField()
    credit_2 = FloatField()
    formula = StringField()
    deposit_paid = FloatField()
    second_installment_paid = FloatField()
    third_installment_paid = FloatField()
    final_installment_paid = FloatField()
    balance_owed = FloatField()


class StudentPersonalData(Extended):
    first_name = StringField()
    last_name = StringField()
    gender = StringField()
    program = ReferenceField(Program, reverse_delete_rule=NULLIFY)
    airport_code = ReferenceField(AirportCode, reverse_delete_rule=NULLIFY)
    date_of_application = DateTimeField()
    date_of_birth = DateTimeField()
    address_line_1 = StringField()
    address_line_2 = StringField()
    address_city = StringField()
    address_postal_code = StringField()
    address_country = StringField()
    phone_extension = StringField()
    phone_number = StringField()
    nationality = StringField()
    school_name = StringField()
    school_type = StringField()
    average_grades = StringField()



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
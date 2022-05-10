from extensions.aws_cognito import client
from extensions.aws_cognito import pool_id
from extensions.aws_cognito import client_id
from extensions.aws_cognito import schema_attributes


def authenticate(username=None, password=None, session=None, refresh=None):
    if session:
        client.respond_to_auth_challenge(
            ClientId=client_id,
            ChallengeName="NEW_PASSWORD_REQUIRED",
            Session=session,
            ChallengeResponses={
                "USERNAME": username,
                "NEW_PASSWORD": password,
            },
        )

    if refresh:
        return client.initiate_auth(
            ClientId=client_id,
            AuthFlow="REFRESH_TOKEN",
            AuthParameters={
                "REFRESH_TOKEN": refresh,
            },
        )

    return client.initiate_auth(
        ClientId=client_id,
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={
            "USERNAME": username,
            "PASSWORD": password,
        },
    )


def user(access_token):
    return client.get_user(AccessToken=access_token)


# def sign_up(username, password, email, user_type):
#     return client.sign_up(
#         ClientId=client_id,
#         Username=username,
#         Password=password,
#         UserAttributes=[
#             {"Name": "email", "Value": email},
#             {"Name": "custom:user_type", "Value": user_type},
#         ],
#         ClientMetadata={"String": "string"},
#     )


def admin_add_user_to_group(*args, **kwargs):
    return client.admin_add_user_to_group(
        UserPoolId=pool_id, Username=kwargs["username"], GroupName=kwargs["group"]
    )


def admin_create_user(*args, **kwargs):
    return {
        y["Name"].replace("custom:", ""): y["Value"]
        for y in client.admin_create_user(
            UserPoolId=pool_id,
            Username=kwargs["email"],
            UserAttributes=[
                {"Name": "custom:{}".format(name), "Value": value}
                for name, value in kwargs.items()
                if name != "email"
            ]
            + [
                {"Name": "email", "Value": kwargs["email"]},
                {"Name": "email_verified", "Value": "true"},
            ],
            ForceAliasCreation=False,
            DesiredDeliveryMediums=[
                "EMAIL",
            ],
        )["User"]["Attributes"]
    }


def admin_update_user_attributes(user_id, **kwargs):
    return client.admin_update_user_attributes(
        UserPoolId=pool_id,
        Username=user_id,
        UserAttributes=[
            {"Name": "custom:{}".format(key), "Value": val}
            for key, val in kwargs.items()
        ],
    )


def list_users():
    return [
        {y["Name"].replace("custom:", ""): y["Value"] for y in x["Attributes"]}
        for x in client.list_users(
            UserPoolId=pool_id,
        )["Users"]
    ]


def admin_get_user(user_id):
    return {
        x["Name"].replace("custom:", ""): x["Value"]
        for x in client.admin_get_user(UserPoolId=pool_id, Username=user_id)[
            "UserAttributes"
        ]
    }


def forgot_password(username):
    return client.forgot_password(Username=username, ClientId=client_id)


def set_user_password(username, password):
    return client.admin_set_user_password(
        UserPoolId=pool_id, Username=username, Password=password, Permanent=True
    )


# def change_password(old, new, token):
#     return client.change_password(
#         PreviousPassword=old, ProposedPassword=new, AccessToken=token
#     )


def disable_user(username):
    return client.admin_disable_user(UserPoolId=pool_id, Username=username)


def enable_user(username):
    return client.admin_enable_user(UserPoolId=pool_id, Username=username)


def delete_user(username):
    return (
        client.admin_delete_user(UserPoolId=pool_id, Username=username)
        if os.environ.get("FLASK_ENV") == "development"
        else False
    )

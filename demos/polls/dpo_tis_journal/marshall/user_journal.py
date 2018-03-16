from marshmallow import Schema, fields


class UserJournalSchema(Schema):
    dtime = fields.DateTime()
    action = fields.String()
    user_name = fields.String()

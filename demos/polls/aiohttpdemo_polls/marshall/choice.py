from marshmallow import Schema, fields


class ChoiceSchema(Schema):
    id = fields.Integer()
    choice_text = fields.String()
    votes = fields.Integer()
    question_id = fields.Integer()

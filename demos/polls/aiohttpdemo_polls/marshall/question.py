from marshmallow import Schema, fields


class QuestionSchema(Schema):
    id = fields.Integer()
    question_text = fields.String()
    pub_date = fields.Date()

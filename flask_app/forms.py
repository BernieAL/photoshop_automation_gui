from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,IntegerField
from wtforms.validators import DataRequired


class IntakeForm(FlaskForm):
    token = StringField('Token', validators=[DataRequired()])
    bp_id = IntegerField('BP_ID',validators=[DataRequired()])
    submit = SubmitField('Submit')
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,IntegerField
from wtforms.validators import DataRequired


class IntakeForm(FlaskForm):
    token = StringField('Token', validators=[DataRequired()])
    bp_id = IntegerField('BP_ID',validators=[DataRequired()])
    submit = SubmitField('Submit')
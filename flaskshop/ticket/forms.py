from flask_babel import lazy_gettext
from flask_wtf import FlaskForm as _FlaskForm
from flask_wtf.file import FileSize, FileAllowed
from wtforms import (
    BooleanField,
    DateTimeField,
    DateField,
    DecimalField,
    FieldList,
    FileField,
    MultipleFileField,
    FloatField,
    IntegerField,
    PasswordField,
    RadioField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Regexp, optional

from flaskshop.constant import Permission, SettingValueType
from flaskshop.dashboard.views import FlaskForm


class TicketEntryForm(FlaskForm):
    entry_date = StringField(lazy_gettext("Date"), validators=[DataRequired()])
    tide = RadioField(
        lazy_gettext("AM or PM"),
        choices=[
            (0, lazy_gettext("AM")),
            (1, lazy_gettext("PM")),
        ],
    )
    submit = SubmitField(lazy_gettext("Submit"))

class TicketForm(FlaskForm):
    landing = StringField(lazy_gettext("Landing #"), validators=[DataRequired()])
    weight = IntegerField(lazy_gettext("Weight"), default=0)    
    permit = RadioField(
        lazy_gettext("Select Permit"),
        choices=[
            (0, lazy_gettext("Colt - 60021C")),
            (1, lazy_gettext("Adisen - 59866L")),
            (2, lazy_gettext("Jed - 61279W")),
        ],
        default=0,
    )
    landing_time = DateTimeField(lazy_gettext("Landing Time"))
    ticket_notes = TextAreaField(lazy_gettext("Notes"))
    submit = SubmitField(lazy_gettext("Submit"))   
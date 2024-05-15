from wtforms import widgets, StringField, SubmitField, TextAreaField, PasswordField, BooleanField, SelectField, SelectMultipleField, ValidationError
from wtforms.validators import DataRequired, Length, regexp, EqualTo
from flask_wtf import FlaskForm

def validate_min_tags(form, field):
    if len(field.data) < 1:
        raise ValidationError('At least one tag must be selected.')

def validate_max_tags(form, field):
    if len(field.data) > 6:
        raise ValidationError('No more than 6 tags can be selected.')
    
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

class QuestionForm(FlaskForm):
    title = StringField('Question', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Post')
    tags = MultiCheckboxField('Tags', validators=[DataRequired(), validate_min_tags, validate_max_tags])

    def set_choices(self, choices):
        self.tags.choices = [(choice, choice) for choice in choices]

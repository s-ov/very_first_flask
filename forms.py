from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email()])
    psw = PasswordField("Password: ",
                        validators=[DataRequired("Невірний email"),
                                    Length(min=4, max=100, message="4-100 chars!")])
    remember = BooleanField("Remember me", default=False)
    submit = SubmitField("Enter")


class RegisterForm(FlaskForm):
    name = StringField("Name: ",
                       validators=[Length(min=4, max=100, message="4-100 chars!")])
    email = StringField("Email: ",
                        validators=[Email("Incorrect email")])
    psw = PasswordField("Password: ",
                        validators=[DataRequired(),
                                    Length(min=4, max=100, message="4-100 chars!")])
    psw2 = PasswordField("Password again: ",
                         validators=[DataRequired(),
                                     EqualTo('psw', message="Паролі не співпадають")])
    submit = SubmitField("Реєстрація")

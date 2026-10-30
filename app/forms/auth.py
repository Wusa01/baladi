from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):

    username = StringField(
        "اسم المستخدم أو البريد الإلكتروني",
        validators=[
            DataRequired(message="هذا الحقل مطلوب."),
            Length(max=120),
        ],
    )

    password = PasswordField(
        "كلمة المرور",
        validators=[
            DataRequired(message="كلمة المرور مطلوبة."),
        ],
    )

    remember_me = BooleanField("تذكرني")

    submit = SubmitField("تسجيل الدخول")

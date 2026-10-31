from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
)


class ReportForm(FlaskForm):

    title = StringField(
        "عنوان المشكلة",
        validators=[
            DataRequired(message="يرجى كتابة عنوان المشكلة."),
            Length(max=200),
        ],
    )

    description = TextAreaField(
        "وصف المشكلة",
        validators=[
            DataRequired(message="يرجى وصف المشكلة."),
            Length(min=10, max=10000),
        ],
    )

    category_id = SelectField(
        "تصنيف المشكلة",
        coerce=int,
        validators=[
            DataRequired(message="يرجى اختيار التصنيف."),
        ],
    )

    language = SelectField(
        "لغة البلاغ",
        choices=[
            ("ar", "العربية"),
            ("fr", "Français"),
        ],
        default="ar",
        validators=[DataRequired()],
    )

    neighborhood = StringField(
        "الحي",
        validators=[
            Optional(),
            Length(max=150),
        ],
    )

    reporter_name = StringField(
        "اسمك (اختياري)",
        validators=[
            Optional(),
            Length(max=120),
        ],
    )

    reporter_phone = StringField(
        "رقم الهاتف (اختياري)",
        validators=[
            Optional(),
            Length(max=30),
        ],
    )

    reporter_email = StringField(
        "البريد الإلكتروني (اختياري)",
        validators=[
            Optional(),
            Length(max=120),
        ],
    )

    submit = SubmitField("إرسال البلاغ")

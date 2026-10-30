from datetime import datetime, timezone
from urllib.parse import urlsplit

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    current_user,
    login_user,
    logout_user,
)
from sqlalchemy import or_

from app.extensions import db, limiter
from app.forms.auth import LoginForm
from app.models import User


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def is_safe_redirect_url(target):
    if not target:
        return False

    parsed = urlsplit(target)

    return (
        not parsed.scheme
        and not parsed.netloc
        and target.startswith("/")
        and not target.startswith("//")
    )


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():

    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():

        identity = form.username.data.strip()

        user = User.query.filter(
            or_(
                User.username == identity,
                User.email == identity,
            )
        ).first()

        if user and user.is_active and user.check_password(
            form.password.data
        ):

            login_user(
                user,
                remember=form.remember_me.data,
            )

            user.last_login_at = datetime.now(timezone.utc)
            db.session.commit()

            flash("تم تسجيل الدخول بنجاح.", "success")

            next_page = request.args.get("next")

            if is_safe_redirect_url(next_page):
                return redirect(next_page)

            return redirect(url_for("main.index"))

        flash(
            "بيانات تسجيل الدخول غير صحيحة أو الحساب غير نشط.",
            "danger",
        )

    return render_template(
        "auth/login.html",
        form=form,
    )


@auth_bp.route("/logout", methods=["POST"])
def logout():

    if current_user.is_authenticated:
        logout_user()
        flash("تم تسجيل الخروج.", "success")

    return redirect(url_for("main.index"))

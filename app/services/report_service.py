import secrets
from datetime import datetime, timezone

from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

from app.extensions import db
from app.models import Category, Report


class ReportServiceError(Exception):
    pass


def generate_reference_number():
    date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
    random_part = secrets.token_hex(4).upper()

    return f"BLD-{date_part}-{random_part}"


def create_report(
    title,
    description,
    category_id,
    language="ar",
    neighborhood=None,
    exact_latitude=None,
    exact_longitude=None,
    reporter_name=None,
    reporter_phone=None,
    reporter_email=None,
):
    if not title or not title.strip():
        raise ReportServiceError("عنوان البلاغ مطلوب.")

    if not description or not description.strip():
        raise ReportServiceError("وصف البلاغ مطلوب.")

    if language not in ("ar", "fr"):
        raise ReportServiceError("لغة البلاغ غير مدعومة.")

    category = db.session.get(Category, category_id)

    if category is None or not category.is_active:
        raise ReportServiceError("التصنيف غير موجود أو غير فعال.")

    if (exact_latitude is None) != (exact_longitude is None):
        raise ReportServiceError(
            "يجب إدخال إحداثيي الموقع معاً."
        )

    tracking_token = secrets.token_urlsafe(32)

    report = Report(
        reference_number=generate_reference_number(),
        title=title.strip(),
        description=description.strip(),
        category_id=category.id,
        language=language,
        neighborhood=neighborhood,
        exact_latitude=exact_latitude,
        exact_longitude=exact_longitude,
        reporter_name=reporter_name,
        reporter_phone=reporter_phone,
        reporter_email=reporter_email,
        tracking_token_hash=generate_password_hash(
            tracking_token
        ),
        status=Report.STATUS_SUBMITTED,
        is_public=False,
    )

    try:
        db.session.add(report)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return report, tracking_token


def verify_tracking_token(reference_number, tracking_token):
    report = Report.query.filter_by(
        reference_number=reference_number
    ).first()

    if report is None:
        return None

    if not check_password_hash(
        report.tracking_token_hash,
        tracking_token
    ):
        return None

    return report

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    render_template,
)

from app.extensions import db
from app.forms.report import ReportForm
from app.models import Category
from app.services.report_service import (
    ReportServiceError,
    create_report,
)


main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@main_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "success",
        "application": "Baladi",
        "message": "Baladi API is running",
    }), 200


@main_bp.route("/reports/new", methods=["GET", "POST"])
def new_report():

    form = ReportForm()

    categories = Category.query.filter_by(
        is_active=True
    ).order_by(
        Category.sort_order.asc(),
        Category.id.asc(),
    ).all()

    form.category_id.choices = [
        (0, "اختر تصنيف المشكلة"),
    ] + [
        (category.id, category.name_ar)
        for category in categories
    ]

    if form.validate_on_submit():

        try:
            report, tracking_token = create_report(
                title=form.title.data,
                description=form.description.data,
                category_id=form.category_id.data,
                language=form.language.data,
                neighborhood=form.neighborhood.data,
                reporter_name=form.reporter_name.data,
                reporter_phone=form.reporter_phone.data,
                reporter_email=form.reporter_email.data,
            )

            response = current_app.make_response(
                render_template(
                    "reports/receipt.html",
                    receipt={
                        "reference_number": report.reference_number,
                        "tracking_token": tracking_token,
                    },
                )
            )

            response.headers["Cache-Control"] = "no-store"
            response.headers["Pragma"] = "no-cache"

            return response

        except ReportServiceError as error:
            flash(str(error), "danger")

        except Exception:
            db.session.rollback()

            current_app.logger.exception(
                "Unexpected error while creating a report."
            )

            flash(
                "تعذر إرسال البلاغ حالياً. يرجى المحاولة لاحقاً.",
                "danger",
            )

    return render_template(
        "reports/new.html",
        form=form,
    )

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user

from app.extensions import db
from app.models import Report, User
from app.services.status_service import (
    ALLOWED_TRANSITIONS,
    REVIEWER_TRANSITIONS,
    StatusTransitionError,
    change_report_status,
)
from app.utils.permissions import reviewer_required


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
)


STATUS_LABELS = {
    Report.STATUS_SUBMITTED: "جديد",
    Report.STATUS_UNDER_REVIEW: "قيد المراجعة",
    Report.STATUS_VERIFIED: "تم التحقق",
    Report.STATUS_PUBLISHED: "منشور",
    Report.STATUS_REFERRED: "تمت الإحالة",
    Report.STATUS_IN_PROGRESS: "قيد المعالجة",
    Report.STATUS_RESOLVED: "تم الحل",
    Report.STATUS_CLOSED: "مغلق",
    Report.STATUS_REJECTED: "مرفوض",
    Report.STATUS_DUPLICATE: "بلاغ مكرر",
}


STATUS_CLASSES = {
    Report.STATUS_SUBMITTED: "bg-primary",
    Report.STATUS_UNDER_REVIEW: "bg-warning text-dark",
    Report.STATUS_VERIFIED: "bg-info text-dark",
    Report.STATUS_PUBLISHED: "bg-success",
    Report.STATUS_REFERRED: "bg-secondary",
    Report.STATUS_IN_PROGRESS: "bg-warning text-dark",
    Report.STATUS_RESOLVED: "bg-success",
    Report.STATUS_CLOSED: "bg-dark",
    Report.STATUS_REJECTED: "bg-danger",
    Report.STATUS_DUPLICATE: "bg-secondary",
}


@admin_bp.route("/")
@reviewer_required
def dashboard():

    total_reports = Report.query.count()

    submitted_reports = Report.query.filter_by(
        status=Report.STATUS_SUBMITTED
    ).count()

    under_review_reports = Report.query.filter_by(
        status=Report.STATUS_UNDER_REVIEW
    ).count()

    published_reports = Report.query.filter_by(
        status=Report.STATUS_PUBLISHED
    ).count()

    rejected_reports = Report.query.filter_by(
        status=Report.STATUS_REJECTED
    ).count()

    recent_reports = Report.query.order_by(
        Report.submitted_at.desc()
    ).limit(10).all()

    return render_template(
        "admin/dashboard.html",
        total_reports=total_reports,
        submitted_reports=submitted_reports,
        under_review_reports=under_review_reports,
        published_reports=published_reports,
        rejected_reports=rejected_reports,
        recent_reports=recent_reports,
        status_labels=STATUS_LABELS,
        status_classes=STATUS_CLASSES,
    )


@admin_bp.route("/reports")
@reviewer_required
def reports():

    statuses = list(STATUS_LABELS.keys())
    status = request.args.get("status", "")

    query = Report.query

    if status in statuses:
        query = query.filter_by(status=status)

    reports = query.order_by(
        Report.submitted_at.desc()
    ).paginate(
        page=request.args.get("page", 1, type=int),
        per_page=20,
        error_out=False,
    )

    return render_template(
        "admin/reports.html",
        reports=reports,
        selected_status=status,
        statuses=statuses,
        status_labels=STATUS_LABELS,
        status_classes=STATUS_CLASSES,
    )


@admin_bp.route("/reports/<int:report_id>")
@reviewer_required
def report_detail(report_id):

    report = Report.query.get_or_404(report_id)

    available_transitions = ALLOWED_TRANSITIONS.get(
        report.status,
        set(),
    )

    if current_user.role == User.ROLE_REVIEWER:
        available_transitions = (
            available_transitions
            & REVIEWER_TRANSITIONS.get(report.status, set())
        )

    available_transitions = sorted(available_transitions)

    return render_template(
        "admin/report_detail.html",
        report=report,
        status_labels=STATUS_LABELS,
        status_classes=STATUS_CLASSES,
        available_transitions=available_transitions,
    )


@admin_bp.route(
    "/reports/<int:report_id>/status",
    methods=["POST"],
)
@reviewer_required
def update_report_status(report_id):

    new_status = request.form.get("new_status", "").strip()
    note = request.form.get("note", "").strip()

    try:
        change_report_status(
            report_id=report_id,
            new_status=new_status,
            changed_by_id=current_user.id,
            note=note or None,
        )

        flash("تم تحديث حالة البلاغ بنجاح.", "success")

    except StatusTransitionError as error:
        flash(str(error), "danger")

    except Exception:
        db.session.rollback()
        flash("حدث خطأ أثناء تحديث البلاغ.", "danger")

    return redirect(
        url_for(
            "admin.report_detail",
            report_id=report_id,
        )
    )

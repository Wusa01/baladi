from datetime import datetime, timezone

from app.extensions import db


class ReportStatusHistory(db.Model):

    __tablename__ = "report_status_history"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    report_id = db.Column(
        db.Integer,
        db.ForeignKey("reports.id"),
        nullable=False,
        index=True
    )

    old_status = db.Column(
        db.String(30),
        nullable=True
    )

    new_status = db.Column(
        db.String(30),
        nullable=False
    )

    changed_by_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    note = db.Column(
        db.Text,
        nullable=True
    )

    is_public = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )

    report = db.relationship(
        "Report",
        backref=db.backref(
            "status_history",
            lazy="dynamic",
            order_by="ReportStatusHistory.created_at"
        )
    )

    changed_by = db.relationship(
        "User",
        foreign_keys=[changed_by_id]
    )

    def __repr__(self):
        return (
            f"<ReportStatusHistory "
            f"{self.report_id}: {self.old_status} -> {self.new_status}>"
        )

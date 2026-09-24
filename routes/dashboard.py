"""
User dashboard routes + analytics JSON API.
"""

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user

from models import db
from models.user import User
from models.scan import (
    WebsiteScan, JobScan, EmailScan, WhatsAppScan, QRScan, PaymentScan,
    ProductScan, ClaimScan,
)
from models.report import ScamReport

dashboard_bp = Blueprint("dashboard", __name__)

SCAN_MODELS = (
    WebsiteScan, JobScan, EmailScan, WhatsAppScan, QRScan, PaymentScan,
    ProductScan, ClaimScan,
)


def _counts():
    """Return platform-wide counters for the dashboard."""
    return {
        "total_scans": sum(m.query.count() for m in SCAN_MODELS),
        "dangerous_scans": sum(
            m.query.filter_by(status="dangerous").count() for m in SCAN_MODELS
        ),
        "safe_scans": sum(
            m.query.filter_by(status="safe").count() for m in SCAN_MODELS
        ),
        "scam_reports": ScamReport.query.count(),
        "total_reports": ScamReport.query.count(),
        "users": User.query.count(),
    }


@dashboard_bp.route("/dashboard")
@login_required
def index():
    counts = _counts()
    recent_scans = []
    models_config = (
        (WebsiteScan, "Website", lambda s: s.url),
        (JobScan, "Job", lambda s: s.company_name or s.job_title),
        (EmailScan, "Email", lambda s: s.email_content),
        (WhatsAppScan, "WhatsApp", lambda s: s.scam_type or s.extracted_text),
        (QRScan, "QR Code", lambda s: s.decoded_url),
        (PaymentScan, "Payment", lambda s: s.screenshot_path),
        (ProductScan, "Product", lambda s: s.product_name),
        (ClaimScan, "Claim", lambda s: s.claim_text),
    )
    for model_cls, label, target_fn in models_config:
        for item in model_cls.query.order_by(model_cls.created_at.desc()).limit(5).all():
            target_val = target_fn(item) or "-"
            recent_scans.append({
                "type": label,
                "target": str(target_val)[:40],
                "trust_score": item.trust_score,
                "status": item.status,
                "created_at": item.created_at,
            })
    recent_scans = sorted(recent_scans, key=lambda s: s["created_at"], reverse=True)[:8]
    # Reports belonging to this user: submitted while signed in, or submitted
    # anonymously with their email address.
    my_reports = (
        ScamReport.query
        .outerjoin(ScamReport.user)
        .filter(
            db.or_(
                ScamReport.user_id == current_user.id,
                ScamReport.reporter_email == current_user.email,
            )
        )
        .order_by(ScamReport.created_at.desc())
        .all()
    )

    # Count unviewed replies for notifications without mutating them on GET.
    new_updates = sum(
        1 for report in my_reports for reply in report.replies if not reply.is_viewed
    )

    return render_template(
        "dashboard.html",
        counts=counts,
        recent_scans=recent_scans,
        my_reports=my_reports,
        new_updates=new_updates,
        user=current_user,
    )


@dashboard_bp.route("/api/reports/<int:report_id>/mark-viewed", methods=["POST"])
@login_required
def mark_report_viewed(report_id):
    report = ScamReport.query.filter_by(id=report_id, user_id=current_user.id).first()
    if report:
        for reply in report.replies:
            reply.is_viewed = True
        db.session.commit()
    return jsonify({"success": True})


@dashboard_bp.route("/api/dashboard-stats")
@login_required
def stats():
    """JSON statistics consumed by dashboard charts."""
    return jsonify({"success": True, **_counts()})

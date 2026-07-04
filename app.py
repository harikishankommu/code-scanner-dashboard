from fastapi import FastAPI, Request, UploadFile, File, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse

from scanner import run_all_scans, count_by_severity
from database import create_table, save_scan, get_scan_history, clear_scan_history

import csv
import json
from io import StringIO, BytesIO
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

create_table()


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".py"}
MAX_UPLOAD_SIZE = 2 * 1024 * 1024  # 2 MB


LATEST_SCAN = {
    "scan_target": "No scan yet",
    "issues": []
}


def calculate_risk_score(counts):
    raw_score = (
        counts["critical"] * 10
        + counts["high"] * 7
        + counts["medium"] * 4
        + counts["low"] * 1
    )

    risk_score = min(raw_score, 100)

    if risk_score >= 80:
        risk_status = "Critical Risk"
        risk_class = "critical-risk"
    elif risk_score >= 50:
        risk_status = "High Risk"
        risk_class = "high-risk"
    elif risk_score >= 20:
        risk_status = "Medium Risk"
        risk_class = "medium-risk"
    elif risk_score > 0:
        risk_status = "Low Risk"
        risk_class = "low-risk"
    else:
        risk_status = "Clean"
        risk_class = "clean-risk"

    return risk_score, risk_status, risk_class


def add_priority_to_issues(issues):
    for issue in issues:
        severity = issue.get("severity", "UNKNOWN").upper()

        if severity == "CRITICAL":
            issue["priority"] = "P0"
        elif severity == "HIGH":
            issue["priority"] = "P1"
        elif severity == "MEDIUM":
            issue["priority"] = "P2"
        elif severity == "LOW":
            issue["priority"] = "P3"
        else:
            issue["priority"] = "P4"

    return issues


def build_dashboard_context(
    issues,
    scan_target,
    alert_message=None,
    alert_type="info"
):
    issues = add_priority_to_issues(issues)
    counts = count_by_severity(issues)
    history = get_scan_history()
    risk_score, risk_status, risk_class = calculate_risk_score(counts)

    return {
        "total_scans": len(history),
        "critical": counts["critical"],
        "high": counts["high"],
        "medium": counts["medium"],
        "low": counts["low"],
        "risk_score": risk_score,
        "risk_status": risk_status,
        "risk_class": risk_class,
        "issues": issues,
        "history": history,
        "scan_target": scan_target,
        "alert_message": alert_message,
        "alert_type": alert_type,
    }


@app.get("/")
def home(request: Request):
    context = build_dashboard_context([], "No scan yet")

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context=context,
    )


@app.get("/scan")
def scan_project(request: Request):
    scan_target = "sample_project"

    issues = run_all_scans(scan_target)
    issues = add_priority_to_issues(issues)

    counts = count_by_severity(issues)
    save_scan(len(issues), counts)

    LATEST_SCAN["scan_target"] = scan_target
    LATEST_SCAN["issues"] = issues

    context = build_dashboard_context(
        issues,
        scan_target,
        "Sample project scanned successfully.",
        "success"
    )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context=context,
    )


@app.post("/upload")
def upload_and_scan(request: Request, file: UploadFile = File(...)):
    original_filename = Path(file.filename or "").name
    extension = Path(original_filename).suffix.lower()

    if not original_filename:
        context = build_dashboard_context(
            [],
            "No scan yet",
            "No file selected.",
            "error"
        )

        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context=context,
        )

    if extension not in ALLOWED_EXTENSIONS:
        context = build_dashboard_context(
            [],
            "No scan yet",
            "Only Python .py files are supported currently.",
            "error"
        )

        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context=context,
        )

    file_bytes = file.file.read()

    if len(file_bytes) > MAX_UPLOAD_SIZE:
        context = build_dashboard_context(
            [],
            original_filename,
            "File is too large. Maximum allowed size is 2 MB.",
            "error"
        )

        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context=context,
        )

    safe_filename = f"{uuid4().hex}_{original_filename}"
    uploaded_path = UPLOAD_DIR / safe_filename

    try:
        uploaded_path.write_bytes(file_bytes)

        issues = run_all_scans(str(uploaded_path))
        issues = add_priority_to_issues(issues)

        # Show original uploaded filename instead of internal UUID filename
        for issue in issues:
            issue["file"] = original_filename

        counts = count_by_severity(issues)
        save_scan(len(issues), counts)

        LATEST_SCAN["scan_target"] = original_filename
        LATEST_SCAN["issues"] = issues

        context = build_dashboard_context(
            issues,
            original_filename,
            f"{original_filename} scanned successfully. Uploaded file was deleted after scanning.",
            "success"
        )

        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context=context,
        )

    except Exception as error:
        context = build_dashboard_context(
            [],
            original_filename,
            f"Scan failed: {str(error)}",
            "error"
        )

        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context=context,
        )

    finally:
        if uploaded_path.exists():
            uploaded_path.unlink()


@app.get("/clear-history")
def clear_history(request: Request):
    clear_scan_history()

    LATEST_SCAN["scan_target"] = "No scan yet"
    LATEST_SCAN["issues"] = []

    context = build_dashboard_context(
        [],
        "No scan yet",
        "Scan history cleared successfully.",
        "success"
    )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context=context,
    )


def generate_report_data():
    issues = LATEST_SCAN.get("issues", [])
    scan_target = LATEST_SCAN.get("scan_target", "No scan yet")

    if not issues:
        scan_target = "sample_project"
        issues = run_all_scans(scan_target)

    issues = add_priority_to_issues(issues)
    counts = count_by_severity(issues)
    risk_score, risk_status, risk_class = calculate_risk_score(counts)

    report = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "scan_target": scan_target,
        "total_issues": len(issues),
        "risk_score": risk_score,
        "risk_status": risk_status,
        "severity_summary": {
            "critical": counts["critical"],
            "high": counts["high"],
            "medium": counts["medium"],
            "low": counts["low"],
        },
        "issues": issues,
    }

    return report


@app.get("/export")
@app.get("/export/csv")
def export_csv_report():
    report = generate_report_data()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["Secure Code Scanner Report"])
    writer.writerow(["Generated At", report["generated_at"]])
    writer.writerow(["Scan Target", report["scan_target"]])
    writer.writerow(["Total Issues", report["total_issues"]])
    writer.writerow(["Risk Score", report["risk_score"]])
    writer.writerow(["Risk Status", report["risk_status"]])
    writer.writerow([])

    writer.writerow(["Severity Summary"])
    writer.writerow(["Critical", report["severity_summary"]["critical"]])
    writer.writerow(["High", report["severity_summary"]["high"]])
    writer.writerow(["Medium", report["severity_summary"]["medium"]])
    writer.writerow(["Low", report["severity_summary"]["low"]])
    writer.writerow([])

    writer.writerow(["Tool", "Severity", "Priority", "File", "Line", "Issue"])

    for issue in report["issues"]:
        writer.writerow([
            issue.get("tool", "-"),
            issue.get("severity", "-"),
            issue.get("priority", "-"),
            issue.get("file", "-"),
            issue.get("line", "-"),
            issue.get("message", "-"),
        ])

    output.seek(0)

    filename = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        },
    )


@app.get("/export/json")
def export_json_report():
    report = generate_report_data()

    filename = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    json_data = json.dumps(report, indent=4)

    return Response(
        content=json_data,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        },
    )


@app.get("/export/pdf")
def export_pdf_report():
    report = generate_report_data()

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Secure Code Scanner Report", styles["Title"]))
    elements.append(Spacer(1, 14))

    summary_data = [
        ["Generated At", report["generated_at"]],
        ["Scan Target", report["scan_target"]],
        ["Total Issues", str(report["total_issues"])],
        ["Risk Score", str(report["risk_score"])],
        ["Risk Status", report["risk_status"]],
        ["Critical", str(report["severity_summary"]["critical"])],
        ["High", str(report["severity_summary"]["high"])],
        ["Medium", str(report["severity_summary"]["medium"])],
        ["Low", str(report["severity_summary"]["low"])],
    ]

    summary_table = Table(summary_data, colWidths=[140, 330])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eff6ff")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#111827")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Vulnerability Findings", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    findings_data = [["Tool", "Severity", "Priority", "File", "Line", "Issue"]]

    for issue in report["issues"]:
        findings_data.append([
            issue.get("tool", "-"),
            issue.get("severity", "-"),
            issue.get("priority", "-"),
            Paragraph(escape(str(issue.get("file", "-"))), styles["BodyText"]),
            str(issue.get("line", "-")),
            Paragraph(escape(str(issue.get("message", "-"))), styles["BodyText"]),
        ])

    findings_table = Table(
        findings_data,
        colWidths=[55, 65, 55, 105, 40, 190],
        repeatRows=1,
    )

    findings_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d1d5db")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    elements.append(findings_table)

    doc.build(elements)
    buffer.seek(0)

    filename = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        },
    )
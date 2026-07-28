"""
Report Generator for calculating adherence metrics and exporting CSV/HTML reports.
"""

import csv
from datetime import datetime
from typing import Dict, Any, List
from models.reminder import ReminderModel
from models.user import UserModel


class ReportGenerator:
    """Calculates adherence statistics and generates reports."""

    @classmethod
    def calculate_adherence_metrics(cls, user_id: int, start_date: str = "", end_date: str = "") -> Dict[str, Any]:
        """Calculates medicine adherence metrics for a user within an optional date range."""
        logs = ReminderModel.search_and_filter_logs(
            user_id=user_id,
            search_term="",
            status_filter="All",
            start_date=start_date,
            end_date=end_date
        )

        total = len(logs)
        taken = sum(1 for log in logs if log['status'] == 'Taken')
        missed = sum(1 for log in logs if log['status'] == 'Missed')
        pending = sum(1 for log in logs if log['status'] == 'Pending')

        completed_total = taken + missed
        if completed_total > 0:
            rate = (taken / completed_total) * 100.0
        else:
            rate = 100.0 if taken > 0 else 0.0

        return {
            "total_doses": total,
            "taken_doses": taken,
            "missed_doses": missed,
            "pending_doses": pending,
            "adherence_rate": round(rate, 1)
        }

    @classmethod
    def export_to_csv(cls, user_id: int, filepath: str, search_term: str = "",
                      status_filter: str = "All", start_date: str = "", end_date: str = "") -> bool:
        """Exports medicine reminder logs to CSV format."""
        try:
            logs = ReminderModel.search_and_filter_logs(
                user_id=user_id,
                search_term=search_term,
                status_filter=status_filter,
                start_date=start_date,
                end_date=end_date
            )

            with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                # Header row
                writer.writerow([
                    "Log ID", "Medicine Name", "Dosage", "Scheduled Date",
                    "Scheduled Time", "Status", "Marked At", "Notes"
                ])

                for log in logs:
                    writer.writerow([
                        log['log_id'],
                        log['medicine_name'],
                        log['dosage'],
                        log['scheduled_date'],
                        log['scheduled_time'],
                        log['status'],
                        log['marked_at'] or "-",
                        log['log_notes'] or log['med_notes'] or ""
                    ])
            return True
        except Exception as e:
            print(f"[Reporter] Error exporting CSV: {e}")
            return False

    @classmethod
    def generate_html_report(cls, user_id: int, filepath: str, search_term: str = "",
                             status_filter: str = "All", start_date: str = "", end_date: str = "") -> bool:
        """Generates a clean HTML report document."""
        try:
            user = UserModel.get_by_id(user_id)
            username = user['full_name'] or user['username'] if user else "User"
            metrics = cls.calculate_adherence_metrics(user_id, start_date, end_date)
            logs = ReminderModel.search_and_filter_logs(
                user_id=user_id,
                search_term=search_term,
                status_filter=status_filter,
                start_date=start_date,
                end_date=end_date
            )

            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Medicine Adherence Report - {username}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc; color: #1e293b; margin: 0; padding: 30px; }}
        .container {{ max-width: 900px; margin: 0 auto; background: #ffffff; border-radius: 12px; padding: 30px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
        .header {{ border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center; }}
        h1 {{ color: #0f766e; margin: 0; font-size: 24px; }}
        .meta {{ font-size: 13px; color: #64748b; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 30px; }}
        .stat-card {{ background: #f1f5f9; padding: 15px; border-radius: 8px; text-align: center; }}
        .stat-val {{ font-size: 22px; font-weight: bold; color: #0f172a; margin-top: 5px; }}
        .stat-label {{ font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }}
        .adherence {{ background: #ccfbf1; color: #0f766e; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th {{ background: #f8fafc; color: #475569; font-weight: 600; text-align: left; padding: 12px; border-bottom: 2px solid #e2e8f0; font-size: 13px; }}
        td {{ padding: 12px; border-bottom: 1px solid #f1f5f9; font-size: 13px; }}
        .badge {{ padding: 4px 8px; border-radius: 9999px; font-weight: 600; font-size: 11px; display: inline-block; }}
        .badge-taken {{ background: #dcfce7; color: #166534; }}
        .badge-missed {{ background: #fee2e2; color: #991b1b; }}
        .badge-pending {{ background: #fef3c7; color: #92400e; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>💊 Medicine Adherence & History Report</h1>
                <div class="meta">Patient / User: <strong>{username}</strong> | Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card adherence">
                <div class="stat-label">Adherence Rate</div>
                <div class="stat-val">{metrics['adherence_rate']}%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Taken</div>
                <div class="stat-val" style="color: #166534;">{metrics['taken_doses']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Missed</div>
                <div class="stat-val" style="color: #991b1b;">{metrics['missed_doses']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Pending Doses</div>
                <div class="stat-val" style="color: #92400e;">{metrics['pending_doses']}</div>
            </div>
        </div>

        <h2>Detailed Reminder Logs</h2>
        <table>
            <thead>
                <tr>
                    <th>Date & Time</th>
                    <th>Medicine Name</th>
                    <th>Dosage</th>
                    <th>Status</th>
                    <th>Action Timestamp</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>
"""

            for log in logs:
                st = log['status']
                badge_class = f"badge-{st.lower()}"
                html_content += f"""
                <tr>
                    <td>{log['scheduled_date']} {log['scheduled_time']}</td>
                    <td><strong>{log['medicine_name']}</strong></td>
                    <td>{log['dosage']}</td>
                    <td><span class="badge {badge_class}">{st}</span></td>
                    <td>{log['marked_at'] or '-'}</td>
                    <td>{log['log_notes'] or log['med_notes'] or '-'}</td>
                </tr>
"""

            html_content += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
            with open(filepath, mode="w", encoding="utf-8") as f:
                f.write(html_content)
            return True
        except Exception as e:
            print(f"[Reporter] Error generating HTML report: {e}")
            return False

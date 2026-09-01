import csv
import io
from flask import Blueprint, request, jsonify, Response
from app.services.aggregation_service import AggregationService
from app.models.event_model import EventModel
from app.services.serializers import serialize_events_list

export_bp = Blueprint("export_bp", __name__)

@export_bp.route("/api/export/csv", methods=["GET"])
def export_csv():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    export_type = request.args.get("type", default="traffic") # 'traffic' or 'events'

    output = io.StringIO()
    writer = csv.writer(output)

    if export_type == "events":
        # Raw events export
        writer.writerow(["ID", "Event Name", "Session ID", "User ID", "URL Path", "Referrer", "Device", "Browser", "OS", "Country", "Timestamp"])
        where_clause, params = AggregationService._build_date_filter(start_date, end_date)
        from app.db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT id, event_name, session_id, user_id, url_path, referrer, device_type, browser, os, country, created_at
            FROM events
            {where_clause}
            ORDER BY created_at DESC, id DESC
            LIMIT 5000
        """, params)
        for row in cursor.fetchall():
            writer.writerow([row["id"], row["event_name"], row["session_id"], row["user_id"] or "", row["url_path"], row["referrer"] or "", row["device_type"], row["browser"], row["os"], row["country"], row["created_at"]])
        conn.close()
    else:
        # Default: Daily traffic time-series export
        writer.writerow(["Date Bucket", "Pageviews", "Total Events", "Unique Visitors"])
        timeseries = AggregationService.get_timeseries_traffic(start_date=start_date, end_date=end_date, interval="day")
        for row in timeseries:
            writer.writerow([row["bucket"], row["pageviews"], row["total_events"], row["unique_visitors"]])

    csv_data = output.getvalue()
    output.close()

    filename = f"analytics_export_{export_type}.csv"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@export_bp.route("/api/export/json", methods=["GET"])
def export_json():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    overview = AggregationService.get_overview_metrics(start_date=start_date, end_date=end_date)
    timeseries = AggregationService.get_timeseries_traffic(start_date=start_date, end_date=end_date, interval="day")
    breakdowns = AggregationService.get_breakdowns(start_date=start_date, end_date=end_date)
    top_pages = AggregationService.get_top_pages(start_date=start_date, end_date=end_date, limit=20)

    return jsonify({
        "timeframe": {
            "start_date": start_date or "All Time",
            "end_date": end_date or "All Time"
        },
        "overview": overview,
        "timeseries": timeseries,
        "breakdowns": breakdowns,
        "top_pages": top_pages
    }), 200

from flask import Blueprint, request, jsonify
from app.services.aggregation_service import AggregationService

analytics_bp = Blueprint("analytics_bp", __name__)

@analytics_bp.route("/api/analytics/overview", methods=["GET"])
def get_overview():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    metrics = AggregationService.get_overview_metrics(start_date=start_date, end_date=end_date)
    return jsonify({
        "timeframe": {
            "start_date": start_date or "All Time",
            "end_date": end_date or "All Time"
        },
        "metrics": metrics
    }), 200

@analytics_bp.route("/api/analytics/timeseries", methods=["GET"])
def get_timeseries():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    interval = request.args.get("interval", default="day")

    if interval not in ["hour", "day", "month"]:
        interval = "day"

    timeseries_data = AggregationService.get_timeseries_traffic(
        start_date=start_date,
        end_date=end_date,
        interval=interval
    )
    return jsonify({
        "interval": interval,
        "count": len(timeseries_data),
        "data": timeseries_data
    }), 200

@analytics_bp.route("/api/analytics/breakdown", methods=["GET"])
def get_breakdowns():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    breakdowns = AggregationService.get_breakdowns(start_date=start_date, end_date=end_date)
    return jsonify(breakdowns), 200

@analytics_bp.route("/api/analytics/top-pages", methods=["GET"])
def get_top_pages():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    limit = request.args.get("limit", default=10, type=int)
    limit = min(max(limit, 1), 100)

    top_pages = AggregationService.get_top_pages(
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    return jsonify({
        "limit": limit,
        "count": len(top_pages),
        "pages": top_pages
    }), 200

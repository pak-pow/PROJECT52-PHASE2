import sqlite3
from datetime import datetime, timedelta
from app.db import get_db_connection

class AggregationService:
    @classmethod
    def get_overview_metrics(cls, start_date: str = None, end_date: str = None) -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Date range filtering clauses
        where_clause, params = cls._build_date_filter(start_date, end_date)

        # 1. Total Pageviews & Total Events
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total_events,
                COUNT(CASE WHEN event_name = 'pageview' THEN 1 END) as pageviews,
                COUNT(DISTINCT session_id) as unique_visitors,
                COUNT(DISTINCT user_id) as unique_users
            FROM events
            {where_clause}
        """, params)
        primary_stats = dict(cursor.fetchone() or {})

        # 2. Bounce Rate Calculation (Sessions with exactly 1 event)
        cursor.execute(f"""
            SELECT COUNT(*) as single_event_sessions
            FROM (
                SELECT session_id, COUNT(*) as event_count
                FROM events
                {where_clause}
                GROUP BY session_id
                HAVING event_count = 1
            )
        """, params)
        single_event_sessions = cursor.fetchone()["single_event_sessions"]

        total_sessions = primary_stats.get("unique_visitors", 0)
        bounce_rate = round((single_event_sessions / total_sessions * 100), 2) if total_sessions > 0 else 0.0

        # 3. Average Pageviews Per Session
        total_pageviews = primary_stats.get("pageviews", 0)
        avg_views_per_session = round((total_pageviews / total_sessions), 2) if total_sessions > 0 else 0.0

        # 4. Previous Period Comparison Delta
        delta = cls._calculate_period_delta(cursor, start_date, end_date, total_pageviews, total_sessions)

        conn.close()

        return {
            "total_events": primary_stats.get("total_events", 0),
            "pageviews": total_pageviews,
            "unique_visitors": total_sessions,
            "unique_users": primary_stats.get("unique_users", 0),
            "bounce_rate_pct": bounce_rate,
            "avg_views_per_session": avg_views_per_session,
            "growth_deltas": delta
        }

    @classmethod
    def get_timeseries_traffic(cls, start_date: str = None, end_date: str = None, interval: str = "day") -> list:
        conn = get_db_connection()
        cursor = conn.cursor()

        where_clause, params = cls._build_date_filter(start_date, end_date)

        # SQLite strftime format string
        if interval == "hour":
            date_fmt = "%Y-%m-%d %H:00:00"
        elif interval == "month":
            date_fmt = "%Y-%m-01"
        else: # default: day
            date_fmt = "%Y-%m-%d"

        cursor.execute(f"""
            SELECT 
                strftime('{date_fmt}', created_at) as bucket,
                COUNT(CASE WHEN event_name = 'pageview' THEN 1 END) as pageviews,
                COUNT(*) as total_events,
                COUNT(DISTINCT session_id) as unique_visitors
            FROM events
            {where_clause}
            GROUP BY bucket
            ORDER BY bucket ASC
        """, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(r) for r in rows]

    @classmethod
    def get_breakdowns(cls, start_date: str = None, end_date: str = None) -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()

        where_clause, params = cls._build_date_filter(start_date, end_date)

        def _get_distribution(column_name: str, limit: int = 10) -> list:
            cursor.execute(f"""
                SELECT 
                    COALESCE({column_name}, 'Unknown') as label,
                    COUNT(*) as count
                FROM events
                {where_clause}
                GROUP BY label
                ORDER BY count DESC
                LIMIT ?
            """, params + [limit])
            rows = cursor.fetchall()
            total = sum(r["count"] for r in rows)
            return [
                {
                    "label": r["label"],
                    "count": r["count"],
                    "percentage": round((r["count"] / total * 100), 2) if total > 0 else 0.0
                }
                for r in rows
            ]

        devices = _get_distribution("device_type")
        browsers = _get_distribution("browser")
        os_list = _get_distribution("os")
        countries = _get_distribution("country")
        referrers = _get_distribution("referrer")

        conn.close()

        return {
            "devices": devices,
            "browsers": browsers,
            "operating_systems": os_list,
            "countries": countries,
            "referrers": referrers
        }

    @classmethod
    def get_top_pages(cls, start_date: str = None, end_date: str = None, limit: int = 10) -> list:
        conn = get_db_connection()
        cursor = conn.cursor()

        where_clause, params = cls._build_date_filter(start_date, end_date)

        cursor.execute(f"""
            SELECT 
                url_path,
                COUNT(*) as views,
                COUNT(DISTINCT session_id) as unique_visitors
            FROM events
            {where_clause}
            GROUP BY url_path
            ORDER BY views DESC
            LIMIT ?
        """, params + [limit])
        rows = cursor.fetchall()
        conn.close()

        total_views = sum(r["views"] for r in rows)
        return [
            {
                "url_path": r["url_path"],
                "views": r["views"],
                "unique_visitors": r["unique_visitors"],
                "share_pct": round((r["views"] / total_views * 100), 2) if total_views > 0 else 0.0
            }
            for r in rows
        ]

    @staticmethod
    def _build_date_filter(start_date: str = None, end_date: str = None) -> tuple:
        conditions = []
        params = []
        if start_date:
            conditions.append("created_at >= ?")
            params.append(start_date if len(start_date) > 10 else f"{start_date} 00:00:00")
        if end_date:
            conditions.append("created_at <= ?")
            params.append(end_date if len(end_date) > 10 else f"{end_date} 23:59:59")
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        return where_clause, params

    @staticmethod
    def _calculate_period_delta(cursor, start_date: str, end_date: str, current_views: int, current_sessions: int) -> dict:
        if not start_date or not end_date:
            return {"pageviews_delta_pct": 0.0, "visitors_delta_pct": 0.0}

        try:
            d_start = datetime.strptime(start_date[:10], "%Y-%m-%d")
            d_end = datetime.strptime(end_date[:10], "%Y-%m-%d")
            duration = (d_end - d_start).days + 1

            prev_end = d_start - timedelta(days=1)
            prev_start = prev_end - timedelta(days=duration - 1)

            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN event_name = 'pageview' THEN 1 END) as prev_pageviews,
                    COUNT(DISTINCT session_id) as prev_visitors
                FROM events
                WHERE created_at >= ? AND created_at <= ?
            """, (f"{prev_start.strftime('%Y-%m-%d')} 00:00:00", f"{prev_end.strftime('%Y-%m-%d')} 23:59:59"))
            prev_stats = cursor.fetchone()

            prev_views = prev_stats["prev_pageviews"] if prev_stats else 0
            prev_visitors = prev_stats["prev_visitors"] if prev_stats else 0

            views_delta = round(((current_views - prev_views) / prev_views * 100), 2) if prev_views > 0 else 0.0
            visitors_delta = round(((current_sessions - prev_visitors) / prev_visitors * 100), 2) if prev_visitors > 0 else 0.0

            return {
                "pageviews_delta_pct": views_delta,
                "visitors_delta_pct": visitors_delta,
                "previous_pageviews": prev_views,
                "previous_visitors": prev_visitors
            }
        except Exception:
            return {"pageviews_delta_pct": 0.0, "visitors_delta_pct": 0.0}

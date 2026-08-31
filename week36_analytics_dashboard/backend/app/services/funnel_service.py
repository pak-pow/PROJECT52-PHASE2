from app.db import get_db_connection
from app.models.funnel_model import FunnelModel
from app.services.aggregation_service import AggregationService

class FunnelService:
    @classmethod
    def calculate_funnel_metrics(cls, funnel_id: int, start_date: str = None, end_date: str = None) -> dict:
        funnel = FunnelModel.get_by_id(funnel_id)
        if not funnel:
            return None

        steps = funnel.get("steps", [])
        if not steps:
            return {
                "funnel_id": funnel["id"],
                "name": funnel["name"],
                "description": funnel["description"],
                "total_steps": 0,
                "overall_conversion_pct": 0.0,
                "steps_analysis": []
            }

        conn = get_db_connection()
        cursor = conn.cursor()

        where_clause, params = AggregationService._build_date_filter(start_date, end_date)
        if where_clause:
            where_event_clause = f"{where_clause} AND event_name = ?"
        else:
            where_event_clause = "WHERE event_name = ?"

        # Track surviving session IDs through each sequential stage
        current_step_sessions = None
        steps_analysis = []
        initial_visitors_count = 0

        for idx, step in enumerate(steps):
            event_name = step["event_name"]
            
            if idx == 0:
                # First step: all distinct sessions that completed the first event
                cursor.execute(f"""
                    SELECT DISTINCT session_id
                    FROM events
                    {where_event_clause}
                """, params + [event_name])
                rows = cursor.fetchall()
                current_step_sessions = set(r["session_id"] for r in rows)
                initial_visitors_count = len(current_step_sessions)
                visitors_reached = initial_visitors_count
                step_conversion_pct = 100.0 if initial_visitors_count > 0 else 0.0
                drop_off_count = 0
                drop_off_pct = 0.0
            else:
                if not current_step_sessions:
                    visitors_reached = 0
                    step_conversion_pct = 0.0
                    drop_off_count = steps_analysis[-1]["visitors_reached"]
                    drop_off_pct = 100.0 if drop_off_count > 0 else 0.0
                else:
                    # Sequential matching: sessions from previous step that also did this event
                    placeholders = ",".join("?" for _ in current_step_sessions)
                    query = f"""
                        SELECT DISTINCT session_id
                        FROM events
                        {where_event_clause}
                        AND session_id IN ({placeholders})
                    """
                    cursor.execute(query, params + [event_name] + list(current_step_sessions))
                    rows = cursor.fetchall()
                    survived_sessions = set(r["session_id"] for r in rows)
                    
                    prev_count = steps_analysis[-1]["visitors_reached"]
                    visitors_reached = len(survived_sessions)
                    step_conversion_pct = round((visitors_reached / prev_count * 100), 2) if prev_count > 0 else 0.0
                    drop_off_count = prev_count - visitors_reached
                    drop_off_pct = round((drop_off_count / prev_count * 100), 2) if prev_count > 0 else 0.0
                    
                    current_step_sessions = survived_sessions

            steps_analysis.append({
                "step_order": step["step_order"],
                "step_name": step["step_name"],
                "event_name": step["event_name"],
                "visitors_reached": visitors_reached,
                "step_conversion_pct": step_conversion_pct,
                "drop_off_count": drop_off_count,
                "drop_off_pct": drop_off_pct,
                "overall_conversion_pct": round((visitors_reached / initial_visitors_count * 100), 2) if initial_visitors_count > 0 else 0.0
            })

        conn.close()

        final_reached = steps_analysis[-1]["visitors_reached"] if steps_analysis else 0
        overall_conversion = round((final_reached / initial_visitors_count * 100), 2) if initial_visitors_count > 0 else 0.0

        return {
            "funnel_id": funnel["id"],
            "name": funnel["name"],
            "description": funnel["description"],
            "total_steps": len(steps),
            "initial_visitors": initial_visitors_count,
            "final_conversions": final_reached,
            "overall_conversion_pct": overall_conversion,
            "steps_analysis": steps_analysis
        }

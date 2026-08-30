import json

def serialize_event(event_dict: dict) -> dict:
    if not event_dict:
        return {}
    res = dict(event_dict)
    if "metadata_json" in res and res["metadata_json"]:
        try:
            res["metadata"] = json.loads(res["metadata_json"])
        except Exception:
            res["metadata"] = {}
    else:
        res["metadata"] = {}
    res.pop("metadata_json", None)
    return res

def serialize_events_list(events_list: list) -> list:
    return [serialize_event(e) for e in events_list] if events_list else []

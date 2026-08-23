import json

def serialize_notification(notif_dict: dict) -> dict:
    if not notif_dict:
        return {}
    
    variables = {}
    if notif_dict.get("variables_json"):
        try:
            variables = json.loads(notif_dict["variables_json"])
        except Exception:
            variables = {}

    return {
        "id": notif_dict.get("id"),
        "idempotency_key": notif_dict.get("idempotency_key"),
        "user_id": notif_dict.get("user_id"),
        "recipient": notif_dict.get("recipient"),
        "channel": notif_dict.get("channel"),
        "template_name": notif_dict.get("template_name"),
        "subject": notif_dict.get("subject"),
        "content": notif_dict.get("content"),
        "variables": variables,
        "status": notif_dict.get("status"),
        "attempts": notif_dict.get("attempts", 0),
        "error_message": notif_dict.get("error_message"),
        "created_at": str(notif_dict.get("created_at")),
        "sent_at": str(notif_dict.get("sent_at")) if notif_dict.get("sent_at") else None
    }

def serialize_template(tmpl_dict: dict) -> dict:
    if not tmpl_dict:
        return {}
    return {
        "id": tmpl_dict.get("id"),
        "name": tmpl_dict.get("name"),
        "channel": tmpl_dict.get("channel"),
        "subject": tmpl_dict.get("subject"),
        "body_template": tmpl_dict.get("body_template"),
        "created_at": str(tmpl_dict.get("created_at"))
    }

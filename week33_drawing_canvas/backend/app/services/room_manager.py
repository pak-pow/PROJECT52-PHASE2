import random
import string
import threading
import time

AVATAR_COLORS = [
    "#ef4444", "#f97316", "#f59e0b", "#10b981", 
    "#06b6d4", "#3b82f6", "#8b5cf6", "#ec4899"
]

class RoomManager:
    """Thread-safe in-memory Room Manager and Canvas Stroke Store."""
    def __init__(self):
        self._rooms = {}       # room_code -> { "created_at": float, "users": dict, "strokes": list }
        self._sid_map = {}     # sid -> { "room_code": str, "username": str, "color": str }
        self._lock = threading.Lock()

    def generate_room_code(self) -> str:
        chars = string.ascii_uppercase + string.digits
        return "CANVAS-" + "".join(random.choices(chars, k=5))

    def create_room(self, room_code: str = None) -> str:
        with self._lock:
            if not room_code:
                room_code = self.generate_room_code()
            room_code = room_code.upper().strip()
            if room_code not in self._rooms:
                self._rooms[room_code] = {
                    "created_at": time.time(),
                    "users": {},      # sid -> user_info dict
                    "strokes": []     # list of stroke data dicts
                }
            return room_code

    def join_room(self, room_code: str, sid: str, username: str) -> dict:
        room_code = room_code.upper().strip()
        with self._lock:
            if room_code not in self._rooms:
                self._rooms[room_code] = {
                    "created_at": time.time(),
                    "users": {},
                    "strokes": []
                }
            
            # Assign user color
            color = random.choice(AVATAR_COLORS)
            user_info = {
                "sid": sid,
                "username": username or "Anonymous Artist",
                "color": color,
                "joined_at": time.time()
            }

            self._rooms[room_code]["users"][sid] = user_info
            self._sid_map[sid] = {
                "room_code": room_code,
                "username": user_info["username"],
                "color": color
            }

            return {
                "room_code": room_code,
                "user": user_info,
                "users_list": list(self._rooms[room_code]["users"].values()),
                "strokes_history": self._rooms[room_code]["strokes"]
            }

    def leave_room(self, sid: str) -> tuple[str, dict]:
        with self._lock:
            mapping = self._sid_map.pop(sid, None)
            if not mapping:
                return None, None
            
            room_code = mapping["room_code"]
            if room_code in self._rooms:
                left_user = self._rooms[room_code]["users"].pop(sid, None)
                remaining_users = list(self._rooms[room_code]["users"].values())
                return room_code, {
                    "user": left_user,
                    "remaining_users": remaining_users
                }
            return None, None

    def add_stroke(self, room_code: str, stroke_data: dict):
        room_code = room_code.upper().strip()
        with self._lock:
            if room_code in self._rooms:
                self._rooms[room_code]["strokes"].append(stroke_data)

    def clear_canvas(self, room_code: str):
        room_code = room_code.upper().strip()
        with self._lock:
            if room_code in self._rooms:
                self._rooms[room_code]["strokes"].clear()

    def get_room_details(self, room_code: str) -> dict:
        room_code = room_code.upper().strip()
        with self._lock:
            if room_code in self._rooms:
                room = self._rooms[room_code]
                return {
                    "room_code": room_code,
                    "created_at": room["created_at"],
                    "user_count": len(room["users"]),
                    "users": list(room["users"].values()),
                    "stroke_count": len(room["strokes"])
                }
            return None

room_manager = RoomManager()

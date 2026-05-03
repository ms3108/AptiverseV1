"""
Battle Room Manager — WebSocket connections + real-time battle logic
Implements Redis-backed state (leaderboard as sorted set, battle state as JSON).
Falls back gracefully to in-memory when Redis is unavailable.
"""
import json
import os
import asyncio
import random
import string
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import WebSocket


# ---------------------------------------------------------------------------
# Redis helper
# ---------------------------------------------------------------------------
_redis_client = None
_redis_available: Optional[bool] = None  # None=untested


def _get_redis():
    global _redis_client, _redis_available
    if _redis_available is False:
        return None
    if _redis_client is not None:
        return _redis_client
    try:
        import redis as redis_lib
        url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        _redis_client = redis_lib.from_url(url, decode_responses=True, socket_connect_timeout=1)
        _redis_client.ping()
        _redis_available = True
        print("✅ Redis connected for battle state")
        return _redis_client
    except Exception as e:
        _redis_available = False
        print(f"⚠️ Redis unavailable — battles using in-memory state: {e}")
        return None


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def calculate_score(is_correct: bool, time_taken_seconds: float, max_time: int = 60) -> int:
    """Base 100 pts for correct + up to 50 speed bonus."""
    if not is_correct:
        return 0
    base_points = 100
    speed_bonus = int(50 * (1 - min(time_taken_seconds, max_time) / max_time))
    return base_points + speed_bonus


def generate_room_code(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


# ---------------------------------------------------------------------------
# Battle state backend (Redis or in-memory)
# ---------------------------------------------------------------------------
BATTLE_TTL = 3600  # 1 hour TTL on Redis keys


def _redis_state_key(room_code: str) -> str:
    return f"battle:{room_code}:state"


def _redis_lb_key(room_code: str) -> str:
    return f"battle:{room_code}:leaderboard"


def _redis_user_key(room_code: str) -> str:
    return f"battle:{room_code}:users"


class ConnectionManager:
    def __init__(self):
        # room_code -> list of WebSocket connections (always in-memory — WS are local)
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # websocket -> user info
        self.user_info: Dict[WebSocket, dict] = {}
        # in-memory fallback state
        self._mem_states: Dict[str, dict] = {}

    # ------------------------------------------------------------------
    # State storage helpers
    # ------------------------------------------------------------------

    def _save_state(self, room_code: str, state: dict) -> None:
        r = _get_redis()
        if r:
            try:
                r.setex(_redis_state_key(room_code), BATTLE_TTL, json.dumps(state))
                return
            except Exception:
                pass
        self._mem_states[room_code] = state

    def _load_state(self, room_code: str) -> dict:
        r = _get_redis()
        if r:
            try:
                raw = r.get(_redis_state_key(room_code))
                if raw:
                    return json.loads(raw)
            except Exception:
                pass
        return self._mem_states.get(room_code, {})

    def _delete_state(self, room_code: str) -> None:
        r = _get_redis()
        if r:
            try:
                r.delete(
                    _redis_state_key(room_code),
                    _redis_lb_key(room_code),
                    _redis_user_key(room_code),
                )
            except Exception:
                pass
        self._mem_states.pop(room_code, None)

    # ------------------------------------------------------------------
    # Leaderboard helpers (Redis sorted set or in-memory)
    # ------------------------------------------------------------------

    def _lb_add_points(self, room_code: str, user_id: int, points: int) -> None:
        r = _get_redis()
        if r:
            try:
                r.zincrby(_redis_lb_key(room_code), points, str(user_id))
                r.expire(_redis_lb_key(room_code), BATTLE_TTL)
                return
            except Exception:
                pass
        # in-memory fallback
        state = self._load_state(room_code)
        lb = state.get("leaderboard", {})
        uid = str(user_id)
        if uid not in lb:
            lb[uid] = {"user_id": user_id, "score": 0, "correct_answers": 0, "total_time": 0.0, "username": ""}
        lb[uid]["score"] += points
        state["leaderboard"] = lb
        self._save_state(room_code, state)

    def _lb_get_sorted(self, room_code: str) -> List[dict]:
        """Return leaderboard sorted by score desc."""
        state = self._load_state(room_code)
        lb = state.get("leaderboard", {})
        entries = list(lb.values())
        entries.sort(key=lambda x: (-x["score"], x.get("total_time", 0)))
        for i, entry in enumerate(entries):
            entry["rank"] = i + 1
        return entries

    # ------------------------------------------------------------------
    # WebSocket connection management
    # ------------------------------------------------------------------

    async def connect(self, websocket: WebSocket, room_code: str, user_id: int, username: str):
        await websocket.accept()
        print(f"🔌 {username} (ID:{user_id}) → room {room_code}")

        self.active_connections.setdefault(room_code, [])
        self.active_connections[room_code].append(websocket)
        self.user_info[websocket] = {"user_id": user_id, "username": username, "room_code": room_code}

        # Persist user metadata in state
        state = self._load_state(room_code)
        users = state.get("users", {})
        users[str(user_id)] = {"user_id": user_id, "username": username}
        state["users"] = users
        self._save_state(room_code, state)

        print(f"✅ {username} joined {room_code}. Total: {len(self.active_connections[room_code])}")
        await self.broadcast_to_room(room_code, {
            "type": "user_joined",
            "user_id": user_id,
            "username": username,
            "participant_count": len(self.active_connections[room_code]),
        })

    def disconnect(self, websocket: WebSocket):
        info = self.user_info.pop(websocket, None)
        if not info:
            return
        room_code = info["room_code"]
        conns = self.active_connections.get(room_code, [])
        if websocket in conns:
            conns.remove(websocket)
        if not conns:
            self.active_connections.pop(room_code, None)
            self._delete_state(room_code)

    async def broadcast_to_room(self, room_code: str, message: dict):
        conns = self.active_connections.get(room_code, [])
        print(f"🔊 broadcast '{message.get('type')}' → {len(conns)} connections in {room_code}")
        disconnected = []
        sent = 0
        for conn in list(conns):
            try:
                await conn.send_json(message)
                sent += 1
            except Exception as e:
                print(f"❌ send error: {e}")
                disconnected.append(conn)
        print(f"✅ sent {sent}/{len(conns)}")
        for conn in disconnected:
            self.disconnect(conn)

    async def send_personal_message(self, websocket: WebSocket, message: dict):
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(websocket)

    # ------------------------------------------------------------------
    # Battle state management
    # ------------------------------------------------------------------

    def initialize_battle_state(self, room_code: str, questions: List[dict], num_questions: int):
        state = {
            "current_question_index": 0,
            "questions": questions[:num_questions],
            "num_questions": num_questions,
            "started_at": datetime.now().isoformat(),
            "question_start_time": None,
            "leaderboard": {},
            "users": {},
            "status": "in_progress",
        }
        self._save_state(room_code, state)

    def get_battle_state(self, room_code: str) -> dict:
        return self._load_state(room_code)

    def update_leaderboard(
        self,
        room_code: str,
        user_id: int,
        username: str,
        is_correct: bool,
        time_taken: float,
        points: int,
    ):
        state = self._load_state(room_code)
        if not state:
            return

        lb = state.get("leaderboard", {})
        uid = str(user_id)
        if uid not in lb:
            lb[uid] = {
                "user_id": user_id,
                "username": username,
                "score": 0,
                "correct_answers": 0,
                "total_time": 0.0,
            }
        lb[uid]["score"] += points
        lb[uid]["total_time"] += time_taken
        if is_correct:
            lb[uid]["correct_answers"] += 1
        state["leaderboard"] = lb
        self._save_state(room_code, state)

        # Also update Redis sorted set if available
        r = _get_redis()
        if r and points > 0:
            try:
                r.zincrby(_redis_lb_key(room_code), points, str(user_id))
                r.expire(_redis_lb_key(room_code), BATTLE_TTL)
            except Exception:
                pass

    def get_sorted_leaderboard(self, room_code: str) -> List[dict]:
        return self._lb_get_sorted(room_code)


# ---------------------------------------------------------------------------
# Global singleton
# ---------------------------------------------------------------------------
manager = ConnectionManager()

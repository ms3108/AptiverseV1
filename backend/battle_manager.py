"""
Battle Room Manager - Handles WebSocket connections and real-time battle logic
"""
from typing import Dict, List, Set
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime
import random
import string


class ConnectionManager:
    def __init__(self):
        # room_code -> list of WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
        # room_code -> battle state
        self.battle_states: Dict[str, dict] = {}
        
        # websocket -> user info
        self.user_info: Dict[WebSocket, dict] = {}
    
    async def connect(self, websocket: WebSocket, room_code: str, user_id: int, username: str):
        """Connect a user to a battle room"""
        await websocket.accept()
        print(f"🔌 User {username} (ID: {user_id}) connecting to room {room_code}")
        
        if room_code not in self.active_connections:
            self.active_connections[room_code] = []
            print(f"📝 Created new connections list for room {room_code}")
        
        self.active_connections[room_code].append(websocket)
        self.user_info[websocket] = {
            "user_id": user_id,
            "username": username,
            "room_code": room_code
        }
        print(f"✅ User {username} added to room {room_code}. Total connections: {len(self.active_connections[room_code])}")
        
        # Notify all participants about new user
        await self.broadcast_to_room(room_code, {
            "type": "user_joined",
            "user_id": user_id,
            "username": username,
            "participant_count": len(self.active_connections[room_code])
        })
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect a user from their battle room"""
        if websocket in self.user_info:
            user_data = self.user_info[websocket]
            room_code = user_data["room_code"]
            
            if room_code in self.active_connections:
                self.active_connections[room_code].remove(websocket)
                
                # If room is empty, clean up
                if not self.active_connections[room_code]:
                    del self.active_connections[room_code]
                    if room_code in self.battle_states:
                        del self.battle_states[room_code]
            
            del self.user_info[websocket]
    
    async def broadcast_to_room(self, room_code: str, message: dict):
        """Send a message to all participants in a room"""
        if room_code in self.active_connections:
            connection_count = len(self.active_connections[room_code])
            print(f"🔊 broadcast_to_room: Sending '{message.get('type')}' to {connection_count} connections in room {room_code}")
            disconnected = []
            sent_count = 0
            for connection in self.active_connections[room_code]:
                try:
                    await connection.send_json(message)
                    sent_count += 1
                except Exception as e:
                    print(f"❌ Error sending to connection: {e}")
                    disconnected.append(connection)
            
            print(f"✅ Successfully sent to {sent_count}/{connection_count} connections")
            # Clean up disconnected clients
            for connection in disconnected:
                self.disconnect(connection)
    
    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """Send a message to a specific user"""
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(websocket)
    
    def initialize_battle_state(self, room_code: str, questions: List[dict], num_questions: int):
        """Initialize battle state when battle starts"""
        self.battle_states[room_code] = {
            "current_question_index": 0,
            "questions": questions[:num_questions],
            "num_questions": num_questions,
            "started_at": datetime.now().isoformat(),
            "question_start_time": None,
            "leaderboard": {},  # user_id -> {score, correct, total_time}
            "status": "in_progress"
        }
    
    def get_battle_state(self, room_code: str) -> dict:
        """Get current battle state"""
        return self.battle_states.get(room_code, {})
    
    def update_leaderboard(self, room_code: str, user_id: int, username: str, 
                          is_correct: bool, time_taken: float, points: int):
        """Update leaderboard for a room"""
        if room_code not in self.battle_states:
            return
        
        state = self.battle_states[room_code]
        
        if user_id not in state["leaderboard"]:
            state["leaderboard"][user_id] = {
                "user_id": user_id,
                "username": username,
                "score": 0,
                "correct_answers": 0,
                "total_time": 0.0
            }
        
        state["leaderboard"][user_id]["score"] += points
        state["leaderboard"][user_id]["total_time"] += time_taken
        if is_correct:
            state["leaderboard"][user_id]["correct_answers"] += 1
    
    def get_sorted_leaderboard(self, room_code: str) -> List[dict]:
        """Get sorted leaderboard (by score desc, then time asc)"""
        if room_code not in self.battle_states:
            return []
        
        leaderboard = list(self.battle_states[room_code]["leaderboard"].values())
        # Sort by score descending, then by time ascending (faster is better)
        leaderboard.sort(key=lambda x: (-x["score"], x["total_time"]))
        
        # Add rank
        for i, entry in enumerate(leaderboard):
            entry["rank"] = i + 1
        
        return leaderboard


# Global connection manager instance
manager = ConnectionManager()


def generate_room_code(length: int = 6) -> str:
    """Generate a random room code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def calculate_score(is_correct: bool, time_taken_seconds: float, max_time: int = 60) -> int:
    """
    Calculate score based on correctness and speed
    - Correct answer: base 100 points
    - Speed bonus: up to 50 points (faster = more points)
    - Wrong answer: 0 points
    """
    if not is_correct:
        return 0
    
    base_points = 100
    
    # Speed bonus: linear decrease from 50 to 0 over max_time seconds
    if time_taken_seconds <= max_time:
        speed_bonus = int(50 * (1 - time_taken_seconds / max_time))
    else:
        speed_bonus = 0
    
    return base_points + speed_bonus

"""
Database migration script to add battle room tables
Run this to create the necessary tables for the battle room feature
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/aptiverse_db")
engine = create_engine(DATABASE_URL)

def run_migration():
    print("Starting battle room migration...")
    
    with engine.connect() as conn:
        # Create battle_rooms table
        print("Creating battle_rooms table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS battle_rooms (
                id SERIAL PRIMARY KEY,
                room_code VARCHAR UNIQUE NOT NULL,
                creator_id INTEGER NOT NULL REFERENCES users(id),
                topic VARCHAR NOT NULL,
                num_questions INTEGER NOT NULL,
                status VARCHAR DEFAULT 'waiting',
                started_at TIMESTAMP WITH TIME ZONE,
                completed_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        conn.commit()
        
        # Create battle_participants table
        print("Creating battle_participants table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS battle_participants (
                id SERIAL PRIMARY KEY,
                battle_room_id INTEGER NOT NULL REFERENCES battle_rooms(id),
                user_id INTEGER NOT NULL REFERENCES users(id),
                score INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0,
                total_time_seconds FLOAT DEFAULT 0.0,
                rank INTEGER,
                joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        conn.commit()
        
        # Create battle_questions table
        print("Creating battle_questions table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS battle_questions (
                id SERIAL PRIMARY KEY,
                battle_room_id INTEGER NOT NULL REFERENCES battle_rooms(id),
                question_id INTEGER NOT NULL REFERENCES questions(id),
                question_order INTEGER NOT NULL
            );
        """))
        conn.commit()
        
        # Create battle_answers table
        print("Creating battle_answers table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS battle_answers (
                id SERIAL PRIMARY KEY,
                participant_id INTEGER NOT NULL REFERENCES battle_participants(id),
                question_id INTEGER NOT NULL REFERENCES questions(id),
                user_answer VARCHAR NOT NULL,
                is_correct BOOLEAN NOT NULL,
                time_taken_seconds FLOAT NOT NULL,
                points_earned INTEGER DEFAULT 0,
                answered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        conn.commit()
        
        # Create indexes for better performance
        print("Creating indexes...")
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_battle_rooms_room_code ON battle_rooms(room_code);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_battle_rooms_status ON battle_rooms(status);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_battle_participants_user_id ON battle_participants(user_id);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_battle_participants_battle_room_id ON battle_participants(battle_room_id);"))
        conn.commit()
        
        print("✅ Battle room migration completed successfully!")
        print("\nNew tables created:")
        print("  - battle_rooms")
        print("  - battle_participants")
        print("  - battle_questions")
        print("  - battle_answers")

if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"❌ Migration failed: {e}")

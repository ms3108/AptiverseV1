"""
Migration: Add time_per_question column to battle_rooms table
"""
from sqlalchemy import create_engine, text
from database import engine
import os

def migrate():
    print("🔄 Starting migration: Add time_per_question to battle_rooms")
    print("="*60)
    
    try:
        with engine.connect() as conn:
            # Check if column already exists
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='battle_rooms' 
                AND column_name='time_per_question'
            """)
            
            result = conn.execute(check_query)
            exists = result.fetchone() is not None
            
            if exists:
                print("⏭️  Column 'time_per_question' already exists. Skipping migration.")
                print("="*60)
                return
            
            # Add the column with default value
            print("➕ Adding 'time_per_question' column to battle_rooms table...")
            alter_query = text("""
                ALTER TABLE battle_rooms 
                ADD COLUMN time_per_question INTEGER NOT NULL DEFAULT 60
            """)
            
            conn.execute(alter_query)
            conn.commit()
            
            print("✅ Column added successfully!")
            print("   - Column name: time_per_question")
            print("   - Data type: INTEGER")
            print("   - Default value: 60 seconds")
            print("   - Nullable: NOT NULL")
            
            # Update existing battle rooms to have default value
            print("\n🔄 Updating existing battle rooms with default time...")
            update_query = text("""
                UPDATE battle_rooms 
                SET time_per_question = 60 
                WHERE time_per_question IS NULL
            """)
            
            result = conn.execute(update_query)
            conn.commit()
            
            updated_count = result.rowcount
            print(f"✅ Updated {updated_count} existing battle rooms")
            
            print("="*60)
            print("✅ Migration completed successfully!")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    migrate()

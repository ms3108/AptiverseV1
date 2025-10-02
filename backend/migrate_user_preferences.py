"""
Migration script to add daily_practice_count field to users table
"""
from sqlalchemy import text
from database import engine

def migrate():
    """Add daily_practice_count column to users table"""
    with engine.connect() as conn:
        try:
            # Check if column exists
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='daily_practice_count';
            """)
            result = conn.execute(check_query)
            
            if result.fetchone():
                print("✅ Column 'daily_practice_count' already exists")
                return
            
            # Add the column
            alter_query = text("""
                ALTER TABLE users 
                ADD COLUMN daily_practice_count INTEGER DEFAULT 10;
            """)
            conn.execute(alter_query)
            conn.commit()
            
            print("✅ Successfully added 'daily_practice_count' column to users table")
            print("   Default value: 10 questions per practice set")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            conn.rollback()

if __name__ == "__main__":
    print("🔄 Starting migration: Add daily_practice_count to users...")
    migrate()
    print("✅ Migration complete!")

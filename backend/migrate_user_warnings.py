"""
Migration: Add user_warnings table
"""
from sqlalchemy import create_engine, text
from database import DATABASE_URL
import sys

def run_migration():
    """Add user_warnings table to database"""
    engine = create_engine(DATABASE_URL)
    
    migrations = [
        # Step 1: Create user_warnings table
        """
        CREATE TABLE IF NOT EXISTS user_warnings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            report_id INTEGER REFERENCES reported_posts(id) ON DELETE SET NULL,
            reason TEXT NOT NULL,
            issued_by_admin_id INTEGER NOT NULL REFERENCES users(id),
            is_read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Step 2: Create indexes
        """
        CREATE INDEX IF NOT EXISTS idx_user_warnings_user_id ON user_warnings(user_id)
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_user_warnings_is_read ON user_warnings(is_read)
        """,
    ]
    
    try:
        with engine.connect() as conn:
            for i, migration in enumerate(migrations, 1):
                print(f"Running step {i}/{len(migrations)}...")
                conn.execute(text(migration))
                conn.commit()
                print(f"✅ Step {i}/{len(migrations)} completed")
            
            print("\n✅ Migration completed successfully!")
            print("📊 user_warnings table created with indexes")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()

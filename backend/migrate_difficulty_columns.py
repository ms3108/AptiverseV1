"""
Database migration to add difficulty algorithm columns to Question table
Run this after deploying the updated code
"""
from database import SessionLocal
from sqlalchemy import text

def migrate():
    db = SessionLocal()
    try:
        print("🔄 Starting migration: Adding difficulty tracking columns...")
        
        # Check if columns already exist
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='questions' AND column_name='difficulty_score'
        """))
        
        if result.fetchone():
            print("✅ Columns already exist. Migration skipped.")
            return
        
        # Add new columns
        migrations = [
            "ALTER TABLE questions ADD COLUMN IF NOT EXISTS difficulty_score FLOAT",
            "ALTER TABLE questions ADD COLUMN IF NOT EXISTS difficulty_confidence FLOAT DEFAULT 0.0",
            "ALTER TABLE questions ADD COLUMN IF NOT EXISTS difficulty_history JSON DEFAULT '[]'",
            "ALTER TABLE questions ADD COLUMN IF NOT EXISTS tier_stats JSON DEFAULT '{}'",
        ]
        
        for migration_sql in migrations:
            print(f"  Running: {migration_sql}")
            db.execute(text(migration_sql))
        
        db.commit()
        print("✅ Migration completed successfully!")
        print("\n📊 Next steps:")
        print("  1. Run: python -m backend.difficulty_algorithm (to recalculate all difficulties)")
        print("  2. Or call: GET /admin/recalculate-difficulties endpoint")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()

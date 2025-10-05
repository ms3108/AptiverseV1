"""
Migration: Add Hybrid Difficulty Tracking Fields to Questions Table
"""
from sqlalchemy import text
from database import engine

def migrate():
    """Add new columns for hybrid difficulty tracking"""
    
    migrations = [
        # Store original difficulty
        """
        ALTER TABLE questions 
        ADD COLUMN IF NOT EXISTS initial_difficulty VARCHAR
        """,
        
        # Heuristic-based score (0-1)
        """
        ALTER TABLE questions 
        ADD COLUMN IF NOT EXISTS heuristic_score FLOAT DEFAULT 0.5
        """,
        
        # Performance tracking
        """
        ALTER TABLE questions 
        ADD COLUMN IF NOT EXISTS total_attempts INTEGER DEFAULT 0
        """,
        
        """
        ALTER TABLE questions 
        ADD COLUMN IF NOT EXISTS correct_attempts INTEGER DEFAULT 0
        """,
        
        """
        ALTER TABLE questions 
        ADD COLUMN IF NOT EXISTS total_time_seconds FLOAT DEFAULT 0
        """,
        
        """
        ALTER TABLE questions 
        ADD COLUMN IF NOT EXISTS avg_time_seconds FLOAT DEFAULT 0
        """,
        
        # Performance-based difficulty score
        """
        ALTER TABLE questions 
        ADD COLUMN IF NOT EXISTS performance_difficulty FLOAT
        """,
        
        # Alpha weight for hybrid calculation
        """
        ALTER TABLE questions 
        ADD COLUMN IF NOT EXISTS alpha_weight FLOAT DEFAULT 0.7
        """,
        
        # Last update timestamp
        """
        ALTER TABLE questions 
        ADD COLUMN IF NOT EXISTS last_difficulty_update TIMESTAMP WITH TIME ZONE
        """
    ]
    
    print("🔄 Running migration: Add hybrid difficulty fields...")
    
    with engine.connect() as conn:
        for i, migration in enumerate(migrations, 1):
            try:
                conn.execute(text(migration))
                conn.commit()
                print(f"  ✅ Step {i}/{len(migrations)} completed")
            except Exception as e:
                print(f"  ⚠️  Step {i} (might already exist): {str(e)[:100]}")
    
    print("\n✅ Migration completed!")
    print("\nNext steps:")
    print("1. Run: python hybrid_difficulty.py")
    print("2. Choose option 1 to initialize heuristic scores")

if __name__ == "__main__":
    migrate()

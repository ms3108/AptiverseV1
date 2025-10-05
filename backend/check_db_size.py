"""
Check database size and table counts
"""
from database import SessionLocal
from models import Question, User, Badge, UserProgress, BattleRoom, Post, Achievement
from sqlalchemy import text

db = SessionLocal()

try:
    print("\n" + "="*60)
    print("📊 DATABASE STATISTICS")
    print("="*60 + "\n")
    
    # Table counts
    tables = [
        ("Questions", Question),
        ("Users", User),
        ("Badges", Badge),
        ("User Progress", UserProgress),
        ("Battle Rooms", BattleRoom),
        ("Posts", Post),
        ("Achievements", Achievement),
    ]
    
    total_rows = 0
    for name, model in tables:
        try:
            count = db.query(model).count()
            total_rows += count
            print(f"{name:.<30} {count:>6} rows")
        except Exception as e:
            print(f"{name:.<30} ERROR: {str(e)[:30]}")
    
    print(f"\n{'Total Rows':.<30} {total_rows:>6}")
    
    # Database size query (PostgreSQL specific)
    print("\n" + "-"*60)
    print("💾 STORAGE ANALYSIS")
    print("-"*60 + "\n")
    
    try:
        result = db.execute(text("""
            SELECT 
                pg_size_pretty(pg_database_size(current_database())) as db_size,
                pg_database_size(current_database()) as db_size_bytes
        """)).fetchone()
        
        db_size = result[0]
        db_size_bytes = result[1]
        db_size_mb = db_size_bytes / (1024 * 1024)
        free_tier_mb = 512
        usage_percent = (db_size_mb / free_tier_mb) * 100
        
        print(f"Database Size:          {db_size}")
        print(f"Size in MB:             {db_size_mb:.2f} MB")
        print(f"Free Tier Limit:        {free_tier_mb} MB")
        print(f"Usage:                  {usage_percent:.2f}%")
        print(f"Remaining:              {free_tier_mb - db_size_mb:.2f} MB")
        
        if usage_percent < 50:
            print(f"\n✅ Status: SAFE - Well within free tier!")
        elif usage_percent < 80:
            print(f"\n⚠️  Status: MODERATE - Monitor closely")
        else:
            print(f"\n🚨 Status: HIGH - Consider cleanup or upgrade soon")
            
    except Exception as e:
        print(f"Could not get database size: {e}")
    
    # Table sizes
    print("\n" + "-"*60)
    print("📦 TABLE SIZES")
    print("-"*60 + "\n")
    
    try:
        result = db.execute(text("""
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
                pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            LIMIT 10
        """)).fetchall()
        
        for row in result:
            size_kb = row[3] / 1024
            print(f"{row[1]:.<30} {row[2]:>10} ({size_kb:.1f} KB)")
            
    except Exception as e:
        print(f"Could not get table sizes: {e}")
    
    print("\n" + "="*60)
    print("✅ Database statistics retrieved successfully!")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}\n")
finally:
    db.close()

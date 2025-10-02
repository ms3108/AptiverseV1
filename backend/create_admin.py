"""
Create admin account and migrate database for admin features
"""
from sqlalchemy import text
from database import SessionLocal, engine
from models import User, BannedEmail, AdminActionLog, ReportedPost
from auth import get_password_hash
import sys

def migrate_admin_tables():
    """Add admin-related columns and tables"""
    print("🔄 Migrating database for admin features...")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # Add admin columns to users table
        print("\n📋 Adding admin columns to users table...")
        admin_columns = [
            ("is_admin", "BOOLEAN DEFAULT FALSE"),
            ("is_banned", "BOOLEAN DEFAULT FALSE"),
            ("is_permanently_banned", "BOOLEAN DEFAULT FALSE"),
            ("ban_reason", "TEXT"),
            ("banned_at", "TIMESTAMP WITH TIME ZONE"),
            ("banned_by_admin_id", "INTEGER REFERENCES users(id)")
        ]
        
        for column_name, column_type in admin_columns:
            try:
                db.execute(text(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {column_name} {column_type}"))
                print(f"  ✅ Added column: {column_name}")
            except Exception as e:
                print(f"  ⚠️  Column {column_name} might already exist: {str(e)}")
        
        db.commit()
        print("\n✅ Users table migration complete!")
        
        # Create admin action logs table
        print("\n📋 Creating admin_action_logs table...")
        try:
            AdminActionLog.__table__.create(engine, checkfirst=True)
            print("  ✅ admin_action_logs table created")
        except Exception as e:
            print(f"  ⚠️  Table might already exist: {str(e)}")
        
        # Create banned emails table
        print("\n📋 Creating banned_emails table...")
        try:
            BannedEmail.__table__.create(engine, checkfirst=True)
            print("  ✅ banned_emails table created")
        except Exception as e:
            print(f"  ⚠️  Table might already exist: {str(e)}")
        
        # Create reported posts table
        print("\n📋 Creating reported_posts table...")
        try:
            ReportedPost.__table__.create(engine, checkfirst=True)
            print("  ✅ reported_posts table created")
        except Exception as e:
            print(f"  ⚠️  Table might already exist: {str(e)}")
        
        print("\n" + "=" * 70)
        print("✅ Database migration completed successfully!")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Migration failed: {str(e)}")
        return False
    finally:
        db.close()


def create_admin_account(email: str, password: str):
    """Create or update admin account"""
    print("\n🔧 Setting up admin account...")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # Check if user exists
        admin = db.query(User).filter(User.email == email).first()
        
        if admin:
            print(f"\n📧 User with email {email} already exists")
            # Update to admin
            admin.is_admin = True
            admin.hashed_password = get_password_hash(password)
            admin.is_verified = True  # Ensure admin is verified
            print(f"  ✅ Updated {admin.username} to admin with new password")
        else:
            # Create new admin user
            admin = User(
                email=email,
                username="admin",
                hashed_password=get_password_hash(password),
                is_verified=True,
                is_admin=True,
                xp=0,
                level=1
            )
            db.add(admin)
            print(f"  ✅ Created new admin account: {email}")
        
        db.commit()
        
        print("\n" + "=" * 70)
        print("✅ Admin account setup complete!")
        print(f"\n📧 Email: {email}")
        print(f"🔑 Password: {password}")
        print("\n⚠️  IMPORTANT: Keep these credentials secure!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Failed to create admin account: {str(e)}")
        return False
    finally:
        db.close()


def main():
    print("\n" + "🔐 APTIVERSE ADMIN SETUP".center(70, "="))
    print()
    
    # Step 1: Migrate database
    if not migrate_admin_tables():
        print("\n❌ Migration failed. Admin setup aborted.")
        sys.exit(1)
    
    # Step 2: Create admin account
    admin_email = "misna5984@gmail.com"
    admin_password = "S5iKorE*lXevedod&&$l3Ib"
    
    if not create_admin_account(admin_email, admin_password):
        print("\n❌ Admin account creation failed.")
        sys.exit(1)
    
    print("\n" + "🎉 SETUP COMPLETE!".center(70, "="))
    print()
    print("You can now:")
    print("  1. Log in with the admin credentials")
    print("  2. Access admin endpoints at /admin/*")
    print("  3. Manage users, questions, and reports")
    print()


if __name__ == "__main__":
    main()

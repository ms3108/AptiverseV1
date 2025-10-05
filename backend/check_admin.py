from database import SessionLocal
from models import User
from auth import verify_password

db = SessionLocal()
admin = db.query(User).filter(User.email == 'misna5984@gmail.com').first()

if admin:
    print(f"Email: {admin.email}")
    print(f"Username: {admin.username}")
    print(f"Is Admin: {admin.is_admin}")
    print(f"Is Verified: {admin.is_verified}")
    print(f"Hash starts with: {admin.hashed_password[:30]}")
    
    # Test password verification
    test_password = "S5iKorE*lXevedod&&$l3Ib"
    is_valid = verify_password(test_password, admin.hashed_password)
    print(f"\nPassword verification test: {is_valid}")
else:
    print("Admin user not found!")

db.close()

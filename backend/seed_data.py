"""Seed initial data for the vehicle maintenance app"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import bcrypt

load_dotenv()

async def seed_data():
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'vehicle_maintenance')]
    
    print("🌱 Seeding database...")
    
    # Hash password
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Clear existing data
    await db.users.delete_many({})
    await db.services.delete_many({})
    await db.promotions.delete_many({})
    await db.technician_profiles.delete_many({})
    
    print("✓ Cleared existing data")
    
    # Create users
    users_data = [
        {
            "email": "customer@test.com",
            "password_hash": hash_password("password123"),
            "role": "customer",
            "full_name": "Ahmed Al-Salem",
            "phone": "+966501234567",
            "created_at": datetime.utcnow()
        },
        {
            "email": "dispatcher@test.com",
            "password_hash": hash_password("password123"),
            "role": "dispatcher",
            "full_name": "Sara Al-Qahtani",
            "phone": "+966507654321",
            "created_at": datetime.utcnow()
        },
        {
            "email": "technician@test.com",
            "password_hash": hash_password("password123"),
            "role": "technician",
            "full_name": "Mohammed Al-Otaibi",
            "phone": "+966509876543",
            "created_at": datetime.utcnow()
        },
        {
            "email": "admin@test.com",
            "password_hash": hash_password("password123"),
            "role": "admin",
            "full_name": "Fatima Al-Harbi",
            "phone": "+966503456789",
            "created_at": datetime.utcnow()
        }
    ]
    
    users_result = await db.users.insert_many(users_data)
    print(f"✓ Created {len(users_result.inserted_ids)} users")
    
    # Get technician user ID for profile
    technician_user = await db.users.find_one({"role": "technician"})
    
    # Create technician profile
    if technician_user:
        tech_profile = {
            "user_id": str(technician_user["_id"]),
            "vehicle_number": "ABC-1234",
            "skills": ["Oil Change", "Brake Repair", "Battery Replacement"],
            "rating_avg": 4.8,
            "rating_count": 25,
            "available": True,
            "current_location": {
                "latitude": 24.7136,
                "longitude": 46.6753,
                "address": "Riyadh, Saudi Arabia"
            }
        }
        await db.technician_profiles.insert_one(tech_profile)
        print("✓ Created technician profile")
    
    # Create service catalog
    services_data = [
        {
            "name": "Oil Change",
            "category": "Maintenance",
            "base_price": 150.0,
            "description": "Complete engine oil change with filter replacement",
            "duration_minutes": 30,
            "active": True
        },
        {
            "name": "Brake Inspection & Repair",
            "category": "Safety",
            "base_price": 300.0,
            "description": "Full brake system inspection and repair",
            "duration_minutes": 60,
            "active": True
        },
        {
            "name": "Battery Replacement",
            "category": "Electrical",
            "base_price": 400.0,
            "description": "New battery installation with testing",
            "duration_minutes": 20,
            "active": True
        },
        {
            "name": "Tire Rotation",
            "category": "Maintenance",
            "base_price": 100.0,
            "description": "Rotate all four tires for even wear",
            "duration_minutes": 30,
            "active": True
        },
        {
            "name": "AC Service",
            "category": "Comfort",
            "base_price": 250.0,
            "description": "Air conditioning system check and gas refill",
            "duration_minutes": 45,
            "active": True
        },
        {
            "name": "Engine Diagnostic",
            "category": "Diagnostic",
            "base_price": 200.0,
            "description": "Complete engine diagnostic scan",
            "duration_minutes": 30,
            "active": True
        }
    ]
    
    services_result = await db.services.insert_many(services_data)
    print(f"✓ Created {len(services_result.inserted_ids)} services")
    
    # Create promotions
    now = datetime.utcnow()
    promotions_data = [
        {
            "code": "WELCOME20",
            "discount_type": "PERCENT",
            "discount_value": 20.0,
            "effective_start": now,
            "effective_end": now + timedelta(days=30),
            "min_spend": 200.0,
            "active": True,
            "used_count": 0
        },
        {
            "code": "SAVE50",
            "discount_type": "FIXED_AMOUNT",
            "discount_value": 50.0,
            "effective_start": now,
            "effective_end": now + timedelta(days=60),
            "min_spend": 300.0,
            "active": True,
            "used_count": 0
        },
        {
            "code": "SUMMER25",
            "discount_type": "PERCENT",
            "discount_value": 25.0,
            "effective_start": now,
            "effective_end": now + timedelta(days=90),
            "min_spend": 500.0,
            "active": True,
            "used_count": 0
        }
    ]
    
    promotions_result = await db.promotions.insert_many(promotions_data)
    print(f"✓ Created {len(promotions_result.inserted_ids)} promotions")
    
    print("\n✨ Seeding complete!")
    print("\n📧 Test Accounts:")
    print("   Customer:    customer@test.com / password123")
    print("   Dispatcher:  dispatcher@test.com / password123")
    print("   Technician:  technician@test.com / password123")
    print("   Admin:       admin@test.com / password123")
    print("\n🎫 Test Coupons: WELCOME20, SAVE50, SUMMER25")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_data())

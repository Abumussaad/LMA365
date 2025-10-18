from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
import jwt
import bcrypt


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'vehicle_maintenance')]

# JWT Settings
SECRET_KEY = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Create the main app
app = FastAPI(title="Vehicle Maintenance API")
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ==================== MODELS ====================

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return str(v)


class UserRole:
    CUSTOMER = "customer"
    DISPATCHER = "dispatcher"
    TECHNICIAN = "technician"
    ADMIN = "admin"


class JobStatus:
    REQUESTED = "REQUESTED"
    ASSIGNED = "ASSIGNED"
    EN_ROUTE = "EN_ROUTE"
    ON_SITE = "ON_SITE"
    COMPLETION_PENDING = "COMPLETION_PENDING"
    CLOSED = "CLOSED"
    CANCELLED_FREE = "CANCELLED_FREE"
    CANCELLED_LATE = "CANCELLED_LATE"
    CANCELLED_ONSITE = "CANCELLED_ONSITE"


# User Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str
    full_name: str
    phone: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    email: EmailStr
    role: str
    full_name: str
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User


# Service Catalog Models
class ServiceItem(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    name: str
    category: str
    base_price: float
    description: Optional[str] = None
    duration_minutes: int = 60
    active: bool = True

    class Config:
        populate_by_name = True


class ServiceItemCreate(BaseModel):
    name: str
    category: str
    base_price: float
    description: Optional[str] = None
    duration_minutes: int = 60


# Service Request Models
class LocationData(BaseModel):
    latitude: float
    longitude: float
    address: str


class RequestedService(BaseModel):
    service_id: str
    quantity: int = 1


class ServiceRequestCreate(BaseModel):
    vehicle_plate: str
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    location: LocationData
    scheduled_time: datetime
    services: List[RequestedService]
    notes: Optional[str] = None
    coupon_code: Optional[str] = None


class ServiceRequest(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    customer_id: str
    vehicle_plate: str
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    location: LocationData
    scheduled_time: datetime
    services: List[RequestedService]
    notes: Optional[str] = None
    status: str = JobStatus.REQUESTED
    coupon_code: Optional[str] = None
    discount_amount: float = 0.0
    total_amount: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_technician_ids: List[str] = []

    class Config:
        populate_by_name = True


# Technician Profile
class TechnicianProfile(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    user_id: str
    vehicle_number: str
    skills: List[str] = []
    rating_avg: float = 0.0
    rating_count: int = 0
    available: bool = True
    current_location: Optional[LocationData] = None

    class Config:
        populate_by_name = True


class TechnicianProfileCreate(BaseModel):
    vehicle_number: str
    skills: List[str] = []


# Job Models
class PhotoCapture(BaseModel):
    phase: str  # BEFORE, MID, AFTER
    image_base64: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    location: Optional[LocationData] = None


class PartUsed(BaseModel):
    part_id: str
    part_name: str
    quantity: int
    unit_price: float


class CompletionReport(BaseModel):
    labor_minutes: int
    parts_used: List[PartUsed]
    notes: Optional[str] = None
    customer_signature: Optional[str] = None


class Job(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    request_id: str
    technician_id: str
    status: str = JobStatus.ASSIGNED
    photos: List[PhotoCapture] = []
    parts_used: List[PartUsed] = []
    completion_report: Optional[CompletionReport] = None
    rating: Optional[int] = None
    review: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        populate_by_name = True


# Promotion Models
class Promotion(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    code: str
    discount_type: str  # PERCENT, FIXED_AMOUNT
    discount_value: float
    effective_start: datetime
    effective_end: datetime
    min_spend: float = 0.0
    active: bool = True
    usage_limit: Optional[int] = None
    used_count: int = 0

    class Config:
        populate_by_name = True


class PromotionCreate(BaseModel):
    code: str
    discount_type: str
    discount_value: float
    effective_start: datetime
    effective_end: datetime
    min_spend: float = 0.0
    usage_limit: Optional[int] = None


# Invoice Models
class InvoiceLineItem(BaseModel):
    description: str
    quantity: int
    unit_price: float
    total: float


class Invoice(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    job_id: str
    customer_id: str
    line_items: List[InvoiceLineItem]
    subtotal: float
    discount: float = 0.0
    tax: float = 0.0
    total: float
    payment_status: str = "PENDING"  # PENDING, PAID, FAILED
    payment_method: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    paid_at: Optional[datetime] = None

    class Config:
        populate_by_name = True


# ==================== HELPER FUNCTIONS ====================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        user["_id"] = str(user["_id"])
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_role(required_roles: List[str]):
    async def role_checker(current_user: Dict = Depends(get_current_user)):
        if current_user.get("role") not in required_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker


# ==================== AUTH ROUTES ====================

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    # Check if user exists
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_dict = user_data.dict()
    user_dict["password_hash"] = hash_password(user_data.password)
    del user_dict["password"]
    user_dict["created_at"] = datetime.utcnow()
    
    result = await db.users.insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)
    
    # Create token
    token = create_access_token({"sub": user_dict["_id"], "role": user_dict["role"]})
    
    user_obj = User(**user_dict)
    return TokenResponse(access_token=token, user=user_obj)


@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user["_id"] = str(user["_id"])
    token = create_access_token({"sub": user["_id"], "role": user["role"]})
    
    user_obj = User(**user)
    return TokenResponse(access_token=token, user=user_obj)


@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: Dict = Depends(get_current_user)):
    return User(**current_user)


# ==================== SERVICE CATALOG ROUTES ====================

@api_router.post("/services", response_model=ServiceItem)
async def create_service(
    service: ServiceItemCreate,
    current_user: Dict = Depends(require_role([UserRole.ADMIN]))
):
    service_dict = service.dict()
    result = await db.services.insert_one(service_dict)
    service_dict["_id"] = str(result.inserted_id)
    return ServiceItem(**service_dict)


@api_router.get("/services", response_model=List[ServiceItem])
async def get_services():
    services = await db.services.find({"active": True}).to_list(100)
    return [ServiceItem(**{**s, "_id": str(s["_id"])}) for s in services]


@api_router.get("/services/{service_id}", response_model=ServiceItem)
async def get_service(service_id: str):
    service = await db.services.find_one({"_id": ObjectId(service_id)})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    service["_id"] = str(service["_id"])
    return ServiceItem(**service)


# ==================== SERVICE REQUEST ROUTES ====================

@api_router.post("/requests", response_model=ServiceRequest)
async def create_request(
    request_data: ServiceRequestCreate,
    current_user: Dict = Depends(require_role([UserRole.CUSTOMER]))
):
    # Calculate total
    total = 0.0
    for req_service in request_data.services:
        service = await db.services.find_one({"_id": ObjectId(req_service.service_id)})
        if service:
            total += service["base_price"] * req_service.quantity
    
    # Apply coupon if provided
    discount = 0.0
    if request_data.coupon_code:
        promo = await db.promotions.find_one({
            "code": request_data.coupon_code,
            "active": True,
            "effective_start": {"$lte": datetime.utcnow()},
            "effective_end": {"$gte": datetime.utcnow()}
        })
        if promo and total >= promo.get("min_spend", 0):
            if promo["discount_type"] == "PERCENT":
                discount = total * (promo["discount_value"] / 100)
            else:
                discount = promo["discount_value"]
    
    request_dict = request_data.dict()
    request_dict["customer_id"] = current_user["_id"]
    request_dict["total_amount"] = total - discount
    request_dict["discount_amount"] = discount
    request_dict["status"] = JobStatus.REQUESTED
    request_dict["created_at"] = datetime.utcnow()
    request_dict["assigned_technician_ids"] = []
    
    result = await db.service_requests.insert_one(request_dict)
    request_dict["_id"] = str(result.inserted_id)
    
    logger.info(f"Service request created: {request_dict['_id']}")
    return ServiceRequest(**request_dict)


@api_router.get("/requests", response_model=List[ServiceRequest])
async def get_requests(current_user: Dict = Depends(get_current_user)):
    query = {}
    if current_user["role"] == UserRole.CUSTOMER:
        query["customer_id"] = current_user["_id"]
    
    requests = await db.service_requests.find(query).sort("created_at", -1).to_list(100)
    return [ServiceRequest(**{**r, "_id": str(r["_id"])}) for r in requests]


@api_router.get("/requests/{request_id}", response_model=ServiceRequest)
async def get_request(request_id: str, current_user: Dict = Depends(get_current_user)):
    request = await db.service_requests.find_one({"_id": ObjectId(request_id)})
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    request["_id"] = str(request["_id"])
    return ServiceRequest(**request)


@api_router.post("/requests/{request_id}/assign")
async def assign_technician(
    request_id: str,
    technician_id: str,
    current_user: Dict = Depends(require_role([UserRole.DISPATCHER]))
):
    request = await db.service_requests.find_one({"_id": ObjectId(request_id)})
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Update request
    await db.service_requests.update_one(
        {"_id": ObjectId(request_id)},
        {
            "$set": {"status": JobStatus.ASSIGNED},
            "$push": {"assigned_technician_ids": technician_id}
        }
    )
    
    # Create job
    job_dict = {
        "request_id": request_id,
        "technician_id": technician_id,
        "status": JobStatus.ASSIGNED,
        "photos": [],
        "parts_used": [],
        "created_at": datetime.utcnow()
    }
    result = await db.jobs.insert_one(job_dict)
    
    logger.info(f"Request {request_id} assigned to technician {technician_id}")
    return {"message": "Technician assigned successfully", "job_id": str(result.inserted_id)}


# ==================== TECHNICIAN ROUTES ====================

@api_router.post("/technicians/profile", response_model=TechnicianProfile)
async def create_technician_profile(
    profile_data: TechnicianProfileCreate,
    current_user: Dict = Depends(require_role([UserRole.TECHNICIAN]))
):
    profile_dict = profile_data.dict()
    profile_dict["user_id"] = current_user["_id"]
    profile_dict["rating_avg"] = 0.0
    profile_dict["rating_count"] = 0
    profile_dict["available"] = True
    
    result = await db.technician_profiles.insert_one(profile_dict)
    profile_dict["_id"] = str(result.inserted_id)
    return TechnicianProfile(**profile_dict)


@api_router.get("/technicians", response_model=List[TechnicianProfile])
async def get_technicians(current_user: Dict = Depends(require_role([UserRole.DISPATCHER, UserRole.ADMIN]))):
    technicians = await db.technician_profiles.find({"available": True}).to_list(100)
    return [TechnicianProfile(**{**t, "_id": str(t["_id"])}) for t in technicians]


@api_router.get("/technicians/jobs")
async def get_technician_jobs(current_user: Dict = Depends(require_role([UserRole.TECHNICIAN]))):
    jobs = await db.jobs.find({"technician_id": current_user["_id"]}).sort("created_at", -1).to_list(100)
    return [Job(**{**j, "_id": str(j["_id"])}) for j in jobs]


@api_router.post("/jobs/{job_id}/accept")
async def accept_job(job_id: str, current_user: Dict = Depends(require_role([UserRole.TECHNICIAN]))):
    job = await db.jobs.find_one({"_id": ObjectId(job_id), "technician_id": current_user["_id"]})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    await db.jobs.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {"status": JobStatus.EN_ROUTE}}
    )
    
    await db.service_requests.update_one(
        {"_id": ObjectId(job["request_id"])},
        {"$set": {"status": JobStatus.EN_ROUTE}}
    )
    
    return {"message": "Job accepted"}


@api_router.post("/jobs/{job_id}/photos")
async def upload_photo(
    job_id: str,
    photo: PhotoCapture,
    current_user: Dict = Depends(require_role([UserRole.TECHNICIAN]))
):
    job = await db.jobs.find_one({"_id": ObjectId(job_id), "technician_id": current_user["_id"]})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    await db.jobs.update_one(
        {"_id": ObjectId(job_id)},
        {"$push": {"photos": photo.dict()}}
    )
    
    if photo.phase == "BEFORE":
        await db.jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {"status": JobStatus.ON_SITE}}
        )
        await db.service_requests.update_one(
            {"_id": ObjectId(job["request_id"])},
            {"$set": {"status": JobStatus.ON_SITE}}
        )
    
    return {"message": "Photo uploaded successfully"}


@api_router.post("/jobs/{job_id}/complete")
async def complete_job(
    job_id: str,
    report: CompletionReport,
    current_user: Dict = Depends(require_role([UserRole.TECHNICIAN]))
):
    job = await db.jobs.find_one({"_id": ObjectId(job_id), "technician_id": current_user["_id"]})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    await db.jobs.update_one(
        {"_id": ObjectId(job_id)},
        {
            "$set": {
                "status": JobStatus.COMPLETION_PENDING,
                "completion_report": report.dict(),
                "parts_used": [part.dict() for part in report.parts_used],
                "completed_at": datetime.utcnow()
            }
        }
    )
    
    await db.service_requests.update_one(
        {"_id": ObjectId(job["request_id"])},
        {"$set": {"status": JobStatus.COMPLETION_PENDING}}
    )
    
    return {"message": "Job completed, awaiting customer confirmation"}


@api_router.post("/jobs/{job_id}/close")
async def close_job(
    job_id: str,
    rating: int,
    review: Optional[str] = None,
    current_user: Dict = Depends(require_role([UserRole.CUSTOMER]))
):
    job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    request = await db.service_requests.find_one({"_id": ObjectId(job["request_id"])})
    if request["customer_id"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await db.jobs.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {"status": JobStatus.CLOSED, "rating": rating, "review": review}}
    )
    
    await db.service_requests.update_one(
        {"_id": ObjectId(job["request_id"])},
        {"$set": {"status": JobStatus.CLOSED}}
    )
    
    # Update technician rating
    tech_profile = await db.technician_profiles.find_one({"user_id": job["technician_id"]})
    if tech_profile:
        new_count = tech_profile.get("rating_count", 0) + 1
        new_avg = ((tech_profile.get("rating_avg", 0) * tech_profile.get("rating_count", 0)) + rating) / new_count
        await db.technician_profiles.update_one(
            {"user_id": job["technician_id"]},
            {"$set": {"rating_avg": new_avg, "rating_count": new_count}}
        )
    
    return {"message": "Job closed successfully"}


# ==================== PROMOTIONS ROUTES ====================

@api_router.post("/promotions", response_model=Promotion)
async def create_promotion(
    promo: PromotionCreate,
    current_user: Dict = Depends(require_role([UserRole.ADMIN]))
):
    promo_dict = promo.dict()
    promo_dict["active"] = True
    promo_dict["used_count"] = 0
    
    result = await db.promotions.insert_one(promo_dict)
    promo_dict["_id"] = str(result.inserted_id)
    return Promotion(**promo_dict)


@api_router.get("/promotions", response_model=List[Promotion])
async def get_promotions(current_user: Dict = Depends(require_role([UserRole.ADMIN]))):
    promos = await db.promotions.find().to_list(100)
    return [Promotion(**{**p, "_id": str(p["_id"])}) for p in promos]


@api_router.post("/promotions/validate")
async def validate_coupon(code: str):
    promo = await db.promotions.find_one({
        "code": code,
        "active": True,
        "effective_start": {"$lte": datetime.utcnow()},
        "effective_end": {"$gte": datetime.utcnow()}
    })
    if not promo:
        raise HTTPException(status_code=404, detail="Invalid or expired coupon")
    
    promo["_id"] = str(promo["_id"])
    return Promotion(**promo)


# ==================== ANALYTICS ROUTES ====================

@api_router.get("/analytics/summary")
async def get_analytics(current_user: Dict = Depends(require_role([UserRole.ADMIN]))):
    total_requests = await db.service_requests.count_documents({})
    completed_jobs = await db.jobs.count_documents({"status": JobStatus.CLOSED})
    active_technicians = await db.technician_profiles.count_documents({"available": True})
    
    # Revenue calculation
    invoices = await db.invoices.find({"payment_status": "PAID"}).to_list(1000)
    total_revenue = sum(inv.get("total", 0) for inv in invoices)
    
    return {
        "total_requests": total_requests,
        "completed_jobs": completed_jobs,
        "active_technicians": active_technicians,
        "total_revenue": total_revenue
    }


# ==================== PAYMENT ROUTES (MOCKED) ====================

@api_router.post("/payments/initiate")
async def initiate_payment(
    job_id: str,
    current_user: Dict = Depends(require_role([UserRole.CUSTOMER]))
):
    """Mock PayTabs payment initiation"""
    job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    request = await db.service_requests.find_one({"_id": ObjectId(job["request_id"])})
    if request["customer_id"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Mock payment URL
    logger.info(f"Mock payment initiated for job {job_id}")
    return {
        "payment_url": f"https://mock-paytabs.com/pay/{job_id}",
        "transaction_id": f"MOCK-{job_id}",
        "amount": request["total_amount"]
    }


@api_router.post("/payments/webhook")
async def payment_webhook(payload: Dict[Any, Any]):
    """Mock PayTabs webhook"""
    logger.info(f"Payment webhook received: {payload}")
    # In production, verify webhook signature and update payment status
    return {"status": "received"}


# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
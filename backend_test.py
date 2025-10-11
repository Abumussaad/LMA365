#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Vehicle Maintenance App
Tests all authentication, service catalog, request flow, and job management functionality
"""

import requests
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import sys

# Configuration
BASE_URL = "https://mobile-repair-2.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

# Test data
TEST_USERS = {
    "customer": {"email": "customer@test.com", "password": "password123", "role": "customer", "full_name": "Test Customer"},
    "dispatcher": {"email": "dispatcher@test.com", "password": "password123", "role": "dispatcher", "full_name": "Test Dispatcher"},
    "technician": {"email": "technician@test.com", "password": "password123", "role": "technician", "full_name": "Test Technician"},
    "admin": {"email": "admin@test.com", "password": "password123", "role": "admin", "full_name": "Test Admin"}
}

# Global variables to store tokens and IDs
tokens = {}
user_ids = {}
service_ids = []
request_id = None
job_id = None
technician_profile_id = None

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def log_success(self, test_name: str):
        print(f"✅ {test_name}")
        self.passed += 1
    
    def log_failure(self, test_name: str, error: str):
        print(f"❌ {test_name}: {error}")
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY: {self.passed}/{total} tests passed")
        if self.errors:
            print(f"\nFAILED TESTS:")
            for error in self.errors:
                print(f"  - {error}")
        print(f"{'='*60}")
        return self.failed == 0

result = TestResult()

def make_request(method: str, endpoint: str, data: Optional[Dict] = None, token: Optional[str] = None) -> requests.Response:
    """Make HTTP request with proper headers and error handling"""
    url = f"{BASE_URL}{endpoint}"
    headers = HEADERS.copy()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=30)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        raise

def test_user_registration():
    """Test user registration for all roles"""
    print("\n🔐 Testing User Registration...")
    
    for role, user_data in TEST_USERS.items():
        try:
            response = make_request("POST", "/auth/register", user_data)
            
            if response.status_code == 201 or response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    tokens[role] = data["access_token"]
                    user_ids[role] = data["user"]["_id"]
                    result.log_success(f"Register {role}")
                else:
                    result.log_failure(f"Register {role}", "Missing token or user in response")
            elif response.status_code == 400 and "already registered" in response.text:
                # User already exists, try to login instead
                login_response = make_request("POST", "/auth/login", {
                    "email": user_data["email"],
                    "password": user_data["password"]
                })
                if login_response.status_code == 200:
                    data = login_response.json()
                    tokens[role] = data["access_token"]
                    user_ids[role] = data["user"]["_id"]
                    result.log_success(f"Register {role} (existing user)")
                else:
                    result.log_failure(f"Register {role}", f"Login failed: {login_response.status_code}")
            else:
                result.log_failure(f"Register {role}", f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            result.log_failure(f"Register {role}", str(e))

def test_user_login():
    """Test user login for all roles"""
    print("\n🔑 Testing User Login...")
    
    for role, user_data in TEST_USERS.items():
        try:
            login_data = {"email": user_data["email"], "password": user_data["password"]}
            response = make_request("POST", "/auth/login", login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    tokens[role] = data["access_token"]
                    user_ids[role] = data["user"]["_id"]
                    result.log_success(f"Login {role}")
                else:
                    result.log_failure(f"Login {role}", "Missing token or user in response")
            else:
                result.log_failure(f"Login {role}", f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            result.log_failure(f"Login {role}", str(e))

def test_jwt_validation():
    """Test JWT token validation"""
    print("\n🎫 Testing JWT Token Validation...")
    
    for role in TEST_USERS.keys():
        if role in tokens:
            try:
                response = make_request("GET", "/auth/me", token=tokens[role])
                if response.status_code == 200:
                    data = response.json()
                    if data.get("role") == role:
                        result.log_success(f"JWT validation {role}")
                    else:
                        result.log_failure(f"JWT validation {role}", f"Role mismatch: expected {role}, got {data.get('role')}")
                else:
                    result.log_failure(f"JWT validation {role}", f"Status: {response.status_code}")
            except Exception as e:
                result.log_failure(f"JWT validation {role}", str(e))

def test_role_based_access():
    """Test role-based access control"""
    print("\n🛡️ Testing Role-Based Access Control...")
    
    # Test customer trying to access admin route
    if "customer" in tokens:
        try:
            response = make_request("GET", "/promotions", token=tokens["customer"])
            if response.status_code == 403:
                result.log_success("RBAC: Customer blocked from admin route")
            else:
                result.log_failure("RBAC: Customer blocked from admin route", f"Expected 403, got {response.status_code}")
        except Exception as e:
            result.log_failure("RBAC: Customer blocked from admin route", str(e))

def test_service_catalog():
    """Test service catalog functionality"""
    print("\n🛠️ Testing Service Catalog...")
    global service_ids
    
    # First, create some services as admin
    if "admin" in tokens:
        test_services = [
            {"name": "Oil Change", "category": "Maintenance", "base_price": 50.0, "description": "Standard oil change", "duration_minutes": 30},
            {"name": "Brake Inspection", "category": "Safety", "base_price": 75.0, "description": "Complete brake system check", "duration_minutes": 45},
            {"name": "Tire Rotation", "category": "Maintenance", "base_price": 40.0, "description": "Rotate all four tires", "duration_minutes": 20},
            {"name": "Battery Test", "category": "Electrical", "base_price": 25.0, "description": "Battery health check", "duration_minutes": 15},
            {"name": "Air Filter Replacement", "category": "Maintenance", "base_price": 35.0, "description": "Replace engine air filter", "duration_minutes": 10},
            {"name": "Coolant Flush", "category": "Maintenance", "base_price": 80.0, "description": "Complete coolant system flush", "duration_minutes": 60}
        ]
        
        for service in test_services:
            try:
                response = make_request("POST", "/services", service, token=tokens["admin"])
                if response.status_code in [200, 201]:
                    data = response.json()
                    service_ids.append(data["_id"])
                    result.log_success(f"Create service: {service['name']}")
                else:
                    result.log_failure(f"Create service: {service['name']}", f"Status: {response.status_code}")
            except Exception as e:
                result.log_failure(f"Create service: {service['name']}", str(e))
    
    # Test getting services (public endpoint)
    try:
        response = make_request("GET", "/services")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) >= 6:
                result.log_success("Get services list")
                # Store service IDs for later use
                service_ids.extend([service["_id"] for service in data[:6]])
            else:
                result.log_failure("Get services list", f"Expected list with 6+ services, got {len(data) if isinstance(data, list) else 'not a list'}")
        else:
            result.log_failure("Get services list", f"Status: {response.status_code}")
    except Exception as e:
        result.log_failure("Get services list", str(e))
    
    # Test non-admin user cannot create services
    if "customer" in tokens:
        try:
            test_service = {"name": "Unauthorized Service", "category": "Test", "base_price": 100.0}
            response = make_request("POST", "/services", test_service, token=tokens["customer"])
            if response.status_code == 403:
                result.log_success("RBAC: Customer blocked from creating services")
            else:
                result.log_failure("RBAC: Customer blocked from creating services", f"Expected 403, got {response.status_code}")
        except Exception as e:
            result.log_failure("RBAC: Customer blocked from creating services", str(e))

def test_technician_profile():
    """Create technician profile for testing"""
    print("\n👨‍🔧 Testing Technician Profile...")
    global technician_profile_id
    
    if "technician" in tokens:
        try:
            profile_data = {
                "vehicle_number": "TECH-001",
                "skills": ["Oil Change", "Brake Repair", "Electrical"]
            }
            response = make_request("POST", "/technicians/profile", profile_data, token=tokens["technician"])
            if response.status_code in [200, 201]:
                data = response.json()
                technician_profile_id = data["_id"]
                result.log_success("Create technician profile")
            else:
                result.log_failure("Create technician profile", f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            result.log_failure("Create technician profile", str(e))

def test_promotions():
    """Test promotions functionality"""
    print("\n🎁 Testing Promotions...")
    
    if "admin" in tokens:
        # Create test promotions
        test_promotions = [
            {
                "code": "WELCOME20",
                "discount_type": "PERCENT",
                "discount_value": 20.0,
                "effective_start": datetime.utcnow().isoformat(),
                "effective_end": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "min_spend": 0.0
            },
            {
                "code": "SAVE50",
                "discount_type": "FIXED_AMOUNT",
                "discount_value": 50.0,
                "effective_start": datetime.utcnow().isoformat(),
                "effective_end": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "min_spend": 100.0
            },
            {
                "code": "SUMMER25",
                "discount_type": "PERCENT",
                "discount_value": 25.0,
                "effective_start": datetime.utcnow().isoformat(),
                "effective_end": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "min_spend": 75.0
            }
        ]
        
        for promo in test_promotions:
            try:
                response = make_request("POST", "/promotions", promo, token=tokens["admin"])
                if response.status_code in [200, 201]:
                    result.log_success(f"Create promotion: {promo['code']}")
                else:
                    result.log_failure(f"Create promotion: {promo['code']}", f"Status: {response.status_code}")
            except Exception as e:
                result.log_failure(f"Create promotion: {promo['code']}", str(e))
        
        # Test getting promotions
        try:
            response = make_request("GET", "/promotions", token=tokens["admin"])
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    result.log_success("Get promotions list")
                else:
                    result.log_failure("Get promotions list", "Response is not a list")
            else:
                result.log_failure("Get promotions list", f"Status: {response.status_code}")
        except Exception as e:
            result.log_failure("Get promotions list", str(e))
    
    # Test coupon validation
    try:
        response = make_request("POST", "/promotions/validate?code=WELCOME20")
        if response.status_code == 200:
            result.log_success("Validate coupon: WELCOME20")
        else:
            result.log_failure("Validate coupon: WELCOME20", f"Status: {response.status_code}")
    except Exception as e:
        result.log_failure("Validate coupon: WELCOME20", str(e))

def test_service_requests():
    """Test service request creation and management"""
    print("\n📋 Testing Service Requests...")
    global request_id
    
    if "customer" in tokens and service_ids:
        # Test request with coupon
        try:
            request_data = {
                "vehicle_plate": "ABC-123",
                "vehicle_make": "Toyota",
                "vehicle_model": "Camry",
                "location": {
                    "latitude": 25.2048,
                    "longitude": 55.2708,
                    "address": "Dubai Marina, Dubai, UAE"
                },
                "scheduled_time": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
                "services": [
                    {"service_id": service_ids[0], "quantity": 1},
                    {"service_id": service_ids[1], "quantity": 1},
                    {"service_id": service_ids[2], "quantity": 1}
                ],
                "notes": "Please call before arrival",
                "coupon_code": "TESTDISCOUNT"
            }
            
            response = make_request("POST", "/requests", request_data, token=tokens["customer"])
            if response.status_code in [200, 201]:
                data = response.json()
                request_id = data["_id"]
                if data.get("discount_amount", 0) > 0:
                    result.log_success("Create service request with coupon")
                else:
                    result.log_failure("Create service request with coupon", "No discount applied")
            else:
                result.log_failure("Create service request with coupon", f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            result.log_failure("Create service request with coupon", str(e))
        
        # Test request without coupon
        try:
            request_data_no_coupon = {
                "vehicle_plate": "XYZ-789",
                "vehicle_make": "Honda",
                "vehicle_model": "Civic",
                "location": {
                    "latitude": 25.1972,
                    "longitude": 55.2744,
                    "address": "JBR, Dubai, UAE"
                },
                "scheduled_time": (datetime.utcnow() + timedelta(hours=3)).isoformat(),
                "services": [
                    {"service_id": service_ids[0], "quantity": 1}
                ],
                "notes": "Standard service"
            }
            
            response = make_request("POST", "/requests", request_data_no_coupon, token=tokens["customer"])
            if response.status_code in [200, 201]:
                result.log_success("Create service request without coupon")
            else:
                result.log_failure("Create service request without coupon", f"Status: {response.status_code}")
        except Exception as e:
            result.log_failure("Create service request without coupon", str(e))
        
        # Test customer viewing own requests
        try:
            response = make_request("GET", "/requests", token=tokens["customer"])
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) >= 1:
                    result.log_success("Customer view own requests")
                else:
                    result.log_failure("Customer view own requests", f"Expected list with requests, got {len(data) if isinstance(data, list) else 'not a list'}")
            else:
                result.log_failure("Customer view own requests", f"Status: {response.status_code}")
        except Exception as e:
            result.log_failure("Customer view own requests", str(e))
    
    # Test dispatcher viewing all requests
    if "dispatcher" in tokens:
        try:
            response = make_request("GET", "/requests", token=tokens["dispatcher"])
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    result.log_success("Dispatcher view all requests")
                else:
                    result.log_failure("Dispatcher view all requests", "Response is not a list")
            else:
                result.log_failure("Dispatcher view all requests", f"Status: {response.status_code}")
        except Exception as e:
            result.log_failure("Dispatcher view all requests", str(e))

def test_technician_assignment():
    """Test technician assignment by dispatcher"""
    print("\n👥 Testing Technician Assignment...")
    global job_id
    
    if "dispatcher" in tokens and request_id and "technician" in user_ids:
        # Get available technicians
        try:
            response = make_request("GET", "/technicians", token=tokens["dispatcher"])
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    result.log_success("Get available technicians")
                else:
                    result.log_failure("Get available technicians", "Response is not a list")
            else:
                result.log_failure("Get available technicians", f"Status: {response.status_code}")
        except Exception as e:
            result.log_failure("Get available technicians", str(e))
        
        # Assign technician to request
        try:
            response = make_request("POST", f"/requests/{request_id}/assign?technician_id={user_ids['technician']}", token=tokens["dispatcher"])
            if response.status_code == 200:
                data = response.json()
                if "job_id" in data:
                    job_id = data["job_id"]
                    result.log_success("Assign technician to request")
                else:
                    result.log_failure("Assign technician to request", "No job_id in response")
            else:
                result.log_failure("Assign technician to request", f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            result.log_failure("Assign technician to request", str(e))

def test_technician_job_flow():
    """Test complete technician job workflow"""
    print("\n🔧 Testing Technician Job Flow...")
    
    if "technician" in tokens and job_id:
        # Get technician jobs
        try:
            response = make_request("GET", "/technicians/jobs", token=tokens["technician"])
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) >= 1:
                    result.log_success("Get technician jobs")
                else:
                    result.log_failure("Get technician jobs", f"Expected list with jobs, got {len(data) if isinstance(data, list) else 'not a list'}")
            else:
                result.log_failure("Get technician jobs", f"Status: {response.status_code}")
        except Exception as e:
            result.log_failure("Get technician jobs", str(e))
        
        # Accept job
        try:
            response = make_request("POST", f"/jobs/{job_id}/accept", token=tokens["technician"])
            if response.status_code == 200:
                result.log_success("Accept job")
            else:
                result.log_failure("Accept job", f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            result.log_failure("Accept job", str(e))
        
        # Upload BEFORE photo
        try:
            # Create mock base64 image data
            mock_image = base64.b64encode(b"mock_image_data").decode('utf-8')
            photo_data = {
                "phase": "BEFORE",
                "image_base64": mock_image,
                "location": {
                    "latitude": 25.2048,
                    "longitude": 55.2708,
                    "address": "Dubai Marina, Dubai, UAE"
                }
            }
            response = make_request("POST", f"/jobs/{job_id}/photos", photo_data, token=tokens["technician"])
            if response.status_code == 200:
                result.log_success("Upload BEFORE photo")
            else:
                result.log_failure("Upload BEFORE photo", f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            result.log_failure("Upload BEFORE photo", str(e))
        
        # Complete job
        try:
            completion_data = {
                "labor_minutes": 45,
                "parts_used": [
                    {
                        "part_id": "OIL-001",
                        "part_name": "Engine Oil 5W-30",
                        "quantity": 1,
                        "unit_price": 25.0
                    },
                    {
                        "part_id": "FILTER-001",
                        "part_name": "Oil Filter",
                        "quantity": 1,
                        "unit_price": 15.0
                    }
                ],
                "notes": "Service completed successfully",
                "customer_signature": "mock_signature_data"
            }
            response = make_request("POST", f"/jobs/{job_id}/complete", completion_data, token=tokens["technician"])
            if response.status_code == 200:
                result.log_success("Complete job")
            else:
                result.log_failure("Complete job", f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            result.log_failure("Complete job", str(e))

def test_customer_closeout():
    """Test customer job closeout and rating"""
    print("\n⭐ Testing Customer Closeout...")
    
    if "customer" in tokens and job_id:
        try:
            closeout_data = {
                "review": "Excellent service! Very professional and quick."
            }
            response = make_request("POST", f"/jobs/{job_id}/close?rating=5", closeout_data, token=tokens["customer"])
            if response.status_code == 200:
                result.log_success("Customer close job with rating")
            else:
                result.log_failure("Customer close job with rating", f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            result.log_failure("Customer close job with rating", str(e))

def test_analytics():
    """Test analytics dashboard"""
    print("\n📊 Testing Analytics...")
    
    if "admin" in tokens:
        try:
            response = make_request("GET", "/analytics/summary", token=tokens["admin"])
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_requests", "completed_jobs", "active_technicians", "total_revenue"]
                if all(field in data for field in required_fields):
                    result.log_success("Get analytics summary")
                else:
                    missing = [field for field in required_fields if field not in data]
                    result.log_failure("Get analytics summary", f"Missing fields: {missing}")
            else:
                result.log_failure("Get analytics summary", f"Status: {response.status_code}")
        except Exception as e:
            result.log_failure("Get analytics summary", str(e))

def main():
    """Run all tests"""
    print(f"🚀 Starting Vehicle Maintenance App Backend Tests")
    print(f"Base URL: {BASE_URL}")
    print("="*60)
    
    try:
        # Authentication Tests
        test_user_registration()
        test_user_login()
        test_jwt_validation()
        test_role_based_access()
        
        # Service Catalog Tests
        test_service_catalog()
        
        # Technician Profile Setup
        test_technician_profile()
        
        # Promotions Tests
        test_promotions()
        
        # Service Request Flow Tests
        test_service_requests()
        
        # Assignment and Job Flow Tests
        test_technician_assignment()
        test_technician_job_flow()
        test_customer_closeout()
        
        # Analytics Tests
        test_analytics()
        
        # Final summary
        success = result.summary()
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n💥 Critical error during testing: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
# 📋 Updated User Roles & Requirements (LMA365)

## Additional Specifications from LMA365.docx

This document supplements the original requirements with detailed role specifications from the uploaded document.

---

## 👥 Detailed User Roles

### 1. Administrator

**Core Responsibilities:**
- ✅ Managing users and their access
- ✅ Adding/managing services with:
  - Service type
  - Estimated time to complete
  - **Parts required** (inventory items needed)
  - Service cost
- ✅ Issuing promotions and coupons with:
  - Active periods
  - Specific start/end dates
- ✅ Issuing account statements and invoices
- ✅ Granting access to corporate customer users

**Already Implemented:**
- ✅ User management (via registration)
- ✅ Service catalog with pricing and duration
- ✅ Promotions with date ranges and codes
- ✅ Analytics dashboard

**Additional Features Needed:**
- 🔄 **Parts required field** in service definition
- 🔄 **User access management UI** (grant/revoke access)
- 🔄 **Account statements** generation
- 🔄 **Corporate user provisioning**

---

### 2. Customer (Two Types)

#### a) Individual Customer

**Registration & Features:**
- ✅ Self-registration through registration screen
- 🔄 **Add vehicle(s) data** with:
  - Make
  - Model
  - Year
  - VIN
  - Plate number
  - Odometer
- 🔄 **Multiple vehicles** per customer
- ✅ Request service(s) for registered vehicles

**Current Implementation:**
- ✅ Registration screen exists
- ✅ Can create service requests
- ⚠️ Vehicle data only captures: plate, make, model (missing: year, VIN, odometer)
- ⚠️ No vehicle list management (can't add multiple vehicles)

**Additional Features Needed:**
- 🔄 **Vehicle management screen** (add, edit, delete vehicles)
- 🔄 **Vehicle data fields**: Year, VIN, Odometer
- 🔄 **Select from my vehicles** when creating request

#### b) Corporate Customer

**Special Features:**
- 🔄 Users **granted by administrator** (not self-registration)
- 🔄 **Excel import** for vehicle list
- 🔄 Bulk vehicle registration
- 🔄 Corporate account management

**Required Fields in Excel Import:**
- Make
- Model
- Year
- VIN
- Plate number
- Odometer

**Current Implementation:**
- ⚠️ No distinction between individual and corporate customers
- ⚠️ No Excel import feature
- ⚠️ No corporate account structure

**Additional Features Needed:**
- 🔄 **Corporate account type** in user model
- 🔄 **Excel import endpoint** for vehicles
- 🔄 **Admin UI** to grant corporate user access
- 🔄 **Corporate dashboard** for fleet management

---

### 3. Dispatcher

**Core Responsibilities:**
- ✅ Managing service requests
- ✅ Assigning service jobs to technician (or service van)
- 🔄 **Adding technician and service van data**
- ✅ Accessing active, completed, and canceled service jobs
- 🔄 **Changing assignment** of service jobs
- 🔄 **Performance reports** (daily, weekly, monthly, or custom period)

**Current Implementation:**
- ✅ View all service requests
- ✅ View available technicians
- ✅ Assign technicians to requests
- ✅ Can see job statuses

**Additional Features Needed:**
- 🔄 **Add/edit technician UI** (currently only profile creation)
- 🔄 **Service van management** (register vans, assign to technicians)
- 🔄 **Reassign jobs** after initial assignment
- 🔄 **Performance reports** with filters:
  - Daily report
  - Weekly report
  - Monthly report
  - Custom date range
  - Metrics: completed jobs, avg time, technician performance, revenue

---

## 🆕 New Features Required

### 1. Vehicle Management System

**Database Schema:**
```python
class Vehicle(BaseModel):
    id: Optional[str]
    customer_id: str
    make: str
    model: str
    year: int  # NEW
    vin: str  # NEW (Vehicle Identification Number)
    plate_number: str
    odometer: int  # NEW (in kilometers or miles)
    created_at: datetime
    updated_at: datetime
```

**API Endpoints:**
```
POST   /api/vehicles                 # Add vehicle
GET    /api/vehicles                 # List my vehicles
GET    /api/vehicles/{vehicle_id}    # Get vehicle details
PUT    /api/vehicles/{vehicle_id}    # Update vehicle
DELETE /api/vehicles/{vehicle_id}    # Delete vehicle
```

**Frontend Screens (Flutter):**
- Vehicle list screen
- Add vehicle screen
- Edit vehicle screen
- Vehicle detail screen

---

### 2. Corporate Customer System

**Database Schema:**
```python
class User(BaseModel):
    # ... existing fields
    account_type: str  # "individual" or "corporate"
    corporate_account_id: Optional[str]  # If corporate user
    
class CorporateAccount(BaseModel):
    id: Optional[str]
    company_name: str
    contact_email: str
    contact_phone: str
    billing_address: str
    payment_terms: str  # "prepaid" or "monthly"
    created_at: datetime
    active: bool
```

**API Endpoints:**
```
# Admin only
POST   /api/corporate-accounts              # Create corporate account
GET    /api/corporate-accounts              # List all corporate accounts
POST   /api/corporate-accounts/{id}/users   # Grant user access
POST   /api/vehicles/import                 # Import vehicles from Excel
```

**Excel Import Format:**
```
| Make   | Model  | Year | VIN              | Plate Number | Odometer |
|--------|--------|------|------------------|--------------|----------|
| Toyota | Camry  | 2020 | 1HGBH41JXMN109186| ABC-1234    | 45000    |
```

---

### 3. Service Van Management

**Database Schema:**
```python
class ServiceVan(BaseModel):
    id: Optional[str]
    van_number: str
    make: str
    model: str
    year: int
    plate_number: str
    assigned_technician_id: Optional[str]
    current_location: Optional[LocationData]
    active: bool
    created_at: datetime
```

**API Endpoints:**
```
POST   /api/service-vans              # Add service van
GET    /api/service-vans              # List all vans
PUT    /api/service-vans/{van_id}     # Update van
POST   /api/service-vans/{van_id}/assign/{tech_id}  # Assign to technician
```

---

### 4. Job Reassignment

**API Endpoint:**
```
POST   /api/jobs/{job_id}/reassign
Content-Type: application/json

{
  "new_technician_id": "68e9a0638c17ec10320e86b1",
  "reason": "Original technician unavailable"
}
```

**Business Logic:**
- Only dispatcher can reassign
- Can't reassign completed jobs
- Notify both technicians
- Log reassignment in audit trail

---

### 5. Performance Reports

**API Endpoint:**
```
GET /api/reports/performance?period=daily&start_date=2025-01-01&end_date=2025-01-31

Response:
{
  "period": "daily",
  "start_date": "2025-01-01",
  "end_date": "2025-01-31",
  "total_jobs": 150,
  "completed_jobs": 145,
  "canceled_jobs": 5,
  "total_revenue": 45000.00,
  "avg_completion_time_minutes": 52,
  "technician_performance": [
    {
      "technician_id": "...",
      "technician_name": "Mohammed Al-Otaibi",
      "jobs_completed": 45,
      "avg_rating": 4.8,
      "total_revenue": 13500.00
    }
  ],
  "daily_breakdown": [...]
}
```

**Report Types:**
- Daily: Group by day
- Weekly: Group by week
- Monthly: Group by month
- Custom: User-specified date range

---

## 🔄 Updated Service Model

**Enhanced Service Schema:**
```python
class ServiceItem(BaseModel):
    id: Optional[str]
    name: str
    category: str
    base_price: float
    description: Optional[str]
    duration_minutes: int
    required_parts: List[str]  # NEW: List of part IDs/names
    active: bool
```

---

## 📊 Summary of Changes Needed

### Backend Updates:

1. **Vehicle Management** (NEW)
   - Add Vehicle model with all fields
   - CRUD endpoints for vehicles
   - Excel import for corporate customers

2. **Corporate Accounts** (NEW)
   - CorporateAccount model
   - Admin endpoints to manage corporate accounts
   - Grant user access functionality

3. **Service Van Management** (NEW)
   - ServiceVan model
   - CRUD endpoints
   - Assignment to technicians

4. **Job Reassignment** (NEW)
   - Reassignment endpoint
   - Business logic for reassignment rules

5. **Performance Reports** (NEW)
   - Analytics aggregation
   - Multiple report types (daily, weekly, monthly, custom)
   - Technician performance metrics

6. **Enhanced Service Model** (UPDATE)
   - Add required_parts field
   - Update service creation/update endpoints

### Frontend (Flutter) Screens Needed:

**Customer:**
- ✅ Login/Register (existing)
- 🔄 **Vehicle List** (new)
- 🔄 **Add/Edit Vehicle** (new)
- ✅ Service Request (update to select from vehicles)
- ✅ Request List (existing)

**Dispatcher:**
- ✅ Dashboard (existing)
- ✅ Assign Technician (existing)
- 🔄 **Reassign Job** (new)
- 🔄 **Add Technician** (new)
- 🔄 **Manage Service Vans** (new)
- 🔄 **Performance Reports** (new)

**Admin:**
- ✅ Service Catalog (existing)
- ✅ Promotions (existing)
- 🔄 **User Management** (new)
- 🔄 **Corporate Accounts** (new)
- 🔄 **Grant Access** (new)
- 🔄 **Account Statements** (new)

**Technician:**
- ✅ Job List (existing)
- ✅ Accept/Complete Jobs (existing)
- ✅ Photo Upload (existing)

---

## 🎯 Priority Implementation Order

**Phase 1: Core Enhancements** (High Priority)
1. Vehicle management system
2. Update service request to use vehicles
3. Enhanced service model with required parts

**Phase 2: Corporate Features** (Medium Priority)
4. Corporate account system
5. Excel import for vehicles
6. User access management

**Phase 3: Operational Features** (Medium Priority)
7. Service van management
8. Job reassignment
9. Performance reports

**Phase 4: Financial Features** (Lower Priority)
10. Account statements generation
11. Enhanced invoicing

---

## 📝 Notes for Flutter Implementation

1. **Vehicle Management**: Create a dedicated vehicle module with CRUD operations
2. **Excel Import**: Use `excel` package in Flutter for reading/parsing Excel files
3. **Corporate vs Individual**: Show different UIs based on account_type
4. **Reports**: Use charts package (fl_chart) for visualizing performance data
5. **Service Van Tracking**: Consider using maps for real-time van location

---

## ✅ What's Already Implemented

From the original requirements, these are complete:
- ✅ User authentication (login/register)
- ✅ Service catalog
- ✅ Service request creation (basic)
- ✅ Technician assignment
- ✅ Job workflow (accept, photos, complete)
- ✅ Rating system
- ✅ Promotions/coupons with dates
- ✅ Basic analytics

**Backend is 90% complete for MVP. The additional features above are enhancements based on LMA365 specification.**

---

**Next Steps:**
1. Review this specification
2. Prioritize which features to implement first
3. I can update the backend API to include these new features
4. You can build the Flutter frontend against the enhanced API

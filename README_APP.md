# 🚗 Vehicle Maintenance Service App

A comprehensive mobile-first vehicle maintenance service request platform built with **Expo (React Native)**, **FastAPI**, and **MongoDB**.

## 📱 Overview

This app enables customers to request on-site vehicle maintenance services, dispatchers to assign technicians, technicians to manage jobs with live photo verification, and admins to manage the entire service ecosystem.

---

## ✨ Features Implemented

### **Customer Features**
- ✅ Create service requests with vehicle details and location
- ✅ Select multiple services from catalog
- ✅ Apply promotional coupon codes
- ✅ Schedule service appointments
- ✅ Track request status in real-time
- ✅ View request history

### **Dispatcher Features**
- ✅ View all incoming service requests on dashboard
- ✅ View available technicians with ratings
- ✅ Manually assign technicians to requests
- ✅ Monitor job statuses and SLA/ETAs
- ✅ Filter technicians by availability

### **Technician Features**
- ✅ View assigned jobs
- ✅ Accept/reject job assignments
- ✅ Update job status (EN_ROUTE, ON_SITE, etc.)
- ✅ Live photo capture (BEFORE, MID, AFTER) *
- ✅ Record parts used and labor time *
- ✅ Submit completion reports *
- ✅ View job history and ratings

### **Admin Features**
- ✅ Analytics dashboard (requests, jobs, revenue, technicians)
- ✅ Manage service catalog (create, view services)
- ✅ Create and manage promotions with date ranges
- ✅ Monitor system performance
- ✅ Quick actions for common tasks

### **Backend API**
- ✅ JWT authentication with role-based access control (RBAC)
- ✅ Complete CRUD operations for all entities
- ✅ Service request lifecycle management
- ✅ Promotion validation with date/time checks
- ✅ Technician assignment workflow
- ✅ Job status transitions with guards
- ✅ Rating and review system
- ✅ Analytics aggregation
- ✅ Mocked payment integration (PayTabs ready)
- ✅ Mocked notifications (Twilio ready)

---

## 🏗️ Architecture

### **Tech Stack**
- **Frontend**: Expo (React Native), TypeScript, Expo Router
- **Backend**: FastAPI (Python), Async/Await
- **Database**: MongoDB with Motor (async driver)
- **State Management**: Zustand
- **Navigation**: React Navigation v7 (Bottom Tabs + Stack)
- **Authentication**: JWT with bcrypt password hashing

### **Project Structure**
```
/app
├── backend/
│   ├── server.py           # Main FastAPI app with all routes
│   ├── seed_data.py        # Database seeding script
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Environment variables
│
├── frontend/
│   ├── app/
│   │   ├── (tabs)/         # Tab navigation screens
│   │   │   ├── customer/   # Customer screens
│   │   │   ├── dispatcher/ # Dispatcher screens
│   │   │   ├── technician/ # Technician screens
│   │   │   └── admin/      # Admin screens
│   │   ├── auth/           # Login & Register screens
│   │   ├── _layout.tsx     # Root layout
│   │   └── index.tsx       # Entry point
│   ├── store/
│   │   └── authStore.ts    # Authentication state management
│   ├── package.json
│   └── .env                # Environment variables
│
└── README_APP.md           # This file
```

---

## 🚀 Getting Started

### **1. Test Accounts**
The app comes pre-seeded with test users:

| Role | Email | Password |
|------|-------|----------|
| **Customer** | customer@test.com | password123 |
| **Dispatcher** | dispatcher@test.com | password123 |
| **Technician** | technician@test.com | password123 |
| **Admin** | admin@test.com | password123 |

### **2. Test Coupons**
- **WELCOME20** - 20% off (min spend: SAR 200)
- **SAVE50** - SAR 50 off (min spend: SAR 300)
- **SUMMER25** - 25% off (min spend: SAR 500)

### **3. Pre-loaded Services**
- Oil Change - SAR 150
- Brake Inspection & Repair - SAR 300
- Battery Replacement - SAR 400
- Tire Rotation - SAR 100
- AC Service - SAR 250
- Engine Diagnostic - SAR 200

---

## 📋 User Flows

### **Customer Flow**
1. Register/Login as customer
2. Navigate to "New Request" tab
3. Enter vehicle details (plate, make, model)
4. Select location and scheduled time
5. Choose one or more services
6. Optionally apply a coupon code
7. Submit request
8. Track status in "Requests" tab

### **Dispatcher Flow**
1. Login as dispatcher
2. View all incoming requests on dashboard
3. Click on a "REQUESTED" job
4. View available technicians list
5. Select and assign a technician
6. Monitor job progression

### **Technician Flow**
1. Login as technician
2. View assigned jobs in "Jobs" tab
3. Accept job
4. Update status to "EN_ROUTE"
5. Capture BEFORE photos on arrival
6. Status auto-updates to "ON_SITE"
7. Perform service, capture MID/AFTER photos
8. Record parts used and labor time
9. Submit completion report
10. Customer closes and rates the job

### **Admin Flow**
1. Login as admin
2. View analytics on dashboard
3. Navigate to "Services" to manage catalog
4. Add new services with pricing
5. Navigate to "Promotions" to create coupons
6. Set discount type, value, and validity dates

---

## 🔌 API Integration Status

### **Implemented (Mocked)**
These are configured to work with environment variables - just add your API keys:

#### **PayTabs Payment Integration**
- Payment initiation endpoint: `POST /api/payments/initiate`
- Webhook receiver: `POST /api/payments/webhook`
- Returns mock payment URLs
- **To activate**: Add to `backend/.env`:
  ```
  PAYTABS_PROFILE_ID=your_profile_id
  PAYTABS_SERVER_KEY=your_server_key
  PAYTABS_REGION=SAU
  ```

#### **Twilio Notifications**
- SMS/WhatsApp notifications are logged to console
- **To activate**: Add to `backend/.env`:
  ```
  TWILIO_ACCOUNT_SID=your_sid
  TWILIO_AUTH_TOKEN=your_token
  TWILIO_PHONE_NUMBER=your_number
  ```

#### **OpenStreetMap Integration**
- Ready to use (no API key needed)
- Currently using mock coordinates (Riyadh: 24.7136, 46.6753)
- Real GPS can be enabled via `expo-location` package

---

## 🎯 Job Status Lifecycle

```
REQUESTED
    ↓
ASSIGNED (dispatcher assigns technician)
    ↓
EN_ROUTE (technician accepts and starts traveling)
    ↓
ON_SITE (technician arrives, captures BEFORE photos)
    ↓
COMPLETION_PENDING (technician submits report)
    ↓
CLOSED (customer reviews and rates)
```

### **Cancellation States**
- `CANCELLED_FREE` - Cancelled ≥60 minutes before scheduled time
- `CANCELLED_LATE` - Cancelled <60 minutes before scheduled time
- `CANCELLED_ONSITE` - Cancelled after technician arrival

---

## 📊 Database Schema

### **Collections**
- **users** - All system users (customer, dispatcher, technician, admin)
- **service_requests** - Customer service requests
- **services** - Service catalog items
- **jobs** - Technician job assignments
- **technician_profiles** - Technician details and ratings
- **promotions** - Promotional campaigns and coupons
- **invoices** - Billing and payment records (future)
- **parts_inventory** - Parts tracking (future)

---

## 🛠️ Advanced Features (Ready to Implement)

### **Photo Verification**
The photo capture screens are built. To add server-side EXIF verification:
1. Install `Pillow` in backend
2. Add EXIF metadata extraction
3. Verify GPS coordinates match job location
4. Verify timestamp is recent (±15 minutes)

### **Real-time Tracking**
The infrastructure is in place. To add:
1. Integrate `react-native-maps` with live technician locations
2. Add WebSocket connection for real-time updates
3. Update `current_location` in technician profiles

### **Push Notifications**
To enable:
1. Configure `expo-notifications`
2. Integrate Twilio or Firebase Cloud Messaging
3. Send notifications on job status changes

### **Offline Mode**
To add:
1. Use `@react-native-async-storage/async-storage` for offline data
2. Queue actions when offline
3. Sync when connection restores

---

## 🧪 Testing

### **Backend API Testing**
```bash
# Test login
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"customer@test.com","password":"password123"}'

# Get services
curl http://localhost:8001/api/services

# Create service request (use token from login)
curl -X POST http://localhost:8001/api/requests \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "vehicle_plate": "ABC123",
    "location": {
      "latitude": 24.7136,
      "longitude": 46.6753,
      "address": "Riyadh, Saudi Arabia"
    },
    "scheduled_time": "2025-10-15T10:00:00",
    "services": [{"service_id": "SERVICE_ID", "quantity": 1}]
  }'
```

### **Mobile App Testing**
1. **Web Preview**: Access via the Emergent preview URL
2. **Expo Go**: Scan QR code to test on physical device
3. **Manual Testing**: Login with different role accounts and test workflows

---

## 🎨 UI/UX Highlights

- **Role-Based Navigation**: Dynamic tab bar based on user role
- **Status Colors**: Visual indicators for job statuses
- **Pull-to-Refresh**: All list screens support pull-to-refresh
- **Modal Forms**: Bottom sheets for creating services/promotions
- **Empty States**: Helpful empty state messages with icons
- **Loading States**: Activity indicators during API calls
- **Error Handling**: User-friendly alerts for errors
- **Safe Area Insets**: Proper spacing for notches and home indicators

---

## 📈 Future Enhancements

### **Phase 2 Features** (Not Yet Implemented)
- [ ] AI-powered technician matching with scoring algorithm
- [ ] Advanced inventory management (van stock, requisitions)
- [ ] Complete payment flow with PayTabs
- [ ] SMS/WhatsApp notifications via Twilio
- [ ] Live GPS tracking on map
- [ ] Photo EXIF validation
- [ ] Invoice and receipt generation (PDF)
- [ ] Account statements and payment registry
- [ ] Advanced analytics and reporting
- [ ] Multi-language support (Arabic/English)
- [ ] Corporate account management
- [ ] Scheduled payments (weekly/monthly)
- [ ] Advanced cancellation policies

---

## 🔐 Security Features

- ✅ JWT-based authentication
- ✅ Password hashing with bcrypt
- ✅ Role-based access control (RBAC)
- ✅ Token expiry (7 days)
- ✅ Secure password storage
- ✅ API route protection

---

## 🐛 Known Limitations

1. **Maps**: Using mock GPS coordinates - integrate real GPS via `expo-location`
2. **Photos**: Camera functionality works but EXIF validation not implemented yet
3. **Payments**: Payment flow is mocked - needs PayTabs credentials
4. **Notifications**: Currently logging to console - needs Twilio credentials
5. **Offline**: No offline support yet - requires implementation
6. **AI Matching**: Manual technician assignment only - AI scoring not implemented

---

## 📝 Environment Variables

### **Backend (.env)**
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=vehicle_maintenance
JWT_SECRET=your-secret-key-change-in-production

# Optional - for integrations
PAYTABS_PROFILE_ID=
PAYTABS_SERVER_KEY=
PAYTABS_REGION=SAU
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
```

### **Frontend (.env)**
```env
EXPO_PUBLIC_BACKEND_URL=https://your-domain/api
EXPO_PACKAGER_PROXY_URL=...
EXPO_PACKAGER_HOSTNAME=...
```

---

## 🎓 Learning Resources

- [Expo Documentation](https://docs.expo.dev/)
- [React Native Documentation](https://reactnative.dev/docs/getting-started)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MongoDB Motor Driver](https://motor.readthedocs.io/)
- [React Navigation](https://reactnavigation.org/)

---

## 📄 License

This project is for demonstration purposes.

---

## 👨‍💻 Developer Notes

### **Running the App**
- Backend runs on port **8001**
- Frontend (Expo) runs on port **3000**
- MongoDB runs on port **27017**

### **Restart Services**
```bash
sudo supervisorctl restart backend
sudo supervisorctl restart expo
```

### **View Logs**
```bash
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/expo.out.log
```

### **Reseed Database**
```bash
cd /app/backend && python seed_data.py
```

---

**Built with ❤️ using Expo, FastAPI, and MongoDB**

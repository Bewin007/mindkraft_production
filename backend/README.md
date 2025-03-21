
# Mindkraft25 API Documentation

Authors: Bewin Felix and Dharshan Kumar J

## Table of Contents
### Authentication
| Endpoint | Method | Description | Status |
|----------|---------|-------------|---------|
| `user/register/` | `POST` | Create new user account with MKID | ✅ |
| `user/verify-otp/` | `POST` | Verify OTP with Email associated with registered MKID | ✅ |
| `user/login/` | `POST` | Authenticate user and get access token | ✅ |
| `user/logout/` | `POST` | End current user session | ✅ |
| `user/forgot-password/` | `POST` | Request password reset OTP | ✅ |
| `user/reset-password/` | `POST` | Reset password using OTP | ✅ |

### Events
| Endpoint | Method | Description | Status |
|----------|---------|-------------|---------|
| `api/event/` | `GET` | Get list of all events | ✅ |
| `api/event/` | `POST` | Create a new event | ✅ |
| `api/event/filter/` | `GET` | Get events filtered by category/type/division | ✅ |

### Cart & Registration
| Endpoint | Method | Description | Status |
|----------|---------|-------------|---------|
| `api/cart/` | `GET` | View items in user's cart | ✅ |
| `api/cart/` | `POST` | Add events to cart | ✅ |
| `api/registered-events/` | `GET` | View all events user has registered for | ✅ |


## Authentication

### Register User
**Endpoint:** `POST /user/register/`

**Description:** Create new user account with MKID

**Request Body for user :**
```json
{
    "email": "dharshankumarlearn@gmail.com",
    "first_name": "register",
    "last_name": "test",
    "register_no": "FAC2021001",
    "mobile_no": "9876543211",
    "date_of_birth": "1985-05-20",
    "password": "register12345",
    "is_faculty": true,
    "intercollege": false,
    "is_enrolled": true
}
```

**Request Body for student:**
```json
{
    "email": "pinonravi@karunya.edu.in",
    "first_name": "register",
    "last_name": "test",
    "register_no": "STU2021001",
    "mobile_no": "9876543211",
    "date_of_birth": "2000-05-20",
    "password": "register12345",
    "is_faculty": false,
    "intercollege": false,
    "is_enrolled": true,
    "student": {
        "college_name": "Karunya",
        "branch": "Computer Science",
        "dept": "Engineering",
        "year_of_study": 2,
        "tshirt": false
    }
}
```


**Response:**
```json
{
    "message": "OTP sent to your email. It will expire in 10 minutes.",
    "email": "dharshankumarlearn@gmail.com"
}
```

### Verify-OTP for registertion
**Endpoint:** `POST user/verify-otp/`

**Description:** Verify OTP with Email associated with registered MKID

**Request Body:**
```json
{
  "email":"dharshankumarlearn@gmail.com",  
  "otp": "162765"
}
```

**Response:**
```json
{
    "message": "Registration successful",
    "user": {
        "id": 13,
        "email": "dharshankumarlearn@gmail.com",
        "first_name": "register",
        "last_name": "test",
        "register_no": "STU2021001",
        "mobile_no": "9876543211",
        "date_of_birth": "2000-05-20",
        "mkid": "MK2500003",
        "is_faculty": false,
        "intercollege": false,
        "is_enrolled": true,
        "student": null
    }
}
```

### Login
**Endpoint:** `POST /user/login/`

**Description:** Authenticate user and get access token

**Request Body:**
```json
{
    "email": "test@gmail.com",
    "password": "test12345"
}
```

**Response:**
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "email": "test@gmail.com",
    "intercollege": false
}
```
If intercollege is false means the student is Internal Student


### Logout
**Endpoint:** `POST /user/logout/`

**Description:** End current user session

**Headers:**
```
Authorization: Bearer <access_token>
```
**Request Body:**
```json
{

"refresh_token":  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczOTM1OTc0NywiaWF0IjoxNzM5MjczMzQ3LCJqdGkiOiI4MGVhZWYzNWE0ZDY0ZjM0OWUyYzExMjI3MzczZWUzZCIsInVzZXJfaWQiOjEsImN1c3RvbV9kYXRhIjp7ImVtYWlsIjoidGVzdEBnbWFpbC5jb20ifX0.4tPx3rFbOesQTPYpxRB_9wxH5PRf0GPLJFHXSP3VwN0"

}
```
**Response:**
```json
{
    "message": "Successfully logged out"
}
```

### Send-OTP for forgot password
**Endpoint:** `POST user/forgot-password/`

**Description:** Request password reset OTP 

**Request Body:**
```json
{
    "email": "dharshankumarlearn@gmail.com"
}
```

**Response:**
```json
{
    "message": "If a user with this email exists, they will receive a password reset OTP."
}
```

### Verify-OTP for forgot password
**Endpoint:** `POST user/reset-password/`

**Description:** Reset password using OTP

**Request Body:**
```json
{
    "email": "dharshankumarlearn@gmail.com",
    "otp": "371110",  // OTP received in email
    "new_password": "newpassword12345",
    "confirm_password": "newpassword12345"
}
```

**Response:**
```json
{
    "message": "Password successfully reset"
}
```

## Events

### List Events
**Endpoint:** `GET /api/event/`

**Description:** Get list of all events

**Response:**
```json
{
    "status": "success",
    "message": "Events retrieved successfully",
    "data": [
        {
            "eventid": "MK25E0001",
            "eventname": "testevent",
            "description": "testevent",
            "type": "tech",
            "category": 1,
            "category_name": "test",
            "division": "ctc",
            "start_time": "2025-02-10T18:55:34Z",
            "end_time": "2025-02-10T18:55:36Z",
            "price": "12.00",
            "participation_strength_setlimit": 12
        }
    ]
}
```

### Create Event
**Endpoint:** `POST /api/event/`

**Description:** Create a new event

**Request Body:**
```json
{
    "eventname": "Hackathon 2025",
    "description": "24-hour coding competition where teams build innovative solutions",
    "type": "TECHNICAL",
    "category": 1,
    "division": "GENERAL",
    "start_time": "2025-03-15T09:00:00Z",
    "end_time": "2025-03-16T09:00:00Z",
    "price": 500,
    "participation_strength_setlimit": 100
}
```

**Response:**
```json
{
    "eventid": "MK25E0003",
    "eventname": "Hackathon 2025",
    "description": "24-hour coding competition where teams build innovative solutions",
    "type": "TECHNICAL",
    "category": 1,
    "category_name": "test",
    "division": "GENERAL",
    "start_time": "2025-03-15T09:00:00Z",
    "end_time": "2025-03-16T09:00:00Z",
    "price": "500.00",
    "participation_strength_setlimit": 100
}
```

### Filter Events
**Endpoint:** `GET /api/event/filter/`

**Description:** Get events filtered by category/type/division

**Query Parameters:**
- `category`: Event category
- `type`: Event type
- `division`: Event division

**Example Request:**
```
GET /api/events/filter/?type=TECHNICAL
```

**Response:**
```json
{
    "status": "success",
    "message": "Filtered events retrieved successfully",
    "data": [
        {
            "eventid": "MK25E0003",
            "eventname": "Hackathon 2025",
            "description": "24-hour coding competition where teams build innovative solutions",
            "type": "TECHNICAL",
            "category": 1,
            "category_name": "test",
            "division": "GENERAL",
            "start_time": "2025-03-15T09:00:00Z",
            "end_time": "2025-03-16T09:00:00Z",
            "price": "500.00",
            "participation_strength_setlimit": 100
        }
    ]
}
```

## Cart & Registration

### View Cart
**Endpoint:** `GET /api/cart/`

**Description:** View items in user's cart

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Response:**
```json
{
    "status": "success",
    "message": "Cart items retrieved successfully",
    "data": [
        {
            "id": 1,
            "MKID": 1,
            "user_mkid": "MK2500001",
            "events": ["MK25E0001", "MK25E0003"],
            "events_detail": [
                {
                    "eventid": "MK25E0001",
                    "eventname": "testevent",
                    "description": "testevent",
                    "type": "tech",
                    "category": 1,
                    "category_name": "test",
                    "division": "ctc",
                    "start_time": "2025-02-10T18:55:34Z",
                    "end_time": "2025-02-10T18:55:36Z",
                    "price": "12.00",
                    "participation_strength_setlimit": 12
                }
            ],
            "added_at": "2025-02-11T09:33:09.230519Z",
            "updated_at": "2025-02-11T09:33:09.230650Z"
        }
    ]
}
```

### Add to Cart
**Endpoint:** `POST /api/cart/`

**Description:** Add events to cart

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "events": ["MK25E0003"]
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Items added to cart successfully",
    "data": {
        "id": 2,
        "MKID": 2,
        "user_mkid": "MK2500002",
        "events": ["MK25E0003"],
        "events_detail": [
            {
                "eventid": "MK25E0003",
                "eventname": "Hackathon 2025",
                "description": "24-hour coding competition where teams build innovative solutions",
                "type": "TECHNICAL",
                "category": 1,
                "category_name": "test",
                "division": "GENERAL",
                "start_time": "2025-03-15T09:00:00Z",
                "end_time": "2025-03-16T09:00:00Z",
                "price": "500.00",
                "participation_strength_setlimit": 100
            }
        ],
        "added_at": "2025-02-11T09:52:02.233759Z",
        "updated_at": "2025-02-11T09:52:02.234290Z"
    }
}
```

### View Registered Events
**Endpoint:** `GET /api/registered-events/`

**Description:** View all events user has registered for

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "status": "success",
    "message": "Registered events retrieved successfully",
    "data": {
        "registered_events": [
            {
                "MKID": 2,
                "user_mkid": "MK2500002",
                "event": "MK25E0001",
                "event_name": "testevent",
                "payment_status": true,
                "registered_at": "2025-02-11T09:53:18.889841Z",
                "updated_at": "2025-02-11T09:53:18.889873Z"
            }
        ],
        "total_events": 2,
        "total_amount": 512.0
    }
}
```
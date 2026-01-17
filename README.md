# 🏠 Airbnb Clone Project - Unified Backend System

## 🎉 Complete Integration of All ALX Backend Services

This project integrates **all ALX backend services** into a single, unified Django application ready for deployment.

## 📦 Integrated Services

1. **Security App** - IP Tracking, Rate Limiting, Anomaly Detection
2. **Properties App** - Property Listings with Redis Caching
3. **CRM App** - GraphQL Customer Relationship Management
4. **Travel App** - Travel Listings & Bookings
5. **Messaging App** - User Communication System

## 🚀 Quick Start

### Automated Setup (Recommended)

```bash
cd /home/j_view/Projects/airbnb-clone-project
./setup.sh
```

### Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp env.example .env
# Edit .env with your settings

# 4. Run migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Collect static files
python manage.py collectstatic --noinput
```

## 🏃 Running the Application

### Start Services

**Terminal 1: Django Server**
```bash
python manage.py runserver
```

**Terminal 2: Celery Worker**
```bash
celery -A airbnb_clone worker --loglevel=info
```

**Terminal 3: Celery Beat (Optional)**
```bash
celery -A airbnb_clone beat --loglevel=info
```

### Or Use Docker

```bash
docker-compose up -d
```

## 🌐 Access Points

- **Main API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/
- **Swagger Docs**: http://localhost:8000/swagger/
- **GraphQL**: http://localhost:8000/graphql/

## 📚 API Endpoints

### Security (`/api/security/`)
- `GET /api/security/` - Home
- `POST /api/security/login/` - Login
- `GET /api/security/logs/` - Request logs
- `GET /api/security/suspicious/` - Suspicious IPs
- `GET /api/security/blocked/` - Blocked IPs

### Properties (`/api/properties/`)
- `GET /api/properties/` - List properties (cached)
- `GET /api/properties/metrics/` - Cache metrics

### CRM (`/api/crm/` or `/graphql/`)
- `POST /api/crm/graphql/` - GraphQL endpoint
- `POST /graphql/` - Alternative GraphQL endpoint

### Travel (`/api/travel/`)
- `GET /api/travel/listings/` - List travel listings
- `POST /api/travel/listings/` - Create listing
- `GET /api/travel/bookings/` - List bookings
- `POST /api/travel/bookings/` - Create booking

### Messaging (`/api/messaging/`)
- `GET /api/messaging/conversations/` - List conversations
- `POST /api/messaging/conversations/` - Create conversation
- `GET /api/messaging/messages/` - List messages
- `POST /api/messaging/messages/` - Send message

### Authentication
- `POST /api/token/` - Get JWT token
- `POST /api/token/refresh/` - Refresh token

## 🔧 Required Services

- **Redis** - For caching (Properties app)
- **RabbitMQ** - For Celery (Required for Milestone 6)
- **PostgreSQL** - Recommended database (SQLite for development)

## 📖 Documentation

- **COMPLETE_SETUP_GUIDE.md** - Complete setup instructions
- **FINAL_INTEGRATION_SUMMARY.md** - Integration summary
- **MILESTONE_6_DEPLOYMENT_GUIDE.md** - Production deployment guide (in parent directory)

## 🎯 Features

- ✅ Unified Django project with multiple apps
- ✅ JWT Authentication
- ✅ IP Tracking & Security
- ✅ Redis Caching
- ✅ GraphQL API
- ✅ RESTful APIs
- ✅ Swagger Documentation
- ✅ Celery Background Tasks
- ✅ Docker Support
- ✅ Production Ready

## 🚀 Deployment

For production deployment, see:
- `MILESTONE_6_DEPLOYMENT_GUIDE.md` (in parent directory)
- `DEPLOYMENT_SETUP.md`

## ✅ Status

**All ALX services have been successfully integrated and the system is ready for deployment!**

---

**For detailed setup instructions, see `COMPLETE_SETUP_GUIDE.md`**

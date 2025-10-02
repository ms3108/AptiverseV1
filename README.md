# Aptiverse - Full-Stack Authentication System

A complete full-stack application with JWT-based authentication, email verification, and modern UI.

## Features

- ✅ **Backend**: FastAPI (Python)
- ✅ **Frontend**: React + TailwindCSS
- ✅ **Database**: PostgreSQL
- ✅ **Authentication**: JWT-based auth with email verification
- ✅ **Email Service**: SendGrid integration
- ✅ **Security**: Bcrypt password hashing
- ✅ **Containerization**: Docker + Docker Compose

## Project Structure

```
Aptiverse V1/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication logic
│   ├── database.py          # Database configuration
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Backend Docker configuration
│   └── .env.example         # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── context/         # Auth context
│   │   ├── App.js           # Main app component
│   │   └── index.js         # Entry point
│   ├── public/
│   ├── package.json         # Node dependencies
│   ├── Dockerfile           # Frontend Docker configuration
│   └── tailwind.config.js   # TailwindCSS configuration
├── docker-compose.yml       # Docker Compose configuration
├── .env.example             # Root environment variables
└── README.md
```

## API Endpoints

- **POST** `/register` - Register a new user
- **GET** `/verify-email?token=<token>` - Verify email address
- **POST** `/login` - Login with credentials
- **GET** `/me` - Get current user info (protected)

## Prerequisites

- Docker and Docker Compose installed
- Gmail account (for email verification) - Optional, see setup options below

## Setup Instructions

### 1. Clone and Navigate

```bash
cd "c:\Users\misna\PycharmProjects\Aptiverse V1"
```

### 2. Configure Email (Choose One Option)

#### **Option A: Gmail SMTP (Recommended for Development)**

1. Enable 2-Step Verification: https://myaccount.google.com/security
2. Generate App Password: https://myaccount.google.com/apppasswords
3. See detailed guide: [GMAIL_SETUP.md](GMAIL_SETUP.md)

#### **Option B: Skip Email Verification (Fastest)**

Users will be auto-verified on signup. Just set `SKIP_EMAIL_VERIFICATION=true` in `.env`

#### **Option C: Console Mode (No Configuration)**

Don't configure Gmail. Verification links will print to console logs.

### 3. Set Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your configuration:

**For Gmail SMTP:**
```env
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password
SKIP_EMAIL_VERIFICATION=false
```

**For Quick Testing (No Email):**
```env
SKIP_EMAIL_VERIFICATION=true
```

### 4. Launch the Application

```bash
docker-compose up --build
```

This will start:
- **PostgreSQL**: localhost:5432
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000

### 5. Access the Application

- **Frontend**: Open http://localhost:3000 in your browser
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **API Alternative Docs**: http://localhost:8000/redoc

## Usage Flow

### 1. Register a New User

1. Go to http://localhost:3000/signup
2. Fill in email, username, and password (min 8 characters)
3. Click "Sign up"
4. Check your email for verification link

### 2. Verify Email

1. Click the verification link in your email
2. You'll be redirected to the verification page
3. After successful verification, you can log in

### 3. Login

1. Go to http://localhost:3000/login
2. Enter your email and password
3. Click "Sign in"
4. You'll be redirected to your dashboard

### 4. Access Protected Routes

Once logged in, you can access:
- Dashboard at `/dashboard`
- Your profile information via the `/me` endpoint

## Development

### Running Without Docker

#### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm start
```

Make sure PostgreSQL is running and update the `DATABASE_URL` in `backend/database.py`.

## Database Schema

### Users Table

| Column              | Type      | Description                |
|---------------------|-----------|----------------------------|
| id                  | Integer   | Primary key                |
| email               | String    | User email (unique)        |
| username            | String    | Username (unique)          |
| hashed_password     | String    | Bcrypt hashed password     |
| is_verified         | Boolean   | Email verification status  |
| verification_token  | String    | Email verification token   |
| created_at          | DateTime  | Account creation timestamp |
| updated_at          | DateTime  | Last update timestamp      |

## Security Features

- ✅ Passwords hashed with bcrypt
- ✅ JWT tokens for authentication
- ✅ Email verification required before login
- ✅ CORS configuration for API security
- ✅ Protected routes requiring authentication
- ✅ Secure token-based email verification

## Tech Stack Details

### Backend
- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Relational database
- **Pydantic**: Data validation
- **Python-JOSE**: JWT token handling
- **Passlib + Bcrypt**: Password hashing
- **SendGrid**: Email delivery service

### Frontend
- **React 18**: UI library
- **React Router**: Navigation
- **TailwindCSS**: Utility-first CSS
- **Axios**: HTTP client
- **Context API**: State management

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **PostgreSQL**: Database container

## Troubleshooting

### Email not sending?
- **Gmail:** Make sure you're using an App Password (not regular password)
- **Gmail:** Check 2-Step Verification is enabled
- See detailed troubleshooting: [GMAIL_SETUP.md](GMAIL_SETUP.md)
- Look at backend logs: `docker-compose logs backend`
- **Quick fix:** Set `SKIP_EMAIL_VERIFICATION=true` in `.env`

### Database connection errors?
- Ensure PostgreSQL container is healthy: `docker-compose ps`
- Check database credentials in docker-compose.yml

### Frontend not loading?
- Check if backend is running: `curl http://localhost:8000`
- Verify CORS settings in backend/main.py
- Check browser console for errors

### Port already in use?
- Change ports in docker-compose.yml if needed
- Stop conflicting services

## Environment Variables

### Backend (.env)
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key (change in production!)
- `GMAIL_USER`: Your Gmail address
- `GMAIL_APP_PASSWORD`: Gmail App Password (16 characters)
- `SKIP_EMAIL_VERIFICATION`: Set to `true` to auto-verify users (development only)

## Production Deployment

**Before deploying to production:**

1. Change `SECRET_KEY` to a strong, random value
2. Use environment-specific `.env` files
3. Enable HTTPS/SSL
4. Update CORS origins to your production domain
5. Use managed PostgreSQL service
6. Set up proper logging and monitoring
7. Configure rate limiting
8. Enable database backups

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please create an issue in the repository.

---

**Built with ❤️ using FastAPI, React, and Docker**

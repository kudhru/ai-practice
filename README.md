# OCaml Quiz Application

## Installation

### Install PostgreSQL (Ubuntu)
```bash
# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo service postgresql start

# Verify installation
psql --version


### Install Node.js and npm (Ubuntu)
```bash
# Update package list
sudo apt update

# Install Node.js and npm
sudo apt install nodejs npm

# Verify installation
node --version
npm --version
```

### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup PostgreSQL database (run as postgres user)
sudo -u postgres bash scripts/setup_db.sh my_user my_password

# Create .env file
cp .env.example .env
# Edit .env with your configuration
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# or if you use yarn
yarn install
# or if you use pnpm
pnpm install

# Create .env.local file
cp .env.example .env.local
# Edit .env.local with your configuration
```

## Running the Application

### Start Backend Server
```bash
cd backend
uvicorn main:app --reload
```

### Start Frontend Development Server
```bash
cd frontend
npm run dev
# or
yarn dev
# or
pnpm dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
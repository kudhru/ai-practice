#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <db_user> <db_password> <db_name>"
    exit 1
fi

# Get values from command line
DB_USER=$1
DB_PASSWORD=$2
DB_NAME=$3

# Create database and user
psql postgres <<EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
\c $DB_NAME
GRANT ALL ON SCHEMA public TO $DB_USER;
EOF

echo "Database setup completed!"
echo "Please update your .env file with:"
echo "DB_USER=$DB_USER"
echo "DB_PASSWORD=$DB_PASSWORD"
echo "DB_NAME=$DB_NAME" 
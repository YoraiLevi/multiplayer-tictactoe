#!/bin/bash

# Start backend
cd backend
./run.sh "$@" &
BACKEND_PID=$!
cd ..

# Start frontend
cd frontend
./run.sh "$@" &
FRONTEND_PID=$!
cd ..

# Function to kill both processes
cleanup() {
    echo "Cleaning up..."
    kill $BACKEND_PID $FRONTEND_PID
}

# Trap EXIT signal to run cleanup
trap cleanup EXIT

# Wait for any process to exit
wait -n
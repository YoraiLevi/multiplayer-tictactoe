#!/bin/bash

# Change to the src directory
cd src

# Start uvicorn with all passed arguments
uvicorn app.main:app "$@" 
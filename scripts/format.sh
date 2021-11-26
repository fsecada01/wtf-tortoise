#!/bin/bash

echo "Running isort..."
isort .
echo "-----"

echo "Running black..."
black .

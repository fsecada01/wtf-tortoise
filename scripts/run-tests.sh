#!/bin/bash

python -m pytest --cov=wtftortoise.orm --cov-report xml --cov-report html --cov-fail-under 90 -s $@

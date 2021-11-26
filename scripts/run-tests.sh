#!/bin/bash

coverage run --source wtftortoise.orm -m unittest discover tests && coverage html 

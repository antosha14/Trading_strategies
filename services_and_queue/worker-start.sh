#! /usr/bin/env bash
set -e

#! python /app/app/celeryworker_pre_start.py

celery -A services_and_queue worker -l INFO -c 1

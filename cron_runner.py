#!/usr/bin/env python3
"""
Manual Cron Runner - Executes scheduled jobs that are due
This is a workaround for the broken heartbeat-cron connection
"""
import json
import time
import os
from datetime import datetime

CRON_FILE = "/home/node/.openclaw/cron/jobs.json"

def get_due_jobs():
    """Find jobs that are due"""
    now = time.time() * 1000  # milliseconds
    due = []
    
    with open(CRON_FILE, 'r') as f:
        data = json.load(f)
    
    for job in data.get('jobs', []):
        if not job.get('enabled', True):
            continue
        
        schedule = job.get('schedule', {})
        schedule_kind = schedule.get('kind')
        
        # Check if due
        is_due = False
        next_run = job.get('state', {}).get('nextRunAtMs')
        
        if next_run and now >= next_run:
            is_due = True
        elif not next_run:
            # If no nextRunAtMs, check if it's time-based (cron/at/every)
            if schedule_kind == 'every':
                interval = schedule.get('everyMs', 60000)
                last_run = job.get('state', {}).get('lastRunAtMs', 0)
                if now - last_run >= interval:
                    is_due = True
        
        if is_due:
            due.append(job)
    
    return due

def run_job(job):
    """Run a job's payload"""
    payload = job.get('payload', {})
    text = payload.get('text', '')
    session_target = job.get('sessionTarget', 'main')
    
    if text:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📤 {job.get('name')}: {text}")
        return text
    return None

# Test mode - just check what's due
if __name__ == "__main__":
    due = get_due_jobs()
    print(f"Due jobs: {len(due)}")
    for job in due:
        name = job.get('name', 'Unknown')
        text = job.get('payload', {}).get('text', 'No text')
        print(f"  - {name}: {text}")

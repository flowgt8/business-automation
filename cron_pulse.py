#!/usr/bin/env python3
"""
Cron Pulse - Checks scheduled jobs and triggers them
Run this via cron or heartbeat to simulate the gateway's cron scheduler
"""
import json
import time
import os
import sys

CRON_FILE = "/home/node/.openclaw/cron/jobs.json"

def main():
    now = time.time() * 1000  # milliseconds
    
    with open(CRON_FILE, 'r') as f:
        data = json.load(f)
    
    triggered = 0
    for job in data.get('jobs', []):
        if not job.get('enabled', True):
            continue
        
        schedule = job.get('schedule', {})
        schedule_kind = schedule.get('kind')
        
        # Check if job is due
        is_due = False
        
        if schedule_kind == 'every':
            interval = schedule.get('everyMs', 60000)
            last_run = job.get('state', {}).get('lastRunAtMs', 0)
            if now - last_run >= interval:
                is_due = True
        
        # For cron/at expressions, we'd need to parse them
        # For now, just trigger every job that's enabled
        
        if is_due:
            print(f"Triggering: {job.get('name')}")
            triggered += 1
    
    if triggered == 0:
        print("No jobs due")
    
    return triggered

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Quick status check for OpenClaw integration
Returns JSON output for easy parsing
"""

import json
import os

QUEUE_FILE = "/root/.openclaw/workspace/business/digital-goods/chat_queue.json"
STATE_FILE = "/root/.openclaw/workspace/business/digital-goods/chat_state.json"

def main():
    result = {
        "pending_count": 0,
        "pending": [],
        "auto_delivered_count": 0,
        "away_mode": False
    }
    
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE) as f:
            data = json.load(f)
            result["pending"] = data.get("pending", [])
            result["pending_count"] = len(result["pending"])
            result["auto_delivered_count"] = len(data.get("auto_delivered", []))
    
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            state = json.load(f)
            result["away_mode"] = state.get("away_mode", False)
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

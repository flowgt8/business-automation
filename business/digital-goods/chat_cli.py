#!/usr/bin/env python3
"""
Chat CLI - Easy interface for managing Plati chats
Usage: python3 chat_cli.py [command]
"""

import subprocess
import sys
import json
import os

QUEUE_FILE = "/root/.openclaw/workspace/business/digital-goods/chat_queue.json"

def load_queue():
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, "r") as f:
            return json.load(f)
    return {"pending": [], "auto_delivered": []}

def show_help():
    print("""
🤖 Plati Chat Manager - CLI

Commands:
  status        Show pending chats
  reply <id>    Reply to a chat (interactive)
  away on       Enable away mode (auto-reply)
  away off      Disable away mode
  check         Force check for new chats
  delivered     Show auto-delivered orders
  help          Show this help

Examples:
  python3 chat_cli.py status
  python3 chat_cli.py reply 123456
  python3 chat_cli.py away on
""")

def show_status():
    queue = load_queue()
    pending = queue.get("pending", [])
    delivered = queue.get("auto_delivered", [])
    
    print(f"\n📊 Chat Status")
    print("=" * 50)
    print(f"🕐 Pending replies: {len(pending)}")
    print(f"⚡️ Auto-delivered: {len(delivered)}")
    
    if pending:
        print("\n📋 Pending Chats:")
        print("-" * 50)
        for i, chat in enumerate(pending[:5], 1):
            print(f"\n{i}. Order #{chat['invoice']}")
            print(f"   Product: {chat['product'][:45]}")
            print(f"   From: {chat['email']}")
            msg = chat.get('message', '')
            if msg:
                print(f"   💬 \"{msg[:70]}{'...' if len(msg) > 70 else ''}\"")
        
        if len(pending) > 5:
            print(f"\n   ... and {len(pending) - 5} more")
        
        print("\n" + "=" * 50)
        print("To reply: python3 chat_cli.py reply <invoice_number>")
    print()

def interactive_reply(invoice_id):
    queue = load_queue()
    chat = None
    for c in queue.get("pending", []):
        if c["invoice"] == invoice_id:
            chat = c
            break
    
    if not chat:
        print(f"❌ Chat #{invoice_id} not found in pending queue")
        return
    
    print(f"\n📩 Order #{invoice_id}")
    print(f"Product: {chat['product']}")
    print(f"Email: {chat['email']}")
    print(f"\n💬 Buyer said:\n\"{chat.get('message', 'No message')}\"")
    print("\n" + "-" * 50)
    
    message = input("\nYour reply: ")
    if not message.strip():
        print("❌ Empty reply - cancelled")
        return
    
    confirm = input(f"Send to {chat['email']}? (y/n): ").lower()
    if confirm != 'y':
        print("❌ Cancelled")
        return
    
    # Send via monitor
    result = subprocess.run([
        sys.executable, "chat_monitor.py",
        "--reply", invoice_id,
        "--message", message
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Reply sent successfully!")
    else:
        print(f"❌ Failed: {result.stderr}")

def set_away(mode):
    result = subprocess.run([
        sys.executable, "chat_monitor.py",
        "--away", mode
    ], capture_output=True, text=True)
    print(f"🌙 Away mode {'enabled' if mode == 'on' else 'disabled'}")

def check_chats():
    print("🔍 Checking for new chats...")
    subprocess.run([sys.executable, "chat_monitor.py", "--check"])

def show_delivered():
    queue = load_queue()
    delivered = queue.get("auto_delivered", [])
    
    print(f"\n⚡️ Auto-Delivered Orders ({len(delivered)})")
    print("=" * 50)
    
    for chat in delivered[-10:]:  # Show last 10
        print(f"#{chat['invoice']} | {chat['product'][:40]}... | {chat['timestamp']}")
    print()

def main():
    if len(sys.argv) < 2:
        show_status()
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        show_status()
    elif command == "help" or command == "-h":
        show_help()
    elif command == "reply":
        if len(sys.argv) < 3:
            print("Usage: python3 chat_cli.py reply <invoice_id>")
            return
        interactive_reply(sys.argv[2])
    elif command == "away":
        if len(sys.argv) < 3 or sys.argv[2] not in ["on", "off"]:
            print("Usage: python3 chat_cli.py away <on|off>")
            return
        set_away(sys.argv[2])
    elif command == "check":
        check_chats()
    elif command == "delivered":
        show_delivered()
    else:
        print(f"Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()

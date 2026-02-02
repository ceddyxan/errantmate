#!/usr/bin/env python3
"""
Timezone fix for UTC+3 (Kenya time)
"""

from datetime import datetime, timedelta

def get_local_time():
    """Get current time in UTC+3 (Kenya timezone)"""
    return datetime.utcnow() + timedelta(hours=3)

def get_local_date():
    """Get current date in UTC+3 (Kenya timezone)"""
    return (datetime.utcnow() + timedelta(hours=3)).date()

# Test the timezone fix
if __name__ == "__main__":
    print("Timezone Fix Test")
    print("=" * 30)
    print(f"UTC Time: {datetime.utcnow()}")
    print(f"Local UTC+3 Time: {get_local_time()}")
    print(f"Local UTC+3 Date: {get_local_date()}")
    print(f"Time Difference: {get_local_time() - datetime.utcnow()}")

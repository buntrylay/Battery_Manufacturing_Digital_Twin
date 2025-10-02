#!/usr/bin/env python3
"""
Test script for the notification queue system.
This script tests the notification queue without requiring the full server.
"""

import sys
import os
import asyncio
import json

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from server.notification_queue import (
    notification_queue, 
    create_machine_notification, 
    notify_machine_status
)


async def test_notification_queue():
    """Test the notification queue functionality."""
    print("Testing Notification Queue System")
    print("=" * 40)
    
    # Test 1: Create a notification
    print("1. Creating a test notification...")
    notification = create_machine_notification(
        machine_id="mixing",
        line_type="anode",
        process_name="mixing_anode",
        status="running",
        data={"stage": "test", "message": "Test notification"}
    )
    print(f"   Created notification: {notification.to_dict()}")
    
    # Test 2: Add notification to queue
    print("\n2. Adding notification to queue...")
    notification_queue.add_notification(notification)
    print(f"   Queue size: {notification_queue.get_queue_size()}")
    
    # Test 3: Send multiple notifications
    print("\n3. Sending multiple notifications...")
    for i in range(3):
        notify_machine_status(
            machine_id="mixing",
            line_type="anode" if i % 2 == 0 else "cathode",
            process_name=f"mixing_{'anode' if i % 2 == 0 else 'cathode'}",
            status="running",
            data={"stage": f"test_{i}", "message": f"Test notification {i}"}
        )
    
    print(f"   Queue size after multiple notifications: {notification_queue.get_queue_size()}")
    
    # Test 4: Retrieve notifications
    print("\n4. Retrieving notifications from queue...")
    try:
        for i in range(4):  # We added 4 notifications total
            notification = await notification_queue.get_notification()
            print(f"   Retrieved notification {i+1}: {notification.to_dict()}")
    except Exception as e:
        print(f"   Error retrieving notification: {e}")
    
    print(f"   Final queue size: {notification_queue.get_queue_size()}")
    
    print("\n✅ Notification queue test completed successfully!")


async def test_subscriber_system():
    """Test the subscriber system."""
    print("\nTesting Subscriber System")
    print("=" * 30)
    
    # Create a subscriber
    subscriber = notification_queue.subscribe()
    print("1. Created subscriber")
    
    # Send a notification
    notify_machine_status(
        machine_id="mixing",
        line_type="anode",
        process_name="mixing_anode",
        status="running",
        data={"stage": "subscriber_test", "message": "Test for subscriber"}
    )
    print("2. Sent notification")
    
    # Check if subscriber received it
    try:
        notification = await asyncio.wait_for(subscriber.get(), timeout=1.0)
        print(f"3. Subscriber received: {notification.to_dict()}")
    except asyncio.TimeoutError:
        print("3. Subscriber did not receive notification within timeout")
    except Exception as e:
        print(f"3. Error in subscriber: {e}")
    
    # Clean up
    notification_queue.unsubscribe(subscriber)
    print("4. Unsubscribed and cleaned up")


if __name__ == "__main__":
    print("Starting notification queue tests...")
    asyncio.run(test_notification_queue())
    asyncio.run(test_subscriber_system())
    print("\n🎉 All tests completed!")

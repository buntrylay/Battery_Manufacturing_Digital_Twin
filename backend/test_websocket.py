#!/usr/bin/env python3
"""
Test script for WebSocket functionality.
This script tests the WebSocket connection and notification system.
"""

import asyncio
import websockets
import json
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from server.notification_queue import notify_machine_status


async def test_websocket_client():
    """Test WebSocket client that connects to the server and listens for messages."""
    uri = "ws://localhost:8000/ws/status"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket server!")
            print("Listening for machine notifications...")
            print("=" * 50)
            
            # Listen for messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    print(f"Received notification:")
                    print(f"  Machine: {data['machine_id']} ({data['line_type']})")
                    print(f"  Process: {data['process_name']}")
                    print(f"  Status: {data['status']}")
                    print(f"  Stage: {data['data']['stage']}")
                    print(f"  Message: {data['data']['message']}")
                    print(f"  Timestamp: {data['timestamp']}")
                    print("-" * 30)
                except json.JSONDecodeError:
                    print(f"Received non-JSON message: {message}")
                except Exception as e:
                    print(f"Error processing message: {e}")
                    
    except ConnectionRefusedError:
        print("Could not connect to WebSocket server. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"WebSocket error: {e}")


def test_notification_sending():
    """Test sending notifications directly to the queue."""
    print("Testing notification sending...")
    
    # Send some test notifications
    notify_machine_status(
        machine_id="mixing",
        line_type="anode",
        process_name="mixing_anode",
        status="running",
        data={"stage": "test", "message": "Test notification from anode mixing machine"}
    )
    
    notify_machine_status(
        machine_id="mixing",
        line_type="cathode",
        process_name="mixing_cathode",
        status="running",
        data={"stage": "test", "message": "Test notification from cathode mixing machine"}
    )
    
    print("Test notifications sent!")


if __name__ == "__main__":
    print("WebSocket Test Script")
    print("===================")
    print()
    
    # First, send some test notifications
    test_notification_sending()
    print()
    
    # Then start the WebSocket client
    print("Starting WebSocket client...")
    asyncio.run(test_websocket_client())

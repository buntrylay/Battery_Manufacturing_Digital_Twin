"""
Notification queue system for WebSocket communication between machines and frontend.
This module provides a thread-safe queue for machines to send real-time updates.
"""

import asyncio
import json
import threading
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class MachineNotification:
    """Represents a notification from a machine about its current state."""

    machine_id: str
    line_type: str
    process_name: str
    status: str  # "running", "idle", "completed", "error"
    timestamp: str
    data: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class NotificationQueue:
    """
    Thread-safe queue for machine notifications.
    Machines can add notifications, 
    and WebSocket handlers can consume them
    Future: Database integration to consume machine data from the notification queue.
    """

    def __init__(self, max_size: int = 1000):
        # the queue is used to store the notifications
        self._queue = asyncio.Queue(maxsize=max_size)
        # the lock is used to synchronize the access to the queue. Only one thread/process can access the queue at a time.
        self._lock = threading.Lock()
        # the subscribers are the queues that will receive the notifications
        self._subscribers: List[asyncio.Queue] = []

    def add_notification(self, notification: MachineNotification):
        """
        Add a notification to the queue.
        This method is thread-safe and can be called from any thread.
        """
        try:
            # Schedule the coroutine to run in the event loop.
            # this event loop belongs to the main thread - v2_server.py.
            # get the event loop. if there is no event loop, raise a runtime error based on the documentation.
            loop = asyncio.get_event_loop()
            '''
            Things that an event loop can be doing in the main thread (in v2_server.py):
            - Running coroutines (asyncio.create_task)
            - Running tasks (asyncio.run)
            - Running callbacks (asyncio.run)
            - Running timers
            - Running network operations (asyncio.run)
            - Running file operations (asyncio.run)
            - Running system calls (asyncio.run)
            '''
            if loop.is_running():
                asyncio.create_task(self._add_notification_async(notification))
            else:
                loop.run_until_complete(self._add_notification_async(notification))
        except RuntimeError:
            # If no event loop is running, create a new one
            asyncio.run(self._add_notification_async(notification))

    async def _add_notification_async(self, notification: MachineNotification):
        """Internal async method to add notification to queue. 
        Because each subscriber has their own async queue."""
        try:
            await self._queue.put(notification)
            # Notify all subscribers
            for subscriber in self._subscribers:
                try:
                    await subscriber.put(notification)
                except asyncio.QueueFull:
                    # Skip this subscriber if their queue is full
                    pass
        except asyncio.QueueFull:
            # If the main queue is full, remove the oldest item
            try:
                await self._queue.get()
                await self._queue.put(notification)
            except asyncio.QueueEmpty:
                pass

    async def get_notification(self) -> MachineNotification:
        """Get the next notification from the queue."""
        return await self._queue.get()
    
    '''currently unused. the whole system is accessing the main notification queue directly.'''
    def subscribe(self) -> asyncio.Queue:
        """Subscribe to notifications. Returns a queue that will receive all new notifications."""
        subscriber_queue = asyncio.Queue(maxsize=100)
        self._subscribers.append(subscriber_queue)
        # return the subscriber queue that will receive all new notifications.
        return subscriber_queue

    def unsubscribe(self, subscriber_queue: asyncio.Queue):
        """Unsubscribe from notifications."""
        if subscriber_queue in self._subscribers:
            self._subscribers.remove(subscriber_queue)

    def get_queue_size(self) -> int:
        """Get the current size of the notification queue."""
        return self._queue.qsize()


# Global notification queue instance. Like a singleton.
notification_queue = NotificationQueue()


def create_machine_notification(
    machine_id: str,
    line_type: str,
    process_name: str,
    status: str,
    data: Dict[str, Any] = None,
) -> MachineNotification:
    """Helper function to create a machine notification."""
    return MachineNotification(
        machine_id=machine_id,
        line_type=line_type,
        process_name=process_name,
        status=status,
        timestamp=datetime.now().isoformat(),
        data=data or {},
    )


def notify_machine_status(
    machine_id: str,
    line_type: str,
    process_name: str,
    status: str,
    data: Dict[str, Any] = None,
):
    """Helper function to quickly send a machine status notification. No async involved."""
    notification = create_machine_notification(
        machine_id, line_type, process_name, status, data
    )
    notification_queue.add_notification(notification)

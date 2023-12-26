import asyncio

from src.apps.event_listener.app import EventListenerApp

event_listener = EventListenerApp()
asyncio.run(event_listener())

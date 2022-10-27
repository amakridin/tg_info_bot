from src.apps.event_listener.app import EventListenerApp
import asyncio

event_listener = EventListenerApp()
asyncio.run(event_listener.run())
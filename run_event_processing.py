from src.apps.event_processing.app import EventProcessingApp
import asyncio

event_listener = EventProcessingApp()

asyncio.run(event_listener.run())

import asyncio

from src.core.scenario_processing import ScenarioProcessing


async def run():
    s = ScenarioProcessing(3)
    await s.load_scenario()


if __name__ == "__main__":
    print("!!!")
    asyncio.run(run())
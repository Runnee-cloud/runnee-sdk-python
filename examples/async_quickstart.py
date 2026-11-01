import os
import asyncio
from runnee import AsyncRunnee


async def main() -> None:
    async with AsyncRunnee(api_key=os.environ["RUNNEE_API_KEY"]) as client:
        result = await client.execute(code="function main(){return 10+20;}")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())

import asyncio


def prepare_filename(text: str) -> str:
    keepcharacters = (" ", ".", "_", "/", "-")
    result = "".join(c for c in text if c.isalnum() or c in keepcharacters).strip().replace(" ", "_")
    return result


async def factorial(name, number):
    f = 1
    for i in range(2, number + 1):
        print(f"Task {name}: Compute factorial({number}), currently i={i}...")
        await asyncio.sleep(1)
        f *= i
    print(f"Task {name}: factorial({number}) = {f}")
    return f

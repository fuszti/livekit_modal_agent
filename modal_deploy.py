from modal import App, Image, Secret, Dict, fastapi_endpoint, FunctionCall
import asyncio
import os

# Import the entrypoint function from main.py
from main import entrypoint

# Create a Modal image with required dependencies
image = Image.debian_slim().pip_install(
    "aiohttp~=3.11.9",
    "livekit",
    "livekit-agents[google,silero,deepgram,turn-detector]~=1.0.20",  # Adjust to a version available in the mirror
    "python-dotenv",
    "fastapi[standard]",
)

# Copy main.py to /app, run its download command, and add /app to PYTHONPATH
image = image.add_local_file("main.py", remote_path="/app/main.py", copy=True) \
             .run_commands("python /app/main.py download-files") \
             .env({"PYTHONPATH": "/app"})

app = App("livekit-agent", image=image)

# Create a persisted dict to track active rooms
room_dict = Dict.from_name("room-dict", create_if_missing=True)

# Import the necessary components within the image context
with image.imports():
    from livekit import rtc
    from livekit.agents import JobContext
    from livekit.agents.worker import Worker, WorkerOptions

@app.function(
    image=image,
    secrets=[Secret.from_name("livekit")],
    timeout=3000
)
async def run_agent_worker(room_name: str):
    """
    Run a LiveKit worker for a specific room.
    This function is executed in a Modal container when a room is created.
    """
    print(f"Running worker for room {room_name}")

    worker = Worker(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            ws_url=os.environ.get("LIVEKIT_URL"),
        )
    )

    try:
        await worker.run()  # Wait for the worker to finish
    except asyncio.CancelledError:
        print(f"Worker for room {room_name} was cancelled. Cleaning up...")
        await worker.drain()
        await worker.aclose()
        print(f"Worker for room {room_name} shutdown complete.")
        raise  # Re-raise to propagate the cancellation
    finally:
        await worker.drain()
        await worker.aclose()


@app.function(image=image)
@fastapi_endpoint(method="POST")
async def run_livekit_agent(request: dict):
    from aiohttp import web

    room_name = request["room"]["sid"]

    ## check whether the room is already in the room_dict
    if room_name in room_dict and request["event"] == "room_started":
        print(
            f"Received web event for room {room_name} that already has a worker running"
        )
        return web.Response(status=200)

    if request["event"] == "room_started":
        call = run_agent_worker.spawn(room_name)
        room_dict[room_name] = call.object_id
        print(f"Worker for room {room_name} spawned")

    elif request["event"] == "room_finished":
        if room_name in room_dict:
            function_call = FunctionCall.from_id(room_dict[room_name])
            # spin down the Modal function
            function_call.cancel()
            # delete the room from the room_dict
            del room_dict[room_name]
            print(f"Worker for room {room_name} spun down")

    return web.Response(status=200)

if __name__ == "__main__":
    # For local testing
    print("This script is meant to be deployed to Modal")
    print("Run 'modal deploy agent/modal_deploy_bad.py' to deploy")
    print("After deploying, get the webhook URL from the Modal deployment output and configure it in your LiveKit project settings.")

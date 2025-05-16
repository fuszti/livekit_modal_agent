# LiveKit AI Agent

This repository contains a LiveKit AI voice agent implementation that can be run locally or deployed to Modal.

## Overview

The agent uses LiveKit's agent framework to create a voice assistant that can process audio input and respond with synthesized speech. The agent leverages several components:

- Speech-to-Text (STT) via Deepgram
- Large Language Model (LLM) via Google's Gemini
- Text-to-Speech (TTS) via Deepgram
- Voice Activity Detection (VAD) via Silero
- Turn detection via LiveKit's multilingual model

## Prerequisites

Before running the agent, ensure you have the following:

- Python 3.8 or higher
- pip package manager
- A LiveKit account with API credentials
- API keys for the services being used (Deepgram, Google)

## Setup and Installation

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai_kihivas_demo.git
   cd ai_kihivas_demo/agent
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the agent directory with your API keys:
   ```
   LIVEKIT_URL=wss://your-livekit-url.livekit.cloud
   LIVEKIT_API_KEY=your_api_key
   LIVEKIT_API_SECRET=your_api_secret
   DEEPGRAM_API_KEY=your_deepgram_api_key
   GOOGLE_API_KEY=your_google_api_key
   ```

### Running Locally

To run the agent locally:

```bash
python main.py dev
```


## Deploying to Modal

[Modal](https://modal.com) is a serverless platform that makes deploying AI applications simple. The agent includes a `modal_deploy.py` script for easy deployment.

### Prerequisites for Modal Deployment

1. Create a Modal account at [modal.com](https://modal.com)
2. Install the Modal CLI:
   ```bash
   pip install modal
   ```
3. Set up Modal CLI authentication:
   ```bash
   modal setup
   ```

### Setting Up Secrets in Modal

Before deploying, you need to create a Modal secret that contains your environment variables:

```bash
modal secret create livekit \
  LIVEKIT_URL=wss://your-livekit-url.livekit.cloud \
  LIVEKIT_API_KEY=your_api_key \
  LIVEKIT_API_SECRET=your_api_secret \
  DEEPGRAM_API_KEY=your_deepgram_api_key
```

For Google's Gemini, if you're using service account credentials, you'll need to provide them as well. You can either add the JSON content directly to the above command or create a separate secret for it.

### Deployment Steps

1. Deploy your agent to Modal:
   ```bash
   modal deploy agent/modal_deploy.py
   ```

2. After successful deployment, Modal will display a webhook URL. Configure this URL in your **LiveKit project** settings as a webhook endpoint.

3. When a room is created in LiveKit, it will trigger the webhook, which will spin up your agent in Modal.

### Modal Environment Configuration

The Modal deployment uses the following configuration:

- A Debian Slim-based container with Python 3.12
- Required Python dependencies installed via pip
- Local files copied to the container
- Secrets mounted for API keys and credentials
- Scalable infrastructure based on room demand

## How It Works

1. When a user connects to a LiveKit room, LiveKit server sends a webhook notification to Modal.
2. Modal spins up a container with your agent.
3. The agent connects to the LiveKit room and begins processing audio.
4. When the conversation ends, the container is automatically shut down to save resources.

## Advanced Configuration

### Modal Deployment Options

The Modal deployment in `modal_deploy.py` includes:

- Room tracking via a persisted dictionary
- Timeout settings for container lifecycle
- Automatic cleanup when rooms are finished
- Webhook event handling

### Worker Options

You can customize the agent worker behavior by modifying the `WorkerOptions` in `main.py`:

```python
agents.cli.run_app(agents.WorkerOptions(
    entrypoint_fnc=entrypoint,
    # Add additional options here
))
```

## Troubleshooting

- **Authentication Issues**: Ensure your API keys are correct and properly set in environment variables or Modal secrets.
- **Connection Failures**: Verify your LiveKit URL is correct and accessible.
- **Missing Dependencies**: Make sure all required Python packages are installed.
- **Modal Deployment Issues**: Check Modal's deployment logs for detailed error information.

## Resources

- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [Modal Documentation](https://modal.com/docs/guide)
- [LiveKit Agent Playground](https://github.com/livekit/agents-playground) - A web UI for testing agents

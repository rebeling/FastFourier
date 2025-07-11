# FastFourier

An AI-powered mock interview platform that provides real-time audio processing and analysis to help users practice and improve their interview skills.

## Features

- Real-time audio recording and transcription
- AI-generated interview questions based on job titles and topics
- Detailed feedback on answers with markdown formatting
- Retry functionality to re-record answers
- WebSocket-based audio streaming for smooth user experience

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd FastFourier
   ```

2. Install dependencies using uv:
   ```bash
   uv sync
   ```

## Configuration

Create a `.env` file in the root directory and add your API keys:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=mistralai/mistral-small-3.2-24b-instruct:free
```

## Running the Application

Start the development server:
```bash
fastapi dev --app app
```

“If FastAPI doesn’t run properly with uv, try running it directly with:

```bash
uvicorn app.main:app --reload”
```

The application will be available at `http://localhost:8000`

## Tech Stack

- **Backend**: FastAPI with WebSocket support
- **AI/ML**:
  - OpenAI Whisper (speech-to-text transcription)
  - pydantic-ai with OpenRouter provider
- **Frontend**: HTML, CSS, JavaScript with Tailwind CSS
- **Templates**: Jinja2 for server-side rendering
- **Audio Processing**: Web Audio API for real-time audio streaming
- **Package Management**: uv for Python dependency management

## Usage

1. Enter your job title and topic (optional)
2. Click "Start" to begin the interview
3. Click "Start Recording" to record your answer
4. Click "Done" when finished recording
5. Review your transcription and AI feedback
6. Use "Retry" to re-record the same question or "Next Question" to continue

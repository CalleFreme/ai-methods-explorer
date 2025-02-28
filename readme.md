# AI Methods Explorer

A full-stack web application that demonstrates different AI approaches to solving specific problems using Python (FastAPI) backend and Next.js TypeScript frontend.

## Features

- 🤖 Text summarization using HuggingFace's BART model
- 🎭 Sentiment analysis using DistilBERT
- 💬 Interactive AI assistant chatbot
- 📚 Gallery view of AI services
- 📊 Request history tracking
- 🔄 CI/CD pipeline with GitHub Actions

## Tech Stack

- **Backend**: FastAPI, Python, SQLite
- **Frontend**: Next.js, TypeScript, React, Tailwind CSS
- **AI Integration**: HuggingFace Inference API
- **DevOps**: GitHub Actions for CI/CD

## Getting Started

### Prerequisites

- Python 3.8+ and Node.js 16+
- HuggingFace account with API key
- Git

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   
   # On Windows (PowerShell)
   .\venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your HuggingFace API key:
   ```
   HF_API_KEY=your_huggingface_api_key
   ```

5. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
   The backend will be available at http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at http://localhost:3000

## Project Structure

```
ai-methods-explorer/
├── .github/
│   └── workflows/
│       └── main.yml       # CI/CD configuration
├── backend/
│   ├── main.py            # FastAPI application
│   ├── requirements.txt   # Python dependencies
│   └── test_main.py       # Backend tests
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx   # Home page with gallery
│   │   │   └── tool/[id]/ # Individual tool pages
│   │   └── components/
│   │       └── ChatBot.tsx # AI assistant component
│   ├── package.json
│   └── ...
└── README.md
```

## CI/CD Setup

The project includes GitHub Actions workflows for continuous integration and deployment:

1. Ensure your repository contains the `.github/workflows/main.yml` file
2. Add your HuggingFace API key as a GitHub Secret named `HF_API_KEY`
3. Push your code to the main branch to trigger the workflow

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm run test
```

## Future Improvements

- Add more AI methods (image generation, text classification)
- Implement user authentication
- Add a more sophisticated database (PostgreSQL)
- Enhance the AI assistant with more capabilities
- Implement deployment to cloud platforms (AWS, Azure, etc.)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- HuggingFace for providing the AI models
- FastAPI and Next.js documentation

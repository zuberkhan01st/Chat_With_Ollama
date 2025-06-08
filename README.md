# Ollama Real-Time Chat Application

This project is a real-time, multi-user chat application powered by a local LLM (LLaMA 3) using Ollama. It features a FastAPI backend with Socket.IO for asynchronous messaging and a Streamlit frontend. The entire system is containerized using Docker Compose.

## Features
- Real-time chat with multiple users
- Local LLM responses via Ollama
- Asynchronous communication using Socket.IO
- Streamlit-based frontend
- Fully containerized (Docker Compose)

## Prerequisites
- Docker & Docker Compose

## Quick Start
1. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
   cd Chat_With_Ollama
   ```
2. **Start the application:**
   ```sh
   docker-compose up --build
   ```
3. **Access the frontend:**
   Open [http://localhost:8501](http://localhost:8501) in your browser.

## Project Structure
```
Chat_With_Ollama/
├── backend/         # FastAPI + Socket.IO backend
├── frontend/        # Streamlit frontend
├── docker-compose.yml
├── README.md
```

## Customization
- Change the LLM model in `docker-compose.yml` and backend code if desired.

## Stopping the App
```sh
docker-compose down
```

## Contact
Submit your GitHub link to: chiragchawla@21spheres.com

---

**Good luck!**
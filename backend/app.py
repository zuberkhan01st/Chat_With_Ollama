import socketio
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import httpx
import json

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = FastAPI()
app_sio = socketio.ASGIApp(sio, app)

OLLAMA_API_URL = "http://ollama:11434/api/generate"  # Docker service name for Ollama

class ChatRequest(BaseModel):
    user: str
    message: str

@app.get('/')
def main():
    return {"message": "Server is working"}

@app.post('/chat')
async def chat_endpoint(request: ChatRequest):
    """HTTP endpoint for chat - simpler than Socket.IO"""
    try:
        print(f"Received message from {request.user}: {request.message}")
        
        # Get response from Ollama
        full_response = ""
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", OLLAMA_API_URL, json={
                "model": "tinyllama", 
                "prompt": request.message,
                "stream": True
            }) as response:
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            chunk = json.loads(line)
                            full_response += chunk.get("response", "")
                            if chunk.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue
        
        print(f"Sending response: {full_response[:100]}...")
        return {"message": full_response, "user": "llm"}
        
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

@sio.event
async def connect(sid, environ):
    print(f"User connected: {sid}")
    # Send immediate confirmation
    await sio.emit('connection_confirmed', {'status': 'connected', 'sid': sid}, to=sid)

@sio.event
def disconnect(sid):
    print(f"User disconnected: {sid}")

@sio.event
async def chat_message(sid, data):
    user = data.get('user', 'anonymous')
    message = data.get('message', '')
    
    print(f"Received message from {user}: {message}")
    
    try:
        # Aggregate streaming response from Ollama
        full_response = ""
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", OLLAMA_API_URL, json={
                "model": "tinyllama", 
                "prompt": message,
                "stream": True
            }) as response:
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            chunk = json.loads(line)
                            full_response += chunk.get("response", "")
                            if chunk.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue
        
        # Send response back to client
        print(f"Sending response to {sid}: {full_response[:100]}...")
        await sio.emit('chat_response', {
            'user': 'llm', 
            'message': full_response
        }, to=sid)
        
    except Exception as e:
        print(f"Error processing message: {e}")
        await sio.emit('chat_response', {
            'user': 'system', 
            'message': f'Error: {str(e)}'
        }, to=sid)

if __name__ == "__main__":
    uvicorn.run(app_sio, host="0.0.0.0", port=8000)
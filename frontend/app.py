import streamlit as st
import requests
import json
import time

st.title("Ollama Real-Time Chat")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'waiting' not in st.session_state:
    st.session_state['waiting'] = False

# Test backend connection
def test_connection():
    try:
        response = requests.get("http://backend:8000/", timeout=5)
        return response.json().get("message") == "Server is working"
    except:
        return False

# Send message directly via HTTP (simpler approach)
def send_message_http(user, message):
    try:
        response = requests.post(
            "http://backend:8000/chat", 
            json={"user": user, "message": message},
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# UI Layout
st.subheader("Connection Status")
if test_connection():
    st.success("✅ Backend server is running")
    server_connected = True
else:
    st.error("❌ Cannot connect to backend server")
    server_connected = False

if server_connected:
    st.subheader("Chat")
    
    # User input
    user = st.text_input("Your name", value="user1")
    
    # Message form
    with st.form("message_form", clear_on_submit=True):
        message = st.text_area("Message", placeholder="Type your message here...")
        send_clicked = st.form_submit_button("Send Message", disabled=st.session_state['waiting'])
        
        if send_clicked and message.strip():
            # Add user message
            st.session_state['messages'].append({
                'user': user, 
                'message': message,
                'timestamp': time.time()
            })
            
            st.session_state['waiting'] = True
            st.rerun()

    # Show waiting status
    if st.session_state['waiting']:
        with st.spinner("Getting response from LLM..."):
            # Get the last user message
            last_message = st.session_state['messages'][-1]
            
            # Send to backend
            result = send_message_http(last_message['user'], last_message['message'])
            
            if 'error' in result:
                st.session_state['messages'].append({
                    'user': 'system',
                    'message': f"Error: {result['error']}",
                    'timestamp': time.time()
                })
            else:
                st.session_state['messages'].append({
                    'user': 'llm',
                    'message': result.get('message', 'No response'),
                    'timestamp': time.time()
                })
            
            st.session_state['waiting'] = False
            st.rerun()

    # Display chat messages
    st.subheader("Chat History")
    if st.session_state['messages']:
        for msg in st.session_state['messages']:
            if msg['user'] == 'llm':
                with st.chat_message("assistant"):
                    st.write(msg['message'])
            elif msg['user'] == 'system':
                with st.chat_message("assistant"):
                    st.error(msg['message'])
            else:
                with st.chat_message("user"):
                    st.write(f"**{msg['user']}**: {msg['message']}")
    else:
        st.info("No messages yet. Send a message to start!")

    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state['messages'] = []
        st.rerun()

else:
    st.info("Please ensure the backend server is running and accessible.")
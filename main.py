from fastapi import FastAPI, WebSocket, Request, Form, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

connected_users = {}

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(username: str = Form(...)):
    response = RedirectResponse(url="/chat", status_code=302)
    response.set_cookie(key="username", value=username)
    return response

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("main.html", {"request": request, "username": username})

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    connected_users[websocket] = username
    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "message":
                msg = f"{username}: {data['text']}"
                for client in connected_users:
                    await client.send_json({"type": "message", "text": msg})
            elif data["type"] == "typing":
                for client in connected_users:
                    if client != websocket:
                        await client.send_json({"type": "typing", "text": f"{username} is typing..."})
    except WebSocketDisconnect:
        connected_users.pop(websocket, None)
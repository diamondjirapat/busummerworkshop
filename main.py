from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List
from datetime import datetime , date
from pydantic import BaseModel

app = FastAPI()

app.mount("/static", StaticFiles(directory="templates"), name="static")

templates = Jinja2Templates(directory="templates")
templates.env.globals['url_for'] = app.url_path_for

class Todo(BaseModel):
    id: int
    task: str
    dur: date

todos: List[Todo] = []
current_id = 1

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "todos": todos})

# @app.get("/todos")
# def get_all_todos():
#     if not todos:
#         raise HTTPException(status_code=404, detail="No todos")
#     return todos

@app.get("/todos")
def get_all_todos(request: Request):
        return templates.TemplateResponse("index.html", {
        "request": request,
        "todos": [todo for todo in todos],
        "error": None
    })


@app.post("/create-todo")
def create_todo(item: str = Form(...), due: str = Form(...)):
    global current_id
    try:
        due_date = datetime.strptime(due, "%Y-%m-%d").date()
    except ValueError:
        return {"error": "use YYYY-MM-DD."}

    todos.append(Todo(id=current_id, task=item, dur=due_date))
    current_id += 1
    return RedirectResponse("/", status_code=303)

@app.post("/delete-todo")
def delete_todo(todo_id: int = Form(...)):
    global todos
    todos = [todo for todo in todos if todo.id != todo_id]
    return RedirectResponse("/", status_code=303)

@app.post("/edit-todo/{todo_id}")
def update_todo(todo_id: int, item: str = Form(...), due: str = Form(...)):
    for todo in todos:
        if todo.id == todo_id:
            try:
                todo.task = item
                todo.dur = datetime.strptime(due, "%Y-%m-%d").date()
                break
            except ValueError:
                raise HTTPException(status_code=400, detail="use YYYY-MM-DD.")
    else:
        raise HTTPException(status_code=404, detail="cant fond to dos")

    return RedirectResponse("/", status_code=303)

@app.get("/upcomming")
def show_upcomming(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "todos": [todo for todo in todos if todo.dur >= date.today()],
        "error": None
    })

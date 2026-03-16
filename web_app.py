import os
import shutil
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from openpyxl import Workbook

from mahle_tecalliance_batch_v13 import run, ensure_workdir_is_script_dir


BASE_DIR = Path(__file__).resolve().parent
RUNS_DIR = BASE_DIR / "runs"
RUNS_DIR.mkdir(exist_ok=True)
SAMPLE_INPUT_PATH = BASE_DIR / "Sample_Input.xlsx"

app = FastAPI(title="Mahle Part Number Search")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/runs", StaticFiles(directory=str(RUNS_DIR)), name="runs")

tasks: Dict[str, Dict[str, Any]] = {}
tasks_lock = threading.Lock()


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def set_task(task_id: str, **kwargs):
    with tasks_lock:
        if task_id not in tasks:
            tasks[task_id] = {}
        tasks[task_id].update(kwargs)


def add_task_event(task_id: str, message: str):
    with tasks_lock:
        task = tasks.get(task_id)
        if not task:
            return
        events = task.setdefault("events", [])
        events.append(f"[{now_text()}] {message}")
        if len(events) > 200:
            del events[:-200]


def get_task(task_id: str) -> Dict[str, Any]:
    with tasks_lock:
        task = tasks.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="找不到任務")
        return dict(task)


def is_cancel_requested(task_id: str) -> bool:
    with tasks_lock:
        task = tasks.get(task_id, {})
        return bool(task.get("cancel_requested", False))


def ensure_sample_input_exists():
    if SAMPLE_INPUT_PATH.exists():
        return
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(["Search_No"])
    for part_no in ["LR015556", "LR106642", "LR115952", "GX7319710BC", "97057311100"]:
        ws.append([part_no])
    wb.save(SAMPLE_INPUT_PATH)


def run_task(task_id: str, input_path: Path, output_path: Path, task_dir: Path):
    old_cwd = os.getcwd()
    try:
        set_task(task_id, status="running", started_at=now_text())
        add_task_event(task_id, "任務開始執行")

        def on_progress(done: int, total: int, query: str, status: str):
            set_task(
                task_id,
                done=done,
                total=total,
                progress=0 if total == 0 else int(done * 100 / total),
                current_query=query,
                last_status=status,
            )
            query_part = f" | {query}" if query else ""
            add_task_event(task_id, f"{done}/{total} | {status}{query_part}")

        os.chdir(task_dir)
        summary = run(
            input_xlsx=str(input_path),
            output_xlsx=str(output_path),
            headless=True,
            progress_cb=on_progress,
            cancel_cb=lambda: is_cancel_requested(task_id),
        )

        if summary.get("cancelled"):
            set_task(
                task_id,
                status="cancelled",
                finished_at=now_text(),
                output_file=str(output_path) if output_path.exists() else "",
                summary=summary,
            )
            add_task_event(task_id, "任務已取消（保留已完成部分結果）")
        else:
            set_task(
                task_id,
                status="completed",
                finished_at=now_text(),
                output_file=str(output_path),
                progress=100,
                summary=summary,
            )
            add_task_event(task_id, "任務完成")
    except Exception as e:
        set_task(task_id, status="failed", finished_at=now_text(), error=str(e))
        add_task_event(task_id, f"任務失敗: {e}")
    finally:
        os.chdir(old_cwd)


@app.get("/")
def home(request: Request):
    with tasks_lock:
        task_list = [{**v, "task_id": k} for k, v in tasks.items()]
        task_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return templates.TemplateResponse("index.html", {"request": request, "tasks": task_list[:20]})


@app.post("/api/tasks")
async def create_task(input_file: UploadFile = File(...)):
    if not input_file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="只支援 .xlsx 檔案")

    task_id = uuid.uuid4().hex[:12]
    task_dir = RUNS_DIR / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    input_path = task_dir / "Input.xlsx"
    output_path = task_dir / "Output.xlsx"

    content = await input_file.read()
    input_path.write_bytes(content)

    set_task(
        task_id,
        status="queued",
        created_at=now_text(),
        progress=0,
        done=0,
        total=0,
        current_query="",
        last_status="",
        output_file="",
        input_file=str(input_path),
        error="",
        cancel_requested=False,
        events=[],
    )
    add_task_event(task_id, "任務已建立，等待執行")

    t = threading.Thread(target=run_task, args=(task_id, input_path, output_path, task_dir), daemon=True)
    t.start()
    return {"task_id": task_id}


@app.get("/api/tasks/{task_id}")
def task_status(task_id: str):
    return get_task(task_id)


@app.get("/api/tasks")
def list_tasks():
    with tasks_lock:
        task_list = [{**v, "task_id": k} for k, v in tasks.items()]
        task_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"tasks": task_list}


@app.post("/api/tasks/cleanup")
def cleanup_tasks():
    removable = {"completed", "failed", "cancelled"}
    removed_ids = []
    with tasks_lock:
        for task_id, task in list(tasks.items()):
            if str(task.get("status", "")) in removable:
                removed_ids.append(task_id)
                del tasks[task_id]

    # Best-effort remove old task folders.
    removed_dirs = 0
    for task_id in removed_ids:
        task_dir = RUNS_DIR / task_id
        if task_dir.exists() and task_dir.is_dir():
            try:
                shutil.rmtree(task_dir)
                removed_dirs += 1
            except Exception:
                pass

    return {"removed_count": len(removed_ids), "removed_dirs": removed_dirs}


@app.post("/api/tasks/{task_id}/cancel")
def cancel_task(task_id: str):
    with tasks_lock:
        task = tasks.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="找不到任務")
        status = str(task.get("status", ""))
        if status in {"completed", "failed", "cancelled"}:
            return {"task_id": task_id, "status": status, "message": "任務已結束"}
        task["cancel_requested"] = True
        if status in {"queued", "running"}:
            task["status"] = "cancelling"
    add_task_event(task_id, "使用者要求取消任務")
    return {"task_id": task_id, "status": "cancelling", "message": "已送出取消要求"}


@app.get("/api/tasks/{task_id}/download")
def download_result(task_id: str):
    task = get_task(task_id)
    output_file = task.get("output_file")
    if not output_file:
        raise HTTPException(status_code=400, detail="任務尚未完成")
    if not os.path.exists(output_file):
        raise HTTPException(status_code=404, detail="輸出檔不存在")
    return FileResponse(output_file, filename=f"Output_{task_id}.xlsx")


@app.get("/api/sample-input")
def download_sample_input():
    ensure_sample_input_exists()
    return FileResponse(str(SAMPLE_INPUT_PATH), filename="Sample_Input.xlsx")


if __name__ == "__main__":
    import uvicorn

    ensure_workdir_is_script_dir()
    ensure_sample_input_exists()
    host = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("web_app:app", host=host, port=port, reload=False)

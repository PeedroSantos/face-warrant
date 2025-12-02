from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Header
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, FileResponse, Response
from typing import Optional
from fastapi.staticfiles import StaticFiles
import cv2
import numpy as np
from io import BytesIO
import base64
import os
from pathlib import Path
import asyncio
from datetime import datetime
try:
    import psutil
except Exception:
    psutil = None
import platform
import shutil
try:
    import torch
except Exception:
    torch = None
import tempfile

from face_processor import FaceRecognizer, FaceDatabase

app = FastAPI(title="Face Recognition System")

Path("uploaded_files").mkdir(exist_ok=True)
Path("known_faces").mkdir(exist_ok=True)
Path("static").mkdir(exist_ok=True)
Path("css").mkdir(exist_ok=True)
Path("templates").mkdir(exist_ok=True)

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
if os.path.exists("uploaded_files"):
    app.mount("/uploaded_files", StaticFiles(directory="uploaded_files"), name="uploaded_files")
if os.path.exists("css"):
    app.mount("/css", StaticFiles(directory="css"), name="css")

db = FaceDatabase("known_faces")
recognizer = FaceRecognizer("faces.pt", db)

webcam_active = False
webcam_lock = asyncio.Lock()

# Track app start time for uptime in health endpoint
app_start_time = datetime.now()


@app.get("/", response_class=HTMLResponse)
async def get_home():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/api/add-known-face")
async def add_known_face(name: str = Form(...), file: UploadFile = File(...), wanted: bool = Form(False)):
    try:
        contents = await file.read()
        file_path = f"uploaded_files/{datetime.now().timestamp()}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(contents)
        print(f"[add_known_face] Saved file: {file_path}")

        image = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)
        print(f"[add_known_face] Image shape: {image.shape if image is not None else 'None'}")
        success = False
        try:
            if image is not None:
                yres = recognizer.yolo_model(image)
                dets = yres[0].boxes
                print(f"[add_known_face] YOLO detections: {len(dets)}")
                if len(dets) > 0:
                    x1, y1, x2, y2 = dets[0].xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    h, w = image.shape[:2]
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(w, x2), min(h, y2)
                    face_img = image[y1:y2, x1:x2]
                    print(f"[add_known_face] Cropped face shape: {face_img.shape}, size: {face_img.size}")
                    if face_img.size != 0:
                        success = db.add_face_from_array(face_img, name, wanted)
                    print(f"[add_known_face] add_face_from_array result: {success}")
        except Exception as e:
            print(f"[add_known_face] YOLO/crop error: {e}")
            success = False

        if not success:
            try:
                print(f"[add_known_face] Trying fallback: full image array")
                if image is not None:
                    success = db.add_face_from_array(image, name, wanted)
                    print(f"[add_known_face] Fallback result: {success}")
                else:
                    print(f"[add_known_face] Image is None, trying file path")
                    success = db.add_face(name, image_path=file_path, wanted=wanted)
                    print(f"[add_known_face] File path result: {success}")
            except Exception as e:
                print(f"[add_known_face] Fallback error: {e}")
                success = False
        
        if success:
            return {"status": "success", "message": f"Face for '{name}' added successfully"}
        else:
            return {"status": "error", "message": "No face detected in image"}
    except Exception as e:
        print(f"[add_known_face] Top-level error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/recognize-image")
async def recognize_image(file: UploadFile = File(...)):
    try:
        # Ler imagem enviada
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        results = recognizer.detect_and_recognize_faces(image)

        output_image = recognizer.draw_results(image, results)

        _, buffer = cv2.imencode('.jpg', output_image)
        img_b64 = base64.b64encode(buffer).decode("ascii")

        response_faces = []

        for (name, confidence, wanted), (top, right, bottom, left) in zip(
            results["recognized"],
            results["face_locations"]
        ):
            response_faces.append({
                "status": "wanted" if wanted else "clear",
                "name": name,
                "confidence": float(confidence),
                "wanted": wanted,
                "box": {
                    "x": int(left),
                    "y": int(top),
                    "w": int(right - left),
                    "h": int(bottom - top)
                }
            })

        return {
            "status": "success",
            "total_faces": len(response_faces),
            "faces": response_faces,
            "image": f"data:image/jpeg;base64,{img_b64}"
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/recognize-video")
async def recognize_video(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        timestamp = str(datetime.now().timestamp()).replace(".", "_")
        input_path = f"uploaded_files/{timestamp}_input_{file.filename}"
        output_path = f"uploaded_files/{timestamp}_output.mp4"
        
        with open(input_path, "wb") as f:
            f.write(contents)
        
        cap = cv2.VideoCapture(input_path)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        if fps == 0:
            fps = 30
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
        
        frame_count = 0
        recognized_count = 0
        people_found = {}
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            results = None
            if frame_count % 5 == 0:
                results = recognizer.detect_and_recognize_faces(frame)
                
                for rec in results["recognized"]:
                    # rec expected: (name, confidence, wanted)
                    try:
                        name = rec[0]
                        conf = rec[1]
                        wanted_flag = bool(rec[2]) if len(rec) > 2 else False
                    except Exception:
                        # fallback for unexpected format
                        continue

                    if name != "Unknown":
                        if name not in people_found:
                            people_found[name] = {"count": 0, "wanted": wanted_flag}
                        people_found[name]["count"] += 1
                        # If any detection shows wanted, keep it as wanted
                        if wanted_flag:
                            people_found[name]["wanted"] = True
                        recognized_count += 1
            else:
                results = recognizer.detect_and_recognize_faces(frame)
            
            if results:
                frame = recognizer.draw_results(frame, results)
            
            out.write(frame)
            frame_count += 1
        
        cap.release()
        out.release()
        # Validate the written output with OpenCV to ensure it is readable
        try:
            test_cap = cv2.VideoCapture(output_path)
            if not test_cap.isOpened():
                print(f"Warning: output video '{output_path}' cannot be opened by OpenCV.")
            else:
                ret_test, _ = test_cap.read()
                print(f"Output video first frame read success: {ret_test}")
            test_cap.release()
        except Exception as e:
            print(f"Error validating output video: {e}")
        
        if not os.path.exists(output_path):
            raise Exception("Video file was not created")
        
        file_size = os.path.getsize(output_path)
        if file_size == 0:
            raise Exception("Video file is empty")
        
        print(f"Video created successfully: {output_path}, size: {file_size} bytes")
        
        os.remove(input_path)

        # Try re-encoding to a more compatible codec container for web browsers (H264)
        try_reencode = True
        if try_reencode:
            try:
                reencoded_path = f"{output_path}.re.mp4"
                print(f"Attempting re-encode to H264-like fourcc for better browser compatibility: {reencoded_path}")
                cap_re = cv2.VideoCapture(output_path)
                if cap_re.isOpened():
                    w = int(cap_re.get(cv2.CAP_PROP_FRAME_WIDTH))
                    h = int(cap_re.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps_r = int(cap_re.get(cv2.CAP_PROP_FPS)) or fps
                    codecs_to_try = ["avc1", "H264", "X264", "mp4v"]
                    reencoded = False
                    for codec in codecs_to_try:
                        try:
                            fourcc_re = cv2.VideoWriter_fourcc(*codec)
                            out_re = cv2.VideoWriter(reencoded_path, fourcc_re, fps_r, (w, h))
                            if not out_re.isOpened():
                                print(f"Codec {codec} didn't open writer")
                                continue
                            cap_re.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            while True:
                                ret_r, frame_r = cap_re.read()
                                if not ret_r:
                                    break
                                out_re.write(frame_r)
                            out_re.release()
                            reencoded = True
                            print(f"Re-encoding succeeded with codec {codec}")
                            break
                        except Exception as e:
                            print(f"Re-encode attempt with {codec} failed: {e}")
                    cap_re.release()
                    if reencoded and os.path.exists(reencoded_path):
                        os.replace(reencoded_path, output_path)
                        print(f"Reencoded file replaced the output: {output_path}")
                    else:
                        if os.path.exists(reencoded_path):
                            os.remove(reencoded_path)
            except Exception as e:
                print(f"Error during optional re-encoding: {e}")
        
        recognized_list = [{"name": n, "count": v["count"], "wanted": v.get("wanted", False)} for n, v in people_found.items()]

        return {
            "status": "success",
            "total_frames": frame_count,
            "recognized_faces": recognized_list,
            "total_recognized": recognized_count,
            "video_url": f"/api/video/{timestamp}",
            "video_static_url": f"/uploaded_files/{os.path.basename(output_path)}",
            "file_size": file_size
        }
    except Exception as e:
        print(f"Video processing error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/webcam-stream")
async def webcam_stream():
    """
    Stream MJPEG frames from the server's camera.
    If the camera cannot be opened we return a 503 so clients can handle it.
    The generator checks `webcam_active` to stop streaming when `/api/stop-webcam` is called.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[webcam_stream] Camera not available (index 0)")
        raise HTTPException(status_code=503, detail="Camera not available on server")

    async def generate():
        global webcam_active

        async with webcam_lock:
            webcam_active = True

        try:
            frame_count = 0
            while webcam_active:
                ret, frame = cap.read()
                if not ret:
                    print("[webcam_stream] No frame received from camera")
                    break

                frame = cv2.resize(frame, (640, 480))

                if frame_count % 2 == 0:
                    results = recognizer.detect_and_recognize_faces(frame)
                    frame = recognizer.draw_results(frame, results)

                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n'
                       b'Content-Length: ' + str(len(frame_bytes)).encode() + b'\r\n\r\n'
                       + frame_bytes + b'\r\n')

                frame_count += 1

                await asyncio.sleep(0.01)
        finally:
            cap.release()
            async with webcam_lock:
                webcam_active = False

    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.post("/api/stop-webcam")
async def stop_webcam():
    async with webcam_lock:
        webcam_active = False
    return {"status": "success"}


@app.get("/api/webcam-status")
async def webcam_status():
    """Quick non-streaming check to see whether the camera can be opened on the server.
    Useful for the client to validate availability before trying to stream.
    """
    try:
        cap = cv2.VideoCapture(0)
        available = cap.isOpened()
        if available:
            cap.release()
        return {"available": available}
    except Exception as e:
        print(f"[webcam_status] Error checking camera: {e}")
        return {"available": False}


@app.get("/api/known-faces")
async def get_known_faces():
    known = db.get_all_names()
    return {"known_faces": known, "count": len(known)}


@app.post('/api/set-wanted')
async def set_wanted(name: str = Form(...), wanted: bool = Form(...)):
    try:
        updated = db.set_wanted(name, wanted)
        if updated:
            return {"status": "success", "message": f"Updated wanted status for {name}"}
        else:
            return {"status": "error", "message": f"No matching name {name} found"}
    except Exception as e:
        print(f"[set-wanted] Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/list-videos")
async def list_videos():
    files = [f for f in os.listdir("uploaded_files") if f.endswith("_output.mp4")]
    return {"videos": files, "count": len(files)}


@app.post("/api/clear-database")
async def clear_database():
    db.known_encodings = []
    db.known_names = []
    db.known_wanted = []
    db.save_database()
    return {"status": "success", "message": "Database cleared"}


@app.get("/api/video/{video_id}")
async def get_video(video_id: str, range: Optional[str] = Header(None)):
    try:
        video_path = None
        for file in os.listdir("uploaded_files"):
            if video_id in file and "_output.mp4" in file:
                video_path = os.path.join("uploaded_files", file)
                break
        
        if not video_path or not os.path.exists(video_path):
            print(f"Video not found for ID: {video_id}")
            print(f"Files in uploaded_files: {os.listdir('uploaded_files')}")
            raise HTTPException(status_code=404, detail="Video not found")
        
        print(f"Serving video: {video_path}")
        print(f"Range Header: {range}")
        
        file_size = os.path.getsize(video_path)
        print(f"Video file_size: {file_size}")
        
        if range:
            try:
                range_val = range.strip().lower()
                if range_val.startswith("bytes="):
                    range_val = range_val.replace("bytes=", "")
                start_str, end_str = range_val.split("-")
                start = int(start_str) if start_str else 0
                end = int(end_str) if end_str else file_size - 1
                end = min(end, file_size - 1)
                if start > end:
                    return Response(status_code=416)

                length = end - start + 1
                with open(video_path, "rb") as f:
                    f.seek(start)
                    data = f.read(length)

                headers = {
                    "Content-Range": f"bytes {start}-{end}/{file_size}",
                    "Accept-Ranges": "bytes",
                    "Content-Length": str(length),
                    "Content-Disposition": f"inline; filename={os.path.basename(video_path)}",
                }
                return Response(content=data, status_code=206, media_type="video/mp4", headers=headers)
            except Exception as e:
                print(f"Range processing error: {e}")
                # fall back to sending entire file

        return FileResponse(
            path=video_path,
            media_type="video/mp4",
            filename=os.path.basename(video_path),
            headers={
                "Content-Disposition": f"inline; filename={os.path.basename(video_path)}",
                "Accept-Ranges": "bytes",
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error serving video: {e}")
        raise HTTPException(status_code=400, detail=str(e))


async def health_check():
    try:
        # Model / version info
        try:
            model_info = str(recognizer.yolo_model)
        except Exception:
            model_info = "YOLO (unknown details)"

        # Known faces and DB
        known_faces = len(db.get_all_names())
        database_loaded = len(db.known_encodings) > 0

        # faces.pt presence
        faces_pt_exists = os.path.exists("faces.pt")

        # Torch / CUDA
        if torch is not None:
            try:
                torch_version = torch.__version__
                cuda_available = torch.cuda.is_available()
                cuda_count = torch.cuda.device_count() if cuda_available else 0
                try:
                    cuda_name = torch.cuda.get_device_name(0) if cuda_available and cuda_count > 0 else None
                except Exception:
                    cuda_name = None
            except Exception:
                torch_version = None
                cuda_available = False
                cuda_count = 0
                cuda_name = None
        else:
            torch_version = None
            cuda_available = False
            cuda_count = 0
            cuda_name = None

        # System metrics
        if psutil is not None:
            try:
                mem = psutil.virtual_memory()
                cpu_percent = psutil.cpu_percent(interval=0.1)
            except Exception:
                mem = None
                cpu_percent = None
        else:
            mem = None
            cpu_percent = None
        try:
            disk_usage = shutil.disk_usage('.')
            disk_free_gb = disk_usage.free // (1024 * 1024 * 1024)
        except Exception:
            disk_free_gb = None

        # Webcam availability (fast check)
        try:
            cap = cv2.VideoCapture(0)
            webcam_ok = cap.isOpened()
            if webcam_ok:
                cap.release()
        except Exception:
            webcam_ok = False

        # uptime
        uptime_seconds = (datetime.now() - app_start_time).total_seconds()

        # Compose a lightweight summary for simpler UI rendering
        uptime_str = str(datetime.now() - app_start_time).split('.')[0]  # HH:MM:SS
        simple = {
            "ok": True,
            "known_faces": known_faces,
            "database_loaded": database_loaded,
            "webcam_available": webcam_ok,
            "cpu_percent": cpu_percent if cpu_percent is not None else None,
            "memory_percent": mem.percent if mem is not None else None,
            "disk_free_gb": disk_free_gb,
            "model": model_info,
            "uptime": uptime_str,
        }

        return {
            "status": "ok",
            "model": model_info,
            "known_faces": known_faces,
            "database_loaded": database_loaded,
            "faces_pt_exists": faces_pt_exists,
            "torch_version": torch_version,
            "cuda_available": cuda_available,
            "cuda_count": cuda_count,
            "cuda_name": cuda_name,
            "memory_percent": mem.percent if mem is not None else None,
            "cpu_percent": cpu_percent,
            "disk_free_gb": disk_free_gb,
            "webcam_available": webcam_ok,
            "uptime_seconds": uptime_seconds,
            "platform": platform.platform(),
            "simple": simple,
        }
    except Exception as e:
        print(f"[health_check] Exception assembling health info: {e}")
        return {"status": "error", "detail": str(e)}

@app.get('/api/health')
async def get_health():
    return await health_check()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

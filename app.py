from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import cv2
import numpy as np
from io import BytesIO
import base64
import os
from pathlib import Path
import asyncio
from datetime import datetime

from face_processor import FaceRecognizer, FaceDatabase

app = FastAPI(title="Face Recognition System")

Path("uploaded_files").mkdir(exist_ok=True)
Path("known_faces").mkdir(exist_ok=True)
Path("static").mkdir(exist_ok=True)
Path("templates").mkdir(exist_ok=True)

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

db = FaceDatabase("known_faces")
recognizer = FaceRecognizer("faces.pt", db)

webcam_active = False
webcam_lock = asyncio.Lock()


@app.get("/", response_class=HTMLResponse)
async def get_home():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/api/add-known-face")
async def add_known_face(name: str = Form(...), file: UploadFile = File(...)):
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
                        success = db.add_face_from_array(face_img, name)
                        print(f"[add_known_face] add_face_from_array result: {success}")
        except Exception as e:
            print(f"[add_known_face] YOLO/crop error: {e}")
            success = False

        if not success:
            try:
                print(f"[add_known_face] Trying fallback: full image array")
                if image is not None:
                    success = db.add_face_from_array(image, name)
                    print(f"[add_known_face] Fallback result: {success}")
                else:
                    print(f"[add_known_face] Image is None, trying file path")
                    success = db.add_face(file_path, name)
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
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        results = recognizer.detect_and_recognize_faces(image)
        
        output_image = recognizer.draw_results(image, results)
        
        _, buffer = cv2.imencode('.jpg', output_image)
        buffer_bytes = buffer.tobytes()
        img_b64 = base64.b64encode(buffer_bytes).decode('ascii')
        
        response_data = {
            "recognized_faces": [
                {"name": name, "confidence": float(conf)}
                for name, conf in results["recognized"]
            ],
            "total_faces": len(results["recognized"])
        }
        
        return {
            "status": "success",
            "data": response_data,
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
                
                for name, conf in results["recognized"]:
                    if name != "Unknown":
                        if name not in people_found:
                            people_found[name] = 0
                        people_found[name] += 1
                        recognized_count += 1
            else:
                results = recognizer.detect_and_recognize_faces(frame)
            
            if results:
                frame = recognizer.draw_results(frame, results)
            
            out.write(frame)
            frame_count += 1
        
        cap.release()
        out.release()
        
        if not os.path.exists(output_path):
            raise Exception("Video file was not created")
        
        file_size = os.path.getsize(output_path)
        if file_size == 0:
            raise Exception("Video file is empty")
        
        print(f"Video created successfully: {output_path}, size: {file_size} bytes")
        
        os.remove(input_path)
        
        return {
            "status": "success",
            "total_frames": frame_count,
            "recognized_faces": people_found,
            "total_recognized": recognized_count,
            "video_url": f"/api/video/{timestamp}",
            "file_size": file_size
        }
    except Exception as e:
        print(f"Video processing error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/webcam-stream")
async def webcam_stream():
    async def generate():
        global webcam_active
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            yield b'error: Camera not available'
            return
        
        async with webcam_lock:
            webcam_active = True
        
        try:
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
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


@app.get("/api/known-faces")
async def get_known_faces():
    known = db.get_all_names()
    return {"known_faces": known, "count": len(known)}


@app.post("/api/clear-database")
async def clear_database():
    db.known_encodings = []
    db.known_names = []
    db.save_database()
    return {"status": "success", "message": "Database cleared"}


@app.get("/api/video/{video_id}")
async def get_video(video_id: str):
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
        return StreamingResponse(
            open(video_path, "rb"),
            media_type="video/mp4",
            headers={"Content-Disposition": "inline"}
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error serving video: {e}")
        raise HTTPException(status_code=400, detail=str(e))


async def health_check():
    return {
        "status": "ok",
        "model": "YOLOv11",
        "known_faces": len(db.get_all_names()),
        "database_loaded": len(db.known_encodings) > 0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

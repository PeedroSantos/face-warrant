import os
import numpy as np
import cv2
from deepface import DeepFace
from pathlib import Path
from typing import List, Tuple, Dict
import pickle


class FaceDatabase:
    def __init__(self, database_dir: str = "known_faces", model_name: str = "Facenet"):
        self.database_dir = Path(database_dir)
        self.database_dir.mkdir(exist_ok=True)
        self.encodings_file = self.database_dir / "encodings.pkl"
        self.known_encodings = []
        self.known_names = []
        self.known_wanted = []
        self.model_name = model_name
        self.load_database()

    def add_face(self, name, image_path=None, image_array=None, wanted=False):
        try:
            embedding = DeepFace.represent(img_path=image_path,
                                           model_name=self.model_name,
                                           enforce_detection=False)
            if not embedding:
                print(f"No face found in {image_path}")
                return False

            encoding = np.array(embedding[0]['embedding'])
            self.known_encodings.append(encoding)
            self.known_names.append(name)
            self.known_wanted.append(wanted)
            self.save_database()
            return True
        except Exception as e:
            print(f"Error adding face: {e}")
            return False

    def add_face_from_array(self, image_array: np.ndarray, name: str, wanted: bool = False) -> bool:
        try:
            try:
                img_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            except Exception:
                img_rgb = image_array

            embedding = DeepFace.represent(img_path=img_rgb,
                                           model_name=self.model_name,
                                           enforce_detection=False)
            if not embedding:
                return False

            encoding = np.array(embedding[0]['embedding'])
            self.known_encodings.append(encoding)
            self.known_names.append(name)
            self.known_wanted.append(wanted)
            self.save_database()
            return True
        except Exception as e:
            print(f"Error adding face: {e}")
            return False

    def save_database(self):
        data = {
            "encodings": self.known_encodings,
            "names": self.known_names,
            'wanted': self.known_wanted
        }
        with open(self.encodings_file, "wb") as f:
            pickle.dump(data, f)

    def load_database(self):
        if self.encodings_file.exists():
            try:
                with open(self.encodings_file, "rb") as f:
                    data = pickle.load(f)
                    self.known_encodings = [np.array(e) for e in data["encodings"]]
                    self.known_names = data["names"]
                    self.known_wanted = data.get('wanted', [])
            except Exception as e:
                print(f"Error loading database: {e}")

    def get_all_names(self) -> List[str]:
        # Return a list of dicts: {"name": name, "wanted": bool}
        result = {}
        for i, n in enumerate(self.known_names):
            w = False
            if i < len(self.known_wanted):
                w = bool(self.known_wanted[i])
            if n in result:
                # if any entry for same person is wanted, keep it wanted
                result[n] = result[n] or w
            else:
                result[n] = w
        return [{"name": k, "wanted": v} for k, v in result.items()]

    def set_wanted(self, name: str, wanted: bool = True):
        """
        Set the wanted flag for all entries with the given name. Returns True if updated at least one entry.
        """
        updated = False
        for i, n in enumerate(self.known_names):
            if n == name:
                while i >= len(self.known_wanted):
                    self.known_wanted.append(False)
                self.known_wanted[i] = bool(wanted)
                updated = True
        if updated:
            self.save_database()
        return updated


class FaceRecognizer:
    def __init__(self, model_path: str = "faces.pt", database: FaceDatabase = None, deepface_model_name: str = "Facenet"):
        from ultralytics import YOLO
        self.yolo_model = YOLO(model_path)
        self.database = database or FaceDatabase()
        self.tolerance = 0.4
        self.model_name = deepface_model_name
        
    def compare_with_database(self, encoding):
        if encoding is None:
            return "Unknown", 0.0, -1

        if not self.database.known_encodings:
            return "Unknown", 0.0, -1

        distances = []
        for db_enc in self.database.known_encodings:
            db_e = np.array(db_enc).astype(np.float64)
            enc = np.array(encoding).astype(np.float64)

            norm_prod = np.linalg.norm(db_e) * np.linalg.norm(enc)
            if norm_prod == 0:
                distances.append(np.inf)
                continue

            cos_sim = np.dot(db_e, enc) / norm_prod
            cos_dist = 1 - cos_sim
            distances.append(cos_dist)

        distances = np.array(distances)
        min_idx = np.argmin(distances)
        min_distance = distances[min_idx]

        if min_distance < self.tolerance:
            name = self.database.known_names[min_idx]
            confidence = 1 - min_distance
            return name, confidence, min_idx

        return "Unknown", 0.0, -1


    def detect_and_recognize_faces(
        self,
        image: np.ndarray,
        confidence_threshold: float = 0.5
    ) -> Dict:
        results = {
            "faces": [],
            "recognized": [],
            "face_locations": [],
            "face_encodings": []
        }
        yolo_results = self.yolo_model(image, conf=confidence_threshold)
        detections = yolo_results[0].boxes

        if len(detections) == 0:
            return results

        face_locations = []
        face_encodings = []

        for detection in detections:
            x1, y1, x2, y2 = detection.xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            h, w = image.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            face_locations.append((y1, x2, y2, x1))

            face_image = image[y1:y2, x1:x2]
            if face_image.size == 0:
                face_encodings.append(None)
                continue

            try:
                face_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            except Exception:
                face_rgb = face_image

            try:
                embed = DeepFace.represent(img_path=face_rgb,
                                           model_name=self.model_name,
                                           enforce_detection=False)
            except Exception:
                embed = None

            if embed:
                emb = np.array(embed[0]['embedding'])
                face_encodings.append(emb)
            else:
                face_encodings.append(None)

        results["face_locations"] = face_locations
        results["face_encodings"] = face_encodings

        if self.database.known_encodings:
            for encoding in face_encodings:
                name, confidence, index = self.compare_with_database(encoding)
                wanted = False
                if index != -1 and len(self.database.known_wanted) > index:
                    wanted = bool(self.database.known_wanted[index])
                results["recognized"].append((name, confidence, wanted))

        else:
            results["recognized"] = [("Unknown", 0.0, False)] * len(face_encodings)

        return results
    def draw_results(self, image: np.ndarray, detection_results: Dict) -> np.ndarray:
        output = image.copy()

        for face_loc, (name, confidence, wanted) in zip(
            detection_results["face_locations"], 
            detection_results["recognized"]
        ):
            y1, x2, y2, x1 = face_loc

            if name == "Unknown":
                color = (0, 255, 255)   # Amarelo
                label = "Desconhecido"
            else:
                if wanted:
                    color = (0, 0, 255)  # Vermelho
                    label = f"{name} ({confidence:.2f}) [WANTED]"
                else:
                    color = (0, 255, 0)  
                    label = f"{name} ({confidence:.2f})"

            cv2.rectangle(output, (x1, y1), (x2, y2), color, 2)

            cv2.putText(
                output,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

        return output

    def recognize(self, image_array, tolerance=0.4):
        detections = self.detect_and_recognize_faces(image_array)

        results = []
        for det in detections["recognized"]:
            name, confidence, index = det

            if index != -1:
                wanted = self.database.known_wanted[index]
            else:
                wanted = False

            results.append({
                "name": name,
                "confidence": confidence,
                "wanted": wanted
            })

        return results

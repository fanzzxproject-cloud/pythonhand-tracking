import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
import threading
import time
import urllib.request
import os
from gtts import gTTS
import pygame
import tempfile

# ─────────────────────────────────────────────
#  Pesan untuk setiap angka jari
# ─────────────────────────────────────────────
MESSAGES = {
    1: "Halo perkenalkan",
    2: "Nama saya",
    3: "Fanzzx saya",
    4: "Adalah pengembang",
    5: "Program ini",
}

COLOR_ACCENT = (0, 200, 255)
COLOR_WHITE  = (255, 255, 255)
COLOR_GREEN  = (80, 220, 130)
COLOR_DARK   = (15, 10, 30)

# ─────────────────────────────────────────────
#  Download model MediaPipe
# ─────────────────────────────────────────────
MODEL_PATH = "hand_landmarker.task"
MODEL_URL  = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

def download_model():
    if not os.path.exists(MODEL_PATH):
        print("Mendownload model MediaPipe... (~5MB, sekali saja)")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Model berhasil didownload!")

# ─────────────────────────────────────────────
#  Pre-generate semua audio saat startup
# ─────────────────────────────────────────────
pygame.mixer.init()
AUDIO_CACHE = {}

def pregenerate_audio():
    print("Menyiapkan suara Google Indonesia...")
    for angka, teks in MESSAGES.items():
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp.close()
        tts = gTTS(text=teks, lang="id", slow=False)
        tts.save(tmp.name)
        AUDIO_CACHE[angka] = tmp.name
    print("Suara siap!")

_tts_lock   = threading.Lock()
_tts_thread = None

def speak(angka):
    global _tts_thread
    def _run():
        with _tts_lock:
            path = AUDIO_CACHE.get(angka)
            if path and os.path.exists(path):
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.05)
    if _tts_thread is None or not _tts_thread.is_alive():
        _tts_thread = threading.Thread(target=_run, daemon=True)
        _tts_thread.start()

# ─────────────────────────────────────────────
#  Hitung jari — metode jarak tip ke wrist
#  Lebih akurat untuk semua kombinasi jari
# ─────────────────────────────────────────────
def dist2d(a, b):
    return ((a.x - b.x)**2 + (a.y - b.y)**2) ** 0.5

def count_fingers(lm, handedness):
    """
    Setiap jari dianggap NAIK jika:
    - jarak tip ke wrist > jarak pip ke wrist * threshold
    Ini bekerja untuk semua orientasi tangan.
    """
    THRESHOLD = 1.2
    count = 0

    # ── Jempol: pakai sumbu X karena arah berbeda ──
    # Setelah flip, "Right" di mediapipe = tangan kanan user
    if handedness == "Right":
        if lm[4].x < lm[3].x:
            count += 1
    else:
        if lm[4].x > lm[3].x:
            count += 1

    # ── Telunjuk (landmark 8 vs 6) ──
    if dist2d(lm[8], lm[0]) > dist2d(lm[6], lm[0]) * THRESHOLD:
        count += 1

    # ── Jari tengah (12 vs 10) ──
    if dist2d(lm[12], lm[0]) > dist2d(lm[10], lm[0]) * THRESHOLD:
        count += 1

    # ── Jari manis (16 vs 14) ──
    if dist2d(lm[16], lm[0]) > dist2d(lm[14], lm[0]) * THRESHOLD:
        count += 1

    # ── Kelingking (20 vs 18) ──
    if dist2d(lm[20], lm[0]) > dist2d(lm[18], lm[0]) * THRESHOLD:
        count += 1

    return count

# ─────────────────────────────────────────────
#  Gambar tangan
# ─────────────────────────────────────────────
CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (0,9),(9,10),(10,11),(11,12),
    (0,13),(13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20),
    (5,9),(9,13),(13,17),(0,17),
]
TIPS_SET = {4, 8, 12, 16, 20}

def draw_hand(frame, landmarks, h, w):
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    for a, b in CONNECTIONS:
        cv2.line(frame, pts[a], pts[b], (0, 160, 210), 2)
    for i, pt in enumerate(pts):
        r     = 7 if i in TIPS_SET else 4
        color = COLOR_ACCENT if i in TIPS_SET else (220, 220, 220)
        cv2.circle(frame, pt, r, color, -1)
        cv2.circle(frame, pt, r, (0, 0, 0), 1)

# ─────────────────────────────────────────────
#  UI
# ─────────────────────────────────────────────
def draw_overlay(frame, finger_count, message, hand_found):
    h, w = frame.shape[:2]
    panel_h = 150
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, h - panel_h), (w, h), COLOR_DARK, -1)
    cv2.addWeighted(overlay, 0.78, frame, 0.22, 0, frame)
    cv2.line(frame, (0, h - panel_h), (w, h - panel_h), COLOR_ACCENT, 1)

    if hand_found and message:
        cv2.putText(frame, str(finger_count),
                    (25, h - panel_h + 95),
                    cv2.FONT_HERSHEY_DUPLEX, 3.8, COLOR_ACCENT, 6, cv2.LINE_AA)
        cv2.line(frame, (125, h - panel_h + 15), (125, h - 15), COLOR_ACCENT, 2)
        cv2.putText(frame, message, (148, h - panel_h + 78),
                    cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 40, 60), 4, cv2.LINE_AA)
        cv2.putText(frame, message, (145, h - panel_h + 75),
                    cv2.FONT_HERSHEY_DUPLEX, 1.2, COLOR_WHITE, 2, cv2.LINE_AA)
        cv2.putText(frame, "[ jari terdeteksi ]",
                    (148, h - panel_h + 115),
                    cv2.FONT_HERSHEY_PLAIN, 1.15, COLOR_GREEN, 1, cv2.LINE_AA)
    else:
        cv2.putText(frame, "Tunjukkan 1 - 5 jari ke kamera",
                    (w // 2 - 220, h - panel_h + 80),
                    cv2.FONT_HERSHEY_DUPLEX, 0.9, (150, 150, 170), 1, cv2.LINE_AA)

def draw_hud(frame, fps):
    h, w = frame.shape[:2]
    cv2.line(frame, (0, 48), (w, 48), COLOR_ACCENT, 1)
    cv2.putText(frame, f"FPS {fps:.0f}", (15, 36),
                cv2.FONT_HERSHEY_PLAIN, 1.7, COLOR_GREEN, 2, cv2.LINE_AA)
    cv2.putText(frame, "HAND TRACKER  by Fanzzx", (w - 310, 36),
                cv2.FONT_HERSHEY_DUPLEX, 0.75, COLOR_ACCENT, 1, cv2.LINE_AA)

# ─────────────────────────────────────────────
#  Debug — tampilkan status tiap jari di layar
# ─────────────────────────────────────────────
def draw_finger_debug(frame, lm, h, w, handedness):
    THRESHOLD = 1.2
    def dist2d(a, b):
        return ((a.x - b.x)**2 + (a.y - b.y)**2) ** 0.5

    labels = ["Jempol", "Telunjuk", "Tengah", "Manis", "Kelingking"]
    tips   = [4, 8, 12, 16, 20]
    pips   = [3, 6, 10, 14, 18]

    statuses = []
    # Jempol
    if handedness == "Right":
        statuses.append(lm[4].x < lm[3].x)
    else:
        statuses.append(lm[4].x > lm[3].x)
    # 4 jari lain
    for tip, pip in zip(tips[1:], pips[1:]):
        statuses.append(dist2d(lm[tip], lm[0]) > dist2d(lm[pip], lm[0]) * THRESHOLD)

    for i, (label, status) in enumerate(zip(labels, statuses)):
        color = COLOR_GREEN if status else (100, 100, 120)
        text  = f"{label}: {'NAIK' if status else 'turun'}"
        cv2.putText(frame, text, (10, 80 + i * 28),
                    cv2.FONT_HERSHEY_PLAIN, 1.3, color, 2, cv2.LINE_AA)

# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────
def main():
    download_model()
    pregenerate_audio()

    base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
    options = mp_vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=1,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    detector = mp_vision.HandLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)

    prev_count      = -1
    last_speak_time = 0
    SPEAK_COOLDOWN  = 2.5
    prev_time       = time.time()

    count_buffer = []
    BUFFER_SIZE  = 6

    print("=" * 55)
    print("  Hand Tracking - Fanzzx")
    print("  Angkat 1-5 jari ke kamera")
    print("  Tekan Q atau ESC untuk keluar")
    print("=" * 55)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w  = frame.shape[:2]

        rgb      = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result   = detector.detect(mp_image)

        finger_count = 0
        message      = ""
        hand_found   = False

        if result.hand_landmarks and result.handedness:
            landmarks  = result.hand_landmarks[0]
            handedness = result.handedness[0][0].category_name

            draw_hand(frame, landmarks, h, w)
            draw_finger_debug(frame, landmarks, h, w, handedness)

            raw_count = count_fingers(landmarks, handedness)

            count_buffer.append(raw_count)
            if len(count_buffer) > BUFFER_SIZE:
                count_buffer.pop(0)
            finger_count = max(set(count_buffer), key=count_buffer.count)

            message    = MESSAGES.get(finger_count, "")
            hand_found = True

            now = time.time()
            if (finger_count != prev_count and
                    message and
                    now - last_speak_time > SPEAK_COOLDOWN):
                speak(finger_count)
                last_speak_time = now
                prev_count = finger_count
        else:
            count_buffer.clear()
            prev_count = -1

        now_t     = time.time()
        fps       = 1.0 / max(now_t - prev_time, 1e-6)
        prev_time = now_t

        draw_hud(frame, fps)
        draw_overlay(frame, finger_count, message, hand_found)

        cv2.imshow("Hand Tracker - Fanzzx", frame)
        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), ord("Q"), 27):
            break

    cap.release()
    cv2.destroyAllWindows()
    detector.close()
    pygame.mixer.quit()
    for path in AUDIO_CACHE.values():
        try: os.remove(path)
        except: pass
    print("Program selesai.")

if __name__ == "__main__":
    main()

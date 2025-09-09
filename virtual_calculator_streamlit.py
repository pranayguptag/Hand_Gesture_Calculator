import cv2
import numpy as np
import time
import math
import mediapipe as mp
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

# Your existing UI setup and button class goes here...
# ... (all code from the top of your file down to the `run = st.checkbox` line)

# === Streamlit Page Setup ===
st.set_page_config(page_title="Hand Gesture Calculator", layout="wide")
st.markdown("""
<div style='background: linear-gradient(90deg, #191970 0%, #23272F 100%); padding: 20px; border-radius: 15px;'>
    <h1 style='text-align: center; color: #FFD700; font-size: 3em; letter-spacing: 2px;'>🤚 Hand Gesture Calculator</h1>
    <h3 style='text-align: center; color: #00BFFF; font-size: 1.5em;'>Control the calculator with your hand gestures!</h3>
</div>
<div style='background: #23272F; border-radius: 10px; margin-top: 20px; padding: 10px;'>
    <p style='text-align: center; color: #FFD700; font-size: 1.2em;'>Powered by <b>MediaPipe</b> and <b>OpenCV</b></p>
</div>
""", unsafe_allow_html=True)

# === Display Banner Image ===
img_path = os.path.join(os.path.dirname(__file__), "MathGestures.png")
if os.path.exists(img_path):
    st.image(img_path, use_container_width=True)

col1, col2 = st.columns([3, 1])

with col2:
    st.markdown("""
<div style='background: #191970; border-radius: 10px; padding: 20px; color: #FFD700;'>
    <h2 style='color: #FFD700;'>Instructions</h2>
    <ul style='font-size: 1.1em;'>
        <li>Show your hand to the camera.</li>
        <li><span style='color:#00BFFF;'>Pinch (thumb & index)</span> to select a button.</li>
        <li><span style='color:#FF6347;'>Press 'C'</span> to clear, <span style='color:#FFD700;'> '=' </span> to evaluate.</li>
        <li>Uncheck <b>Run Calculator</b> to stop.</li>
    </ul>
    <h3 style='color: #FF69B4;'>Enjoy the magic of AI and Computer Vision!</h3>
    <hr style='border: 1px solid #FFD700;'>
    <p style='color: #00BFFF; font-size: 1em;'>Tip: Use good lighting and keep your hand steady for best results.</p>
</div>
""", unsafe_allow_html=True)

# === Button Class ===
class Button:
    def __init__(self, pos, width, height, value):
        self.pos = pos
        self.width = width
        self.height = height
        self.value = value

    def draw(self, frame, hover=False):
        x, y = self.pos
        color = (0, 255, 0) if hover else (0, 0, 0)
        cv2.rectangle(frame, self.pos, (x + self.width, y + self.height), color, cv2.FILLED)
        cv2.rectangle(frame, self.pos, (x + self.width, y + self.height), (50, 50, 50), 3)
        cv2.putText(frame, self.value, (x + 20, y + 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)

    def is_hover(self, x, y):
        bx, by = self.pos
        return bx < x < bx + self.width and by < y < by + self.height

# === Calculator Layout ===
keys = [
    ["7", "8", "9", "+"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "*"],
    ["C", "0", "=", "/"]
]

button_list = []
for i in range(4):
    for j in range(4):
        xpos = j * 100 + 50
        ypos = i * 100 + 150
        button_list.append(Button((xpos, ypos), 80, 80, keys[i][j]))


# Calculation history
if 'calc_history' not in st.session_state:
    st.session_state['calc_history'] = []
if 'expression' not in st.session_state:
    st.session_state['expression'] = ""
if 'last_click_time' not in st.session_state:
    st.session_state['last_click_time'] = 0

# === Video Processor Class ===
class HandGestureVideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.8)
        self.mp_drawing = mp.solutions.drawing_utils

    def recv(self, frame):
        # Convert the frame to a format compatible with OpenCV
        frm = frame.to_ndarray(format="bgr24")
        
        # --- Your existing processing logic from the `while` loop ---
        rgb = cv2.cvtColor(frm, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)
        h, w, c = frm.shape

        # Draw all buttons
        for button in button_list:
            button.draw(frm)

        # Display the current expression
        cv2.rectangle(frm, (50, 50), (450, 130), (0, 0, 0), cv2.FILLED)
        cv2.putText(frm, st.session_state.get('expression', ''), (60, 115), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 255, 255), 2)

        if result.multi_hand_landmarks:
            hand_landmarks = result.multi_hand_landmarks[0]
            lm_list = []
            for id, lm in enumerate(hand_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((cx, cy))

            self.mp_drawing.draw_landmarks(frm, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

            if lm_list:
                x1, y1 = lm_list[4]
                x2, y2 = lm_list[8]
                length = math.hypot(x2 - x1, y2 - y1)
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                current_time = time.time()

                if length < 40 and (current_time - st.session_state.get('last_click_time', 0)) > 1:
                    for button in button_list:
                        if button.is_hover(cx, cy):
                            selected = button.value
                            if selected == "C":
                                st.session_state['expression'] = ""
                            elif selected == "=":
                                try:
                                    answer = str(eval(st.session_state['expression']))
                                    st.session_state['calc_history'].append((st.session_state['expression'], answer))
                                    st.session_state['expression'] = answer
                                except:
                                    answer = "Error"
                                    st.session_state['calc_history'].append((st.session_state['expression'], answer))
                                    st.session_state['expression'] = answer
                            else:
                                st.session_state['expression'] += selected
                            
                            st.session_state['last_click_time'] = current_time

                            cv2.circle(frm, (cx, cy), 15, (0, 255, 255), cv2.FILLED)

        return frm

# === Streamlit App Logic ===
with col1:
    st.markdown("""
<div style='background: #23272F; border-radius: 10px; padding: 10px; margin-bottom: 10px;'>
    <h3 style='color: #FFD700; text-align: center;'>Live Calculator Panel</h3>
</div>
""", unsafe_allow_html=True)

    # Display the expression box dynamically outside the video stream
    expression_placeholder = st.empty()
    expression_placeholder.markdown(f"""
    <div style='background: #23272F; border-radius: 10px; padding: 10px; margin-top: 10px;'>
        <h2 style='text-align: center; color: #FFD700;'>Expression: {st.session_state.get('expression', '')}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Use webrtc_streamer for live video feed
    webrtc_streamer(key="gesture_calculator", video_processor_factory=HandGestureVideoProcessor)

# Show calculation history below the video stream
if st.session_state['calc_history']:
    st.markdown("""
    <div style='background: #23272F; border-radius: 10px; padding: 10px; margin-top: 20px;'>
        <h3 style='color: #FFD700; text-align: center;'>Calculation History</h3>
        <ul style='color: #00BFFF; font-size: 1.1em;'>
    """, unsafe_allow_html=True)
    for expr, ans in reversed(st.session_state['calc_history'][-10:]):
        st.markdown(f"<li><span style='color:#FFD700;'>{expr}</span> = <b style='color:#32CD32;'>{ans}</b></li>", unsafe_allow_html=True)
    st.markdown("</ul></div>", unsafe_allow_html=True)
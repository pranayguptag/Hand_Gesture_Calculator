import cv2
import numpy as np
import time
import math
import mediapipe as mp
import streamlit as st
import os

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

# Initialize expression and last click time in session state
if 'expression' not in st.session_state:
    st.session_state['expression'] = ""
if 'last_click_time' not in st.session_state:
    st.session_state['last_click_time'] = 0

# === Core Logic Using Streamlit Camera Input ===
with col1:
    st.markdown("""
<div style='background: #23272F; border-radius: 10px; padding: 10px; margin-bottom: 10px;'>
    <h3 style='color: #FFD700; text-align: center;'>Live Calculator Panel</h3>
</div>
""", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='background: #23272F; border-radius: 10px; padding: 10px; margin-top: 10px;'>
        <h2 style='text-align: center; color: #FFD700;'>Expression: {st.session_state['expression']}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Use Streamlit's camera input instead of cv2.VideoCapture
    camera_image_data = st.camera_input("Start Calculator (using Webcam)")
    
    if camera_image_data is not None:
        # Convert the image from Streamlit to a NumPy array for OpenCV
        file_bytes = np.asarray(bytearray(camera_image_data.read()), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # The rest of your processing logic can stay the same
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.8)
        mp_drawing = mp.solutions.drawing_utils

        result = hands.process(rgb)
        h, w, c = frame.shape

        # Draw all buttons
        for button in button_list:
            button.draw(frame)

        # Display the current expression
        cv2.rectangle(frame, (50, 50), (450, 130), (0, 0, 0), cv2.FILLED)
        cv2.putText(frame, st.session_state['expression'], (60, 115), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 255, 255), 2)

        if result.multi_hand_landmarks:
            hand_landmarks = result.multi_hand_landmarks[0]
            lm_list = []
            for id, lm in enumerate(hand_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((cx, cy))

            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Check for pinch (thumb tip & index tip)
            if lm_list:
                x1, y1 = lm_list[4]   # Thumb tip
                x2, y2 = lm_list[8]   # Index tip
                length = math.hypot(x2 - x1, y2 - y1)

                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                current_time = time.time()

                if length < 40 and (current_time - st.session_state['last_click_time']) > 1: # use session state
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

                            # Visual feedback
                            cv2.circle(frame, (cx, cy), 15, (0, 255, 255), cv2.FILLED)

        # Display the processed frame
        st.image(frame, channels="BGR", use_column_width=True)

# Show calculation history below camera
if st.session_state['calc_history']:
    st.markdown("""
    <div style='background: #23272F; border-radius: 10px; padding: 10px; margin-top: 20px;'>
        <h3 style='color: #FFD700; text-align: center;'>Calculation History</h3>
        <ul style='color: #00BFFF; font-size: 1.1em;'>
    """, unsafe_allow_html=True)
    for expr, ans in reversed(st.session_state['calc_history'][-10:]):
        st.markdown(f"<li><span style='color:#FFD700;'>{expr}</span> = <b style='color:#32CD32;'>{ans}</b></li>", unsafe_allow_html=True)
    st.markdown("</ul></div>", unsafe_allow_html=True)
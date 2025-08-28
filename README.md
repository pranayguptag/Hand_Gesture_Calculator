# ![Maths Gesture Banner](MathGestures.png)
# 🤚 Hand Gesture Calculator

An interactive calculator powered by hand gesture recognition using MediaPipe and OpenCV, deployed with Streamlit. Control the calculator with your hand gestures in real time!

---

## 🚀 Features
- Real-time hand gesture recognition for calculator input
- Beautiful, dark-themed Streamlit UI
- Calculation history panel (session-based)
- No database required
- Easy to run locally

---

## 📦 Installation & Setup

1. **Clone the repository:**
	```bash
	git clone https://github.com/pranayguptag/Hand_Gesture_Calculator.git
	cd Hand_Gesture_Calculator
	```

2. **Install dependencies:**
	```bash
	pip install -r requirements.txt
	```
	Or manually install:
	```bash
	pip install opencv-python mediapipe streamlit numpy
	```

3. **(Optional) Add a webcam if not using a laptop camera.**

---

## 🖥️ Usage

1. **Run the Streamlit app:**
	```bash
	streamlit run virtual_calculator_streamlit.py
	```

2. **Open the app in your browser.**

3. **Check 'Run Calculator' to start.**

4. **Show your hand to the camera and use gestures to operate the calculator.**
	- Pinch (thumb & index) to select a button
	- Press 'C' to clear, '=' to evaluate
	- Calculation history appears below the camera

---

## 📸 Screenshots

Add screenshots of your app here:

```
![Calculator UI](screenshots/calculator_ui.png)
![Hand Gesture Example](screenshots/hand_gesture.png)
```

---

## 🎬 Demo Video

Add a demo video here:

```
[![Watch the demo](screenshots/demo_thumb.png)](https://www.youtube.com/watch?v=YOUR_VIDEO_LINK)
```

---

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**GitHub:** [pranayguptag](https://github.com/pranayguptag)

---

## 💡 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 Acknowledgements
- [MediaPipe](https://mediapipe.dev/)
- [OpenCV](https://opencv.org/)
- [Streamlit](https://streamlit.io/)

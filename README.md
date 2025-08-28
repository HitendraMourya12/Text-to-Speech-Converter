# Text-to-Speech-Converter

🔊 Text-to-Speech Converter (Flask + Pyttsx3)

A simple **Text-to-Speech (TTS) web application** built with **Flask** and **pyttsx3** that allows users to convert text into natural-sounding speech. The app provides a clean web interface where users can enter text, choose voices, adjust speech rate, and control volume. The generated speech can be played directly in the browser or downloaded as an audio file.

✨ Features

* 🎤 Convert text to speech using `pyttsx3`
* 🌐 Web interface built with **Flask**
* 🎚️ Adjustable **voice**, **speech rate**, and **volume**
* 📥 Downloadable audio file in `.wav` format
* ⚡ Real-time audio playback in browser
* 🚀 Lightweight and easy to run locally

---

📦 Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/HitendraMourya12/Text-to-Speech-Converter.git
   cd Text-to-Speech-Converter
   ```

2. Install required dependencies:

   ```bash
   pip install flask pyttsx3
   ```

---

▶️ Usage

1. Run the Flask application:

   ```bash
   python web.py
   ```

2. Open your browser and go to:

   ```
   http://localhost:5000
   ```

3. Enter your text, choose voice settings, and click **Convert to Speech** 🎵

---

📂 Project Structure

```
Text-to-Speech-Converter/
│
├── web.py              # Main Flask application
├── templates/
│   └── index.html      # Web UI template
└── README.md           # Project documentation
```

---
📡 API Endpoints

* `/` → Web UI
* `/api/voices` → Get available voices
* `/api/convert` → Convert text to speech (POST JSON: `{text, voice_id, rate, volume}`)
* `/audio/<filename>` → Download generated audio

---

## 🛠️ Requirements

* Python 3.7+
* Flask
* pyttsx3

Install with:

```bash
pip install flask pyttsx3
```

📸 Screenshot (UI Preview)

![UI Preview](https://via.placeholder.com/800x400?text=Text-to-Speech+Converter+Preview)

📌 Future Enhancements

* Add support for multiple languages
* Deploy on cloud (Heroku/Render)
* Provide MP3 output option
* Save conversion history

🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to add.

📜 License

This project is licensed under the **MIT License**.


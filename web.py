from flask import Flask, render_template, request, send_file, jsonify
import pyttsx3
import os
import tempfile
import threading
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure upload folder for temporary audio files
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class TTSConverter:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.setup_engine()
    
    def setup_engine(self):
        """Configure TTS engine with default settings"""
        # Set speech rate (words per minute)
        self.engine.setProperty('rate', 150)
        
        # Set volume (0.0 to 1.0)
        self.engine.setProperty('volume', 0.9)
        
        # Get available voices
        voices = self.engine.getProperty('voices')
        if voices:
            # Set default voice (usually first available)
            self.engine.setProperty('voice', voices[0].id)
    
    def get_voices(self):
        """Get list of available voices"""
        voices = self.engine.getProperty('voices')
        voice_list = []
        for voice in voices:
            voice_list.append({
                'id': voice.id,
                'name': voice.name,
                'gender': getattr(voice, 'gender', 'unknown'),
                'age': getattr(voice, 'age', 'unknown')
            })
        return voice_list
    
    def convert_text_to_speech(self, text, voice_id=None, rate=150, volume=0.9):
        """Convert text to speech and save as audio file"""
        try:
            # Configure engine
            if voice_id:
                self.engine.setProperty('voice', voice_id)
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
            
            # Generate unique filename
            audio_filename = f"tts_audio_{os.getpid()}_{threading.get_ident()}.wav"
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
            
            # Save speech to file
            self.engine.save_to_file(text, audio_path)
            self.engine.runAndWait()
            
            return audio_path
        except Exception as e:
            print(f"Error in TTS conversion: {str(e)}")
            return None

# Initialize TTS converter
tts_converter = TTSConverter()

@app.route('/')
def index():
    """Main page with TTS interface"""
    return render_template('index.html')

@app.route('/api/voices')
def get_voices():
    """API endpoint to get available voices"""
    try:
        voices = tts_converter.get_voices()
        return jsonify({'voices': voices})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/convert', methods=['POST'])
def convert_text():
    """API endpoint to convert text to speech"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        voice_id = data.get('voice_id')
        rate = int(data.get('rate', 150))
        volume = float(data.get('volume', 0.9))
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        if len(text) > 5000:
            return jsonify({'error': 'Text too long (max 5000 characters)'}), 400
        
        # Convert text to speech
        audio_path = tts_converter.convert_text_to_speech(text, voice_id, rate, volume)
        
        if audio_path and os.path.exists(audio_path):
            return jsonify({
                'success': True,
                'audio_url': f'/audio/{os.path.basename(audio_path)}'
            })
        else:
            return jsonify({'error': 'Failed to generate audio'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/audio/<filename>')
def serve_audio(filename):
    """Serve generated audio files"""
    try:
        filename = secure_filename(filename)
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if os.path.exists(audio_path):
            return send_file(audio_path, as_attachment=True, download_name=filename)
        else:
            return "Audio file not found", 404
    except Exception as e:
        return f"Error serving audio: {str(e)}", 500

# HTML Template (save as templates/index.html)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Text to Speech Converter</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        textarea, select, input[type="range"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e1e1;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        textarea {
            min-height: 120px;
            resize: vertical;
            font-family: inherit;
        }
        
        textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .controls {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 25px;
        }
        
        .range-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .range-value {
            min-width: 50px;
            text-align: center;
            font-weight: 600;
            color: #667eea;
        }
        
        .convert-btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .convert-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .convert-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .audio-player {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            text-align: center;
        }
        
        audio {
            width: 100%;
            max-width: 400px;
        }
        
        .error {
            color: #dc3545;
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 8px;
            padding: 12px;
            margin-top: 15px;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #667eea;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
            .controls {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .content {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔊 Text to Speech</h1>
            <p>Convert your text into natural-sounding speech</p>
        </div>
        
        <div class="content">
            <div class="form-group">
                <label for="text-input">Enter text to convert:</label>
                <textarea id="text-input" placeholder="Type or paste your text here... (max 5000 characters)" maxlength="5000"></textarea>
                <small style="color: #666; float: right; margin-top: 5px;">
                    <span id="char-count">0</span>/5000 characters
                </small>
            </div>
            
            <div class="controls">
                <div class="form-group">
                    <label for="voice-select">Voice:</label>
                    <select id="voice-select">
                        <option value="">Loading voices...</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="rate-slider">Speech Rate:</label>
                    <div class="range-group">
                        <input type="range" id="rate-slider" min="50" max="300" value="150">
                        <span class="range-value" id="rate-value">150</span>
                    </div>
                </div>
            </div>
            
            <div class="form-group">
                <label for="volume-slider">Volume:</label>
                <div class="range-group">
                    <input type="range" id="volume-slider" min="0" max="1" step="0.1" value="0.9">
                    <span class="range-value" id="volume-value">0.9</span>
                </div>
            </div>
            
            <button class="convert-btn" id="convert-btn">🎵 Convert to Speech</button>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Converting text to speech...</p>
            </div>
            
            <div id="error-message"></div>
            <div id="audio-container"></div>
        </div>
    </div>

    <script>
        let voices = [];
        
        // DOM elements
        const textInput = document.getElementById('text-input');
        const voiceSelect = document.getElementById('voice-select');
        const rateSlider = document.getElementById('rate-slider');
        const volumeSlider = document.getElementById('volume-slider');
        const convertBtn = document.getElementById('convert-btn');
        const loading = document.getElementById('loading');
        const errorMessage = document.getElementById('error-message');
        const audioContainer = document.getElementById('audio-container');
        const charCount = document.getElementById('char-count');
        const rateValue = document.getElementById('rate-value');
        const volumeValue = document.getElementById('volume-value');
        
        // Load available voices
        async function loadVoices() {
            try {
                const response = await fetch('/api/voices');
                const data = await response.json();
                voices = data.voices;
                
                voiceSelect.innerHTML = '<option value="">Default Voice</option>';
                voices.forEach(voice => {
                    const option = document.createElement('option');
                    option.value = voice.id;
                    option.textContent = `${voice.name} (${voice.gender})`;
                    voiceSelect.appendChild(option);
                });
            } catch (error) {
                console.error('Error loading voices:', error);
                voiceSelect.innerHTML = '<option value="">Default Voice</option>';
            }
        }
        
        // Update character count
        textInput.addEventListener('input', () => {
            charCount.textContent = textInput.value.length;
        });
        
        // Update slider values
        rateSlider.addEventListener('input', () => {
            rateValue.textContent = rateSlider.value;
        });
        
        volumeSlider.addEventListener('input', () => {
            volumeValue.textContent = volumeSlider.value;
        });
        
        // Convert text to speech
        convertBtn.addEventListener('click', async () => {
            const text = textInput.value.trim();
            
            if (!text) {
                showError('Please enter some text to convert.');
                return;
            }
            
            if (text.length > 5000) {
                showError('Text is too long. Maximum 5000 characters allowed.');
                return;
            }
            
            setLoading(true);
            clearError();
            
            try {
                const response = await fetch('/api/convert', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        text: text,
                        voice_id: voiceSelect.value,
                        rate: parseInt(rateSlider.value),
                        volume: parseFloat(volumeSlider.value)
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showAudioPlayer(data.audio_url);
                } else {
                    showError(data.error || 'Failed to convert text to speech.');
                }
            } catch (error) {
                console.error('Error:', error);
                showError('Network error. Please try again.');
            } finally {
                setLoading(false);
            }
        });
        
        function setLoading(isLoading) {
            convertBtn.disabled = isLoading;
            loading.style.display = isLoading ? 'block' : 'none';
        }
        
        function showError(message) {
            errorMessage.innerHTML = `<div class="error">${message}</div>`;
        }
        
        function clearError() {
            errorMessage.innerHTML = '';
        }
        
        function showAudioPlayer(audioUrl) {
            audioContainer.innerHTML = `
                <div class="audio-player">
                    <h3>🎵 Generated Speech</h3>
                    <audio controls>
                        <source src="${audioUrl}" type="audio/wav">
                        Your browser does not support the audio element.
                    </audio>
                    <br><br>
                    <a href="${audioUrl}" download="speech.wav" style="color: #667eea; text-decoration: none;">
                        📥 Download Audio File
                    </a>
                </div>
            `;
        }
        
        // Initialize
        loadVoices();
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    # Create templates directory and save HTML template
    os.makedirs('templates', exist_ok=True)
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(HTML_TEMPLATE)
    
    print("Text-to-Speech Web Application")
    print("==============================")
    print("Requirements:")
    print("pip install flask pyttsx3")
    print("")
    print("To run the application:")
    print("python app.py")
    print("")
    print("Then open: http://localhost:5000")
    
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)

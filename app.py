import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from gtts import gTTS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'audio'
app.secret_key = 'your_secret_key'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def cleanup_old_files():
    now = datetime.now()
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file_creation_time = datetime.fromtimestamp(os.path.getctime(filepath))
        if now - file_creation_time > timedelta(hours=1):
            os.remove(filepath)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['text']
        language = request.form['language']
        speed = request.form.get('speed', 'normal')
        
        if not text:
            flash('Please enter some text to convert!', 'warning')
            return redirect(url_for('index'))
        
        filename = f"output_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            is_slow = False
            if speed == 'slow':
                is_slow = True
            
           
            tts = gTTS(text=text, lang=language, slow=is_slow)
            tts.save(filepath)
            flash('Audio generated successfully!', 'success')
        except Exception as e:
            flash(f'Error generating audio: {str(e)}', 'danger')
            return redirect(url_for('index'))
        
        cleanup_old_files()
        return redirect(url_for('index', audio_file=filename))
    
    audio_file = request.args.get('audio_file')
    return render_template('index.html', audio_file=audio_file)

@app.route('/download/<filename>')
def download(filename):
    safe_filename = os.path.basename(filename)
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], safe_filename), 
                    as_attachment=True, 
                    download_name=f"audio_{safe_filename}")

@app.route('/audio/<filename>')
def audio(filename):
    safe_filename = os.path.basename(filename)
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], safe_filename))

if __name__ == '__main__':
    app.run(debug=True)
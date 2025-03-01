from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('pages/home.html')

@app.route('/image-to-json')
def image_to_json():
    return render_template('pages/image-to-json.html')
    
@app.route('/audio-to-text')
def audio_to_text():
    return render_template('pages/audio-to-text.html')

@app.route('/text-to-feelings')
def text_to_feelings():
    return render_template('pages/text-to-feelings.html')

# text-to-audio
@app.route('/text-to-audio')
def text_to_audio():
    return render_template('pages/text-to-audio.html')
    
@app.route('/image-to-text')
def image_to_text():
    return render_template('pages/image-to-text.html')

@app.route('/voices')
def voices():
    return render_template('pages/voices.html')

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, send_file
from youtube_to_psd import generate_email_image
import uuid
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        youtube_url = request.form['youtube_url']
        headline = request.form['headline']
        color = request.form['color']
        branding = request.form['branding']
        timestamp = request.form.get('timestamp') or None

        output = f"output_{uuid.uuid4().hex}.jpg"

        generate_email_image(
            psd_path="Video.psd",
            youtube_url=youtube_url,
            output_jpg=output,
            headline_text=headline,
            color_hex=color,
            branding=branding,
            still_timestamp=timestamp
        )

        return send_file(output, as_attachment=True)

    return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

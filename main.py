from flask import Flask, send_file, request, redirect, url_for, render_template, jsonify
from infinite import InfiniteContent
import threading
import os
import io

os.system('export "PATH=$PWD/dir/usr/bin:$PATH"')

app = Flask(__name__)


@app.route('/', methods=['GET'])
def get_root():
    with open('templates/index.html', 'r') as file:
        html = file.read()
    return html


@app.route('/generate/', methods=['POST'])
def generate_episode():
    seed = request.form.get('seed')
    episode_no = int(request.form.get('episode_no'))
    api_key = request.form.get('api_key')
    content = InfiniteContent(seed, False, api_key)
    filename = content.filename
    t = threading.Thread(target=content.main, kwargs={
                         'episode_no': episode_no})
    t.start()

    return redirect(f"/status_check/{filename}")


@app.route('/download/<filename>', methods=['GET'])
def download_episode(filename):
    with open(f"results/{filename}", "rb") as f:
        video = io.BytesIO(f.read())

    # os.remove(f"results/{filename}")
    return send_file(video, as_attachment=True, download_name="result.mp4")


@app.route('/status_check/<filename>', methods=['GET'])
def status_checker(filename):
    return render_template("status_checker.html", filename=filename)


@app.route('/status/', methods=['POST'])
def status():
    # Get data from the request
    data = request.json
    filename = data['filename']

    # Process the data and prepare a response
    response_data = {
        'done': os.path.exists(f"results/{filename}")
    }

    # Return a JSON response
    return jsonify(response_data)


if __name__ == '__main__':
    app.run()

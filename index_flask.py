from flask import Flask, render_template, request
import subprocess
from decouple import config

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        token = request.form.get('token')
        mail = request.form.get('mail')

        # Validate the inputs (still an essential step that's not shown here)

        # cmd = ["docker", "run", "dcollect-app", "--username", username, "--token", token, "--mail", mail]
        cmd = ["python", "dcollection.py", "--username", username, "--token", token, "--mail", mail]

        # subprocess.run(cmd)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            # Handle error
            return f"An error occurred: {stderr.decode('utf-8')}"
        else:
            return f"Container started with output: {stdout.decode('utf-8')}"

    return render_template('input_form.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config('PORT', default=5000))


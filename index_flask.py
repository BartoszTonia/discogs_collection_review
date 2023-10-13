from flask import Flask, render_template, request, session
from lib.credentials import Credentials
from decouple import config
import subprocess
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if a job is already running for this session
        if session.get('job_running'):
            return "A job is already running. Please wait."

        # Mark that a job is running
        session['job_running'] = True

        # Load default credentials
        creds = Credentials()

        # Get form values or use defaults if they are empty
        username = request.form.get('username') or creds.user
        token = request.form.get('token') or creds.token
        mail = request.form.get('mail') or creds.mail_out

        # Validate the inputs (still an essential step that's not shown here)

        # cmd = ["docker", "run", "dcollect-app", "--username", username, "--token", token, "--mail", mail]
        cmd = ["python", "dcollection.py", "--user", username, "--token", token, "--mail", mail]

        # subprocess.run(cmd)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            # Handle error
            return f"An error occurred: {stderr.decode('utf-8')}"
        else:
            session['job_running'] = False
            return f"Container started with output: {stdout.decode('utf-8')}"

    return render_template('input_form.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config('PORT', default=5000))


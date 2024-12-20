from flask import Flask, render_template, request, redirect, session, url_for
import os
import csv

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong, unique key

USER_CSV = 'user.csv'
STREAM_CSV = 'stream.csv'

# Helper function to read user credentials from the CSV file
def read_user_credentials():
    users = {}
    if os.path.exists(USER_CSV):
        with open(USER_CSV, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) >= 2:
                    users[row[0]] = row[1]
    return users

# Helper function to save the video ID to the STREAM_CSV file
def save_video_id(video_id):
    """
    Save the given video ID to the STREAM_CSV file.
    Creates the file if it does not exist.
    """
    with open(STREAM_CSV, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([video_id])

# Helper function to read the video ID from the STREAM_CSV file
def read_video_id():
    """
    Read the video ID from the STREAM_CSV file.
    Returns the video ID if it exists, or None if the file is empty.
    """
    if os.path.exists(STREAM_CSV):
        with open(STREAM_CSV, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row:
                    return row[0]
    return None

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()

        if username == 'admin' and password == '1234':
            session['user'] = 'admin'
            return redirect(url_for('admin_page'))

        users = read_user_credentials()
        if username in users and users[username] == password:
            session['user'] = 'user'
            return redirect(url_for('user_page'))

        return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))

    stream_id = read_video_id()
    video_src = None

    if request.method == 'POST':
        # Video link entered by the admin
        video_link = request.form.get('videoLink', '').strip()

        # Preview button logic
        if 'preview' in request.form:
            stream_id = extract_youtube_id(video_link)
            if stream_id:
                save_video_id(stream_id)
                video_src = f"https://www.youtube.com/embed/{stream_id}"
            else:
                return render_template('admin.html', error='Invalid YouTube link', video_src=None, stream_id=None)

        # Start Stream button logic
        elif 'start_stream' in request.form:
            stream_id = read_video_id()
            if stream_id:
                video_src = f"https://www.youtube.com/embed/{stream_id}"
            else:
                return render_template('admin.html', error='No video ID found. Please preview a link first.', video_src=None, stream_id=None)

        # End Stream button logic
        elif 'end_stream' in request.form:
            if os.path.exists(STREAM_CSV):
                os.remove(STREAM_CSV)
            # else 
            stream_id = None
            video_src = None
            

    return render_template('admin.html', video_src=video_src, stream_id=stream_id)

@app.route('/user', methods=['GET'])
def user_page():
    if 'user' not in session or session['user'] != 'user':
        return redirect(url_for('login'))

    stream_id = read_video_id()
    video_src = f"https://www.youtube.com/embed/{stream_id}" if stream_id else None
    return render_template('user.html', video_src=video_src , stream_id=stream_id)
# ,stream_id=stream_id

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Helper function to extract YouTube video ID from a URL
def extract_youtube_id(link):
    """
    Extract the YouTube video ID from a given URL.
    Returns the video ID if found, or None otherwise.
    """
    import re
    match = re.search(r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/live\/)([a-zA-Z0-9_-]{11})', link)
    return match.group(1) if match else None

if __name__ == '__main__':
    app.run(debug=True, host ="0.0.0.0")

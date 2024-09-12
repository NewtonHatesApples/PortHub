from hashlib import sha256
from os import path, getcwd
from random import randint

from cachelib import FileSystemCache
from cs50 import SQL
from flask import Flask, render_template, request, redirect, session, send_file

from flask_session import Session
from datetime import datetime
from pytz import timezone

app = Flask(__name__)

user_db = SQL("sqlite:///users.db")
uploads_db = SQL("sqlite:///uploads.db")
chatRecord_db = SQL("sqlite:///chatRecord.db")

# DO NOT CHANGE ANYTHING IN THE FOLLOWING SECTION!
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "cachelib"
app.config["SESSION_CACHELIB"] = FileSystemCache(cache_dir="flask_session", threshold=500)
app.config["SECRET_KEY"] = "BigSecret!"  # (This is changeable)
app.config["MAX_CONTENT_LENGTH"] = int(1.5 * 1024 * 1024)  # 1.5MB
# SECTION END

UPLOAD_DIRECTORY = "user_uploads"  # Ensure this directory exists (locally, at the same level as app.py) first before changing it!
MAX_FILE_DISPLAY = 30  # Maximum number of files displayed on homepage (Changeable anytime)
MAX_FILE_SIZE = int(1.5 * 1024 * 1024)  # 1.5MB
MAX_PROFILE_DISPLAY = 15  # Maximum number of profiles displayed on search box
BABY_SHARK_LINK = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

CHECK_CONSENT = "ph_consent"  # These are cookies stuff (Changeable anytime)
CHECK_USERNAME = "username"  # These are cookies stuff (NOT Changeable anytime)
CHECK_REGISTER = "REGISTER_NEW"  # These are cookies stuff (Changeable anytime)

CONSENT_VALUE = "consent"  # These are cookies stuff (Changeable anytime)
RESET_CONSENT_VALUE = "not_yet"  # These are cookies stuff (Changeable anytime)
NEW_REGISTER_VALUE = "NEW"  # These are cookies stuff (Changeable anytime)
RESET_REGISTER_VALUE = "nah"  # These are cookies stuff (Changeable anytime)

Session(app)


def valid_register(usr: str, pwd: str):
    if not (4 <= len(usr) <= 16):
        return False, "Username must be between 4 to 16 characters long."
    elif not (len(pwd) >= 8):
        return False, "Password must be at least 8 characters"
    elif " " in usr:
        return False, "Username must not contain spaces."
    elif " " in pwd:
        return False, "Password must not contain spaces."
    if user_db.execute("SELECT * FROM users WHERE username=?;", usr):
        return False, "Username has already been taken."
    return True, "Account registered successfully!"


def validate_upload():
    file = request.files.get("upload_file")
    if file is None or file.filename == "" or file.content_type == "application/octet-stream":
        return False, "No files are selected!"
    elif file.content_length > 3 * 1024 * 1024:
        return False, f"Your file content is {file.content_length / (1024 ** 2)} MB, which is larger than 3MB!"
    else:
        return True, "Valid upload request"


def upload_file():
    uploaded_file = request.files["upload_file"]
    filename = hex(randint(0, 2 ** 64)).replace("0x", "")
    if uploaded_file.content_type.find("+") == -1:
        filetype = uploaded_file.content_type[uploaded_file.content_type.find('/') + 1:]
    else:
        filetype = uploaded_file.content_type[uploaded_file.content_type.find('/') + 1: uploaded_file.content_type.find("+")]
    filename_with_type = f"{filename}.{filetype}"
    file_path = path.join(app.root_path, UPLOAD_DIRECTORY, filename_with_type)
    while not save_upload_to_db(session.get(CHECK_USERNAME), file_path, filename_with_type):
        filename = hex(randint(0, 2 ** 64)).replace("0x", "")
        filename_with_type = f"{filename}.{filetype}"
        file_path = path.join(app.root_path, UPLOAD_DIRECTORY, filename_with_type)
        continue
    else:
        uploaded_file.save(file_path, buffer_size=MAX_FILE_SIZE)
    return True, "File uploaded successfully!"


def validate_login(usr: str, pwd: str):
    enc_password = sha256(pwd.encode()).hexdigest()
    return user_db.execute("SELECT * FROM users WHERE (username=? AND password=?);", usr, enc_password)


def save_upload_to_db(username: str, file_path: str, filename: str):
    if uploads_db.execute("SELECT * FROM uploads WHERE file_path=?;", file_path):
        return False
    else:
        uploads_db.execute("INSERT INTO uploads (username, file_path, filename) VALUES (?, ?, ?);", username, file_path,
                           filename)
        return True


def fetch_files(user=None):
    if user is None:
        file_paths = uploads_db.execute("SELECT filename FROM uploads LIMIT ?;", MAX_FILE_DISPLAY)
    else:
        file_paths = uploads_db.execute("SELECT filename FROM uploads WHERE username=? LIMIT ?;", user,
                                        MAX_FILE_DISPLAY)
    filename_author_list = []
    for file_path in file_paths:
        filename = file_path["filename"]
        author = uploads_db.execute("SELECT username FROM uploads WHERE filename=?;", filename)[0]["username"]
        filename_author_list.append([filename, author])
    return filename_author_list


def fetch_profile(username):
    profile_from_db = user_db.execute("SELECT profile FROM profiles WHERE username=?;", username)
    if not profile_from_db:
        profile_from_user = ""
    else:
        profile_from_user = profile_from_db[0]["profile"]
    return profile_from_user


def check_user_exist(username):
    result = user_db.execute("SELECT username FROM users WHERE username=?;", username)
    return bool(result)


@app.before_request
def validate_consent():
    if request.endpoint != "warning":
        if CHECK_CONSENT not in session:
            session[CHECK_CONSENT] = RESET_CONSENT_VALUE
            if request.endpoint != "static":
                return render_template("warning.html")
        elif session[CHECK_CONSENT] != CONSENT_VALUE:
            if request.endpoint != "static":
                return render_template("warning.html")


@app.route("/search", methods=["GET"])
def search():
    q = request.args.get("q")
    if q:
        list_of_users = user_db.execute("SELECT * FROM users WHERE username LIKE ? LIMIT ?;", '%' + q + '%', MAX_PROFILE_DISPLAY)
        list_of_user_count = []
        for user in list_of_users:
            username = user["username"]
            upload_from_user = uploads_db.execute("SELECT COUNT(*) FROM uploads WHERE username=?;", username)[0]["COUNT(*)"]
            list_of_user_count.append([username, upload_from_user])
    else:
        list_of_user_count = []
    return render_template("search.html", list_of_user_count=list_of_user_count)


@app.route("/", methods=["GET"])
def index():
    if CHECK_USERNAME in session:
        return redirect("/home")
    filename_author_list = fetch_files()
    return render_template("index.html", filename_author_list=filename_author_list)


@app.route("/user_uploads/<path:filename>")
def serve_upload_file(filename):
    if not uploads_db.execute("SELECT * FROM uploads WHERE filename=?;", filename):
        return redirect(BABY_SHARK_LINK)
    file_path = path.join(getcwd(), UPLOAD_DIRECTORY, filename)
    return send_file(file_path)


@app.route("/warning", methods=["POST"], endpoint="warning")
def warning():
    if request.method == "POST":
        if request.form.get("agree") == "agree":
            session[CHECK_CONSENT] = CONSENT_VALUE
            return redirect("/")
        else:
            session[CHECK_CONSENT] = RESET_CONSENT_VALUE
            return redirect(BABY_SHARK_LINK)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if CHECK_REGISTER not in session:
            return render_template("login.html")
        elif session[CHECK_REGISTER] == NEW_REGISTER_VALUE:
            register_message = "Account created successfully!"
            session[CHECK_REGISTER] = RESET_REGISTER_VALUE
            return render_template("login.html", register_message=register_message)
        else:
            return render_template("login.html")
    elif request.method == "POST":
        username, password = request.form.get("username"), request.form.get("password")
        if validate_login(username, password):
            session[CHECK_USERNAME] = username
            return redirect("/home")
        else:
            return render_template("login.html", login_message="Invalid username or password!")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        usr, pwd = request.form.get("username").lower(), request.form.get("password")
        response, message = valid_register(usr, pwd)
        if response:
            enc_password = sha256(pwd.encode()).hexdigest()
            user_db.execute("INSERT INTO users (username, password) VALUES (?, ?);", usr, enc_password)
            session[CHECK_REGISTER] = NEW_REGISTER_VALUE
            return redirect("/login")
        else:
            return render_template("register.html", register_message=message)


@app.route("/home", methods=["GET", "POST"])
def home():
    user = session.get(CHECK_USERNAME)
    if user is None:
        return redirect(BABY_SHARK_LINK)
    if request.method == "GET":
        filename_author_list = fetch_files()
        return render_template("home.html", filename_author_list=filename_author_list)
    if request.method == "POST":
        if request.form.get("user") != session[CHECK_USERNAME]:
            session.clear()
            return redirect("/")
        validity_upload, upload_message = validate_upload()
        if validity_upload:
            validity_success, upload_message = upload_file()
            if validity_success:
                return redirect("/home")
            else:
                return redirect("/home")
        else:
            return redirect("/home")


@app.route("/logout")
def logout():
    session.clear()
    session[CHECK_CONSENT] = CONSENT_VALUE
    return redirect("/")


@app.route("/terms_and_conditions")
def terms_and_conditions():
    return render_template("terms_and_conditions.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    if request.method == "GET":
        if not check_user_exist(username):
            session.clear()
            return redirect(BABY_SHARK_LINK)
        profile_from_user = fetch_profile(username)
        user_uploaded = fetch_files(username)
        return render_template("profile.html", username=username, profile=profile_from_user, uploads=user_uploaded)
    elif request.method == "POST":
        if request.form.get("username") != session.get(CHECK_USERNAME):
            session.clear()
            return redirect(BABY_SHARK_LINK)
        else:
            new_profile = request.form.get("new_profile")
            if new_profile is None or new_profile == "":
                return render_template("profile.html", update_message="Profile submitted must not be empty!",
                                       username=username, profile=fetch_profile(username),
                                       uploads=fetch_files(username))
            else:
                user_db.execute("DELETE FROM profiles WHERE username=?;", username)
                user_db.execute("INSERT INTO profiles (username, profile) VALUES (?, ?);", username, new_profile)
                # No UPDATE statement because need to consider users update profile for the first time
                return redirect(f"/profile/{username}")


@app.route("/info")
def info():
    user_count = user_db.execute("SELECT COUNT(*) FROM users;")[0]["COUNT(*)"]
    upload_count = uploads_db.execute("SELECT COUNT(*) FROM uploads;")[0]["COUNT(*)"]
    time_now = datetime.now(timezone("Asia/Hong_Kong")).strftime("%Y %b %d %H:%M:%S")
    return render_template("info.html", user_count=user_count, upload_count=upload_count, time_now=time_now)


# TODO Patch the bug that same username can exist with uppercase and lowercase difference


@app.route("/forum")
def forum():
    user_count = chatRecord_db.execute("CREATE TABLE chats;")
    return render_template("forum.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

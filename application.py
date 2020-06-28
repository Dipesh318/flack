import os

from collections import deque

from flask import Flask, render_template, session, request, redirect,flash
from flask_socketio import SocketIO, send, emit, join_room, leave_room

from authenticate import auth
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '../project2/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config["SECRET_KEY"] = "my secret key"
socketio = SocketIO(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Keep track of channels created (Check for channel name)
channelsCreated = []

# Keep track of users logged (Check for username)
usersLogged = []

# Instanciate a dict
channelsMessages = {}





@app.route("/", methods=['GET','POST'])
def index():
    if request.method == "POST":
        session.clear()
        username = request.form.get("username")
        if username in usersLogged:
            flash("User Error","danger")
            return render_template("error.html", message="that username already exists!")                   
        usersLogged.append(username)
        session['username'] = username
        session.permanent = True
        flash(f"Welcome {username}")
        return redirect("/")
    else:
        if auth():
            flash("Create a channel or join into existing channel","info")
            return render_template("channel.html", channels=channelsCreated)
        else:
            return render_template("user.html")


@app.route("/change", methods=["GET", "POST"])
def nameChange():
    if auth():
        if request.method == "POST":
            newName = request.form.get("new_name")
            print(session.get('username'))
            currentName = session.get('username')
            session['username'] = newName
            usersLogged.remove(currentName)
            usersLogged.append(newName)
            for room in channelsCreated:
                for data in channelsMessages[room]:
                    if data['user'] == currentName:
                        data['user'] = newName
            flash("Name Changes successful. Refresh to see changes","success")
            return render_template("channel.html", channels= channelsCreated, messages=channelsMessages[session.get('channel')])
        else:
            return render_template("change.html", channels=channelsCreated)
    else:
        flash("Login Error", "danger")
        return render_template("error.html", message="You need to be logged in!")



@app.route("/logout", methods=['GET'])
def logout():
    try:
        usersLogged.remove(session['username'])
    except ValueError:
        pass
    session.clear()
    return redirect("/")

@app.route("/create", methods=['GET','POST'])
def create():
    if auth():
        newChannel = request.form.get("channel")
        if request.method == "POST":

            if newChannel in channelsCreated:
                flash("channel Error", "danger")
                return render_template("error.html", message="Channel by that name already exists!")

            channelsCreated.append(newChannel)
            channelsMessages[newChannel] = []
            
            print(channelsMessages)


            return redirect("/channels/" + newChannel)
        else:
            return render_template("create.html", channels = channelsCreated)
    else:
        flash("Login Error", "danger")
        return render_template("error.html", message="You need to be logged in!")



@app.route("/channels/<channel>", methods=['GET','POST'])
def enter_channel(channel):
    if auth():
        session['channel'] = channel
        if len(channelsMessages[channel]) > 100:
            channelsMessages[channel] = channelsMessages[channel][1:]
        return render_template("channel.html", selectedchannel=channel, channels= channelsCreated, messages=channelsMessages[channel])
    else:
        flash("Login Error", "danger")
        return render_template("error.html", message="You need to be logged in!")




@socketio.on("joined", namespace='/')
def joined():
    room = session.get('channel')
    print( session.get('channel'))
    join_room(room)
    emit('status join', {'userJoined': session.get('username'),'channel': room,'msg': session.get('username') + ' has entered the channel'}, room=room)


@socketio.on("left", namespace='/')
def left():
    room = session.get('channel')
    leave_room(room)
    username = session.get('username')
    session.clear()
    session['username'] = username
   

    emit('status left', {'msg': session.get('username') + ' has left the channel'},room=room)

@socketio.on('send message')
def send_msg(data):
    room = session.get('channel')
    print(data)
    result={"user":session["username"],"time":data['time'],"message":data['message']}
    if len(channelsMessages[room]) > 100:
        channelsMessages[room] = channelsMessages[room][1:]
    channelsMessages[room].append(result)
    print(result)
    emit('show msg',{"user":session["username"],"time":data['time'],"message":data['message']}, room=room)
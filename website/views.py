from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, Message, User
from . import db
import json
from datetime import datetime


#blueprint for all views of site
views = Blueprint('views', __name__)

#Home Page
@views.route('/', methods=['GET', 'POST'])
def welcome():
    return render_template('welcome.html', user=current_user, loggedIn=current_user.is_authenticated)

#Profile Page
@views.route('/profile/<first_name>', methods=['GET', 'POST'])
@login_required
def profile(first_name):
    #finds user with that first name
    user = User.query.filter_by(first_name=first_name).first()
    if user == None:
        #error if user with that first name does not exist
        flash('User %s not found.' % first_name, category='error')
        return redirect(url_for('views.welcome'))
    return render_template("profile.html", user=current_user, profile=user)

#template (delete later)
@views.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note Added!', category='success')

    return render_template("notes.html", user=current_user)

#Friends Page
@views.route('/friends', methods=['GET', 'POST'])
@login_required
def friends():
    if request.method == 'POST':
        #access user's friend's info from different post sites
        #email = request.form.get('friend')
        username = request.form.get('friend')
        personId = request.form.get('accept')
        personId1 = request.form.get('decline')
        
        if username:
            #find user from add friend form// later to add to pending list
            user = User.query.filter_by(username=username).first()
        elif personId:
            #find user from Requests list// later to add to Friends List as both users follow each other
            user = User.query.filter_by(id=personId).first()
        elif personId1:
            #decline from Requests list
            personId1 = personId1[1:]
            user = User.query.filter_by(id=personId1).first()
            user.unfollow(current_user)
            db.session.commit()
            return redirect(url_for('views.friends'))
        else:
            #if user POSTS or clicks on the add friend button without typing any username in
            return redirect(url_for('views.friends'))
        
        if not user:
            flash('User does not exist!', category='error')
        elif user==current_user:
            flash('You cannot friend yourself!', category='error')
        elif user in current_user.followed:
            flash(user.first_name + ' is already added!', category='error')
        else:
            current_user.follow(user)
            db.session.commit()
            flash('Friend Added!', category='success')
        return redirect(url_for('views.friends'))
    else:
        return render_template("friends.html", user=current_user)

#see if you can later remove this and integrate it as part friends():
@views.route('delete-friend', methods=['POST'])
def delete_friend():
    person = json.loads(request.data)
    personId = person['personId']
    person = User.query.get(personId)
    current_user.unfollow(person)
    db.session.commit()
    return jsonify()

@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    
    return jsonify()



#Account Settings
@views.route('/account/<userId>', methods=['GET', 'POST'])
@login_required
def account(userId):
    user = User.query.filter_by(id=userId).first()
    if user != current_user:
        return redirect(url_for('views.welcome'))
    if request.method == 'POST':
        personId = request.form.get('deleteAccount')
        
    return render_template("account.html", user=current_user)

#MESSAGES

#Send Messages
@views.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    #recipient should be username of recipient
    user = User.query.filter_by(username=recipient).first()
    if user == None:
        #error if user with that username does not exist
        flash('Username %s not found.' % recipient, category='error')
        return redirect(url_for('views.welcome'))
    
    if request.method == 'POST':
        form = request.form.get('send')
        msg = Message(sender_id=current_user.id, recipient_id=user.id, body=form)
        db.session.add(msg)
        db.session.commit()
        flash('Message has been sent.')
        return redirect(url_for('views.send_message', recipient=recipient))

    return render_template('send_message.html', user=current_user, recipient=user)

#Read Message Recieved
@views.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    #read receipt
    current_user.last_message_read_time = datetime.utcnow()
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(
        Message.timestamp.desc())
    
    if request.method == 'POST':
        msgId = request.form.get('delete')
        msg = Message.query.filter_by(id=msgId).first()
        if msg:
            current_user.messages_received.remove(msg)
            db.session.commit()
            redirect(url_for('views.messages'))

    return render_template('messages.html', user=current_user, messages=messages, User=User)
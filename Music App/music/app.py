from flask import Flask, render_template, request, redirect, session, url_for
import os
from db import db
import plotly.express as px
import plotly.io as pi
from flask_login import login_user, login_required, current_user
from flask_login import LoginManager




app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)),'music_app.db')}"

db.init_app(app)    
app.app_context().push()


# db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)



app.app_context().push()
app.config['SECRET_KEY'] = 'urushamusicapp'

##########Loading Models ###########

from model import User, Admin, Track, playlist, song

db.create_all()

@login_manager.user_loader
def load_user(user_id):
    # Query and return a user by user_id
    return User.query.get(int(user_id))


recommended_tracks = [
    {'id': 1, 'name': 'Blank Space', 'creator': 'Taylor Swift'},
    {'id': 2, 'name': 'Calm Down', 'creator': 'Rema and Selena Gomez'},
    {'id': 3, 'name': 'Natu Natu', 'creator': 'Rahul Sipligunj and Kaala Bhairava'},
    {'id': 4, 'name': 'Company', 'creator': 'Emiway'},
    {'id': 5, 'name': 'Dilbaro', 'creator': 'Shankar-Ehsaan-Loy'},
    {'id': 6, 'name': 'Kesariya Balam', 'creator': 'Mame Khan'},
    {'id': 7, 'name': 'Love Me Like You Do', 'creator': 'Ellie Goulding'},
    {'id': 8, 'name': 'Loca', 'creator': 'Honey Singh'},
    {'id': 9, 'name': 'Sanak', 'creator': 'Badshah'},
    {'id': 10, 'name': 'Worth It', 'creator': 'Fifth Harmony'},
]


def get_track_from_database(track_id):
    for track in recommended_tracks:
        if track['id'] == track_id:
            return track

@app.route('/')
def Index_Page():
    template_path = os.path.join(app.template_folder, 'Index_Page.html')
    print(f'templatepath is: {template_path}')
    return render_template('Index_Page.html')



##################### User  Authentication ################


@app.route('/UserLogin', methods = ['POST','GET'])
def UserLogin():
    if request.method == 'POST':
        uname = request.form['username']
        pword = request.form['password']
        user_entry = User.query.filter_by(username=uname).first()

        if user_entry is None:
            return render_template('UserLogin.html', message="You are not registered. Please register first.")
        if user_entry.password == pword:
            session['username'] = uname
            session['user_id'] = user_entry.user_id
            login_user(user_entry, remember=True)
            return redirect('/User')
        return render_template('UserLogin.html', message="Incorrect password. Please try again.")
    return render_template('UserLogin.html')



@app.route('/UserRegister', methods=['POST', 'GET'])
def UserRegister():
    if request.method == 'POST':
        uname = request.form['username']
        email = request.form['email']
        pword = request.form['password']

        existing_user = User.query.filter_by(username=uname).first()

        if existing_user is not None:
            return render_template('UserRegister.html', message='User already registered! Use different Username')

        new_user = User(username=uname, email=email, password=pword)
        db.session.add(new_user)
        db.session.commit()

        session['username'] = uname
        session['user_id'] = new_user.user_id
        return redirect('/User')

    return render_template('UserRegister.html')


###################### Admin Authentication #################

@app.route('/AdminLogin', methods=['POST','GET'])
def AdminLogin():
    if request.method == 'POST':
        adminname = request.form['adminname']
        pword = request.form['password']

        Admin_entry = Admin.query.filter_by(adminname=adminname).first()

        if Admin_entry is None:
            return render_template('AdminLogin.html', message="Admin not registered")
        if Admin_entry.password == pword:
            session['adminname'] = adminname
            session['admin_id'] = Admin_entry.admin_id
            return redirect('/AdminDashboard')
        return render_template('AdminLogin.html', message="Incorrect password. Please try again.")
    return render_template('AdminLogin.html')


@app.route('/AdminReg', methods = ['POST','GET'])
def AdminReg():
    if request.method == 'POST':
        adminname = request.form['adminname']
        email = request.form['email']
        pword = request.form['password']

        existing_admin = Admin.query.filter_by(adminname=adminname).first()

        if existing_admin is not None:
            return render_template('AdminReg.html', message='already registered!')

        new_admin = Admin(adminname=adminname, email=email, password=pword)
        db.session.add(new_admin)
        db.session.commit()

        session['adminname'] = adminname
        session['admin_id'] = new_admin.admin_id
        return redirect('/AdminDashboard')

    return render_template('AdminReg.html')



########################### HomePage for users  ###################

@app.route('/User', methods=['POST', 'GET'])
def UserPage():
    recommended_tracks = '1'
    userId = current_user.user_id
    playlists = playlist.query.filter_by(user_id=userId).all()
    newsongs = song.query.filter(song.id > 10).all()
    searchh = song.query.all()

    if request.method == 'POST':
        selected_track_index = request.form.get('selected_track')
        selected_track_index_for_new_song = request.form.get('selected_track_for_new_song')
        searchh = request.form.get('search_query')
        
        if searchh is not None:
            rating= song.query.filter_by(ratings=searchh).first()
            if rating:
                return redirect(url_for('playsong', track_id=rating.id))
        if searchh is not None:
            song_match = song.query.filter_by(track=searchh).first()
            if song_match:
                return redirect(url_for('playsong', track_id=song_match.id))
        if searchh is not None:
            creator_match=song.query.filter_by(creator=searchh).first()
            if creator_match:
                return redirect(url_for('playsong', track_id=creator_match.id))
        if selected_track_index_for_new_song is not None:
            selected_track_index_for_new_song = int(selected_track_index_for_new_song)
            selected_track_index_for_new_song = song.query.get(selected_track_index_for_new_song)

            if selected_track_index_for_new_song:
                return redirect(url_for('playsong', track_id=selected_track_index_for_new_song.id))

        if selected_track_index:
            song_avial=song.query.get(selected_track_index)
            if song_avial: 
                return redirect(url_for('playsong', track_id=selected_track_index))
            else:
                return render_template('UserPage.html', message= 'Song is in the process of complete deletion, it cannot be reviewed right now! Enjoy Listening to other Songs!', recommended_tracks=recommended_tracks, playlists=playlists, newsongs=newsongs)
        
        if 'delete' in request.form:
            delete_playlist= request.form.get('delete_playlist')
            if delete_playlist:
                delete_playlist_id = playlist.query.get(delete_playlist)
                if delete_playlist_id:
                    db.session.delete(delete_playlist_id)
                    db.session.commit()
        return redirect(url_for('UserPage'))

    return render_template('UserPage.html', recommended_tracks=recommended_tracks, playlists=playlists, newsongs=newsongs)


################### Play your Songs #########################

@app.route('/playsong/<int:track_id>', methods=['GET', 'POST'])
def playsong(track_id):
    selected_track = song.query.get(track_id)
    song_url = selected_track.song_url
    if request.method == 'POST':
        
        searchh= request.form.get('search_query')
        if searchh is not None:
            song_match = song.query.filter_by(track=searchh).first()
            if song_match:
                return redirect(url_for('playsong', track_id=song_match.id))
        
        return "listning functionality"

    return render_template('playsong.html', song={'name': selected_track.track, 'creator': selected_track.creator, 'lyrics': selected_track.lyrics}, song_url=song_url,)



#################### Upload your songs #############################


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        title = request.form['title']
        creator = request.form['artist']
        lyrics = request.form['lyrics']
        

        existing_song = song.query.filter(song.track==title).first()

        if existing_song is not None:
            return render_template('Create.html', message='Song already registered!')

        new_song = song(track=title, creator=creator, lyrics=lyrics)
        db.session.add(new_song)
        db.session.commit()

        session['track'] = title
        session['id'] = new_song.id

        return render_template('Create.html', message='Successfully registered your Song!')
    

    return render_template('Create.html')


########################  Admin Can Review All Songs ###############


@app.route('/Reviewtracks', methods=['GET', 'POST'])
def Reviewtracks():
    if request.method == 'POST':
        if 'delete' in request.form:
            song_id_to_delete = request.form.get('song_to_delete')
            if song_id_to_delete:
                song_to_delete = song.query.get(song_id_to_delete)
                if song_to_delete:
                    db.session.delete(song_to_delete)
                    db.session.commit()

        else:
            track = request.form.get('track')
            creator = request.form.get('creator')

            new_song = song(track=track, creator=creator)
            db.session.add(new_song)
            db.session.commit()

    songs = song.query.all()
    return render_template('Reviewtracks.html', songs=songs)



#################### Admin can review all users and creators ################

@app.route('/ReviewCreator', methods=['GET', 'POST'])
def ReviewCreator():
    if request.method == 'POST':
        if 'delete' in request.form:
            Creator_to_delete = request.form.get('Creator_to_delete')
            if Creator_to_delete:
                Creator_to_delete = User.query.filter_by(role='Creator').first()
                if Creator_to_delete:
                    db.session.delete(Creator_to_delete)
                    db.session.commit()

    Users = User.query.all()
    return render_template('ReviewCreator.html', Users=Users)

######################## Creator Can edit Songs #################

@app.route('/edit/<int:song_id>', methods=['GET', 'POST'])
def edit(song_id):
    selected_song = song.query.get(song_id)

    if request.method == 'POST':
        new_title = request.form['new_title']
        new_creator = request.form['new_creator']
        new_lyrics = request.form['new_lyrics']

        selected_song.track = new_title
        selected_song.creator = new_creator
        selected_song.lyrics = new_lyrics
        db.session.commit()
        return redirect(url_for('creatordashboard'))

    return render_template('edit.html', selected_song=selected_song)



####################### Users Can Make a Playlist ######################

@app.route('/myplaylist', methods=['GET', 'POST'])
@login_required
def myplaylist():
    print("Request method:", request.method)
    print("Form data:", request.form)

    all_songs = song.query.all()

    if request.method == 'POST':
        playlist_name = request.form.get('playlist_name')
        selected_song_ids = request.form.getlist('selected_songs[]')

        print("Playlist Name:", playlist_name)
        print("Selected Song IDs:", selected_song_ids)

        playlists = playlist(name=playlist_name,user_id=current_user.user_id)

        for song_id in selected_song_ids:
            Song = song.query.get(song_id)
            playlists.songs.append(Song)

        db.session.add(playlists)
        db.session.commit()

        print("playlist created successfuly")

        return redirect(url_for('UserPage'))

    return render_template('myplaylist.html', all_songs=all_songs)





####################### Creators Authentication############################




@app.route('/creatorreg', methods=['POST', 'GET'])
def creatorreg():
    if request.method == 'POST':
        choice = request.form.get('choice')
        if choice == 'yes':
            user = User.query.filter_by(user_id = current_user.user_id).first()
            user.role = 'creator'
            db.session.commit()
            return redirect('/creatorhomepage')
        elif choice == 'no':
            return redirect('/User')
    if current_user.role == 'creator':
            return redirect('/creatorhomepage')

    return render_template('creatorregistration.html')

@app.route('/creatorhomepage', methods=['POST','GET'])
def creatorhomepage():
    return render_template('creatorhomepage.html')


#################### Admin Dashboard ########################

@app.route('/AdminDashboard', methods=['POST','GET'])
def AdminDashboard():
    data = {
        'Months': ['October', 'November'],
        'Total Users': [350, 1049]
    }
    count = 0
    creator_count = 0
    users = User.query.all()
    for user in users:
        if user.role == 'user':
            count +=1
        else:
            creator_count +=1
    max = 0
    songs = song.query.all()
    for son in songs:
        if son.ratings > max:
            max = son.ratings
    top_track = song.query.filter_by(ratings = max).first()
    top_tracks = song.query.order_by(song.ratings.desc()).limit(3).with_entities(song.track).all()
    top_track_names = [track.track for track in top_tracks]
    firstfig = px.line(data, x='Months', y='Total Users', title='App Usage Statistics')
    firstfig.update_layout(margin=dict(t=50, b=0, l=0, r=0), width=200, height=200)

    line_graph = pi.to_html(firstfig, full_html=False)

    data_pie = {
        'Category': ['User', 'Creator'],
        'Count': [count, creator_count],
    }
    secondfig_pie = px.pie(data_pie, names='Category', values='Count', title='User vs Creator Ratio')

    secondfig_pie.update_layout(margin=dict(t=50, b=0, l=0, r=0), width=200, height=200)
    pie_graph = pi.to_html(secondfig_pie, full_html=False)

    return render_template('AdminDashboard.html', line_graph=line_graph, pie_graph=pie_graph,count = count,creator_count=creator_count, top_track = top_track.track,top_track_names=top_track_names)


########################### Creator DashBoard #################################

@app.route('/creatordashboard', methods=['GET', 'POST'])
def creatordashboard():
    newsongs = song.query.filter(song.id > 10).all()

    if request.method =='POST':
        if 'delete' in request.form:
            delete_song_id = request.form.get('song_to_delete')
            if delete_song_id is not None:
                song_to_delete = song.query.get(delete_song_id)
                if song_to_delete:
                    db.session.delete(song_to_delete)
                    db.session.commit()

                return redirect(url_for('creatordashboard'))
        elif 'edit' in request.form:
            edit_song_id = request.form.get('edit_song')
            if edit_song_id:
                return redirect(url_for('edit', song_id=edit_song_id))     
        
        #if 'edit' in request.form:
            #edit_song= request.form.get('edit_song')
            #return redirect(url_for('edit'))

    return render_template('creatordashboard.html', newsongs=newsongs)


# @app.route('/edit',methods=['POST','GET'])
# def edit():
#  return render_template('edit.html',new_song=edit_song)


if __name__ == "__main__":
    app.run(debug=True)
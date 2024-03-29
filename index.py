# FLASK Tutorial 1 -- We show the bare bones code to get an app up and running

# imports
import os  # os is used to get environment variables IP & PORT
from flask import Flask  # Flask is the web app that we will customize
from flask import render_template
from flask import request, redirect, url_for
from flask import session
import bcrypt
from database import db
from models import Post as Post
from models import Report as Report
from models import User as User
from models import Comment as Comment
from forms import RegisterForm, CommentForm, Theme
from forms import LoginForm

app = Flask(__name__)  # create an app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_note_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'SE3155'

#  Bind SQLAlchemy db object to this Flask app
db.init_app(app)

# Setup models
with app.app_context():
    db.create_all()  # run under the app context


# a_user = {'name': 'mogli', 'email':'mogli@uncc.edu'}

# notes = {1: {'title': 'First note', 'text':'This is my first note', 'date': '10-1-2020'},
#              2: {'title': 'Second note', 'text':'This is my second note', 'date': '10-2-2020'},
#              3: {'title': 'Third note', 'text':'This is my third note', 'date': '10-3-2020'},
#             }

# @app.route is a decorator. It gives the function "index" special powers.
# In this case it makes it so anyone going to "your-url/" makes this function
# get called. What it returns is what is shown as the web page
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    my_posts = db.session.query(Post).all()

    if session.get('user'):
        user = db.session.query(User).filter_by(id=session['user_id']).one()
        form = Theme()
        if form.validate_on_submit():
            user.is_dark = not user.is_dark
            db.session.add(user)
            db.session.commit()
        if user.is_dark:
            css = url_for('static', filename='main_dark.css')
        else:
            css = url_for('static', filename='main.css')
        # if session.get('user'):
        #     return render_template('index.html', user=session['user'], posts=my_posts, form=form, css=css)
        return render_template('index.html', user1=user, user=session['user'], posts=my_posts, form=form, css=css)

    return render_template("index.html", css=url_for('static', filename='main.css'))


@app.route('/myAccount')
def myAccount():
    if session.get('user'):
        css = get_theme()
        my_user = db.session.query(User).filter_by(id=session['user_id']).one()
        my_postz = db.session.query(Post).filter_by(user_id=session['user_id']).all()
        return render_template('myAccount.html', user=my_user, numposts=len(my_postz), css=css)
    else:
        return redirect(url_for("login.html"))


@app.route('/contact')
def contact():
    css = get_theme()
    return render_template("contact.html", user=session['user'], css=css)


@app.route('/about')
def about():
    css = get_theme()
    return render_template("about.html", user=session['user'], css=css)


@app.route('/myAccount/editAccount/', methods=['GET', 'POST'])
def edit_account():
    if session.get('user'):
        css = get_theme()
        if request.method == 'POST':
            # get title data
            first_name = request.form['firstname']
            last_name = request.form['lastname']
            user = db.session.query(User).filter_by(id=session.get('user_id')).one()

            user.first_name = first_name
            user.last_name = last_name

            db.session.add(user)
            db.session.commit()

            return redirect(url_for('myAccount'))

        else:
            # GET request - show new note form to edit note
            # retrieve user from db

            # retrieve note from db
            my_user = db.session.query(User).filter_by(id=session.get('user_id')).one()

            return render_template('editAccount.html', user1=my_user, user=session['user'], css=css)
    else:
        return redirect(url_for('login'))


@app.route('/viewPosts')
def get_posts():
    if session.get('user'):
        css = get_theme()
        # retrieve posts from database
        my_posts = db.session.query(Post).filter_by(user_id=session['user_id']).all()
        return render_template('viewPosts.html', posts=my_posts, user=session['user'], css=css)
    else:
        return redirect(url_for('login'))


@app.route('/viewPosts/<post_id>')
def get_post(post_id):
    my_post = db.session.query(Post).filter_by(id=post_id).one()

    css = get_theme()

    count = my_post.view_count
    my_post.view_count = count + 1

    db.session.add(my_post)
    db.session.commit()

    # create a comment form object
    form = CommentForm()
    return render_template('viewPost.html', post=my_post, user=session['user'], form=form, css=css)


@app.route('/viewPosts/addPost', methods=['GET', 'POST'])
def addPost():
    # print('request method is', request.method)
    if session.get('user'):
        css = get_theme()
        if request.method == 'POST':

            title = request.form['title']
            text = request.form['postText']
            img = request.form['img']
            # print(img)
            # if img == "Add Image":
            #     img = "/static/logo.jpg"
            count = 0
            count_1 = 0

            from datetime import date
            today = date.today()
            today = today.strftime("%m-%d-%Y")
            new_record = Post(title, text, img, today, count, count_1, session['user_id'])
            db.session.add(new_record)
            db.session.commit()
            return redirect(url_for('get_posts'))
        else:
            return render_template('addPost.html', user=session['user'], css=css)
    else:
        # user is not in session, redirect to login
        return render_template(url_for('login'))


@app.route('/viewPosts/edit/<post_id>', methods=['GET', 'POST'])
def update_post(post_id):
    if session.get('user'):
        css = get_theme()
        if request.method == 'POST':
            # get title data
            title = request.form['title']
            text = request.form['postText']
            img = request.form['img']
            post = db.session.query(Post).filter_by(id=post_id).one()

            post.title = title
            post.text = text
            post.img = img

            db.session.add(post)
            db.session.commit()

            return redirect(url_for('get_posts'))

        else:
            # GET request - show new note form to edit note
            # retrieve user from db

            # retrieve note from db
            my_post = db.session.query(Post).filter_by(id=post_id).one()

            return render_template('addPost.html', post=my_post, user=session['user'], css=css)
    else:
        return redirect(url_for('login'))


@app.route('/viewPosts/delete/<post_id>', methods=['POST'])
def delete_post(post_id):
    if session.get('user'):
        my_post = db.session.query(Post).filter_by(id=post_id).one()
        db.session.delete(my_post)
        db.session.commit()

        return redirect(url_for('get_posts'))
    else:
        return redirect(url_for('get_posts'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()

    if request.method == 'POST' and form.validate_on_submit():
        # salt and hash password
        h_password = bcrypt.hashpw(
            request.form['password'].encode('utf-8'), bcrypt.gensalt())
        # get entered user data
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        is_dark = False
        # create user model
        new_user = User(first_name, last_name, request.form['email'], h_password, is_dark)
        # add user to database and commit
        db.session.add(new_user)
        db.session.commit()
        # save the user's name to the session
        session['user'] = first_name
        session['user_id'] = new_user.id  # access id value from user model of this newly added user
        # show user dashboard view
        return redirect(url_for('index'))

    # something went wrong - display register view
    return render_template('register.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    # validate_on_submit only validates using POST
    if login_form.validate_on_submit():
        # we know user exists. We can use one()
        the_user = db.session.query(User).filter_by(email=request.form['email']).one()
        # user exists check password entered matches stored password
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), the_user.password):
            # password match add user info to session
            session['user'] = the_user.first_name
            session['user_id'] = the_user.id
            # render view
            return redirect(url_for('index'))

        # password check failed
        # set error message to alert user
        login_form.password.errors = ["Incorrect username or password."]
        return render_template("login.html", form=login_form)
    else:
        # form did not validate or GET request
        return render_template("login.html", form=login_form)


@app.route('/logout')
def logout():
    # check if a user is saved in session
    if session.get('user'):
        session.clear()

    return redirect(url_for('index'))


@app.route('/viewPosts/<post_id>/comment', methods=['POST'])
def new_comment(post_id):
    if session.get('user'):
        comment_form = CommentForm()
        # validate_on_submit only validates using POST
        if comment_form.validate_on_submit():
            # get comment data
            comment_text = request.form['comment']
            new_record = Comment(comment_text, int(post_id), session['user_id'])
            db.session.add(new_record)
            db.session.commit()

        return redirect(url_for('get_post', post_id=post_id))

    else:
        return redirect(url_for('login'))


@app.route('/viewPost/<post_id>/report', methods=['POST', 'GET'])
def report_post(post_id):
    if session.get('user'):
        my_post = db.session.query(Post).filter_by(id=post_id).one()
        css = get_theme()
        count = my_post.report_count
        my_post.report_count = count + 1
        if my_post.report_count < 3:
            if request.method == 'POST':

                issue = request.form['issue']
                content = request.form['content']
                new_record = Report(issue, content, int(post_id), session['user_id'])
                db.session.add(new_record)
                db.session.commit()
                count += 1
                print(count)
                return redirect(url_for('get_post', post_id=post_id))
            else:
                return render_template('report.html', user=session['user'], css=css)
        else:
            db.session.delete(my_post)
            db.session.commit()
            return redirect(url_for('index'))

    else:
        return redirect(url_for('login'))


def get_theme():
    user = db.session.query(User).filter_by(id=session['user_id']).one()
    if user.is_dark:
        css = url_for('static', filename='main_dark.css')
    else:
        css = url_for('static', filename='main.css')

    return css


app.run(host=os.getenv('IP', '127.0.0.1'), port=int(os.getenv('PORT', 5000)), debug=True)

# To see the web page in your web browser, go to the url,
#   http://127.0.0.1:5000

# Note that we are running with "debug=True", so if you make changes and save it
# the server will automatically update. This is great for development but is a
# security risk for production.

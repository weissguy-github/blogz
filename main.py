from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)

app.config['DEBUG'] =  True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:launchcode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'dA#FDF4fg5gfc9df23jfmvgsd06'

#Create as persistent classes
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')
  
    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

    def __repr__(self):
        return '<User %r>' % self.username

   

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.String(240))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  
    def __init__(self, title, body, usr_obj):
        self.title = title
        self.body = body
        self.owner = usr_obj  #Owner OBJECT

    def __repr__(self):
        return '<Blog %r>' % self.title


# before_request decorator runs function before 
# calling request handler for incoming request
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'list_blogs', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first() #return first response
        if user:
            if check_pw_hash(password, user.pw_hash):
                session['username'] = username  # "remember" user logged in
                flash("Welcome "+user.username)
                return redirect ('/newpost')
            else:
                flash('User password incorrect', 'error')
        else:
            flash('Username does not exist', 'error')

        return redirect('/login')
    else:
        return render_template('/login.html', title="Blogz")


@app.route("/signup", methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template('/signup.html')
    else:
        uname = request.form['username']
        if (len(uname) < 3 or
            len(uname) > 20 or
            uname.find(' ') >= 0):
            uname_error = 'Username must be 3-20 characters with no <space> character'
            uname=''
        elif User.query.filter_by(username=uname).first():
            uname_error = 'Username already exist. Pick different username.'
        else:
            uname_error = ''

        password = request.form['password']
        if (len(password) < 3 or
            len(password) > 20 or
            password.find(' ') >= 0):
            pwd_error = 'Password must be 3-20 characters with no <space> character'
        else:
            pwd_error = ''

        verify = request.form['verify']
        if password != verify:
            vp_error = 'Passwords do not match'
            password = ''
            verify = ''
        else:
            vp_error = ''

        if (uname_error + pwd_error + vp_error) == '':
            session['username'] = uname  # "remember" user logged in
            flash("Logged in")
            new_user = User(uname, password) #Default to null for blogs FK
            db.session.add(new_user)
            db.session.commit()
            return redirect('/newpost')
        else:
            return render_template('signup.html',
                uname=uname,        uname_error=uname_error,
                password=password,  pwd_error=pwd_error,
                verify=verify,      vp_error=vp_error)


@app.route('/newpost', methods=['POST','GET'])
def newpost():
    
    if request.method == 'POST':
        title = request.form['blog_title']
        if title:
            title_error = ''
        else:
            title_error = 'Please fill in the title'

        body = request.form['blog_body']
        if body:
            body_error = ''
        else:
            body_error = 'Please fill in the body'

        if title and body:

            user = User.query.filter_by(username=session['username']).first()
            new_post = Blog(title, body, user)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog?user='+str(user.username))
        else:
            return render_template('/newpost.html',
                blog_title=title,
                title_error=title_error,
                blog_body=body,
                body_error=body_error)
    else:
        return render_template('/newpost.html')

@app.route('/logout', methods=['POST','GET'])
def logout():
    del session['username']
    return redirect('/')


@app.route('/blog', methods=['POST', 'GET'])
def list_blogs():

    id = request.args.get('id')
    user = User.query.filter_by(username=request.args.get('user')).first()

    if id == None:
        if user == None:    #Display all for all users
            blogs = Blog.query.order_by(Blog.id.desc()).all()
        else:       #display all posts for this user
#            blogs = session.query(Blogs).\
            blogs = Blog.query.\
            filter_by(owner_id=user.id).\
            order_by(Blog.id.desc()).all()

#            blogs = Blog.query.\
#            filter_by(owner_id=user.id).\
#            order_by(Blog.id.desc()).all()
    else:           #display that blog entry
        blogs = Blog.query.filter_by(id=id).all()
    
    return render_template('blog.html', title="Blogz", blogs=blogs)

@app.route('/delete-task', methods=['POST'])
def delete_task():
    
    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()

    return redirect("/")

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', title="Blogz", users=users)

if __name__ == '__main__':
    app.run()

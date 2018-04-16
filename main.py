from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['DEBUG'] =  True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:launchcode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'dA#FDF4fg5gfcasdfjmvgsd006'

#Create as persistent class
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(240))
  
    def __init__(self, title, body):
        self.title = title
        self.body = body

# before_request decorator runs function before 
# calling request handler for incoming request
#@app.before_request
#def require_login():
#    allowed_routes = ['login', 'register']
#    if request.endpoint not in allowed_routes and 'email' not in session:
#        return redirect('/login')


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first() #return first response
        if user and user.password == password:
            session['email'] = email  # "remember" user logged in
            flash("Logged in")
            print(session)
            return redirect ('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')


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
            new_post = Blog(title, body)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog?id='+str(new_post.id))
        else:
            return render_template('/newpost.html',
                title="Add Blog Entry",
                blog_title=title,
                title_error=title_error,
                blog_body=body,
                body_error=body_error)
    else:
        return render_template('/newpost.html', title="Add Blog Entry")


@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    id = request.args.get('id')
    if id == None:
        blogs = Blog.query.order_by(Blog.id.desc()).all()
    else:
        #print ("ID = "+id)
        blogs = Blog.query.filter_by(id=id).all()
    
    return render_template('blog.html', title="Build A Blog", blogs=blogs)

@app.route('/delete-task', methods=['POST'])
def delete_task():
    
    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()

    return redirect("/")

if __name__ == '__main__':
    app.run()

import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort

# make a Flask application object called app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = "your secret key"



# Function to open a connection to the database.db file
def get_db_connection():
    # create connection to the database
    conn = sqlite3.connect('database.db')
    
    # allows us to have name-based access to columns
    # the database connection will return rows we can access like regular Python dictionaries
    conn.row_factory = sqlite3.Row

    #return the connection object
    return conn

#function to retrieve post from db by ID
def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()

    if post is None:
        abort(404)
    
    return post

# use the app.route() decorator to create a Flask view function called index()
@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute("SELECT * FROM posts").fetchall()
    conn.close()

    return render_template("index.html", posts=posts)


# route to create a post
@app.route("/create/", methods=("GET", "POST"))
def create():
    #POST or GET
    if request.method == "POST":
        #get title and content
        title = request.form["title"]
        content = request.form["content"]

        #display error if no title/content
        if not title:
            flash("Title is required!")
        elif not content:
            flash ("Content is required!")

        else: #insert data into database
            conn=get_db_connection()
            conn.execute("INSERT INTO posts (title, content) VALUES (?, ?)", (title, content))
            conn.commit()
            conn.close()

            return redirect(url_for("index"))

    return render_template("create.html")

#route to edit post
@app.route("/<int:id>/edit/", methods=["GET", "POST"]) #pass post ID as url parameter
def edit(id):
    #grab post from database with ID
    post = get_post(id)

    #POST or GET
    if request.method == "POST": #process form data, validate, update post, redirect home
        #get title and content
        title = request.form["title"]
        content = request.form["content"]

        #display error if no title/content
        if not title:
            flash("Title is required!")
        elif not content:
            flash ("Content is required!")

        else: #insert data into database
            conn=get_db_connection()
            conn.execute("UPDATE posts SET title = ?, content = ? WHERE id = ?", (title, content, id))
            conn.commit()
            conn.close()

            return redirect(url_for("index"))

    return render_template("edit.html", post=post)

#route to delete post, take id as param
@app.route("/<int:id>/delete/", methods=("POST",))
def delete(id):
    #get the post
    post = get_post(id)
    
    conn = get_db_connection() #connect to db

    conn.execute("DELETE from posts WHERE id = ?", (id,)) #delete post
    conn.commit()
    conn.close()

    flash('"{}" was successfully deleted!'.format(post['title'])) #flash success

    return redirect(url_for("index")) #redirect

app.run()
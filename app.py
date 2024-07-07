from flask import Flask, render_template, url_for, request, redirect, session
from dbconn import get_cassandra_session
from uuid import uuid4, UUID  

#flask init
app = Flask(__name__)
app.secret_key = 'admin'

#рут, если не логин, то редирект на логин, иначе на фид
@app.route('/')
def root():
    if 'username' in session:
        cas_session = get_cassandra_session()
        query = "SELECT * FROM posts"
        rows = cas_session.execute(query)
        posts = [{'username': row.username, 'content': row.content, 'likes': row.likes, 'id': row.id} for row in rows]
        cas_session.shutdown()
        return render_template("feed.html", posts=posts)
    return redirect(url_for("login"))

#логин, получение данных из форм, запрос для заполнения фида 
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method != "POST":
        return render_template("login.html")
    username = request.form["username"]
    password = request.form["password"]
    cas_session = get_cassandra_session()
    query = "SELECT * FROM users WHERE username = %s ALLOW FILTERING"
    rows = cas_session.execute(query, (username,))
    user = next((row for row in rows if row.password_hash == password), None)
    cas_session.shutdown()
    if user:
        session["username"] = user.username
        session["user_id"] = user.user_id
        cas_session = get_cassandra_session()
        query = "SELECT * FROM posts"
        rows = cas_session.execute(query)
        posts = [{'username': row.username, 'content': row.content, 'likes': row.likes, 'id': row.id} for row in rows]
        cas_session.shutdown()
        return render_template("feed.html", posts=posts)
    else:
        error = "Неверный логин или пароль."
        return render_template("login.html", error=error)

#логаут, заверщение сессии
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

#просмотр постов + форма на добавление поста (ограничение 200 символов)
@app.route("/feed", methods=["GET", "POST"])
def feed():
    if 'username' not in session:
        return redirect(url_for("login"))
    cas_session = get_cassandra_session()
    if request.method == "POST":
        content = request.form["content"][:200]
        username = session["username"]
        post_id = uuid4()
        query = "INSERT INTO posts (id, username, content, likes) VALUES (%s, %s, %s, %s)"
        cas_session.execute(query, (post_id, username, content, 0))
    query = "SELECT * FROM posts"
    rows = cas_session.execute(query)
    posts = [{'username': row.username, 'content': row.content, 'likes': row.likes, 'id': row.id} for row in rows]
    cas_session.shutdown()
    return render_template("feed.html", posts=posts)

#лайк посту по его id
@app.route("/like/<post_id>", methods=['POST'])
def like(post_id):
    if 'username' not in session:
        return redirect(url_for("login"))
    cassandra_session = get_cassandra_session()
    query_select = "SELECT likes FROM posts WHERE id = %s"
    result = cassandra_session.execute(query_select, (UUID(post_id),))
    current_likes = result.one()
    if current_likes:
        current_likes = current_likes.likes
    else:
        cassandra_session.shutdown()
        return "Post not found", 404
    updated_likes = current_likes + 1
    query_update = "UPDATE posts SET likes = %s WHERE id = %s"
    cassandra_session.execute(query_update, (updated_likes, UUID(post_id)))
    cassandra_session.shutdown()
    return redirect(url_for("feed"))

#удаление поста, по его id
@app.route("/delete/<post_id>", methods=['POST'])
def delete_post(post_id):
    if 'username' not in session:
        return redirect(url_for("login"))
    cassandra_session = get_cassandra_session()
    query_delete = "DELETE FROM posts WHERE id = %s"
    cassandra_session.execute(query_delete, (UUID(post_id),))
    cassandra_session.shutdown()
    return redirect(url_for("feed"))


if __name__ == "__main__":
    app.run(debug=True)
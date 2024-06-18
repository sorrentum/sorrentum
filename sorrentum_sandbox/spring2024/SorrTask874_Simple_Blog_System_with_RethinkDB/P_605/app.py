from flask import Flask, abort, render_template, request, redirect, url_for
from rethinkdb import RethinkDB

r = RethinkDB()
conn = r.connect("rethinkdb", 28015, db="blog").repl()

app = Flask(__name__)

def create_database():
    if "blog" not in r.db_list().run(conn):

        r.db_create("blog").run(conn)
        r.db("blog").table_create("posts").run(conn)

def add_post(title, content):
    post = {
        "title": title,
        "content": content,
        "comments": []
    }
    r.table("posts").insert(post).run(conn)

def get_posts():
    return list(r.table("posts").run(conn))

def get_post(post_id):
    return r.table("posts").get(post_id).run(conn)

def add_comment(post_id, commenter, comment):
    comment_data = {
        "commenter": commenter,
        "comment": comment
    }
    r.table("posts").get(post_id).update({
        "comments": r.row["comments"].append(comment_data)
    }).run(conn)

def delete_post(post_id):
    result = r.table("posts").get(post_id).delete().run(conn)
    
    if result['deleted'] > 0:
        pass  
    else:
        pass 

def edit_post(post_id, title, content):
    post = {
        "title": title,
        "content": content
    }
    r.table("posts").get(post_id).update(post).run(conn)

def delete_comment(post_id, comment_index):
    r.table("posts").get(post_id).update({
        "comments": r.row["comments"].delete_at(comment_index)
    }).run(conn)

#Routes

@app.route('/')
@app.route('/index')
def index():
    posts = get_posts()
    return render_template('home.html', posts=posts)

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        add_post(title, content)
        return redirect(url_for('index'))
    return render_template('create_post.html')

@app.route('/post/<post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        abort(404)
    return render_template('post.html', post=post)

@app.route('/post/<post_id>/add_comment', methods=['POST'])
def add_comment_route(post_id):
    commenter = request.form['commenter']
    comment = request.form['comment']
    add_comment(post_id, commenter, comment)
    return redirect(url_for('post', post_id=post_id))

@app.route('/post/<post_id>/edit', methods=['GET', 'POST'])
def edit_post_route(post_id):
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        edit_post(post_id, title, content)
        return redirect(url_for('post', post_id=post_id))
    else:
        post = get_post(post_id)
        if post is None:
            abort(404)
        return render_template('edit_post.html', post=post)


@app.route('/post/<post_id>/delete', methods=['POST'])
def delete_post_route(post_id):
    delete_post(post_id)
    return redirect(url_for('index'))


@app.route('/post/<post_id>/delete_comment/<int:comment_index>', methods=['POST'])
def delete_comment_route(post_id, comment_index):
    if request.method == 'POST':
        delete_comment(post_id, comment_index)
        return redirect(url_for('post', post_id=post_id))
    else:
        abort(405)

if __name__ == "__main__":
    create_database()
    app.run(host='0.0.0.0', port=5001)


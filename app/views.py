from app import app
from flask import render_template, flash, redirect, session, url_for, request, g, jsonify, abort
from flask_login import login_required, login_user, logout_user, current_user
from sys import stderr
from copy import copy
from app.forms import RegistrationForm, LoginForm, CreateBookForm, EditBookForm, CreateChapterForm, EditChapterForm, CommentForm
from app.user import User
from app.db import register_user, get_account, get_genres, add_book_with_genres, get_table_data, get_tables, get_books_by_author, get_books_with_genre_by_author, get_book, get_book_plus, edit_book_with_genres, add_chapter, get_chapters_by_book, get_chapter, edit_book_chapter, remove_book, remove_book_chapter, get_browse_data, add_book_comment, get_comments_by_book, add_chapter_comment, get_comments_by_chapter, get_comments_plus_table, report_new_users, report_new_books, report_most_followers, report_most_popular_books, report_most_commented_chapters, update_chapter_views, add_rating, get_rating



####################################
# General Routes
####################################

@app.route('/', methods=['GET', 'POST'])
def index():
    # get top 3 books
    top_books = get_browse_data('book', 'popular', 'decreasing')
    top_books["rows"] = top_books["rows"][0:3]
    print(top_books["rows"][0])
    # get recent 3 chapters
    latest_chapters = get_browse_data('chapter', 'new', 'increasing')
    latest_chapters["rows"] = latest_chapters["rows"][0:3]
    # latest 3 comments
    comments = get_comments_plus_table()
    comments["rows"] = comments["rows"][0:3]
    #
    return render_template('index.html', books=top_books["rows"], chapters=latest_chapters["rows"], comments=comments["rows"])

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    account = get_account(username=current_user.username)
    return render_template('profile.html', account=account)

@app.route('/user/<username>', methods=['GET', 'POST'])
def view_user(username):
    account = get_account(username=username)
    if account == None:
        abort(404)
    return render_template('profile.html', account=account)

def valid_browse_params(entity, sort, order):
    return (
        entity in ['book', 'chapter', 'author'] and
        sort in ['popular', 'new'] and
        order in ['increasing', 'decreasing'])

@app.route('/browse', methods=['GET'])
@app.route('/browse/<entity>', methods=['GET'])
@app.route('/browse/<entity>/<sort>/<order>', methods=['GET'])
def browse(entity='book', sort='popular', order='decreasing'):
    if valid_browse_params(entity, sort, order):
        return render_template('browse.html', entity=entity, sort=sort, order=order, **get_browse_data(entity, sort, order))
    return redirect(url_for('browse'))



####################################
# Book Routes
####################################

@app.route('/book/<int:book_id>/rate', methods=['GET', 'POST'])
def rate_book(book_id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    print(request.form['rating'])
    add_rating(book_id, current_user.user_id, int(request.form['rating']))
    return redirect(url_for('view_book', book_id=book_id))

@app.route('/book/<int:book_id>', methods=['GET'])
def view_book(book_id):
    book = get_book_plus(book_id)
    chapters = get_chapters_by_book(book_id)
    comments = get_comments_by_book(book_id)
    rating = 0
    if current_user.is_authenticated:
        rating = int(get_rating(book_id, current_user.user_id) or 0)
    print(rating)
    return render_template('book/index.html', book=book, chapters=chapters, comments=comments, rating=rating)

def init_edit_book_form(form, book):
    form = EditBookForm(form)
    form.genres.choices = [(genre, genre) for genre in get_genres()]
    if form.title.data == None:
        form.title.data = book['title']
    if form.summary.data == None:
        form.summary.data = book['summary']
    if form.genres.data == None:
        form.genres.data = [genre for genre in book['genres'] if genre != None]
    return form

@app.route('/book/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    old_book = get_book_plus(book_id)
    form = init_edit_book_form(request.form, old_book)
    # form = EditBookForm(request.form)
    # form.genres.choices = [(genre, genre) for genre in get_genres()]
    # form.title.default = old_book['title']
    print(form)
    if request.method == 'POST' and form.validate():
        summary = form.summary.data if form.summary.data else None
        edit_book_with_genres(book_id, form.title.data, form.genres.data, summary, old_book['genres'])
        flash('Book Created')
        return redirect(url_for('view_book', book_id=book_id))
    return render_template('book/edit.html', form=form, book_id=book_id)

@app.route('/book/create', methods=['GET', 'POST'])
@login_required
def create_book():
    form = CreateBookForm(request.form)
    form.genres.choices = [(genre, genre) for genre in get_genres()]
    if request.method == 'POST' and form.validate():
        summary = form.summary.data if form.summary.data else None
        book_id = add_book_with_genres(current_user.user_id, form.title.data, form.genres.data, summary)
        flash('Book Created')
        return redirect(url_for('view_book', book_id=book_id))
    return render_template('book/create.html', form=form)

@app.route('/book/<int:book_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_book(book_id):
    remove_book(book_id)
    return redirect(url_for('publish_index'))



####################################
# Chapter Routes
####################################

@app.route('/book/<int:book_id>/chapter/create', methods=['GET', 'POST'])
@login_required
def create_chapter(book_id):
    book = get_book_plus(book_id)
    form = CreateChapterForm(request.form)
    if request.method == 'POST' and form.validate():
        content = form.content.data if form.content.data else None
        status = 'published' if form.status.data else 'draft'
        chapter_id = add_chapter(book_id, form.title.data, content, status)
        # flash('Chapter Created')
        return redirect(url_for('view_chapter', book_id=book_id, chapter_id=chapter_id))
    return render_template('chapter/create.html', form=form, book=book)

def init_edit_chapter_form(form, chapter):
    form = EditChapterForm(form)
    if form.title.data == None:
        form.title.data = chapter['title']
    if form.content.data == None:
        form.content.data = chapter['content']
    if form.status.data == None:
        form.genres.data = chapter['status'] == 'published'
    return form

@app.route('/book/<int:book_id>/chapter/<int:chapter_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_chapter(book_id, chapter_id):
    book = get_book_plus(book_id)
    chapter = get_chapter(book_id, chapter_id)
    form = init_edit_chapter_form(request.form, chapter)
    if request.method == 'POST' and form.validate():
        content = form.content.data if form.content.data else None
        status = 'published' if form.status.data else 'draft'
        edit_book_chapter(book_id, chapter_id, form.title.data, content, status)
        # flash('Chapter Created')
        return redirect(url_for('view_chapter', book_id=book_id, chapter_id=chapter_id))
    return render_template('chapter/edit.html', form=form, book=book, chapter=chapter)

@app.route('/book/<int:book_id>/chapter/<int:chapter_id>', methods=['GET'])
def view_chapter(book_id, chapter_id):
    book = get_book_plus(book_id)
    chapter = get_chapter(book_id, chapter_id)
    comments = get_comments_by_chapter(chapter_id)
    update_chapter_views(chapter_id, current_user.user_id)
    return render_template('chapter/index.html', book=book, chapter=chapter, comments=comments)


@app.route('/book/<int:book_id>/chapter/<int:chapter_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_chapter(book_id, chapter_id):
    remove_book_chapter(book_id, chapter_id)
    return redirect(url_for('view_book', book_id=book_id, chapter_id=chapter_id))



####################################
# Comment Routes
####################################

@app.route('/book/<int:book_id>/comment/create', methods=['GET', 'POST'])
@login_required
def create_book_comment(book_id):
    book = get_book_plus(book_id)
    form = CommentForm(request.form)
    if request.method == 'POST' and form.validate():
        comment_id = add_book_comment(book_id, form.comment.data, current_user.user_id)
        # flash('Chapter Created')
        return redirect(url_for('view_book', book_id=book_id))
    return render_template('comment/create.html', form=form, book=book)

@app.route('/book/<int:book_id>/comment/create', methods=['GET', 'POST'])
@login_required
def edit_book_comment(book_id):
    book = get_book_plus(book_id)
    form = CommentForm(request.form)
    if request.method == 'POST' and form.validate():
        comment_id = add_book_comment(book_id, form.comment.data, current_user.user_id)
        # flash('Chapter Created')
        return redirect(url_for('view_book', book_id=book_id))
    return render_template('comment/create.html', form=form, book=book)

def init_edit_comment_form(form, comment):
    form = CommentForm(form)
    if form.content.data == None:
        form.content.data = comment['content']
    return form

@app.route('/book/<int:book_id>/chapter/<int:chapter_id>/comment/create', methods=['GET', 'POST'])
@login_required
def create_chapter_comment(book_id, chapter_id):
    book = get_book_plus(book_id)
    chapter = get_chapter(book_id, chapter_id)
    # comment = #########HERHEHREHRHEHRH
    form = init_edit_comment_form(request.form, comment)
    if request.method == 'POST' and form.validate():
        comment_id = add_chapter_comment(chapter_id, form.comment.data, current_user.user_id)
        # flash('Chapter Created')
        return redirect(url_for('view_chapter', book_id=book_id, chapter_id=chapter_id))
    return render_template('comment/create_chapter_comment.html', form=form, book=book, chapter=chapter)


####################################
# Admin Routes
####################################

# @app.context_processor
# def inject_user():
#     return dict(user=g.user)

@app.route('/admin', methods=['GET'])
def admin():
    tables = get_tables()
    return render_template('admin/index.html', tables=tables)

@app.route('/admin/table', methods=['GET'])
def table_index():
    tables = get_tables()
    return render_template('admin/table/index.html', tables=tables)

@app.route('/admin/table/<table>', methods=['GET'])
def table_page(table):
    if table not in get_tables():
        abort(404)

    return render_template('admin/table/table.html', tables=get_tables(), **get_table_data(table))

@app.route('/admin/report', methods=['GET'])
@app.route('/admin/report/<when>', methods=['GET'])
def admin_report(when='day'):
    new_users = report_new_users(when)
    new_books = report_new_books(when)
    most_followers = report_most_followers(when)
    popular_books = report_most_popular_books(when)
    most_commented_chapters = report_most_commented_chapters(when)
    return render_template('admin/report.html', when=when, new_users=new_users, new_books=new_books, most_followers=most_followers, popular_books=popular_books, most_commented_chapters=most_commented_chapters)


####################################
# Publish Routes
####################################

@app.route('/publish', methods=['GET'])
@login_required
def publish_index():
    books = get_books_with_genre_by_author(current_user.user_id)
    return render_template('publish/index.html', books=books)



####################################
# Authentication Routes
####################################

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(get_account(username=form.username.data))
        login_user(user)
        flash('Logged in successfully.')
        next = request.args.get('next')
        print(next)
        return redirect(next or url_for('index'))

    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        register_user(form)
        flash('Thanks for registering')
        return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')



####################################
# 404 Route
####################################

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
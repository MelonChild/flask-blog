# _*_ coding: utf-8 _*_
__author__ = 'Melon'
__date__ = "18/07/16"

import os
import uuid
import random
from . import admin
from flask import render_template,current_app,json,jsonify,url_for,request,session,redirect,flash
from app.models import Nav,Article,Banner,Friendlylink,Tag,Recommend,Webconfig,Page,Album,User,Webconfig,Picture
from functools import wraps
from .forms import LoginForm,ArticleForm,UserForm,PwdForm,WebForm,BannerrForm,AlbumForm
from app import csrf,db,photos
from datetime import datetime
import time
import base64
from os.path import exists
import re

# 修改文件名
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename

# 随机文件名
def gen_rnd_filename():
    filename_prefix = datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))

# 文件重命名，相当于文件移动
def move_file(filename,dir="images",static=""):
    newname = filename.replace('temp',dir)
    if filename and filename.find('temp')> -1 and exists('app'+ static + filename):
        os.rename("app" + static + filename, "app" + static + newname)
        filename = newname

    return filename

# 文件上传
@csrf.exempt
@admin.route('/ckupload', methods=['POST'])
def ckupload():
    t={}
    uploaded = False

    if request.method == 'POST' and 'upload'in request.files:
        fileobj = request.files['upload']
        # 生成随机的文件名
        suffix = os.path.splitext(fileobj.filename)[1]
        filename = 'static/uploads/temp/'+gen_rnd_filename() + suffix
        photos.save(fileobj,name=filename)
        url = photos.url(filename)
        uploaded = True
        t['url'] = '/' + filename
    else:
        t['error']['message'] = 'could not upload this image'
    t['uploaded'] = uploaded

    return json.dumps(t)

# base64存储文件
@admin.route('/upload', methods=['POST'])
def upload():
    t = {}
    uploaded = False
    t['uploaded'] = uploaded

    if request.method == 'POST':
        filename = gen_rnd_filename()
        filedata = request.values.get('datas','').replace('data:image/jpeg;base64,','');
        if filedata:
            imgdata = base64.b64decode(filedata)
            filename = '/static/uploads/temp/' + filename + '.jpeg'
            file = open('app' + filename,'wb')
            file.write(imgdata)
            file.close()
            t['url'] = filename
            t['uploaded'] = True
        else:
            t['error']['message'] = 'could not write this image'
    else:
        t['error']['message'] = 'could not upload this image'


    return json.dumps(t)

# 删除图片
@admin.route('/deleteImg', methods=['POST'])
def deleteImg():
    t = {}
    status = False
    t['status'] = status

    if request.method == 'POST':
        filedata = request.values.get('img','');
        if filedata and exists('app'+filedata):
            os.unlink('app'+filedata)
            t['status'] = True
        else:
            t['error'] = 'image is not exist'
    else:
        t['error'] = 'method is wrong'


    return json.dumps(t)

# 登录修饰器
def admin_login_req(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function

# 权限修饰器
def admin_auth(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_id" not in session or session.get('admin_id') > 1:
            return redirect(url_for("admin.main"))
        return f(*args, **kwargs)

    return decorated_function

# 登录页面
@admin.route('/login',methods=["GET","POST"])
def login():
    form = LoginForm()

    # 登录判断
    print(form.validate_on_submit())
    print(form.errors)
    if form.validate_on_submit():
        data = form.data
        print(data)
        user = User.query.filter_by(active=1).filter_by( username = data['username']).first()
        print(user)
        if not user:
            flash('Username is wrong!', "err")
            return redirect(url_for("admin.login"))

        if not user.check_pwd(data['password']):
            flash('Password is wrong!',"err")
            return redirect(url_for("admin.login"))

        session['admin'] = data["username"]
        session["admin_id"] = user.id
        session['nickname'] = user.nickname

        return redirect(request.args.get("next") or url_for("admin.index"))

    return render_template('admin/login/index.html',form = form)

# 后台首页
@admin.route('/')
@admin_login_req
def index():
    return redirect(url_for("admin.main"))
    return render_template('admin/index/index.html')

# 注销
@admin.route("/logout")
@admin_login_req
def logout():
    session.pop("admin", None)
    session.pop("admin_id", None)

    return redirect(url_for("admin.login"))

# 后台文章列表
@admin.route('/main')
@admin_login_req
def main():
    per_page = 18
    page = request.values.get('page', 1,int)
    # 获取文章
    user = request.values.get('user', 0,int)
    admin_id = session.get('admin_id',0)

    if admin_id==1 and user >0:
        admin_id = user

    if admin_id==1 :
        articles = Article.query.order_by(Article.created_at.desc()).order_by(Article.sort.desc()).paginate(page=page, per_page=per_page)
    else:
        articles = Article.query.filter(Article.user_id == admin_id).order_by(Article.created_at.desc()).order_by(Article.sort.desc()).paginate(page=page, per_page=per_page)

    return render_template('admin/index/main.html',
                           articles = articles)

# 创建文章
@admin.route('/write',methods=["GET","POST"])
@admin_login_req
def write():
    form = ArticleForm()
    if request.method == "GET":
        form.active.data = 0

    # 提交文章
    print(form.validate_on_submit())
    print(form.errors)
    if form.validate_on_submit():
        data = form.data
        tagids = request.values.getlist('tags', int)
        tags = Tag.query.filter(Tag.id.in_(tagids)).all()
        print(data)

        # 图片处理
        content = data["content"]
        demo = re.compile('<img src="(.*?)"', re.S)  # 找到图片正则
        list1 = demo.findall(content)  # 去源码中找匹配到的这个链接
        print(list1)
        for j in list1:
            print(j)
            move_file(j,'ck','')
        data["content"] = content.replace('/temp/','/ck/')

        images = request.values.get('images','')
        imagesdata = images.split(';')
        imagesnew = ''

        for i in imagesdata:
            if i:
                move_file(i)
                imagesnew = i.replace('/temp/','/images/')+ ';'

        article = Article(
            title=data["title"],
            description=data["description"],
            content=data["content"],
            author=data["author"],
            views_num=int(data["views_num"]),
            sort=int(data["sort"]),
            user_id=session.get('admin_id'),
            created_at=int(time.time()),
            images = imagesnew,
            nav_id = request.values.get('nav_id',3,int),
            active = int(data["active"]),
            tags = tags
        )
        db.session.add(article)
        db.session.commit()
        flash("success！", "ok")
        return redirect(url_for('admin.main'))


    navs = Nav.query.filter(Nav.pid > 0).order_by(Nav.sort.asc()).all()
    tags = Tag.query.all()
    return render_template('admin/article/create.html',navs = navs,form = form,tags = tags)

# 删除文章
@admin.route('/deleteArticle',methods=["POST"])
@admin_login_req
def deleteArticle():
    t = {}
    status = False
    t['status'] = status

    if request.method == 'POST':
        id = request.values.get('id', '')
        if id:
            article = Article.query.get(id)
            if article:
                images = article.images.split(';')
                print(images)
                for i in images:
                    if i and exists('app'+i):
                        os.unlink('app' + i)

                if article.content:
                    demo = re.compile('<img src="(.*?)"', re.S)  # 找到图片正则
                    list1 = demo.findall(article.content)  # 去源码中找匹配到的这个链接
                    print(list1)
                    for i in list1:
                        if i and exists('app'+i):
                            os.unlink('app' + i)

                db.session.delete(article)
                db.session.commit()
                t['status'] = True
        else:
            t['error'] = 'blog is not exist'
    else:
        t['error'] = 'method is wrong'

    return json.dumps(t)

# 编辑文章
@admin.route('/edit/<int:id>',methods=["GET","POST"])
@admin_login_req
def edit(id):
    article = Article.query.get_or_404(id)
    form = ArticleForm()

    if request.method == "GET":
        form.active.data = article.active
        form.content.data = article.content
        form.description.data = article.description

    # 提交文章
    print(form.validate_on_submit())
    print(form.errors)
    if form.validate_on_submit():
        data = form.data
        tagids = request.values.getlist('tags',int)
        print(data)
        print(request.values.getlist('tags',int))
        # 图片处理
        content = data["content"]
        demo = re.compile('<img src="(.*?)"', re.S)  # 找到图片正则
        list1 = demo.findall(content)  # 去源码中找匹配到的这个链接
        print(list1)
        for j in list1:
            print(j)
            move_file(j,'ck','')
        data["content"] = content.replace('/temp/','/ck/')

        images = request.values.get('images','')
        imagesdata = images.split(';')
        imagesnew = ''

        for i in imagesdata:
            if i:
                move_file(i)
                imagesnew = i.replace('/temp/','/images/')+ ';'


        article.title=data["title"],
        article.description=data["description"],
        article.content=data["content"],
        article.author=data["author"],
        article.views_num=int(data["views_num"]),
        article.sort=int(data["sort"]),
        article.user_id=session.get('admin_id'),
        article.images = imagesnew,
        article.nav_id = request.values.get('nav_id',3,int),
        article.active = int(data["active"])
        tags = Tag.query.filter(Tag.id.in_(tagids)).all()
        article.tags = tags
        db.session.add(article)
        db.session.commit()
        flash("success！", "ok")
        return redirect(url_for('admin.main'))

    navs = Nav.query.filter(Nav.pid > 0).order_by(Nav.sort.asc()).all()
    tags = Tag.query.all()
    return render_template('admin/article/edit.html',navs = navs,form = form,article = article,tags = tags)

# 用户列表
@admin.route('/users')
@admin_login_req
@admin_auth
def users():
    per_page = 18
    page = request.values.get('page', 1,int)

    users = User.query.paginate(page=page,per_page=per_page)

    return render_template('admin/user/index.html',
                           users = users)

# 用户列表
@admin.route('/users/create',methods=["GET","POST"])
@admin_login_req
@admin_auth
def userCreate():
    form = UserForm()
    if request.method == "GET":
        form.role_id.data = 2;
        form.active.data = 1;

    from werkzeug.security import generate_password_hash
    if form.validate_on_submit():
        data = form.data

        name_count = User.query.filter_by(username=data["username"]).count()
        if name_count > 0:
            flash("用户名已经存在!", "err")
            return redirect(url_for("admin.userCreate"))

        user = User(
            username=data["username"],
            password=generate_password_hash(data["password"]),
            role_id=data["role_id"],
            active=data["active"],
            nickname = data['nickname']
        )
        db.session.add(user)
        db.session.commit()
        flash("添加管理员成功！", "ok")
        return redirect(url_for("admin.users"))

    return render_template('admin/user/create.html',form = form)

# 用户列表
@admin.route('/users/edit/<int:id>',methods=["GET","POST"])
@admin_login_req
@admin_auth
def userEdit(id):
    form = UserForm()
    userdata = User.query.get_or_404(id)

    if request.method == "GET":
        form.username.data = userdata.username;
        form.role_id.data = userdata.role_id;
        form.active.data =  userdata.active;
        form.nickname.data = userdata.nickname;

    from werkzeug.security import generate_password_hash
    if form.validate_on_submit():
        data = form.data

        name_count = User.query.filter_by(username=data["username"]).count()
        if data["username"] != userdata.username and name_count > 0:
            flash("用户名已经存在!", "err")
            return redirect(url_for("admin.userCreate"))

        userdata.username = data["username"],
        userdata.nickname = data['nickname'],
        userdata.password=generate_password_hash(data["password"]),
        userdata.role_id=data["role_id"],
        userdata.active=data["active"]

        db.session.add(userdata)
        db.session.commit()
        flash("修改成功！", "ok")
        return redirect(url_for("admin.users"))

    return render_template('admin/user/create.html',form = form)

# 修改密码
@admin.route('/users/changepwd',methods=["GET","POST"])
@admin_login_req
def cgPwd():
    form = PwdForm()

    id = session["admin_id"]
    user = User.query.get_or_404(id)
    if request.method == 'GET':
        form.nickname.data = user.nickname

    from werkzeug.security import generate_password_hash
    if form.validate_on_submit():
        data = form.data

        if data["old_pwd"] or data["password"]:
            if not user.check_pwd(data["old_pwd"]):
                flash("旧密码错误！", "err")
                return redirect(url_for('admin.cgPwd'))
            user.password=generate_password_hash(data["password"])
        user.nickname = data['nickname']
        session['nickname'] = user.nickname
        db.session.add(user)
        db.session.commit()
        flash("修改成功！", "ok")
        return redirect(url_for("admin.cgPwd"))

    return render_template('admin/user/cgPwd.html',form = form)

# 删除用户
@admin.route('/deleteUser',methods=["POST"])
@admin_login_req
@admin_auth
def deleteUser():
    t = {}
    status = False
    t['status'] = status

    if request.method == 'POST':
        id = request.values.get('id', '')
        if id:
            user = User.query.get(id)
            if user:

                # 更改文章用户
                Article.query.filter_by(user_id=id).update({'user_id':1})

                db.session.delete(user)
                db.session.commit()
                t['status'] = True
        else:
            t['error'] = 'user is not exist'
    else:
        t['error'] = 'method is wrong'

    return json.dumps(t)

# 网站配置
@admin.route('/webconfig',methods=["GET","POST"])
@admin_login_req
@admin_auth
def webconfig():
    form = WebForm()
    web = Webconfig.query.get_or_404(1)
    page = Page.query.get_or_404(1)

    if request.method == "GET":
        form.webname.data = web.webname;
        form.description.data = web.description;
        form.keywords.data = web.keywords;
        form.inscription.data = web.inscription;
        form.inscription_2.data = web.inscription_2;
        form.inscription_3.data = web.inscription_3;
        form.inscription_4.data = web.inscription_4;
        form.author.data = web.author;
        form.position.data = web.position;
        form.summary.data = web.summary;
        form.avatar.data = web.avatar;
        form.wechat.data = web.wechat;

    if form.validate_on_submit():
        data = form.data

        move_file(data["avatar"])
        move_file(data["wechat"])

        web.webname = data["webname"],
        web.description = data["description"],
        web.keywords = data["keywords"],
        web.inscription = data["inscription"],
        web.inscription_2 = data["inscription_2"],
        web.inscription_3 = data["inscription_3"],
        web.inscription_4 = data["inscription_4"],
        web.author = data["author"],
        web.position = data["position"],
        web.summary = data["summary"],
        web.avatar =  data["avatar"].replace('/temp/', '/images/')
        web.wechat =  data["wechat"].replace('/temp/', '/images/')

        db.session.add(web)
        db.session.commit()
        flash("修改成功！", "ok")
        return redirect(url_for("admin.webconfig"))

    return render_template('admin/webconfig/index.html',form = form,web = web,page=page)

# 关于我
@admin.route('/savePage',methods=["GET","POST"])
@admin_login_req
@admin_auth
def savePage():
    t = {}
    status = False
    t['status'] = status

    if request.method == 'POST':
        content = request.values.get('content', '')
        if content:
            page = Page.query.get(1)
            if page:

                demo = re.compile('<img src="(.*?)"', re.S)  # 找到图片正则
                list1 = demo.findall(content)  # 去源码中找匹配到的这个链接
                print(list1)
                for j in list1:
                    print(j)
                    move_file(j, 'ck', '')

                page.content = content.replace('/temp/', '/ck/')
                db.session.add(page)
                db.session.commit()
                t['status'] = True
        else:
            t['error'] = 'page is not exist'
    else:
        t['error'] = 'method is wrong'

    return json.dumps(t)

# bammer
@admin.route('/banners')
@admin_login_req
@admin_auth
def banners():
    per_page = 18
    page = request.values.get('page', 1,int)

    banners = Banner.query.order_by(Banner.active.desc()).order_by(Banner.sort.desc()).paginate(page=page, per_page=per_page)

    return render_template('admin/banner/index.html',
                           banners = banners)

# 提交banner
@admin.route('/banners/add',methods=["GET","POST"])
@admin_login_req
@admin_auth
def bannerAdd():
    form = BannerrForm()
    if request.method == "GET":
        form.active.data = 1
        form.type.data = 1

    # 提交
    print(form.validate_on_submit())
    print(form.errors)
    if form.validate_on_submit():
        data = form.data
        print(data)

        # 图片处理
        move_file(data["picurl"])

        banner = Banner(
            path=data["path"],
            picurl=data["picurl"].replace('/temp/', '/images/'),
            title=data["title"],
            tag=data["tag"],
            type=int(data["type"]),
            sort=int(data["sort"]),
            active = int(data["active"])
        )
        db.session.add(banner)
        db.session.commit()
        flash("success！", "ok")
        return redirect(url_for('admin.banners'))

    return render_template('admin/banner/create.html',form = form)

# 删除banner
@admin.route('/banners/delete',methods=["POST"])
@admin_login_req
@admin_auth
def bannerDel():
    t = {}
    status = False
    t['status'] = status

    if request.method == 'POST':
        id = request.values.get('id', '')
        if id:
            banner = Banner.query.get(id)
            if banner:
                image = banner.picurl
                print(image)
                if image and exists('app' + image):
                    os.unlink('app' + image)

                db.session.delete(banner)
                db.session.commit()
                t['status'] = True
        else:
            t['error'] = 'banner is not exist'
    else:
        t['error'] = 'method is wrong'

    return json.dumps(t)

# 编辑banner
@admin.route('/banners/edit/<int:id>',methods=["GET","POST"])
@admin_login_req
@admin_auth
def bannerEdit(id):
    banner = Banner.query.get_or_404(id)
    form = BannerrForm()

    if request.method == "GET":
        form.active.data = banner.active
        form.type.data = banner.type
        form.path.data = banner.path
        form.picurl.data = banner.picurl
        form.title.data = banner.title
        form.tag.data = banner.tag
        form.sort.data = banner.sort

    # 提交文章
    print(form.validate_on_submit())
    print(form.errors)
    if form.validate_on_submit():
        data = form.data
        print(data)

        # 图片处理
        move_file(data["picurl"])

        banner.path=data["path"],
        banner.picurl=data["picurl"].replace('/temp/', '/images/'),
        banner.title=data["title"],
        banner.tag=data["tag"],
        banner.type=int(data["type"]),
        banner.sort=int(data["sort"]),
        banner.active = int(data["active"])

        db.session.add(banner)
        db.session.commit()
        flash("success！", "ok")
        return redirect(url_for('admin.banners'))

    return render_template('admin/banner/edit.html',form = form,banner = banner)

# 相册列表
@admin.route('/albums')
@admin_login_req
def albums():
    per_page = 18
    page = request.values.get('page', 1,int)
    # 获取相册
    albums = Album.query.order_by(Album.sort.desc()).paginate(page=page,per_page=per_page)

    return render_template('admin/album/index.html',
                           albums = albums)

# 创建图集
@admin.route('/albums/add',methods=["GET","POST"])
@admin_login_req
def albumsAdd():
    form = AlbumForm()

    # 提交
    print(form.validate_on_submit())
    print(form.errors)
    if form.validate_on_submit():
        data = form.data
        print(data)

        # 图片处理
        images = request.values.get('images','')
        imagesdata = images.split(';')
        imagesnew = ''
        print(images)
        print(imagesdata)
        album = Album(
            title=data["title"],
            picture = data["picture"].replace('/temp/', '/images/'),
            like_num=int(data["like_num"]),
            sort=int(data["sort"]),
            pictures = []
        )

        # if images:
        for index in range(len(imagesdata)):
            print(index)
            print(imagesdata[index])
            if imagesdata[index]:
                move_file(imagesdata[index])
                imagesnew = imagesdata[index].replace('/temp/','/images/')
                album.pictures.append(Picture(
                    path = imagesnew,
                    sort=int(index)
                ))

        db.session.add(album)
        db.session.commit()
        flash("success！", "ok")
        return redirect(url_for('admin.albums'))

    return render_template('admin/album/create.html',form = form)

# 删除
@admin.route('/albums/delete',methods=["POST"])
@admin_login_req
def albumsDel():
    t = {}
    status = False
    t['status'] = status

    if request.method == 'POST':
        id = request.values.get('id', '')
        if id:
            album = Album.query.get(id)
            if album:
                images = album.pictures
                print(images)
                for i in images:
                    if i.path and exists('app'+i.path):
                        os.unlink('app' + i.path)

                db.session.delete(album)
                db.session.commit()
                t['status'] = True
        else:
            t['error'] = 'album is not exist'
    else:
        t['error'] = 'method is wrong'

    return json.dumps(t)

# 编辑
@admin.route('/albums/edit/<int:id>',methods=["GET","POST"])
@admin_login_req
def albumsEdit(id):
    album = Album.query.get_or_404(id)
    form = AlbumForm()

    if request.method == "GET":
        form.sort.data = album.sort
        form.title.data = album.title
        form.picture.data = album.picture
        form.like_num.data = album.like_num

    images = ''
    imagesarray = []
    for pictureitem in album.pictures:
        images = images + pictureitem.path + ';'
        imagesarray.append(pictureitem.path)

    print(imagesarray)
    # 提交
    print(form.validate_on_submit())
    print(form.errors)
    if form.validate_on_submit():
        data = form.data
        print(data)

        # 图片处理
        images = request.values.get('images', '')
        imagesdata = images.split(';')
        imagesnew = ''
        print(images)
        print(imagesdata)
        album.title = data["title"]
        album.picture = data["picture"].replace('/temp/', '/images/')
        album.like_num = data["like_num"]
        album.sort = data["sort"]
        album.pictures =[]

        # 删除图片
        for oldimage in imagesarray:
            if oldimage not in imagesdata:
                print(oldimage)
                if oldimage and exists('app' + oldimage):
                    os.unlink('app' + oldimage)

        # if images:
        for index in range(len(imagesdata)):
            print(index)
            print(imagesdata[index])
            if imagesdata[index]:
                move_file(imagesdata[index])
                imagesnew = imagesdata[index].replace('/temp/', '/images/')
                album.pictures.append(Picture(
                    path=imagesnew,
                    sort=int(index)
                ))

        db.session.add(album)
        db.session.commit()
        flash("success！", "ok")
        return redirect(url_for('admin.albums'))

    return render_template('admin/album/edit.html',images = images,form = form,album = album)

# 标签
@admin.route('/tags',methods=["GET","POST"])
@admin_login_req
@admin_auth
def tags():
    if request.method == "POST":
        id = request.values.get('id',0,int)
        title = request.values.get('title', '')
        sort = request.values.get('sort',1,int)

        if title:
            if id > 0:
                tag = Tag.query.get(id)
                if tag:
                    tag.title = title
                    tag.sort = sort
            else:
                tag = Tag(
                    title = title,
                    sort = sort
                )

            db.session.add(tag)
            db.session.commit()

    tags = Tag.query.order_by(Tag.sort.desc()).all()

    return render_template('admin/tag/index.html',
                           tags = tags)

# 删除
@admin.route('/tags/delete',methods=["POST"])
@admin_login_req
@admin_auth
def tagsDel():
    t = {}
    status = False
    t['status'] = status

    if request.method == 'POST':
        id = request.values.get('id', '')
        if id:
            tag = Tag.query.get(id)
            if tag:
                db.session.delete(tag)
                db.session.commit()
                t['status'] = True
        else:
            t['error'] = 'tag is not exist'
    else:
        t['error'] = 'method is wrong'

    return json.dumps(t)

# 推荐
@admin.route('/recommend',methods=["GET","POST"])
@admin_login_req
@admin_auth
def recommend():
    if request.method == "POST":
        title = request.values.get('title', '')
        sort = request.values.get('sort', 1, int)
        article = Article.query.filter_by(active=1).filter(Article.title.like('%' + title + '%')).first()
        if article:
            hasrecommend = Recommend.query.filter_by(article_id=article.id).count()
            print(hasrecommend)
            if hasrecommend==0:
                recommend = Recommend(
                    article_id=article.id,
                    sort=sort
                )

                db.session.add(recommend)
                db.session.commit()

    articles = Recommend.query.order_by(Recommend.sort.desc()).all()

    return render_template('admin/recommend/index.html',
                           articles = articles)

# 删除
@admin.route('/recommend/delete',methods=["POST"])
@admin_login_req
@admin_auth
def recommendDel():
    t = {}
    status = False
    t['status'] = status

    if request.method == 'POST':
        id = request.values.get('id', '',int)

        Recommend.query.filter_by(id=id).delete()
        t['status'] = True
    else:
        t['error'] = 'method is wrong'

    return json.dumps(t)

# 搜索文章标题
@admin.route('/searchArticle',methods=["GET"])
@admin_login_req
@admin_auth
def searchArticle():
    temp={}
    articlesdata = []
    keyword = request.values.get('query', '')
    articles = Article.query.filter_by(active=1).filter(Article.title.like('%' + keyword + '%')).order_by(
        Article.created_at.desc()).order_by(Article.sort.desc()).limit(5).all()
    print(articles)
    for item in articles:
        temp = {}
        if item:
            temp['label'] = item.title
            temp['hex'] = item.author
            articlesdata.append(temp)

    return json.dumps(articlesdata)
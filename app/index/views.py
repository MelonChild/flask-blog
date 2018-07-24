# _*_ coding: utf-8 _*_
__author__ = 'Melon'
__date__ = "18/07/09"

from . import home
from flask import render_template,current_app,json,jsonify,url_for,request
from app.models import Nav,Article,Banner,Friendlylink,Tag,Recommend,Webconfig,Page,Album
from sqlalchemy.sql.expression import func

# 网站导航
@home.app_template_global()
def navs():
    navs = Nav.query.filter(Nav.pid == 0).order_by(Nav.sort.asc()).all()
    return navs

# 网站配置
@home.app_template_global()
def webconfig():
    config = Webconfig.query.get(1)
    return config

# 侧边栏
@home.app_template_global()
def rightcontnets():
    # 获取标签
    rightcontnets.tags = Tag.query.order_by(Tag.sort.desc()).all()
    # 获取友链
    rightcontnets.friendlylinks = Friendlylink.query.order_by(Friendlylink.sort.desc()).all()
    # 获取推荐
    rightcontnets.recommends = Recommend.query.order_by(Recommend.sort.desc()).all()
    return rightcontnets

# 首页
@home.route('/')
def index():
    # 获取文章
    articles = Article.query.filter_by(active=1).order_by(Article.created_at.desc()).order_by(Article.sort.desc()).slice(0,2)
    #获取banner
    banners = Banner.query.filter_by(active=1).order_by(Banner.sort.desc()).all()

    return render_template('index/index/index.html',articles=articles,banners=banners)

# 文章列表
@home.route('/blogs/<int:nav>/<int:page>',methods=['GET'])
@home.route('/blogs/<int:nav>',methods=['GET'])
def blogs(nav,page=1):
    per_page = 10
    # 获取栏目
    currentnav = Nav.query.get(nav)
    # 获取文章
    articles = Article.query.filter(Article.nav_id == nav).filter_by(active=1).order_by(Article.created_at.desc()).order_by(Article.sort.desc()).paginate(page=page,per_page=per_page)

    return render_template('index/article/list.html',
                           articles=articles,
                           currentnav=currentnav)

# 文章列表
@home.route('/timeline/<int:page>',methods=['GET'])
@home.route('/timeline',methods=['GET'])
def timeline(page=1):
    per_page =20
    # 获取文章
    articles = Article.query.filter_by(active=1).order_by(Article.created_at.desc()).order_by(Article.sort.desc()).paginate(page=page,per_page=per_page)

    return render_template('index/article/timeline.html',
                           articles=articles)

# 文章列表
@home.route('/search/<int:page>',methods=['GET'])
@home.route('/search',methods=['GET'])
def search(page=1):
    per_page =20
    # 获取文章
    tag = request.values.get('tag','')
    keyword = request.values.get('keywords','')

    if(tag):
        searchdata = 'tag=' + tag
        tag = Tag.query.get_or_404(tag)
        articles = tag.articles.filter_by(active=1).paginate(page=page,per_page=per_page)
        total = articles.total
        keyword = tag.title


    else:
        articles = Article.query.filter_by(active=1).filter(Article.title.like('%' + keyword + '%')).order_by(
            Article.created_at.desc()).order_by(Article.sort.desc()).paginate(page=page,per_page=per_page)
        searchdata = 'keywords=' + keyword
        total = articles.total

    return render_template('index/article/search.html',
                           articles=articles,
                           searchdata=searchdata,
                           total = total,
                           keyword = keyword)

# 文章详情
@home.route('/blog/<int:id>',methods=['GET'])
def blog(id):
    # 获取文章
    article = Article.query.get_or_404(id)
    Article.query.filter_by(id=id).update({'views_num':Article.views_num + 1})
    # 获取栏目
    currentnav = Nav.query.get(article.nav_id)
    #上一篇
    prev = Article.query.order_by(Article.id.desc()).filter(Article.id < id).first()
    #下一篇
    next = Article.query.order_by(Article.id.asc()).filter(Article.id > id).first()

    # 相关文章
    relations = Article.query.filter(Article.nav_id == article.nav_id).filter(Article.id != id).order_by(func.rand()).limit(6)
    return render_template('index/article/detail.html',
                            article=article,
                            currentnav=currentnav,
                            prev=prev,
                            next=next,
                            relations=relations)

# 关于我
@home.route('/about',methods=['GET'])
def about():
    # 获取文章
    article = Page.query.get_or_404(1)
    return render_template('index/page/about.html',
                            article=article)

# 留言
@home.route('/contact',methods=['GET'])
def contact():
    # 获取文章
    article = Page.query.get_or_404(1)
    return render_template('index/page/contact.html',
                            article=article)

# 图集
@home.route('/albums/<int:page>',methods=['GET'])
@home.route('/albums',methods=['GET'])
def albums(page=1):
    per_page =1
    # 获取文章
    albums = Album.query.order_by(Album.sort.desc()).order_by(Album.id.desc()).paginate(page=page,per_page=per_page)
    return render_template('index/album/index.html',
                           albums=albums)


# 图集
@home.route('/album/<int:id>',methods=['GET'])
@home.route('/album',methods=['GET'])
def album(id=1):
    # 获取图集
    album = Album.query.get_or_404(id)
    returndata = {}
    temp = {}
    returndata['title'] = album.title
    returndata['id'] = album.id
    returndata['start'] = 0
    picturesArr = []
    for picture in album.pictures:
        temp['alt'] = album.title
        temp['src'] = picture.path
        temp['thumb'] = picture.path
        picturesArr.append(temp)

    returndata['data'] = picturesArr
    return jsonify(returndata)

# 图集
@home.route('/likealbum/<int:id>',methods=['GET'])
@home.route('/likealbum',methods=['GET'])
def likealbum(id=1):
    # 获取图集
    result = Album.query.filter_by(id=id).update({'like_num': Album.like_num + 1})
    return jsonify(result)


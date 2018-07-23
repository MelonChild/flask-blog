from . import db
from sqlalchemy import inspect

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)

    def __repr__(self):
        return '<User %r>' % self.username

# 导航表
class Nav(db.Model):
    __tablename__ =  "navs"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer,primary_key=True) #主键
    name = db.Column(db.String(255),unique=True) #导航名
    path = db.Column(db.String(255)) #导航路径
    pid = db.Column(db.Integer,db.ForeignKey('navs.id'),default=0) #父级导航
    sort = db.Column(db.Integer,default=0) # 排序值
    children = db.relationship("Nav")

    def __repr__(self):
        return '<Nav %r>' % self.name

article_tag = db.Table('article_tag',db.metadata,
                       db.Column('article_id',db.Integer,db.ForeignKey('articles.id')),
                       db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')))
# 文章表
class Article(db.Model):
    __tablename__ = "articles"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer,primary_key=True) #主键
    title = db.Column(db.String(255),unique=True) #标题
    description = db.Column(db.Text) #描述
    author = db.Column(db.String(255)) #作者
    images = db.Column(db.String(255))  # 封面图
    content = db.Column(db.Text)  # 内容
    created_at = db.Column(db.Integer) #创建时间
    sort = db.Column(db.Integer,default=0) # 排序值
    views_num = db.Column(db.Integer,default=10) #阅读量
    tags = db.relationship("Tag",secondary=article_tag,backref = db.backref('articles',lazy='dynamic'),lazy='dynamic')
    nav_id = db.Column(db.Integer,db.ForeignKey('navs.id')) #导航
    nav = db.relationship("Nav")
    user_id = db.Column(db.Integer)  # 作者
    active = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<Article %r>' % self.title

# 单页面表
class Page(db.Model):
    __tablename__ = "pages"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(255), unique=True)  # 标题
    content = db.Column(db.Text)  # 内容

    def __repr__(self):
        return '<Page %r>' % self.title

# banner
class Banner(db.Model):
    __tablename__ = "banners"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer,primary_key=True) #主键
    title = db.Column(db.String(255),unique=True) #标题
    path = db.Column(db.String(255)) #路径
    picurl = db.Column(db.String(255))  # 封面图
    tag = db.Column(db.String(255))  # 标签
    sort = db.Column(db.Integer,default=0) # 排序值
    type = db.Column(db.Integer, default=1)  # 类型
    active = db.Column(db.Integer, default=1)  # active

    def __repr__(self):
        return '<Banner %r>' % self.title

# 标签
class Tag(db.Model):
    __tablename__ = "tags"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer,primary_key=True) #主键
    title = db.Column(db.String(255),unique=True) #标题
    sort = db.Column(db.Integer,default=0) # 排序值

    def __repr__(self):
        return '<Tag %r>' % self.title

# 标签
class Friendlylink(db.Model):
    __tablename__ = "friendlylinks"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer,primary_key=True) #主键
    title = db.Column(db.String(255),unique=True) #标题
    path = db.Column(db.String(255), unique=True)  # 路径
    sort = db.Column(db.Integer,default=0) # 排序值

    def __repr__(self):
        return '<link %r>' % self.title

# 推荐文章
class Recommend(db.Model):
    __tablename__ = "recommends"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer,primary_key=True) #主键
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))  # 父级导航
    sort = db.Column(db.Integer,default=0) # 排序值
    article = db.relationship("Article")

    def __repr__(self):
        return '<Recommend %r>' % self.article_id

# 网站配置项
class Webconfig(db.Model):
    __tablename__ = "webconfig"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer,primary_key=True) #主键
    webname = db.Column(db.String(255))  # 网站名称
    description = db.Column(db.String(255))  # 网站描述
    keywords = db.Column(db.String(255))  # 关键词
    inscription = db.Column(db.String(255))  # 铭言
    inscription = db.Column(db.String(255))  # 铭言
    inscription_2 = db.Column(db.String(255))  # 铭言
    inscription_3 = db.Column(db.String(255))  # 铭言
    inscription_4 = db.Column(db.String(255))  # 铭言
    author = db.Column(db.String(255))  # 作者
    position = db.Column(db.String(255))  # 职业
    summary = db.Column(db.String(255))  # 简介
    avatar = db.Column(db.String(255))  #头像
    wechat = db.Column(db.String(255))  # 微信

    def __repr__(self):
        return '<Congig %r>' % self.webname

# 相册
class Album(db.Model):
    __tablename__ = "albums"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer,primary_key=True) #主键
    sort = db.Column(db.Integer,default=0) # 排序值
    like_num = db.Column(db.Integer, default=10)  # 排序值
    title = db.Column(db.String(255))  # 标题
    picture = db.Column(db.String(255))  # 封面
    pictures = db.relationship("Picture",backref="parent",cascade="all, delete-orphan",passive_deletes=True)

    def __repr__(self):
        return '<Album %r>' % self.title

# 相册图集
class Picture(db.Model):
    __tablename__ = "pictures"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer,primary_key=True) #主键
    sort = db.Column(db.Integer,default=0) # 排序值
    album_id = db.Column(db.Integer,db.ForeignKey('albums.id',ondelete='CASCADE'))  # 排序值
    path = db.Column(db.String(255))  # 路径

    def __repr__(self):
        return '<Picture %r>' % self.album_id

    def toDict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

# 后台用户
class User(db.Model):
    __tablename__ = "users"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer,primary_key=True) #主键
    username = db.Column(db.String(255),unique=True)  # 用户名
    password = db.Column(db.Text)  # 密码
    role_id = db.Column(db.Integer)  # 角色
    active = db.Column(db.Integer,default=1) #是否激活
    nickname = db.Column(db.String(255))  # 昵称

    def __repr__(self):
        return '<User %r>' % self.username

    def check_pwd(self,pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password,pwd)

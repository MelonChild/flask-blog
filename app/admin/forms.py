# _*_ coding: utf-8 _*_
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,FileField,TextAreaField,IntegerField,SelectField,RadioField,BooleanField
from wtforms.validators import DataRequired,NumberRange,EqualTo,ValidationError
from app.models import User
from flask_wtf.csrf import CsrfProtect


# 后台登录
class LoginForm(FlaskForm):
    username = StringField(
        "username",
        validators=[
            DataRequired('The username is required!')
        ],
        description="UserName",
        render_kw={
            "class":"form-control",
            "placeholder":'UserName',
            "required": "required"
        }
    )
    password = PasswordField(
        "password",
        validators=[
            DataRequired("The password is required!")
        ],
        description="Password",
        render_kw={
            "class": "form-control",
            "placeholder": "Password ",
            "required": "required"
        }
    )
    submit = SubmitField(
        'LOGIN',
        render_kw={
            "class": "btn btn-primary btn-lg btn-block",
        }
    )

# 文章表单
class ArticleForm(FlaskForm):
    title = StringField(
        "title",
        validators=[
            DataRequired('The title is required!')
        ],
        description="title",
        render_kw={
            "class":"form-control",
            "placeholder": 'title',
            "required": "required"
        }
    )

    author = StringField(
        "author",
        validators=[
            DataRequired('The author is required!')
        ],
        description="author",
        render_kw={
            "class": "form-control",
            "placeholder": 'author',
            "required": "required"
        }
    )

    views_num = IntegerField(
        "views_num",
        validators=[
            NumberRange(message='Type a integer value!')
        ],
        description="views_num",
        render_kw={
            "class": "form-control",
            "placeholder": 'views_num',
            "required": "required"
        }
    )

    sort = IntegerField(
        "sort",
        validators=[
            NumberRange(message='Type a integer value!')
        ],
        description="sort",
        render_kw={
            "class": "form-control",
            "placeholder": 'sort',
            "required": "required"
        }
    )

    description = TextAreaField(
        "description",
        validators=[
            DataRequired("请填写摘要！")
        ],
        description="description",
        render_kw={
            "class": "form-control",
            "placeholder": 'description',
            "required": "required"
        }
    )

    content = TextAreaField(
        "description",
        validators=[
            DataRequired("请填写内容！")
        ],
        description="content",
        render_kw={
            "id" : "editor",
            "class": "form-control",
            "placeholder": 'content',
            "required": "required"
        }
    )
    active = RadioField(
        coerce=int,
        choices=[(v['id'], v['name']) for v in [{'id': 0, 'name': '草稿'}, {'id': 1, 'name': '发布'}]],
        render_kw={
            "class": "form-control active-radio",
        }
    )

# 后台用户表
class UserForm(FlaskForm):
    username = StringField(
        label="管理员名称",
        validators=[
            DataRequired("管理员名称不能为空！")
        ],
        description="管理员名称",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入管理员名称！",
        }
    )
    nickname = StringField(
        label="nickname",
        validators=[
            DataRequired("nickname！")
        ],
        description="nickname",
        render_kw={
            "class": "form-control",
            "placeholder": "nickname！",
        }
    )
    password = PasswordField(
        label="管理员密码",
        validators=[
            DataRequired("管理员密码不能为空！")
        ],
        description="管理员密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入管理员密码！",
        }
    )
    repwd = PasswordField(
        label="管理员重复密码",
        validators=[
            DataRequired("管理员重复密码不能为空！"),
            EqualTo('password', message="两次密码不一致！")
        ],
        description="管理员重复密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入管理员重复密码！",
        }
    )
    role_id = SelectField(
        label="所属角色",
        coerce=int,
        choices=[(v['id'], v['name']) for v in [{'id':2,'name':'编辑'},{'id':1,'name':'超级管理员'}]],
        render_kw={
            "class": "form-control",
        }
    )
    active = RadioField(
        coerce=int,
        choices=[(v['id'], v['name']) for v in [{'id': 1, 'name': '激活'}, {'id': 2, 'name': '禁用'}]],
        render_kw={
            "class": "form-control active-radio",
        }
    )
    submit = SubmitField(
        'Submit',
        render_kw={
            "class": "btn btn-primary",
        }
    )

# 修改密码
class PwdForm(FlaskForm):
    nickname = StringField(
        label="nickname",
        validators=[
            DataRequired("nickname！")
        ],
        description="nickname",
        render_kw={
            "class": "form-control",
            "placeholder": "nickname！",
        }
    )
    old_pwd = PasswordField(
        label="旧密码",
        validators=[
        ],
        description="旧密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入旧密码！",
        }
    )
    password = PasswordField(
        label="新密码",
        validators=[
        ],
        description="新密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入新密码！",
        }
    )
    repwd = PasswordField(
        label="重复密码",
        validators=[
            EqualTo('password', message="两次密码不一致！")
        ],
        description="重复密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入重复密码！",
        }
    )
    submit = SubmitField(
        'Submit',
        render_kw={
            "class": "btn btn-primary",
        }
    )

    def validate_old_pwd(self, field):
        from flask import session
        pwd = field.data
        if pwd:
            name = session["admin"]
            admin = User.query.filter_by(
                username=name
            ).first()
            if not admin.check_pwd(pwd):
                raise ValidationError("旧密码错误！")

# 配置项表单
class WebForm(FlaskForm):
    webname =  StringField(
        label="webname",
        validators=[
            DataRequired("webname！")
        ],
        description="webname",
        render_kw={
            "class": "form-control",
            "placeholder": "webname！",
            "required": "required"
        }
    )
    avatar = StringField(
        label="avatar",
        validators=[
            DataRequired("avatar！")
        ],
        description="avatar",
        render_kw={
            "class": "form-control",
            "placeholder": "avatar！",
            "required": "required"
        }
    )
    wechat = StringField(
        label="wechat",
        validators=[
            DataRequired("wechat！")
        ],
        description="wechat",
        render_kw={
            "class": "form-control",
            "placeholder": "wechat！",
            "required": "required"
        }
    )
    description = TextAreaField(
        "description",
        validators=[
            DataRequired("description！")
        ],
        description="description",
        render_kw={
            "class": "form-control",
            "placeholder": 'description',
            "required": "required"
        }
    )
    keywords = TextAreaField(
        "keywords",
        validators=[
            DataRequired("keywords！")
        ],
        description="keywords",
        render_kw={
            "class": "form-control",
            "placeholder": 'keywords',
            "required": "required"
        }
    )
    inscription = TextAreaField(
        "inscription",
        validators=[
            DataRequired("inscription！")
        ],
        description="inscription",
        render_kw={
            "class": "form-control",
            "placeholder": 'inscription',
            "required": "required"
        }
    )
    inscription_2 = TextAreaField(
        "inscription",
        validators=[
            DataRequired("inscription！")
        ],
        description="inscription",
        render_kw={
            "class": "form-control",
            "placeholder": 'inscription',
            "required": "required"
        }
    )
    inscription_3 = TextAreaField(
        "inscription",
        validators=[
            DataRequired("inscription！")
        ],
        description="inscription",
        render_kw={
            "class": "form-control",
            "placeholder": 'inscription',
            "required": "required"
        }
    )
    inscription_4 = TextAreaField(
        "inscription",
        validators=[
            DataRequired("inscription！")
        ],
        description="inscription",
        render_kw={
            "class": "form-control",
            "placeholder": 'inscription',
            "required": "required"
        }
    )
    author = StringField(
        label="author",
        validators=[
            DataRequired("author！")
        ],
        description="author",
        render_kw={
            "class": "form-control",
            "placeholder": "个人昵称！",
            "required": "required"
        }
    )
    position = StringField(
        label="position",
        validators=[
            DataRequired("position！")
        ],
        description="author",
        render_kw={
            "class": "form-control",
            "placeholder": "岗位！",
            "required": "required"
        }
    )
    summary = TextAreaField(
        "summary",
        validators=[
            DataRequired("summary！")
        ],
        description="summary",
        render_kw={
            "class": "form-control",
            "placeholder": '简介',
            "required": "required"
        }
    )
    submit = SubmitField(
        'Submit',
        render_kw={
            "class": "btn btn-primary",
        }
    )

# banner
class BannerrForm(FlaskForm):
    title = StringField(
        label="title",
        validators=[
            DataRequired("标题不能为空！")
        ],
        description="title",
        render_kw={
            "class": "form-control",
            "placeholder": "title！",
            "required":"required"
        }
    )
    path = StringField(
        label="path",
        validators=[
        ],
        description="path",
        render_kw={
            "class": "form-control",
            "placeholder": "path！",
        }
    )
    picurl = StringField(
        label="picurl",
        validators=[
        ],
        description="picurl",
        render_kw={
            "class": "form-control",
            "placeholder": "picurl！",
            "required": "required"
        }
    )
    tag = StringField(
        label="tag",
        validators=[
        ],
        description="tag",
        render_kw={
            "class": "form-control",
            "placeholder": "tag！",
            "required": "required"
        }
    )
    type = RadioField(
        coerce=int,
        choices=[(v['id'], v['name']) for v in [{'id': 1, 'name': 'banner'}, {'id': 2, 'name': '广告'}]],
        render_kw={
            "class": "form-control active-radio",
        }
    )
    active = RadioField(
        coerce=int,
        choices=[(v['id'], v['name']) for v in [{'id': 1, 'name': '激活'}, {'id': 0, 'name': '禁用'}]],
        render_kw={
            "class": "form-control active-radio",
        }
    )
    sort = IntegerField(
        "sort",
        validators=[
            NumberRange(message='Type a integer value!')
        ],
        description="sort",
        render_kw={
            "class": "form-control",
            "placeholder": 'sort',
            "required": "required"
        }
    )

    submit = SubmitField(
        'Submit',
        render_kw={
            "class": "btn btn-primary",
        }
    )

# album
class AlbumForm(FlaskForm):
    title = StringField(
        label="title",
        validators=[
            DataRequired("标题不能为空！")
        ],
        description="title",
        render_kw={
            "class": "form-control",
            "placeholder": "title！",
            "required":"required"
        }
    )
    picture = StringField(
        label="picture",
        validators=[
        ],
        description="picture",
        render_kw={
            "class": "form-control",
            "placeholder": "picture！",
            "required": "required"
        }
    )
    like_num = IntegerField(
        label="like_num",
        validators=[
            NumberRange(message='Type a integer value!')
        ],
        description="like_num",
        render_kw={
            "class": "form-control",
            "placeholder": "like_num！",
            "required": "required"
        }
    )
    sort = IntegerField(
        "sort",
        validators=[
            NumberRange(message='Type a integer value!')
        ],
        description="sort",
        render_kw={
            "class": "form-control",
            "placeholder": 'sort',
            "required": "required"
        }
    )

    submit = SubmitField(
        'Submit',
        render_kw={
            "class": "btn btn-primary",
        }
    )
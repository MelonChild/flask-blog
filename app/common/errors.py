# _*_ coding: utf-8 _*_
__author__ = 'Melon'
__date__ = "18/07/09"

from flask import render_template
from . import common

# 404页面
@common.app_errorhandler(404)
def page_not_found(e):
    return render_template('common/404.html'), 404

# 异常页面
@common.app_errorhandler(500)
def internal_server_error(e):
    return render_template('common/500.html'), 500
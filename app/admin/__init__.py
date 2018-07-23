# _*_ coding: utf-8 _*_
__author__ = 'Melon'
__date__ = "18/07/16"

from flask import Blueprint

admin = Blueprint("admin",__name__)

from . import views
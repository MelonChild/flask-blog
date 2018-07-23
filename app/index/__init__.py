# _*_ coding: utf-8 _*_
__author__ = 'Melon'
__date__ = "18/07/09"

from flask import Blueprint

home = Blueprint("home",__name__)

from . import views
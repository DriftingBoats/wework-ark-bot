#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API模块初始化文件
"""

from flask import Blueprint

# 创建API蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 配置蓝图，避免斜杠重定向问题
api_bp.url_map.strict_slashes = False

# 导入各个API模块
from . import health
from . import weather
from . import fortune
from . import constellation
from . import message
from . import info

# 注册子蓝图
api_bp.register_blueprint(health.health_bp)
api_bp.register_blueprint(weather.weather_bp)
api_bp.register_blueprint(fortune.fortune_bp)
api_bp.register_blueprint(constellation.constellation_bp)
api_bp.register_blueprint(message.message_bp)
api_bp.register_blueprint(info.info_bp)
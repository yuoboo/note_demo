import sqlalchemy as sa
import sqlalchemy.sql as sasql
from marshmallow import Schema, fields
from . import metadata

"""
CREATE TABLE `t_users` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `username` varchar(20) NOT NULL COMMENT '用户名',
  `password` char(64) NOT NULL COMMENT '已加密的密码',
  `salt` char(64) NOT NULL COMMENT '密钥',
  `mobile` char(11) NOT NULL COMMENT '手机号',
  `email` char(50) NOT NULL COMMENT '邮箱',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_username` (`username`),
  KEY `idx_mobile` (`mobile`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COMMENT='用户';
"""

users_table = sa.Table(
    't_users', metadata,
    sa.Column('id', sa.Integer, nullable=False, primary_key=True, comment='ID'),
    sa.Column('username', sa.VARCHAR(20), nullable=False, comment='用户名'),
    sa.Column('password', sa.CHAR(64), nullable=False, comment='已加密的密码'),
    sa.Column('salt', sa.CHAR(64), nullable=False, comment='密钥'),
    sa.Column('mobile', sa.CHAR(11), nullable=True, comment='手机号'),
    sa.Column('email', sa.VARCHAR(50), nullable=True, comment='邮箱'),
    sa.Column('created_at', sa.DateTime(), nullable=False,
              server_default=sasql.text('CURRENT_TIMESTAMP'), comment='创建时间'),
    sa.Index('idx_username', 'username', unique=True),
    sa.Index('idx_mobile', 'mobile', unique=True),
    comment='用户',
)


class UserSchema(Schema):
    id = fields.Integer()
    username = fields.String()
    mobile = fields.String()
    email = fields.String()
    intro = fields.String()
    createdAt = fields.DateTime(attribute='created_at')

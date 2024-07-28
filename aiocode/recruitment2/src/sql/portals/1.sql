DROP TABLE IF EXISTS `ehr-recruitment`.`t_share_miniqrcode`;
CREATE TABLE `ehr-recruitment`.`t_share_miniqrcode` (
  `c_id` char(32) NOT NULL COMMENT 'ID',
  `c_key` char(32) NOT NULL DEFAULT '' COMMENT 'md5 key',
  `c_url` varchar(400) NOT NULL DEFAULT '' COMMENT '链接地址',
  `c_qr_code` varchar(256) NOT NULL DEFAULT '' COMMENT '分享小程序码',
  `c_add_dt` datetime NOT NULL DEFAULT '0001-01-01 00:00:00' COMMENT '添加时间',
  PRIMARY KEY (`c_id`),
  KEY `idx_key` (`c_key`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分享小程序码';

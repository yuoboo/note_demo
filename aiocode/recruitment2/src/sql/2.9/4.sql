
# 此文件只在测试环境执行

alter table `ehr-recruitment`.t_recruitment_page_record
drop c_desc_title,
drop c_page_type,
drop c_allow_view_desc;

DROP TABLE IF EXISTS `ehr-recruitment`.`t_recruitment_referee_config`;
create TABLE `ehr-recruitment`.`t_recruitment_referee_config` (
  `c_id` char(32) NOT NULL COMMENT 'ID',
  `c_company_id` char(32) NOT NULL COMMENT '企业ID',
  `c_employee_id` char(32) NOT NULL COMMENT '员工Id(内推人)',
  `c_qr_code_type` smallint(6) NOT NULL default '0' COMMENT '二维码类型(1.微信、2.企业微信)',
  `c_qr_code_url` varchar(256) NOT NULL default '' COMMENT '二维码图片地址',
  `c_add_by_id` char(32) NOT NULL DEFAULT '00000000000000000000000000000000' COMMENT '添加人ID',
  `c_add_dt` datetime NOT NULL DEFAULT '0001-01-01 00:00:00' COMMENT '添加时间',
  `c_update_dt` datetime NOT NULL DEFAULT '0001-01-01 00:00:00' COMMENT '修改时间',
  `c_update_by_id` char(32) NOT NULL DEFAULT '00000000000000000000000000000000' COMMENT '修改人ID',
  `c_is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  PRIMARY KEY (`c_id`),
  KEY `idx_com_emp` (`c_company_id`, `c_employee_id`, `c_qr_code_type`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='内推人配置信息表';


DROP TABLE IF EXISTS `ehr-recruitment`.`t_share_position_qr_code`;
create TABLE `ehr-recruitment`.`t_share_position_qr_code` (
  `c_id` char(32) NOT NULL COMMENT 'ID',
  `c_company_id` char(32) NOT NULL COMMENT '企业ID',
  `c_refer_id` char(32) NOT NULL COMMENT '相关id(员工或者渠道)',
  `c_position_record_id` char(32) NOT NULL COMMENT '网页职位ID',
  `c_qr_code_url` varchar(256) NOT NULL default '' COMMENT '职位分享小程序码',
  `c_add_dt` datetime NOT NULL DEFAULT '0001-01-01 00:00:00' COMMENT '添加时间',
  `c_add_by_id` char(32) NOT NULL DEFAULT '00000000000000000000000000000000' COMMENT '添加人ID',
  PRIMARY KEY (`c_id`),
  KEY `idx_share_refer_position` (`c_company_id`, `c_refer_id`, `c_position_record_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='网页职位相关小程序码记录';

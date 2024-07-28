USE `ehr-recruitment`;

ALTER TABLE `t_recruitment_page_record`
	ADD c_allow_delivery tinyint(1) NOT NULL DEFAULT '0' comment '是否允许求职者投递简历';

ALTER TABLE `t_recruitment_page_job_position` ADD c_referral_bonus varchar(32) NOT NULL DEFAULT '' COMMENT '内推奖励';

ALTER TABLE `t_candidate_application_record`
	ADD c_delivery_scene smallint(6) NOT NULL DEFAULT '1' COMMENT '投递场景(1.HR分享投递,2.员工分享投递)',
	ADD c_delivery_type smallint(6) NOT NULL DEFAULT '1' COMMENT '投递人类型(1.求职者, 2.员工)',
	ADD c_referee_id char(32) NOT NULL DEFAULT '00000000000000000000000000000000' COMMENT '内推人id',
    ADD c_referral_bonus varchar(32) NOT NULL DEFAULT '' COMMENT '内推奖励',
    ADD c_is_payed tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否发放奖金';

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


DROP TABLE IF EXISTS `ehr-recruitment`.`t_wework_external_contact`;
create TABLE `ehr-recruitment`.`t_wework_external_contact` (
  `c_id` char(32) NOT NULL COMMENT 'ID',
  `c_company_id` char(32) NOT NULL COMMENT '企业id',
  `c_external_type` smallint(6) NOT NULL default '1' COMMENT '外部联系人类型(1.微信、2.企业微信)',
  `c_external_id` varchar(50) NOT NULL default '' COMMENT '外部联系人id',
  `c_unionid` varchar(50) NOT NULL default '' COMMENT '微信开放平台的唯一身份标识',
  `c_name` varchar(100) NOT NULL COMMENT '名称',
  `c_candidate_id` char(32) NOT NULL COMMENT '候选人id',
  `c_add_dt` datetime NOT NULL DEFAULT '0001-01-01 00:00:00' COMMENT '添加时间',
  `c_update_dt` datetime NOT NULL DEFAULT '0001-01-01 00:00:00' COMMENT '修改时间',
  `c_is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  PRIMARY KEY (`c_id`),
	KEY `idx_com_can` (`c_company_id`, `c_candidate_id`) USING BTREE,
	KEY `idx_com_ext` (`c_company_id`, `c_external_id`) USING BTREE,
	KEY `idx_com_uni` (`c_company_id`, `c_unionid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='企业微信外部联系人表';


DROP TABLE IF EXISTS `ehr-recruitment`.`t_wework_external_contact_data`;
create TABLE `ehr-recruitment`.`t_wework_external_contact_data` (
  `c_id` char(32) NOT NULL COMMENT 'ID',
  `c_company_id` char(32) NOT NULL COMMENT '企业id',
  `c_wework_external_contact_id` char(32) NOT NULL COMMENT '外部联系人id',
  `c_follow_user` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT 'follow_user',
  `c_is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  PRIMARY KEY (`c_id`),
	KEY `idx_com_can` (`c_company_id`, `c_wework_external_contact_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='企业微信外部联系人关联用户数据表';


DROP TABLE IF EXISTS `ehr-recruitment`.`t_wework_external_contact_way`;
create TABLE `ehr-recruitment`.`t_wework_external_contact_way` (
  `c_id` char(32) NOT NULL COMMENT 'ID',
  `c_app_id` int(11) NOT NULL default '1' COMMENT '企业应用appid',
  `c_company_id` char(32) NOT NULL COMMENT '企业id',
  `c_employee_id` char(32) NOT NULL COMMENT '员工id',
  `c_wework_user_id` char(50) NOT NULL COMMENT '企业微信用户id',
  `c_config_id` char(32) NOT NULL COMMENT '联系方式的配置id',
  `c_qr_code` varchar(200) NOT NULL COMMENT '联系我二维码链接',
  `c_add_dt` datetime NOT NULL DEFAULT '0001-01-01 00:00:00' COMMENT '添加时间',
  `c_update_dt` datetime NOT NULL DEFAULT '0001-01-01 00:00:00' COMMENT '修改时间',
  `c_is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  PRIMARY KEY (`c_id`),
	KEY `idx_com_can` (`c_company_id`, `c_app_id`, `c_employee_id`) USING BTREE,
	KEY `idx_com_ext` (`c_company_id`, `c_app_id`, `c_config_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='企业微信联系我二维码管理';

-- 企业介绍信息
ALTER TABLE `ehr-recruitment`.`t_company_introduction`
    ADD COLUMN `c_qrcode_type` tinyint(3) NOT NULL DEFAULT '0' COMMENT '联系人二维码类型' AFTER `c_image_url`,
    ADD COLUMN `c_qrcode_user_id` char(32) NOT NULL DEFAULT '' COMMENT '二维码用户id' AFTER `c_wechat_qrcode`;
update `ehr-recruitment`.`t_company_introduction` set c_qrcode_type=1 where c_wechat_qrcode != "";

-- 招聘渠道新增show_color
-- ALTER TABLE `ehr-recruitment`.t_recruitment_channel
--    ADD COLUMN c_show_color VARCHAR(16) NOT NULL DEFAULT '#000000' COMMENT '显示颜色';

DROP TABLE IF EXISTS `ehr-recruitment`.`t_share_short_url`;
create TABLE `ehr-recruitment`.`t_share_short_url` (
  `c_id` char(32) NOT NULL COMMENT 'ID',
  `c_key` char(32) NOT NULL default '' COMMENT 'md5 key',
  `c_url` varchar(256) NOT NULL default '' COMMENT '链接地址',
  `c_short_url` varchar(256) NOT NULL default '' COMMENT '分享短连接',
  `c_add_dt` datetime NOT NULL DEFAULT '0001-01-01 00:00:00' COMMENT '添加时间',
  PRIMARY KEY (`c_id`),
  KEY `idx_key` (`c_key`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分享短链接';

-- 候选人新增 企业微信外部联系人类型
ALTER TABLE `ehr-recruitment`.t_candidate
    ADD COLUMN c_wework_external_contact smallint(6) NOT NULL DEFAULT 0 COMMENT '企业微信外部联系人类型';

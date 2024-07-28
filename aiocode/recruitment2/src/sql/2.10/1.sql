DROP TABLE IF EXISTS `ehr-recruitment`.`t_talent_activate_record`;
create TABLE `ehr-recruitment`.`t_talent_activate_record` (
  `c_id` char(32) NOT NULL COMMENT 'ID',
  `c_company_id` char(32) NOT NULL COMMENT '企业ID',
  `c_task_id` char(32) NOT NULL COMMENT '任务ID',
  `c_candidate_id` char(32) NOT NULL COMMENT '候选人ID',
  `c_portal_page_id` char(32) NOT NULL  default '' COMMENT '门户网页ID',
  `c_page_position_id` char(32) NOT NULL default '' COMMENT '网页职位ID',
  `c_sms_template_id` char(32) NOT NULL default '' COMMENT '短信模板ID',
  `c_candidate_record_id` char(32) NOT NULL default '' COMMENT '应聘记录ID',
  `c_sms_content` varchar(256) NOT NULL default '' COMMENT '短信内容',
  `c_activate_status` tinyint(3) NOT NULL default '0' COMMENT '激活状态',
  `c_notify_way` tinyint(3) NOT NULL default '1' COMMENT '通知方式',
  `c_is_read` tinyint(1) NOT NULL default '0' COMMENT '是否访问',
  `c_latest_read_dt` datetime NOT NULL DEFAULT '0001-01-01 00:00:00' COMMENT '最新访问时间',
  `c_add_by_id` char(32) NOT NULL DEFAULT '' COMMENT '添加人ID',
  `c_add_dt` datetime NOT NULL DEFAULT '0001-01-01 00:00:00' COMMENT '添加时间',
  `c_update_dt` datetime NOT NULL DEFAULT '0001-01-01 00:00:00' COMMENT '修改时间',
  `c_update_by_id` char(32) NOT NULL DEFAULT '' COMMENT '修改人ID',
  `c_is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  PRIMARY KEY (`c_id`),
  KEY `idx_com_page_sta` (`c_company_id`, `c_portal_page_id`, `c_activate_status`) USING BTREE,
  KEY `idx_status_add_dt` (`c_activate_status`, `c_add_dt`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='人才激活记录表';

ALTER TABLE `ehr-recruitment`.`t_candidate` ADD COLUMN `c_group_id` char(32)   NOT NULL DEFAULT '' COMMENT '人才分组' AFTER `c_wework_external_contact`;
ALTER TABLE `ehr-recruitment`.`t_candidate` ADD COLUMN `c_last_activate_dt` datetime(0) NOT NULL DEFAULT '2016-01-01 00:00:00' COMMENT '最近激活时间' AFTER `c_group_id`;
ALTER TABLE `ehr-recruitment`.`t_candidate` ADD COLUMN `c_activate_count` int(11) NOT NULL DEFAULT '0' COMMENT '激活总数' AFTER `c_last_activate_dt`;
ALTER TABLE `ehr-recruitment`.`t_candidate` ADD COLUMN `c_last_follow_dt` datetime(0) NOT NULL DEFAULT '2016-01-01 00:00:00' COMMENT '最近跟进时间' AFTER `c_activate_count`;

ALTER TABLE `ehr-recruitment`.`t_candidate` ADD INDEX `idx_com_group`(`c_company_id`, `c_talent_is_join`, `c_group_id`) USING BTREE;

INSERT INTO `ehr-blesssms`.`t_template`(`c_company_id`, `c_type`, `c_text`, `c_name`, `c_code`, `c_status`, `c_push`, `c_remark`, `c_add_by`, `c_add_dt`, `c_audit_dt`, `c_review_dt`, `c_audit_by`, `c_count`, `c_is_sys`, `c_is_delete`, `c_update_by`, `c_update_dt`) VALUES (NULL, 5, '亲爱的#人才姓名#，不要一路流连着采集鲜花保存起来，向前走吧，因为沿着你的路鲜花将会不断开放。#公司名称#邀请您查看新机会：#招聘门户链接#', '人才激活 ', '2haohr_recruitment_activate', 2, NULL, '', NULL, '2015-01-01 00:00:00', '2015-01-01 00:00:00', NULL, NULL, 2, 1, 0, NULL, NULL);
INSERT INTO `ehr-blesssms`.`t_template`(`c_company_id`, `c_type`, `c_text`, `c_name`, `c_code`, `c_status`, `c_push`, `c_remark`, `c_add_by`, `c_add_dt`, `c_audit_dt`, `c_review_dt`, `c_audit_by`, `c_count`, `c_is_sys`, `c_is_delete`, `c_update_by`, `c_update_dt`) VALUES (NULL, 5, '亲爱的#人才姓名#，勤奋，让成功充满机遇；自信，让人生充满激情；爱人，让生命愈加完整；朋友，让生活变得丰富。珍惜美好的爱人，珍惜真诚的朋友。#公司名称# 祝您：幸福一生', '节日祝福 ', '2haohr_recruitment_benediction', 2, NULL, '', NULL, '2015-01-01 00:00:00', '2015-01-01 00:00:00', NULL, NULL, 2, 1, 0, NULL, NULL);

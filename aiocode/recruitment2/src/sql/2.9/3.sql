create TABLE `ehr-recruitment`.`t_company_referral_config` (
  `c_id` char(32) NOT NULL COMMENT 'ID',
  `c_company_id` char(32) NOT NULL COMMENT '企业ID',
  `c_desc_title` varchar(100) NOT NULL DEFAULT '' COMMENT '说明标题',
  `c_desc` text NOT NULL COMMENT '内推说明',
  `c_add_dt` datetime NOT NULL DEFAULT '0001-01-01 00:00:00' COMMENT '添加时间',
  `c_add_by_id` char(32) NOT NULL DEFAULT '00000000000000000000000000000000' COMMENT '添加人ID',
  `c_update_dt` datetime NOT NULL DEFAULT '0001-01-01 00:00:00' COMMENT '更新时间',
  `c_update_by_id` char(32) NOT NULL DEFAULT '00000000000000000000000000000000' COMMENT '更新人ID',
  PRIMARY KEY (`c_id`),
  UNIQUE `un_com` (`c_company_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='企业内推配置表';


ALTER TABLE `ehr-recruitment`.`t_job_position` ADD c_referral_bonus varchar(32) NOT NULL DEFAULT '' COMMENT '内推奖励';

-- 修改内推奖励长度
ALTER TABLE `ehr-recruitment`.`t_recruitment_page_job_position` MODIFY COLUMN c_referral_bonus varchar(32) NOT NULL DEFAULT '' COMMENT '内推奖励';
ALTER TABLE `ehr-recruitment`.`t_candidate_application_record` MODIFY COLUMN c_referral_bonus varchar(32) NOT NULL DEFAULT '' COMMENT '内推奖励';

-- 修改默认值为0
ALTER TABLE `ehr-recruitment`.`t_wework_external_contact` MODIFY COLUMN `c_external_type` smallint(6) NOT NULL DEFAULT 0 COMMENT '外部联系人类型(1.微信、2.企业微信)' AFTER `c_company_id`;

ALTER TABLE `ehr-recruitment`.`t_candidate_application_record` ADD c_reason VARCHAR(500) NOT NULL DEFAULT '' COMMENT '投递原因';
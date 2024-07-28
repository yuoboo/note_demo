-- 基础配置表，添加人才状态修改时间相关数据
ALTER TABLE `ehr-recruitment`.`t_company_request` ADD COLUMN `c_talent_status_interval` int(11) NOT NULL DEFAULT 6 COMMENT '人才状态修改间隔时间' AFTER `c_interview_count`;
ALTER TABLE `ehr-recruitment`.`t_company_request` ADD COLUMN `c_talent_status_type` int(11) NOT NULL DEFAULT 1 COMMENT '人才状态修改间隔类型（1、月；2、年）' AFTER `c_talent_status_ interval`;

ALTER TABLE `ehr-recruitment`.`t_candidate` ADD COLUMN `c_last_job_position_name` char(200)   NOT NULL DEFAULT '' COMMENT '最近应聘职位' AFTER `c_last_follow_dt`;
ALTER TABLE `ehr-recruitment`.`t_candidate` MODIFY COLUMN `c_status` tinyint(2) NOT NULL DEFAULT 1 COMMENT '人才状态：1有效人才；2沉默人才' AFTER `c_recruitment_channel_id`;


USE `ehr-recruitment`;

DROP TABLE IF EXISTS `ehr-recruitment`.`t_data_report_history`;
create TABLE `ehr-recruitment`.`t_data_report_history` (
  `c_id` char(32) NOT NULL COMMENT 'ID',
  `c_company_id` char(32) NOT NULL default '' COMMENT '企业ID',
  `c_ev_scene` tinyint NOT NULL default 1 COMMENT '事件类型(1.统计报表，2.BI上报)',
  `c_ev_code` varchar(10) NOT NULL default '' COMMENT '事件编码',
  `c_ev_data` text NOT NULL COMMENT '事件数据',
  `c_status` tinyint NOT NULL DEFAULT '0' COMMENT '上报状态,1.上报成功,2.未上报,3.上报响应报错',
  `c_exec_msg` varchar(500) NOT NULL DEFAULT '' COMMENT '错误信息',
  `c_add_dt` datetime NOT NULL DEFAULT '0001-01-01 00:00:00' COMMENT '添加时间',
  `c_add_by_id` char(32) NOT NULL DEFAULT '' COMMENT '创建人',
  PRIMARY KEY (`c_id`),
  KEY `idx_com_code_add` (`c_company_id`, `c_ev_code`, `c_add_by_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='大数据上报记录表';


# 修改面试轮次
UPDATE `ehr-recruitment`.t_company_request SET c_interview_count=5 WHERE c_interview_count < 5;

# 报告老板新增字段
ALTER TABLE `ehr-recruitment`.t_report_boss_item ADD COLUMN `c_comment` VARCHAR(1000) NOT NULL DEFAULT '' COMMENT '报表解读';


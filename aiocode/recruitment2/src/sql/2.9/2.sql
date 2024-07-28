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
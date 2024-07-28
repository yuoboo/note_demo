CREATE TABLE `ehr-recruitment`.`t_config_custom_search` (
  `c_id` char(32) NOT NULL COMMENT '主键uuid',
  `c_company_id` char(32) NOT NULL COMMENT '企业id',
  `c_scene_type` tinyint(1) NOT NULL default '1' COMMENT '场景类型：1、招聘中；2、已淘汰；',
  `c_user_type` tinyint(1) NOT NULL default '1' COMMENT '用户类型：1、HR；2、员工；',
  `c_add_by_id` char(32) NOT NULL default '' COMMENT '添加人id',
  `c_add_dt` datetime NOT NULL default now() COMMENT '添加时间',
  `c_update_dt` datetime NOT NULL default '2016-01-01 00:00:00' COMMENT '修改时间',
  `c_config` text COMMENT '自定义筛选条件配置json格式',
  PRIMARY KEY (`c_id`),
  KEY `idx_com_stype_utype_addby` (`c_company_id`,`c_scene_type`,`c_user_type`,`c_add_by_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='自定义筛选条件配置';

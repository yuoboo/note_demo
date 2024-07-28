
USE `ehr-recruitment`;

DROP TABLE IF EXISTS `t_talent_group`;
create TABLE `ehr-recruitment`.`t_talent_group` (
  `c_id` char(32) NOT NULL COMMENT 'ID',
  `c_company_id` char(32) NOT NULL COMMENT '企业ID',
  `c_name` char(20) NOT NULL COMMENT '分组名称',
  `c_parent_id` char(32) NOT NULL default '' COMMENT '上级id',
  `c_level` smallint(6) NOT NULL default '1' COMMENT '层级',
  `c_sort` smallint NOT NULL default '0' COMMENT '层级内排序',
  `c_sort_text` varchar(30) NOT NULL default '0' COMMENT '完整排序值',
  `c_desc` varchar(32) NOT NULL default '' COMMENT '描述',
  `c_add_by_id` char(32) NOT NULL DEFAULT '' COMMENT '添加人ID',
  `c_add_dt` datetime NOT NULL DEFAULT '0001-01-01 00:00:00' COMMENT '添加时间',
  `c_update_dt` datetime NOT NULL DEFAULT '0001-01-01 00:00:00' COMMENT '修改时间',
  `c_update_by_id` char(32) NOT NULL DEFAULT '' COMMENT '修改人ID',
  `c_is_delete` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否删除',
  PRIMARY KEY (`c_id`),
  KEY `idx_com_parent` (`c_company_id`, `c_parent_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='人才分组信息表';

-- 标签表增加名称索引
CREATE INDEX idx_com_name ON t_candidate_tag(`c_company_id`, `c_name`);

-- 候选人标签关联表索引加上company_id
DROP INDEX t_candidate_tag_rel_c_candidate_id_index on t_candidate_tag_rel;
DROP INDEX t_candidate_tag_rel_c_tag_id_index on t_candidate_tag_rel;
CREATE INDEX idx_com_candidate ON t_candidate_tag_rel(`c_company_id`, `c_candidate_id`);
CREATE INDEX idx_com_tag ON t_candidate_tag_rel(`c_company_id`, `c_tag_id`);


-- 应聘记录淘汰表增加人才分组字段
ALTER TABLE `ehr-recruitment`.t_candidate_eliminate_record ADD c_talent_group_id CHAR(32) NOT NULL DEFAULT '' COMMENT '人才分组';

alter table `ehr-recruitment`.t_recruitment_channel
 add index idx_name(`c_name`) using btree;

update `ehr-recruitment`.t_recruitment_channel set c_name='人才激活', c_show_color='#E7103B' where c_name='人才库';
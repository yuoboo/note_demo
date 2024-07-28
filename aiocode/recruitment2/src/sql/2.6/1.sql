alter table `ehr-recruitment`.t_report_boss
 add c_query_params varchar(1000) not null default '{}' comment '全局搜索条件',
 add c_chart_heads varchar(1000) not null default '{}' comment '全局报表信息';
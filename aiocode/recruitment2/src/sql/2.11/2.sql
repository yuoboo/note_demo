alter table `ehr-recruitment`.t_talent_activate_record
    add c_send_email_id char(32) not null default '' comment '发件邮件ID',
    add c_email_template_id char(32) not null default '' comment '邮件模板Id',
    add c_sms_response varchar(512) not null default '' comment '短信发送结果',
    add c_email_response varchar(512) not null default '' comment '邮件发送结果';
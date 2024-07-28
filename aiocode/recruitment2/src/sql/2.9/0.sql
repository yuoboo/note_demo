-- 此sql为配合脚本提前执行
use `ehr-recruitment`;

-- 招聘渠道新增show_color
ALTER TABLE `ehr-recruitment`.t_recruitment_channel
    ADD COLUMN c_show_color VARCHAR(16) NOT NULL DEFAULT '#80848f' COMMENT '显示颜色';
ALTER TABLE `ehr-recruitment`.`t_candidate_application_record`
MODIFY COLUMN `c_referral_bonus` varchar(200) NOT NULL DEFAULT '' COMMENT '内推奖励' AFTER `c_referee_id`;


ALTER TABLE `ehr-recruitment`.`t_job_position`
MODIFY COLUMN `c_referral_bonus` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT '' COMMENT '内推奖金' AFTER `c_secret_position`;

ALTER TABLE `ehr-recruitment`.`t_recruitment_page_job_position`
MODIFY COLUMN `c_referral_bonus` varchar(200) NOT NULL DEFAULT '' COMMENT '内推奖励' AFTER `c_poster_position_desc`;
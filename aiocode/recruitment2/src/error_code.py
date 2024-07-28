from enum import Enum, unique


@unique
class Code(Enum):
    SUCCESS = (200, 'SUCCESS')
    FEEDBACK = (200, '')
    UNAUTHORIZED = (401, '未认证')
    FORBIDDEN = (403, '无权限')
    NOTFOUND = (404, '数据不存在')
    METHODNOTSUPPORT = (405, "请求方式不允许")
    AUTHORIZED_FAILED = (401, '认证失败')
    SYSTEM_ERROR = (500, '服务器开小差了，请稍后重试~')

    # 全局业务代码，以 10 开头
    PARAM_ERROR = (10101, '参数错误！')
    PARAM_MISS = (10102, '参数缺失！')
    OVER_FLOW = (10103, '超出访问次数限制！')

    NO_AUTH = (10201, '没有权限！')
    NO_USER = (10202, '获取不到用户！')
    NO_COMPANY = (10203, '获取不到该用户的企业！')

    key_error = (50001, 'key 字段非法。')
    key_not_exist = (50002, '该 key 不存在。')

    no_admin = (50003, '当前用户不是管理员')
    not_auth = (50004, '权限不存在')
    cannot_set_permission = (50005, '当前用户不能设置权限')
    permission_exist = (50006, '用户权限已存在')

    # 全局 1129
    permission_not_exist = (1129001, '无访问权限或数据已被删除')
    company_not_auth = (1129002, '企业未认证，限制发送邮件附件')
    bad_request = (1129003, '错误的请求，可能是参数错误')
    excel_template_error = (1129004, u'模板有误，请下载系统标准模板')
    excel_empty_error = (1129005, u"导入文件内容不能为空")
    fail_load_file = (1129006, u'文件加载失败')
    import_fail = (1129007, u"文件导入信息创建失败")

    # 配置 1123
    config_recruitment_channel_exist = (1123001, '招聘渠道不存在')
    config_eliminated_reason_exist = (1123002, '淘汰原因不存在')
    config_participant_type_exist = (1123003, '参与者类型不存在')
    config_participant_exist = (1123004, '面试官不存在')
    config_interview_information_exist = (1123005, '面试信息不存在')
    config_company_request_open = (1123006, '企业已开通')
    config_eliminated_reason_is_exist = (1123007, '淘汰原因已存在')
    config_recruitment_channel_is_exist = (1123008, '招聘渠道已存在')
    config_company_request_not_open = (1123009, '企业未开通')
    config_email_template_not_found = (1123010, '邮件模板不存在')
    config_email_info_not_found = (1123011, '邮件标题或者内容不能为空')
    config_not_participant = (1123012, '当前用户非面试官')

    # 招聘职位 1121
    job_position_status_not_stop = (1121001, '招聘职位状态不为停止招聘')
    job_position_not_exist = (1121002, '招聘职位不存在')
    job_position_over_flow = (1121003, '个人版招聘职位数量已达到上限，请升级企业版')
    job_position_secret_false = (1121004, "没有保密职位权限, 没法设置保密职位")

    # 候选人 1122
    candidate_is_candidate = (1122001, '此人已存在')
    candidate_is_employee = (1122002, '已是企业员工')
    candidate_is_talent = (1122003, '此人已在人才库')
    candidate_exist = (1122004, '候选人不存在')
    candidate_is_intention = (1122005, '已是待入职人员')
    candidate_already_eliminated = (1122006, '该候选人已被淘汰')
    candidate_group_not_exist = (1122007, '分组不存在')
    custom_field_select_param_error = (1122008, '自定义选项参数错误')
    candidate_in_blacklist = (1122009, "该候选人在黑名单中")
    candidate_resubmit = (1122010, "该候选人重复提交，请稍后再提交")

    # 候选人应聘记录 1125
    candidate_record_is_exist = (1125001, '此人正在应聘该职位')
    candidate_record_exist = (1125002, '候选人应聘记录不存在')
    candidate_status_modify_record_faile = (1125003, '候选人状态变更日志记录失败')
    candidate_record_params_error = (1125004, '参数错误')
    search_condition_count_limited = (1125005, '常用搜索不能超过10个')

    # offer_records 1124
    offer_need_dep = (1124001, '入职部门为必填项')
    offer_candidate_name_required = (1124002, '姓名为必填')
    offer_candidate_mobile_required = (1124003, '手机号为必填')
    offer_entry_sign_fail_send = (1124004, '入职登记表生成失败')
    offer_already_accept = (1124005, 'offer已接受，请勿重复')
    offer_op_frequently = (1124006, '您的操作太频繁')
    offer_already_refuse = (1124007, 'offer已拒绝，请勿重复')
    offer_refuse_reason_invalid = (1124008, '无效的拒绝原因')
    offer_not_participant = (1124009, '当前用户不是参与者')
    offer_no_permission = (1124010, '当前用户没有查看offer列表权限')

    offer_already_expire = (1124009, '无效的offer，请联系HR')
    offer_params_error = (1124010, '参数有误')
    offer_op_forbid = (1124011, '您不是该应聘职位的招聘HR，没有操作权限')
    offer_email_template_not_found = (1124012, u'offer邮件模板不存在')

    offer_error_tips = (1124999, '提示错误')

    resume_assistant_token_create_error = (116001, '简历助手token创建失败')
    sync_task_error = (116002, '简历同步任务已存在')
    candidate_resume_not_exist = (116003, '候选人简历不存在')
    candidate_resume_import_not_exist = (116004, '简历导入任务不存在')
    resume_analyze_failure = (116005, '简历解析失败')
    resume_type_error = (116006, '简历文件类型不被支持')

    # 面试
    interview_not_found = (1125001, '面试不存在')
    interview_template_not_blank = (1125002, '面试模板不能为空')
    candidate_ids_not_empty = (112503, 'candidate_ids不能为空')
    comment_cannot_empty = (112504, '评价不能为空')
    interview_is_commented = (112505, "面试已评价")

    # 敏感词过滤
    sensitive_word_exist = (14002, '内容存在敏感字符')

    # 简历助手相关 1126
    version_no_exist = (1127002, '版本号已经存在')
    company_not_found = (1127003, '没有这个企业')
    company_must_input = (1127004, '企业没有填写')

    # 请求时对公司账号和用户id判断
    company_or_user = (1128001, '参数错误')
    exist_comment_record_code = (1128002, "候选人应聘记录不存在")
    exist_usage = (1128003, "usage该字段必须传入")
    date_range = (1128004, "date该字段必须传入")
    stop_position = (1128005, "stop_position该字段必须传入")

    # 应聘登记表
    company_employee_form_not_exist = (101201, '应聘登记表不存在')
    company_form_not_exist = (1130001, '应聘登记表不存在或已被删除')
    candidate_form_not_exist = (1130002, '候选人应聘登记表不存在或已被删除')
    candidate_form_has_confirmed = (1130003, '候选人应聘登记表已被确认，无法修改')

    # 招聘门户
    recruit_portal_page_not_found = (1140001, "招聘门户网页异常")

    # 企业微信
    we_work_external_user_error = (1150001, "企业微信外部联系人参数有误")

    # 企业介绍
    is_default_comtro = (201204, "默认企业介绍不可删除")
    is_used_comtro = (201404, "企业介绍已经被使用，不可以删除")


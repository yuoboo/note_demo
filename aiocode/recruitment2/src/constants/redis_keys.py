
# 招聘工作台
# 招聘流程
from configs import config

RECRUITMENT_FLOW_API = ("recruit:bench:flow:{company_id}_{user_id}", 60*3)
RECRUITMENT_TREND_API = ("recruit:bench:flow_today:{company_id}_{user_id}", 60*3)

# 最近职位卡片接口缓存
LAST_POSITION_API = ("recruit:bench:position:{company_id}_{user_id}", 60*3)
# 招聘职位今日新增接口缓存
POSITION_TODAY_ADD_API = ("recruit:bench:position_add:{company_id}_{user_id}", 60*3)
# 最近职位埋点ids缓存
LAST_POSITION_IDS = ("recruit:bench:last_position:{company_id}_{user_id}", 60*60*24*30)


# 企业微信
RECRUITMENT_WEWORK_IS_APP = ("recruit:wework:is_app:{params_md5}", 60 * 60 * 24)


# 城市信息列表
COMMON_DISTRICT_LIST = "recruit:common:district:list"
# 管理范围
COMPANY_USER_MANAGE_SCOPE = ("recruit:common:manage_scope:{company_id}_{user_id}", 60*3)

# 招聘配置: 选择表头  这里是旧的缓存key暂时不要为了统一格式修改 不然无法新旧缓存共存
COMPANY_SELECT_HEADER = "recruitment:select:header:record:{company_id}"
USER_SELECT_HEADER = "recruitment:select:header:record:{company_id}:{user_id}"

# 招聘配置: 短信模板
CONFIG_SMS_TEMPLATE_COMPANY_TYPE_LIST = ("recruit:config:sms_template:{company_id}:{type}", 60*60*24*7)
CONFIG_SMS_TEMPLATE_COMPANY_TYPE_GET = ("recruit:config:sms_template:{company_id}:get:{id}", 60*60*24*7)

# 面试联系人
INTERVIEW_INFORMATION_LIST = 'recruit:interview_information:list:{company_id}'

# 招聘职位

# 招聘门户 - 内推网页id缓存
PORTAL_REFERRAL_PAGE_ID = ('recruit:portal:referral_page_id:{company_id}', 60*60*24*7)


_STATS_EXPIRE = config["RECRUIT_STATS_EXPIRE"]
# 招聘报表-招聘进度
RECRUIT_PROGRESS_POSITION = ('recruit:stats:p_progress:{company_id}_{user_id}_{params_md5}', _STATS_EXPIRE)
RECRUIT_PROGRESS_POSITION_SHEET = ('recruit:stats:p_progress_sheet:{company_id}_{user_id}_{params_md5}', _STATS_EXPIRE)
# 招聘报表-候选人转化率（新增候选人、渠道转换）
RECRUIT_TRANSFER_STATS = ('recruit:stats:recruit_transfer:{company_id}_{user_id}_{params_md5}', _STATS_EXPIRE)
# 招聘报表-淘汰原因
ELIMINATED_REASON_STATS = ('recruit:stats:eliminated_reason:{company_id}_{user_id}_{params_md5}', _STATS_EXPIRE)
# 招聘报表-招聘职位工作量
POSITION_WORKLOAD_STATS = ('recruit:stats:position_workload:{company_id}_{user_id}_{params_md5}', _STATS_EXPIRE)
# 招聘报表-招聘团队工作量
HR_WORKLOAD_STATS = ('recruit:stats:hr_workload:{company_id}_{user_id}_{params_md5}', _STATS_EXPIRE)
EMP_WORKLOAD_STATS = ('recruit:stats:emp_workload:{company_id}_{user_id}_{params_md5}', _STATS_EXPIRE)

# 招聘缓存用户中心信息
RECRUIT_UCENTER_USER_INFO = 'recruit:ucenter:user_info'

# 组织部门信息-树形结构
COMPANY_DEPT_TREE_KEY = 'recruit:orgs:dept_tree:{company_id}'
# 组织部门信息-列表结构
COMPANY_DEPT_LIST_KEY = 'recruit:orgs:dept_list:{company_id}'

# 员工信息-员工姓名
EMPLOYEE_NAME_KEY = ('recruit:employee:name_info:{company_id}_{employee_id}', 60*60*2)

PORTALS_WEWORK_ADD_CANDIDATE = ('recruit:portals:wework_add_candidate:{company_id}_{user_id}_{name}_{mobile}', 20)

# 人才激活试发次数
TALENT_ACTIVE_TRY_NOTICE = ('recruit:talent_active:try_count:{company_id}_{user_id}_{date_str}', 60*60*24*3)

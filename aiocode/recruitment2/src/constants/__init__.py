# -*- coding: utf-8 -*-
from utils.enum import Const


WEWORK_2HAOHR_STATE = 'recruitment'


class CredentialType(Const):
    """
    证件类型
    """
    ID = (1, '身份证')
    FOREI_PASS = (2, '外国护照')
    TAIWAN_PASS = (5, '台湾往来')
    HK_MAC_PASS = (6, '港澳通行证')
    OTHER = (7, '其他')
    HK_ID = (8, '香港身份证')
    TAIWAN_ID = (9, '台湾身份证')
    MAC_ID = (10, '澳门身份证')
    FOREI_RESIDENCE = (11, '外国人永久居留证')


class InterviewWay(Const):
    face2face_interview = (1, '现场面试')
    mobile_interview = (2, '电话面试')
    video_interview = (3, '视频面试')


class InvitationStatus(Const):
    """面试邀约状态"""
    OLD_DATA = (-1, "")  # 旧数据显示为空
    UNKNOWN = (0, "未发送")
    NO_ANSWER = (1, "待回复")
    ACCEPT = (2, "已接受")
    REFUSE = (3, "已拒绝")
    INVALID = (4, "已失效")


class EliminatedReasonStep(Const):
    PRIMARY_STEP = (1, "初筛阶段")
    INTERVIEW_STEP = (2, "面试阶段")
    EMPLOY_STEP = (3, "录用阶段")


class SelectFieldUserType(Const):
    hr = (1, 'HR')
    employee = (2, '员工')


class SelectFieldFormType(Const):
    # candidate_list = (1, '候选人列表')  # 新版废弃
    # offer_draft = (2, '已发Offer列表')  # 新版废弃
    interview_date = (3, '面试日程列表')
    talent_list = (4, '人才库列表')
    job_position = (5, "招聘职位")
    job_position_stop = (6, "停止招聘职位")

    # 初筛类型: 待初筛, 初筛通过, 初筛淘汰
    screen_to_be = (10, "待初筛")
    screen_pass = (11, "初筛通过")
    screen_out = (12, "初筛淘汰")

    # 面试类型: 已安排面试， 已面试， 面试通过，面试淘汰
    interview_arranged = (20, "已安排面试")
    interview_completed = (21, "已面试")
    interview_pass = (22, "面试通过")
    interview_out = (23, "面试淘汰")

    # 录用类型: 拟录用，已发offer, 待入职， 已入职， 放弃录用
    employ_intend = (30, "拟录用")
    employ_send_offer = (31, "已发Offer")
    employ_to_hire = (32, "待入职")
    employ_hired = (33, "已入职")
    employ_give_up = (34, "放弃录用")

    # 高级搜索
    advanced_search = (40, "高级搜索-候选人")
    talent_search = (41, "高级搜索-人才")


class CandidateRecordStatus(Const):
    """
    候选人应聘记录状态
    """
    FORM_CREATE = (8, '应聘登记表预创建')  # 填写应聘登记表前预创建
    PRIMARY_STEP1 = (30, '待初筛')
    PRIMARY_STEP2 = (31, '初筛通过')
    PRIMARY_STEP3 = (32, '初筛淘汰')

    INTERVIEW_STEP1 = (40, '已安排面试')
    INTERVIEW_STEP2 = (41, '已面试')
    INTERVIEW_STEP3 = (42, '面试通过')
    INTERVIEW_STEP4 = (43, '面试淘汰')

    EMPLOY_STEP1 = (50, '拟录用')
    EMPLOY_STEP2 = (51, '已发Offer')
    EMPLOY_STEP3 = (52, '待入职')
    EMPLOY_STEP4 = (53, "已入职")
    EMPLOY_STEP5 = (54, "放弃录用")


class RecruitProgressType(Const):
    position = (1, "招聘职位维度")
    department = (2, "用人部门")
    title_cate = (3, "岗位类型")


class JobPositionStatus(Const):
    """
    应聘职位状态
    """
    START = (1, '招聘中')
    STOP = (2, '停止招聘')


class JobPositionEmergencyLevel(Const):
    """招聘职位紧急程度"""
    COMMON = (1, '一般')
    EMERGENCY = (2, '紧急')


class OfferExpireBy(Const):
    normal = (1, "时间到期自动失效")
    # hr重复发offer
    hr = (2, "hr设置")


class OfferStatus(Const):
    none = (0, "无状态")  # 假offer记录需要
    draft = (1, "待接受")
    accept = (2, "已接受")
    expire = (3, "已失效")
    refuse = (4, "已拒绝")


class ReWorkType(Const):
    """
    @desc 工作性质
    """
    FULLTIME = (0, '全职')
    PARTTIME = (1, '兼职')
    LABOR = (2, '实习生')
    RERIRED = (3, '退休返聘')
    LABORDISPATCH = (4, '劳务派遣')
    OUTSOURCE = (5, '外包')
    LABOUR_SERVICES = (6, '劳务')
    DISPATCH = (7, '派遣')
    HOURLY_WORKER = (8, '小时工')
    ZERO_HOUR_WORK = (9, '临时工')
    SOCIAL_APPOINTMENTS = (10, '社会兼职')
    STUDENT_PART_TIME_JOB = (11, '学生兼职')
    TO_LOAN = (12, '借调')
    RETIREMENT_RECRUITMENT = (13, '退休返聘')
    OTHER = (99, '其他')


class OfferRefuseReason(Const):
    unmatched_salary = (1, "薪资不符合")
    accept_other_offer = (2, "已接受其他家Offer")
    give_up_leave = (3, "原公司挽留")
    unmatched_env = (4, "工作环境不符合")
    unmatched_plan = (5, "职业规划不符合")
    unmatched_hire_dt = (6, "入职时间双方无法协调")
    person_reason = (7, "其他个人原因")


class OfferCancelReason(Const):
    nothing = (0, "无")
    require_change = (1, "招聘需求调整")
    dep_refuse = (2, "用人部门放弃录用")
    time_out = (3, "候选人无法及时入职")
    not_real_certificate = (4, "发现学历，证件有误或造假")
    not_real_work = (5, "发现工作履历造假")
    black_list = (6, "已纳入黑名单人员")


class OfferNotifyWay(Const):
    normal = (1, "邮件和短信")
    other = (2, "其他方式")
    EMAIL = (3, '邮件')
    SMS = (4, '短信')


class WorkLoadType(Const):
    """
    工作量统计维度
    """
    position = (1, "招聘职位")
    depart = (2, "用人部门")
    HR = (3, "招聘HR")
    employee = (4, "面试官")


class ParticipantType(Const):
    """
    @desc 参与者类型
    """
    NONE = (0, "未知")
    HR = (1, 'HR')
    EMPLOYEE = (2, '员工')


class CacheType(Const):
    common = (0, "common_redis")    # redis common 连接池 index = 0
    default = (1, "default_redis")  # redis default 连接池 index = 1


class RecruitmentPageStatus(Const):
    on_line = (1, "上架状态")
    off_line = (2, "下架状态")


class PosterType(Const):
    default = (1, "商务")
    type1 = (2, "科技")
    type2 = (3, "星空")
    type3 = (4, "简约")
    type4 = (5, "内推")
    type5 = (6, "样式6")
    type6 = (7, "样式7")
    type7 = (8, "样式8")
    type9 = (9, "样式9")
    custom = (99, '自定义类型')


class PageStyle(Const):
    Style1 = (1, "淡雅")
    Style2 = (2, "暗黑")
    Style3 = (3, "科技")
    Style4 = (4, "青春")


class RecruitPageType(Const):
    """招聘网页类型"""
    wx_recruit = (1, "HR分享投递")
    referral = (2, "员工分享投递")
    talent_activate = (3, "人才激活投递")


class DeliveryType(Const):
    """
    招聘门户投递类型
    """
    candidate = (1, "求职者投递")
    employee = (2, "公司员工投递")
    hr = (3, "HR投递")


class WorkType(Const):
    """
    @desc 工作性质
    """
    full_time = (0, '全职')
    part_time = (1, '兼职')
    labor = (2, '实习')


class SalaryUnit(Const):
    time = (1, "元/次")
    seller = (2, "元/单")
    hour = (3, "元/小时")
    day = (4, "元/天")
    week = (5, "元/周")
    month = (6, "元/月")
    year = (7, "元/年")


class ShowColor(Const):
    """招聘渠道显示颜色"""
    black = ("#80848f", "默认黑色")
    orange = ("#ff9900", "内推橙色")
    purple = ("#8C71F3", "猎头紫色")


class CustomSearchSceneType(Const):
    PROCESS = (1, '招聘中')
    ELIMINATE = (2, '已淘汰')


class ListDisplayMode(Const):
    CARD = (1, '卡片模式')
    LIST = (2, '列表模式')


class BgCheckStatus(Const):
    """背调状态"""
    unsent = (1, "未发起")
    sent = (2, "背调中")
    done = (3, "已完成")


class TalentAssessmentStatus(Const):
    """人才测评状态"""
    unsent = (1, "未发起")
    sent = (2, "测评中")
    done = (3, "已完成")


class RecruitStatsType(Const):
    """
    招聘报表类型
    """
    progress = (1, "招聘进度")
    candidate_transfer = (2, "新增候选人转换")
    channel_transfer = (3, "招聘渠道转换")
    position_workload = (4, "招聘职位工作量")
    team_workload = (5, "招聘团队工作量")
    eliminated_reason = (6, "淘汰原因")


class OfferExamineStatus(Const):
    """
    offer审批状态
    """
    UN_SEND = (0, "未发起")
    NEW = (1, "审批中")
    PASS = (2, "已通过")
    REFUSE = (3, "已拒绝")
    CANCEL = (4, "已撤销")


class WorkExperience(Const):
    """
    @desc 工作年限
    """
    FORMAL = (0, '经验不限')
    ONE = (1, '1年以下')
    TWO = (2, '1-3年')
    THREE = (3, '3-5年')
    FOUR = (4, '5-10年')
    FIVE = (5, '10年以上')


class JobPositionEducation(Const):
    """
    @desc 学历
    """
    UNKNOW = (0, '学历不限')
    PRIMARY = (1, '小学')
    MIDDLE = (2, '初中及以下')
    HIGH = (3, '高中')
    JUNIOR = (4, '大专')
    BACHELOR = (5, '本科')
    MASTER = (6, '硕士')
    DOCTOR = (7, '博士')
    VOCATIONAL_HIGH = (8, '职高')
    SECONDARY = (9, '中专/中技')
    TECHNICAL = (10, '技校')
    ELSE = (11, '其他')
    POST_DOCTOR = (12, '博士后')
    MBA = (13, 'MBA/EMBA')


class JobPositionEducationV1(Const):
    """
    @desc 学历
    """
    UNKNOW = (0, '学历不限')
    PRIMARY = (1, '小学')
    MIDDLE = (2, '初中')
    HIGH = (3, '高中及以上')
    JUNIOR = (4, '大专及以上')
    BACHELOR = (5, '本科及以上')
    MASTER = (6, '硕士及以上')
    DOCTOR = (7, '博士')
    VOCATIONAL_HIGH = (8, '职高')
    SECONDARY = (9, '中专')
    TECHNICAL = (10, '技校')
    ELSE = (11, '其他')
    POST_DOCTOR = (12, '博士后')


class CandidateRecordStage(Const):
    """
    应聘记录阶段
    """
    PRIMARY_STAGE = (1, "初筛阶段")
    INTERVIEW_STAGE = (2, "面试阶段")
    EMPLOY_STAGE = (3, "录用阶段")


class CrStatus(Const):
    """
    候选人应聘记录状态
    """
    FORM_CREATE = (8, '应聘登记表预创建')  # 填写应聘登记表前预创建
    TO_BE_PRELIMINARY_SCREEN = (30, '待初筛')
    PRELIMINARY_SCREEN_PASSED = (31, '初筛通过')
    PRELIMINARY_SCREEN_ELIMINATE = (32, '初筛淘汰')

    INTERVIEW_ARRANGED = (40, '已安排面试')
    INTERVIEWED = (41, '已面试')
    INTERVIEW_PASSED = (42, '面试通过')
    INTERVIEW_ELIMINATE = (43, '面试淘汰')

    PROPOSED_EMPLOYMENT = (50, '拟录用')
    OFFER_ISSUED = (51, '已发Offer')
    TO_BE_EMPLOYED = (52, '待入职')
    EMPLOYED = (53, "已入职")
    EMPLOYMENT_CANCELED = (54, "放弃录用")


class QrCodeSignType(Const):
    """
    @desc 参与者类型
    """
    EMPLOYMENT_FORM = (0, "应聘登记表")
    INTERVIEW_SIGN = (1, "面试签到")
    WX_RECRUITMENT = (2, "微信招聘职位")
    JOB_POSITION = (3, "招聘职位")
    RECRUIT_PORTAL = (4, "招聘门户")


class CandidateRecordSource(Const):
    """
    应聘记录来源
    """
    HR = (1, '2号人事部')
    ASSISTANT = (2, '简历助手')
    HRLO = (3, '三茅网')
    EMPLOYMENT_FORM = (4, '应聘登记表')
    EMP_RECOMMENDATION = (5, '员工推荐')
    WX_RECRUITMENT = (6, '微信招聘')
    SELF_RECOMMENDATION = (7, '候选自荐')


class CommentType(Const):
    """
    评论类型
    """
    STATUS_CHANGE = (1, "状态变更")
    INTERVIEW_TYPE = (2, "面试")
    OFFER_TYPE = (3, "Offer")
    DISCUSS_TYPE = (4, "讨论")
    OTHER_TYPE = (5, "其他")


class OperateType(Const):
    """
    应聘记录的操作类型
    """
    OPERATE_NONE = (0, "不属于操作")
    STATUS_OPERATE01 = (1, "待初筛")
    STATUS_OPERATE02 = (2, "初选通过")
    STATUS_OPERATE03 = (3, "初选淘汰")
    STATUS_OPERATE04 = (4, "已安排面试")
    STATUS_OPERATE05 = (5, "已面试")
    STATUS_OPERATE06 = (6, "面试通过")
    STATUS_OPERATE07 = (7, "面试淘汰")
    STATUS_OPERATE08 = (8, "拟录用")
    STATUS_OPERATE09 = (9, "已发Offer")
    STATUS_OPERATE10 = (10, "待入职")
    STATUS_OPERATE11 = (11, "已入职")
    STATUS_OPERATE12 = (12, "放弃录用")
    OPERATE13 = (13, "转发给面试官")
    OPERATE14 = (14, "发起人才测评")
    OPERATE15 = (15, "安排面试")
    OPERATE16 = (16, "发送应聘登记表")
    OPERATE17 = (17, "修改面试安排")
    OPERATE18 = (18, "取消面试")
    OPERATE19 = (19, "面试签到")
    OPERATE20 = (20, "发起背调调查")
    OPERATE21 = (21, "发起录用审批")
    OPERATE22 = (22, "发Offer")
    OPERATE23 = (23, "发送入职登记表")
    OPERATE24 = (24, "确认入职")
    OPERATE25 = (25, "提交应聘登记表")
    OPERATE26 = (26, "确认应聘登记表")
    OPERATE27 = (27, "审批录用通过")
    OPERATE28 = (28, "审批录用拒绝")
    OPERATE29 = (29, "审批录用撤回")


class QrCodeType(Const):
    """
    二维码类型
    """
    WeiXin = (1, "微信")
    CopWeiXin = (2, "企业微信")


class EmpQrCodeType(Const):
    """
    内推人（员工）二维码类型
    """
    UseHr = (0, "使用HR")
    WeiXin = (1, "微信")
    CopWeiXin = (2, "企业微信")


class TalentActivateStatus(Const):
    """
    人才激活状态
    """
    Null = (0, "无状态")
    Doing = (1, "激活中")
    Success = (2, "激活成功")
    Failed = (3, "激活失败")


class ActivateNotifyWay(Const):
    """
    激活通知方式
    """
    Sms = (1, "短信")
    Email = (2, "邮件")
    Sms_Email = (3, "短信、邮件")


class SmsTemplateType(Const):
    activate = (1, '人才激活短信模板')


class EventScene(Const):
    UNKNOWN = (0, "未知事件")
    SR = (1, "统计报表")  # statistic_report


class EventStatus(Const):
    DEFAULT = (0, "默认状态")
    SUCCESS = (1, "上报成功")
    S_ERROR = (2, "上报前报错")  # send error  发送前报错 未发送
    R_ERROR = (3, "上报后报错")  # response error 发送后响应报错


class EmailTemplateUsage(Const):
    """
    邮件模板的用途
    """
    offer = (1, 'offer_records')
    interview_notify = (2, '面试通知')
    eliminate_notify = (3, '淘汰通知')
    talent_activate = (4, '人才激活')


class NoticeCallBackType(Const):
    """
    通知（短信、邮件）回调场景
    """
    talent_active = (1, "人才激活")


class RequestType(Const):
    """请求类型"""
    get = (1, 'get')
    post = (2, 'post')


class TaskStatus(Const):
    fail = (-1, '任务执行失败')
    half_fail = (-2, '任务执行半失败')  # -2 执行半失败，此状态为一个中间状态值
    success = (0, '任务执行成功')
    wait = (1, '任务等待调度中')
    queue = (2, '任务排队中')
    progress = (3, '任务执行中')
    to_cancel = (4, '任务待取消')
    canceled = (5, '任务已被取消')


class TaskType(Const):
    """
    任务主类型(1、导入；2、导出；3、打包下载；4、员工同步)
    """
    leading = (1, '导入')
    export = (2, '导出')
    download = (3, '打包下载')
    sync = (4, '员工同步')


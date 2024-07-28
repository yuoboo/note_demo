# coding: utf-8
from constants.commons import null_uuid
from services.s_dbs.portals.s_referral_config import ReferralConfigService

REFERRAL_CONFIG = """
<p><b>一. 内推制度</b></p><p>请补充公司具体的内推制度</p><p><b>二. 内推流程</b></p><p>1. 如果你手上没有简历，可以把职位分享出去，让求职者自己投递，参与内推。</p><p>分享职位：</p><p>可以分享一个职位或者分享全部职位，哪里有潜在的候选人，就分享到哪里。</p><p>
<br></p><p>设置联系我二维码：</p><p>招聘门户上有个“联系我”图标，你可以设置求职者点击之后是添加你为好友还是添加HR为好友。</p><p><img src="https://pub-cdn.2haohr.com/75ade9adf31c46739a9aea2c9153a065" alt="设置联系人"><br></p><p>2. 联系我如果设置的是“企业微信二维码”，求职者只要添加了你的企业微信，你就可以在企业微信上进行内推。（需要HR开通企业微信助手）</p><p>3. 如果求职者已经把简历发给你了，你可以直接点击页面上的“推荐简历”按钮进行内推。</p><p><br></p>
"""


class ReferralConfigBusiness(object):

    @classmethod
    async def create_or_update_referral_config(
            cls, company_id: str, user_id: str, validated_data: dict
    ):
        """
        创建或者更新内推说明
        @param company_id:
        @param user_id:
        @param validated_data:
        @return:
        """
        config = await ReferralConfigService.get_config(company_id, ["id"])
        if config:
            await ReferralConfigService.update_config(
                company_id, user_id, validated_data
            )
        else:
            await ReferralConfigService.create_config(
                company_id, user_id, validated_data
            )

        return

    @classmethod
    async def get_referral_config(cls, company_id: str) -> dict:
        """
        获取企业内推设置信息
        @param company_id:
        @return:
        """
        data = await ReferralConfigService.get_config(
            company_id, ["id", "desc_title", "desc", "update_dt"]
        )

        if not data:
            await ReferralConfigService.create_config(
                company_id, null_uuid, {
                    "desc_title": "内推说明",
                    "desc": REFERRAL_CONFIG
                }
            )
            data = await ReferralConfigService.get_config(
                company_id, ["id", "desc_title", "desc", "update_dt"]
            )

        return data

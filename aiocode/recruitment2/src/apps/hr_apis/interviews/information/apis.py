from front.commons.base_apis import HRAuthView
from front.hr_apis.interviews.information.forms import CreateOrUpdateInformationForm
from business.b_interviews import information_biz
from services.s_commons import action_message_svc


class InformationView(HRAuthView):
    async def get(self, request):
        """
        获取面试信息列表
        """
        company_id = request.ctx.company_id
        informations = await information_biz.find(company_id)
        return self.data(informations)

    async def post(self, request):
        """
        创建面试信息
        """
        form = CreateOrUpdateInformationForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company_id = request.ctx.company_id
        user_id = request.ctx.user_id

        information = await information_biz.create(
            company_id=company_id,
            user_id=user_id,
            linkman=form.linkman.data,
            linkman_mobile=form.linkman_mobile.data,
            address=form.address.data,
            province_id=form.province_id.data,
            city_id=form.city_id.data,
            town_id=form.town_id.data
        )

        return self.data(information)

    async def put(self, request, pk):
        """
        修改面试信息
        """
        form = CreateOrUpdateInformationForm(data=request.json)
        if not form.validate():
            return self.error(form.errors)

        company_id = request.ctx.company_id
        user_id = request.ctx.user_id

        information = await information_biz.update(
            id=pk,
            company_id=company_id,
            user_id=user_id,
            linkman=form.linkman.data,
            linkman_mobile=form.linkman_mobile.data,
            address=form.address.data,
            province_id=form.province_id.data,
            city_id=form.city_id.data,
            town_id=form.town_id.data
        )

        return self.data(information)

    async def delete(self, request, pk):
        """
        删除面试信息
        """
        company_id = request.ctx.company_id
        user_id = request.ctx.user_id

        await information_biz.delete(
            id=pk,
            company_id=company_id,
            user_id=user_id
        )

        return self.data(True)

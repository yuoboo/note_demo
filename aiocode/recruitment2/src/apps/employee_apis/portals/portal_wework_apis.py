from sanic_wtf import SanicForm
from wtforms import StringField
from wtforms.validators import UUID
from business.b_wework import WeWorkBusiness
from utils.api_auth import EmployeeBaseView


class PortalWeWorkExternalContactView(EmployeeBaseView):
    class GetForm(SanicForm):
        candidate_id = StringField(validators=[UUID()], label='候选人id')

    async def get(self, request):
        """
        获取外部联系人员工信息
        :param request:
        :return:
        """
        form = self.GetForm(formdata=request.args)
        if not form.validate():
            return self.error(form.errors)

        candidate_id = form.candidate_id.data
        data = await WeWorkBusiness.get_external_contact_employee(request.ctx.user.company_id, candidate_id)
        return self.data(data)

import pytest
import datetime

from business.candidate_record.b_candidate_record_search import CandidateRecordDataFillBusiness
from framework_engine import create_app
from services.s_es.s_candidate_record_es import OldCandidateRecordESService, CandidateRecordESService


app = create_app()


class TestOldCandidateRecordESService:
    @pytest.mark.asyncio
    async def test_get_status_total(self):
        company_id = 'f79b05ee3cc94514a2f62f5cd6aa8b6e'
        permission_job_position_ids = ['01c5a0d370474779a3f59e8d2e9fe3d1', '0b7ab7faad884b02a30b0eee4f6c1880',
                                       '1a67e957082a457290015141c70c3c0b', '1ff7881b19f84316a9d5538e788f20ff',
                                       '269ead84195a4a53a58a9529bec2244a', '2a3a8e94cb55486f9d406fc6745ce8ab',
                                       '2ea00f0fcf7d4ad6a779a6416b3a3b37', '38b14324496545b58abdbe60ce30ea56',
                                       '4c6416c4b0d54a9c87d5a568944b8a44', '53d1052a11654a5ebed482edff26b810',
                                       '5c76241d0539425f8cf58665d0b520bb', '822e266d7c554298ad794a2886377c89',
                                       '9053775e2b17414381a58a8c71b95649', '91ebd5430d404c37997c21c18fa38e23',
                                       '980fb207a5da428c878405853ec4eda2', '9a7d0e9fc05043eda48be89f9c81bfa1',
                                       'a6c3ba2b9ee94f99ac91f4826b8207e3', 'a8e5fca0914f46e2950da57dfa87f957',
                                       'af2814aa6cdb40a2b480c06b2db248d4', 'bad319d0066344c9bc1af8793cded424',
                                       'e1c61444cd5b42bda6f9cb7859a24a9c', 'f29440ccb0134d9e8dca25f8096f3e54',
                                       'f2fa14b8a3634bc3b015f55198d206c1', 'fc122251ded04182ac447f29a94ac87d',
                                       'a35f6c748b754ddf8a55404a73afbaad', 'b4589d400d394957b5415a37b4cab32f',
                                       'b572052775a6402c997acc6b8cf04f10']
        permission_candidate_record_ids = []
        status_list = [30, 31, 40, 41, 42, 50, 51, 52]
        result = await OldCandidateRecordESService.get_status_total(
            company_id=company_id,
            permission_job_position_ids=permission_job_position_ids,
            permission_candidate_record_ids=permission_candidate_record_ids,
            status=status_list
        )
        assert len(result.keys()) > 0

    @pytest.mark.asyncio
    async def test_get_job_position_total(self):
        company_id = 'ab164df86d10491f90ccbece63cc865e'
        permission_job_position_ids = []
        permission_candidate_record_ids = []
        status_list = []
        job_position_ids = ['67bfa58a0e8348ae8ff4ee3b5cbd0176', '9dc8cfbb308b44ecaadc139084eb9072']
        result = await OldCandidateRecordESService.get_job_position_total(
            company_id=company_id,
            permission_job_position_ids=permission_job_position_ids,
            permission_candidate_record_ids=permission_candidate_record_ids,
            job_position_ids=job_position_ids,
            status=status_list
        )
        assert len(result.keys()) > 0

    @pytest.mark.asyncio
    async def test_get_count(self):
        company_id = 'f79b05ee3cc94514a2f62f5cd6aa8b6e'
        permission_job_position_ids = ['01c5a0d370474779a3f59e8d2e9fe3d1', '0b7ab7faad884b02a30b0eee4f6c1880', '1a67e957082a457290015141c70c3c0b', '1ff7881b19f84316a9d5538e788f20ff', '269ead84195a4a53a58a9529bec2244a', '2a3a8e94cb55486f9d406fc6745ce8ab', '2ea00f0fcf7d4ad6a779a6416b3a3b37', '38b14324496545b58abdbe60ce30ea56', '4c6416c4b0d54a9c87d5a568944b8a44', '53d1052a11654a5ebed482edff26b810', '5c76241d0539425f8cf58665d0b520bb', '822e266d7c554298ad794a2886377c89', '9053775e2b17414381a58a8c71b95649', '91ebd5430d404c37997c21c18fa38e23', '980fb207a5da428c878405853ec4eda2', '9a7d0e9fc05043eda48be89f9c81bfa1', 'a6c3ba2b9ee94f99ac91f4826b8207e3', 'a8e5fca0914f46e2950da57dfa87f957', 'af2814aa6cdb40a2b480c06b2db248d4', 'bad319d0066344c9bc1af8793cded424', 'e1c61444cd5b42bda6f9cb7859a24a9c', 'f29440ccb0134d9e8dca25f8096f3e54', 'f2fa14b8a3634bc3b015f55198d206c1', 'fc122251ded04182ac447f29a94ac87d', 'a35f6c748b754ddf8a55404a73afbaad', 'b4589d400d394957b5415a37b4cab32f', 'b572052775a6402c997acc6b8cf04f10']
        permission_candidate_record_ids = []
        status_list = [30, 31, 40, 41, 42, 50, 51, 52]
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        result = await OldCandidateRecordESService.get_count(
            company_id=company_id,
            permission_job_position_ids=permission_job_position_ids,
            permission_candidate_record_ids=permission_candidate_record_ids,
            status=status_list,
            add_date=[today, today]
        )
        assert isinstance(result, int)


class TestCandidateRecordESService:
    def setup(self):
        self.company_id = 'ab164df86d10491f90ccbece63cc865e'
        permission_candidate_record_ids = []
        permission_job_position_ids = ['029b4419f28f4998ac72f0075f92452e', '029e0a55eb1a4fccacf3dd933ef63bac', '02bfc13dfd5346a4917dc088c5a2fd5a', '032d7160b08c4d89b4d4e9d580d11f4e', '03804dd89d4544e1961cf96caf412d2c', '0479bb91b49046a9822c6d02f6c8e44f', '047ebb8c07764686b966e2170c8aa0cb', '049178cc4e6343218ea844beea268e4c', '05430f267b67472598a7c4ff227c08a1', '05b0b7e741e6420ab64d3ee43ccc0cd7', '05dabed3b21c4934a992883442ffe466', '06fd4ae7624d46448494e082e79d46c2', '0745074392da4c69943a2bbd9da369ee', '07dd1251630d497595f2cbd5e6e54c11', '090c15a8070748fdb2f899c531984044', '09324c9c6b364befacc28c13bc752f92', '0a589d88965c4a3685a003d152bda6d7', '0ab8a611a8e34b54b03f039415f69011', '0b7ea704a0cb4092a51239156b41cdaf', '0c2a733cadd846da92548b474e2d3711', '0c7d6ac2610446ef8d6171a0b9626a5e', '0def6941f53c4fbdab4e6e6ac0166686', '0ebb0c7a156c4327bf05ce46b71715fd', '0f6edb0fb9eb4f1ca497beda5ed5a5af', '0f7549e1f04b48f4aaddb5460dece79d', '0fdb57e8b5944be8ab479c9d93c01619', '11183a672fbf43cbbe495b5e8628e066', '115596f8ca1c4e278d08af105048b83e', '12dab07449dc4ada8eff326af68d8957', '142a40fcb6974cc2a4a0da6211d31783', '171514cae4394fb38b03d3b92a321f52', '18feecab2ebe4706a6a05d0bce2f6ee7', '1a575f32698946fd937b49a231f6192c', '1a8150c3647e46a3a2e4af2326a3d87c', '1b237b3f4d654389a066862290dae136', '1baeedc812e74e71a5c4f586b9708249', '1bd320585cfe402ca54fc6a2a6a8d7c0', '1c4df156222a43f8938718d38fd67871', '1cc1940054524b55817b4a84a86405f1', '1de7f44c6c82473d9a8cf2db3043615d', '1e08efee49384f5889a3c39ce4c05ec6', '1e0a8fd541c6421fa17dac6428dfd4f7', '1e9ca2011028459cbc3f98b89850ecc9', '1f4fb65a9b1e49e1801398ef5cb271f3', '1fc88b5dfc9e4a16a5ced7c356e4ebf2', '200857b071f34f39b7719de43e39a920', '209bd84551654f25bc5ffd7952fc2092', '20d2b52a0f614037a7c3e8655688427f', '2165fa7c39a64f849346cc3a2c25786d', '2178dbfc6cec48b08167c4a90d767e31', '21c9f2469550457aa1b520bd7646b3d4', '2256378d3d214240883e5cb899c262a4', '22bcf684c0954d6db0cc7f31313c82be', '236b4aa0de7849f3b6f302ad244a9026', '240b3d1f63ba4de3b7908d77c0f5c474', '2475034ee122441fb17ee73ada5770e3', '25984a40dcd14f1b92f339254dcd6800', '25a443069be449c69fbfa05573fd6c53', '25da197cae594fc5a92da199e9a312cf', '267b013ecb2f4ceb9ca9d600833ebfab', '28e12b066b29464981ce5ab43d2eb7a4', '2a34c6173a414ae087f6da0cdc23b368', '2b42339caefc41fc838ea90656b0835e', '2bcb7d4afeb74782a0ba2cf1ac9aaf21', '2c3fdd6804f3429aaa500fa38c2b47be', '2c71eaa60d6e495089573da96d276527', '2d02c76366f441e4a47f7e3396438f4c', '2d68a86bb5894e6a8a1868abf8b4268d', '2dd2dc6fe36a40679a66011c4e6e91e7', '2de0ddd49d92461d9145e5c3a153f037', '2e1efefbcec24c8dae86d5c9cef1c5b8', '2e25ff1c566e4e29ba48d023bd6bbaed', '2e71cb5c60de44f1bd986e25905faaeb', '2eb8d2d67f2148c6b394853ce62da966', '2f11e2dcca47428e844b7364a8f32581', '310e17e5395a4422b0489b79db74509a', '3142572b9ce04ccea514a4d62a041173', '316dc9628dec4873b635de2a5a361ec6', '31d5f384c933442fa51a43d3dfbf2fe3', '32056e7f7dd843b5978cf29621e583b0', '32675f710c7b4e30bfa8123a76e087cd', '3303539d245e48348ecbf60e5f79591a', '3313def415bd4481aab38926ec475eb4', '33e963cf2c0145df9dafc275cd374226', '343cebf732d6404fa3e4b1ee15c9035e', '35db61b825e54dd1aea18664381c1a5e', '35ea9beee6124645ae3fb6479fa567b2', '361126b41434466ab6b859e7d3f7b04e', '36bf9dbc2f23488a9f30e5425e2ea72b', '3714a05b07b44700a2969348f3feaaf6', '37217893f04b4b75b8d3c1f2dc78af14', '37e315a9e3ef405e80c6ff3a1c4c3c5d', '38d4237e5e804f06a46fd267c0ab9eb9', '395e0adbd7f244c5a4c89b080aa770e8', '399276c6491d43b0a99ceb657e397233', '39a83caf07ea46a7b8f93279e8278b2f', '39d1198f24124e2588e9c72cf98bc625', '3b1b07a21d894645903289d6221746b6', '3b6b26bdcb6640f998226e4efcf128e4', '3c328d931d6f41c69db68c5ee064b860']
        self.search_params = {
            'status': '30,31,40,41,42,50,51,52',
            'permission_job_position_ids': permission_job_position_ids,
            'permission_candidate_record_ids': permission_candidate_record_ids
        }

    @pytest.mark.asyncio
    async def test_get_status_total(self):
        result = await CandidateRecordESService.get_status_total(
            company_id=self.company_id,
            search_params=self.search_params
        )
        assert len(result.keys()) > 0

    @pytest.mark.asyncio
    async def test_get_count(self):
        count = await CandidateRecordESService.get_count(
            company_id=self.company_id,
            search_params=self.search_params
        )
        assert count > 0

    @pytest.mark.asyncio
    async def test_get_list(self):
        count, list = await CandidateRecordESService.get_list(
            company_id=self.company_id,
            search_params=self.search_params
        )
        assert count > 0
        assert len(list) > 0


class TestCandidateRecordDataFillBusiness(object):
    def setup(self):
        self.company_id = 'ab164df86d10491f90ccbece63cc865e'
        self.user_id = '5dfc3e1b81644eb5a7ce4a34005c7026'
        permission_candidate_record_ids = []
        permission_job_position_ids = ['029b4419f28f4998ac72f0075f92452e', '029e0a55eb1a4fccacf3dd933ef63bac',]
        self.search_params = {
            'status': 30,
            'permission_job_position_ids': permission_job_position_ids,
            'permission_candidate_record_ids': permission_candidate_record_ids
        }

    @pytest.mark.asyncio
    async def test_fill_data(self):
        data = [
                {
                    "form_status": 4,
                    "company_id": "ab164df86d10491f90ccbece63cc865e",
                    "job_position_id": "a9d6e58f94574f26a7b2f095cf3124e3",
                    "add_by_id": "6dfbdd5631704091b73cd905a5ae2779",
                    "is_delete": False,
                    "candidate_id": "57d50b98ff5242c3a3b701592b6cf519",
                    "interview_count": 1,
                    "update_dt": "2020-08-18T20:13:35.000+08:00",
                    "add_dt": "2020-08-14T10:44:35.000+08:00",
                    "id": "80fd9bd064ff4730a53e0bbd274d0ebc",
                    "status": 20,
                    "school": "北京大学"
                },
                {
                    "form_status": 2,
                    "company_id": "ab164df86d10491f90ccbece63cc865e",
                    "job_position_id": "74282a9ef58440d78bf9657c2a2c5571",
                    "add_by_id": "00000000000000000000000000000000",
                    "is_delete": False,
                    "candidate_id": "7ef3bec4f46644b480938ff33fc97f1e",
                    "interview_count": 1,
                    "update_dt": "2020-09-01T19:56:06.000+08:00",
                    "add_dt": "2020-09-01T19:56:06.000+08:00",
                    "id": "08cfafab36b8472d84f7a2d5510ca01d",
                    "status": 8
                },
                {
                    "form_status": 1,
                    "company_id": "ab164df86d10491f90ccbece63cc865e",
                    "job_position_id": "11183a672fbf43cbbe495b5e8628e066",
                    "add_by_id": "1fe849d60bca4d968501d72682717419",
                    "is_delete": False,
                    "candidate_id": "76f2281df2d34af0b885d9741e52abd9",
                    "interview_count": 1,
                    "update_dt": "2020-08-14T10:42:23.000+08:00",
                    "add_dt": "2020-08-11T15:42:21.000+08:00",
                    "id": "0a789cd6d9cd4fbf8c5fd2145f3b2b2b",
                    "status": 20
                },
                {
                    "form_status": 1,
                    "company_id": "ab164df86d10491f90ccbece63cc865e",
                    "job_position_id": "90277287721c4775b011636959520d79",
                    "add_by_id": "5dfc3e1b81644eb5a7ce4a34005c7026",
                    "is_delete": False,
                    "candidate_id": "3268f3a118254a73ad27da28ed90540d",
                    "interview_count": 0,
                    "update_dt": "2020-09-17T17:45:36.000+08:00",
                    "recruitment_channel_id": "add3c4fd09184d2eaedf25924bff28a3",
                    "add_dt": "2020-09-17T17:45:36.000+08:00",
                    "id": "cad00d0edd974537ad2afc2487a19770",
                    "status": 30,
                    "profession": "XX专业",
                    "residential_address": "广东深圳南山区XX小区",
                    "birthday": None,
                    "education": 5,
                    "latest_company": [
                        "XX公司"
                    ],
                    "sex": 1,
                    "mobile": "13112345679",
                    "salary_max": 8398,
                    "latest_job": "销售经理",
                    "school": "XX大学",
                    "name": "张三399",
                    "salary_min": 6000,
                    "work_job_list": [
                        "销售经理"
                    ],
                    "email": "zhangsan@xxx.com",
                    "work_experience": None
                },
                {
                    "form_status": 2,
                    "company_id": "ab164df86d10491f90ccbece63cc865e",
                    "job_position_id": "0b7ea704a0cb4092a51239156b41cdaf",
                    "add_by_id": "6dfbdd5631704091b73cd905a5ae2779",
                    "is_delete": False,
                    "candidate_id": "3262215ef8e64d7cb930d753a234c19c",
                    "interview_count": 1,
                    "update_dt": "2020-09-01T22:48:37.000+08:00",
                    "recruitment_channel_id": "add3c4fd09184d2eaedf25924bff28a3",
                    "add_dt": "2020-08-27T19:43:05.000+08:00",
                    "id": "cdae78e293be41519bd9960e71989920",
                    "status": 40,
                    "profession": "XX专业",
                    "residential_address": "广东深圳南山区XX小区",
                    "birthday": None,
                    "education": 5,
                    "latest_company": [
                        "XX公司"
                    ],
                    "sex": 2,
                    "mobile": "15366250000",
                    "salary_max": 8000,
                    "latest_job": "销售经理",
                    "school": "XX大学",
                    "name": "EXCEL导入142",
                    "salary_min": 6000,
                    "work_job_list": [
                        "销售经理"
                    ],
                    "email": "zhangsan@163.com",
                    "work_experience": "2018-06-01"
                },
                {
                    "form_status": 1,
                    "company_id": "ab164df86d10491f90ccbece63cc865e",
                    "job_position_id": "0b7ea704a0cb4092a51239156b41cdaf",
                    "add_by_id": "6dfbdd5631704091b73cd905a5ae2779",
                    "is_delete": False,
                    "candidate_id": "3262215ef8e64d7cb930d753a234c19c",
                    "interview_count": 1,
                    "update_dt": "2020-09-03T11:06:38.000+08:00",
                    "recruitment_channel_id": "add3c4fd09184d2eaedf25924bff28a3",
                    "add_dt": "2020-08-27T19:43:00.000+08:00",
                    "id": "7a92ac9f3f3c474ca644f14fd896af92",
                    "status": 32,
                    "profession": "XX专业",
                    "residential_address": "广东深圳南山区XX小区",
                    "birthday": None,
                    "education": 5,
                    "latest_company": [
                        "XX公司"
                    ],
                    "sex": 2,
                    "mobile": "15366250000",
                    "salary_max": 8000,
                    "latest_job": "销售经理",
                    "school": "XX大学",
                    "name": "EXCEL导入142",
                    "salary_min": 6000,
                    "work_job_list": [
                        "销售经理"
                    ],
                    "email": "zhangsan@163.com",
                    "work_experience": "2018-06-01"
                },
                {
                    "form_status": 1,
                    "company_id": "ab164df86d10491f90ccbece63cc865e",
                    "job_position_id": "90277287721c4775b011636959520d79",
                    "add_by_id": "5dfc3e1b81644eb5a7ce4a34005c7026",
                    "is_delete": False,
                    "candidate_id": "3208687943cb476b9f3f2f071ddceb91",
                    "interview_count": 0,
                    "update_dt": "2020-09-17T17:45:36.000+08:00",
                    "recruitment_channel_id": "add3c4fd09184d2eaedf25924bff28a3",
                    "add_dt": "2020-09-17T17:45:36.000+08:00",
                    "id": "efd686bf1c2c4f8584330e85e4f35ecd",
                    "status": 30,
                    "profession": "XX专业",
                    "residential_address": "广东深圳南山区XX小区",
                    "birthday": None,
                    "education": 5,
                    "latest_company": [
                        "XX公司"
                    ],
                    "sex": 1,
                    "mobile": "13112345678",
                    "salary_max": 9104,
                    "latest_job": "销售经理",
                    "school": "XX大学",
                    "name": "张三1105",
                    "salary_min": 6000,
                    "work_job_list": [
                        "销售经理"
                    ],
                    "email": "zhangsan@xxx.com",
                    "work_experience": None
                },
                {
                    "form_status": 1,
                    "company_id": "ab164df86d10491f90ccbece63cc865e",
                    "job_position_id": "0b7ea704a0cb4092a51239156b41cdaf",
                    "add_by_id": "6dfbdd5631704091b73cd905a5ae2779",
                    "is_delete": False,
                    "candidate_id": "32e0d842290540dc82003cff435bf980",
                    "interview_count": 1,
                    "update_dt": "2020-09-03T11:06:30.000+08:00",
                    "recruitment_channel_id": "add3c4fd09184d2eaedf25924bff28a3",
                    "add_dt": "2020-08-27T19:43:05.000+08:00",
                    "id": "8e23c02aaedc4c77a86fcf821cae38d5",
                    "status": 32,
                    "profession": "XX专业",
                    "residential_address": "广东深圳南山区XX小区",
                    "birthday": None,
                    "education": 5,
                    "latest_company": [
                        "XX公司"
                    ],
                    "sex": 2,
                    "mobile": "15870050000",
                    "salary_max": 8000,
                    "latest_job": "销售经理",
                    "school": "XX大学",
                    "name": "EXCEL导入186",
                    "salary_min": 6000,
                    "work_job_list": [
                        "销售经理"
                    ],
                    "email": "zhangsan@163.com",
                    "work_experience": "2018-06-01"
                },
                {
                    "form_status": 1,
                    "company_id": "ab164df86d10491f90ccbece63cc865e",
                    "job_position_id": "90277287721c4775b011636959520d79",
                    "add_by_id": "5dfc3e1b81644eb5a7ce4a34005c7026",
                    "is_delete": False,
                    "candidate_id": "32efb378101c47a49e48c30b0ef676ea",
                    "interview_count": 0,
                    "update_dt": "2020-09-17T17:45:36.000+08:00",
                    "recruitment_channel_id": "add3c4fd09184d2eaedf25924bff28a3",
                    "add_dt": "2020-09-17T17:45:36.000+08:00",
                    "id": "4c461871feb9413b97113bd2a2feb9ef",
                    "status": 30,
                    "profession": "XX专业",
                    "residential_address": "广东深圳南山区XX小区",
                    "birthday": None,
                    "education": 5,
                    "latest_company": [
                        "XX公司"
                    ],
                    "sex": 1,
                    "mobile": "13112345679",
                    "salary_max": 8262,
                    "latest_job": "销售经理",
                    "school": "XX大学",
                    "name": "张三263",
                    "salary_min": 6000,
                    "work_job_list": [
                        "销售经理"
                    ],
                    "email": "zhangsan@xxx.com",
                    "work_experience": None
                },
                {
                    "company_id": "ab164df86d10491f90ccbece63cc865e",
                    "job_position_id": "11183a672fbf43cbbe495b5e8628e066",
                    "add_by_id": "38f1176f01ed4df1a3fcfb57675d9d45",
                    "is_delete": False,
                    "candidate_id": "3345e5700f3b4615b45bd3507da4f5e6",
                    "interview_count": 0,
                    "update_dt": "2020-11-03T18:25:48.000+08:00",
                    "recruitment_channel_id": "2f9cd81fa3c74b158023fd43973e2c08",
                    "add_dt": "2020-11-03T13:52:49.000+08:00",
                    "id": "6b99161a62074459938ac9dc55856be6",
                    "status": 31,
                    "profession": "",
                    "residential_address": None,
                    "birthday": None,
                    "education": 0,
                    "latest_company": None,
                    "sex": 0,
                    "mobile": "18756787656",
                    "salary_max": None,
                    "latest_job": None,
                    "school": "",
                    "name": "猫猫",
                    "salary_min": None,
                    "work_job_list": None,
                    "email": "",
                    "work_experience": None
                },
                {
                    "form_status": 1,
                    "company_id": "ab164df86d10491f90ccbece63cc865e",
                    "job_position_id": "90277287721c4775b011636959520d79",
                    "add_by_id": "5dfc3e1b81644eb5a7ce4a34005c7026",
                    "is_delete": False,
                    "candidate_id": "31b91a9be04a45c19bba8abdbc07453b",
                    "interview_count": 0,
                    "update_dt": "2020-09-17T17:45:33.000+08:00",
                    "recruitment_channel_id": "add3c4fd09184d2eaedf25924bff28a3",
                    "add_dt": "2020-09-17T17:37:01.000+08:00",
                    "id": "51692d0f260d4a8ba33676d5c26103e0",
                    "status": 30,
                    "profession": "XX专业",
                    "residential_address": "广东深圳南山区XX小区",
                    "birthday": None,
                    "education": 5,
                    "latest_company": [
                        "XX公司"
                    ],
                    "sex": 1,
                    "mobile": "13112345679",
                    "salary_max": 8009,
                    "latest_job": "销售经理",
                    "school": "XX大学",
                    "name": "张三10",
                    "salary_min": 6000,
                    "work_job_list": [
                        "销售经理"
                    ],
                    "email": "zhangsan@xxx.com",
                    "work_experience": None
                },
                {
                    "form_status": 1,
                    "company_id": "ab164df86d10491f90ccbece63cc865e",
                    "job_position_id": "0b7ea704a0cb4092a51239156b41cdaf",
                    "add_by_id": "6dfbdd5631704091b73cd905a5ae2779",
                    "is_delete": False,
                    "candidate_id": "32fd695b08574876bc4a379a6439fb45",
                    "interview_count": 1,
                    "update_dt": "2020-09-03T11:06:30.000+08:00",
                    "recruitment_channel_id": "add3c4fd09184d2eaedf25924bff28a3",
                    "add_dt": "2020-08-27T19:43:05.000+08:00",
                    "id": "940a743d369c4767a53dcfe5f4e71b7b",
                    "status": 32,
                    "profession": "XX专业",
                    "residential_address": "广东深圳南山区XX小区",
                    "birthday": None,
                    "education": 5,
                    "latest_company": [
                        "XX公司"
                    ],
                    "sex": 2,
                    "mobile": "18102800000",
                    "salary_max": 8000,
                    "latest_job": "销售经理",
                    "school": "XX大学",
                    "name": "EXCEL导入195",
                    "salary_min": 6000,
                    "work_job_list": [
                        "销售经理"
                    ],
                    "email": "zhangsan@163.com",
                    "work_experience": "2018-06-01"
                },
                {
                    "form_status": 1,
                    "company_id": "ab164df86d10491f90ccbece63cc865e",
                    "job_position_id": "0b7ea704a0cb4092a51239156b41cdaf",
                    "add_by_id": "6dfbdd5631704091b73cd905a5ae2779",
                    "is_delete": False,
                    "candidate_id": "32e0d842290540dc82003cff435bf980",
                    "interview_count": 3,
                    "update_dt": "2020-09-04T15:30:20.000+08:00",
                    "recruitment_channel_id": "add3c4fd09184d2eaedf25924bff28a3",
                    "add_dt": "2020-08-27T19:43:00.000+08:00",
                    "id": "f06ec8d336ee4944b2dfe443e47c68cc",
                    "status": 41,
                    "profession": "XX专业",
                    "residential_address": "广东深圳南山区XX小区",
                    "birthday": None,
                    "education": 5,
                    "latest_company": [
                        "XX公司"
                    ],
                    "sex": 2,
                    "mobile": "15870050000",
                    "salary_max": 8000,
                    "latest_job": "销售经理",
                    "school": "XX大学",
                    "name": "EXCEL导入186",
                    "salary_min": 6000,
                    "work_job_list": [
                        "销售经理"
                    ],
                    "email": "zhangsan@163.com",
                    "work_experience": "2018-06-01"
                },
                {
                    "form_status": 1,
                    "company_id": "ab164df86d10491f90ccbece63cc865e",
                    "job_position_id": "0b7ea704a0cb4092a51239156b41cdaf",
                    "add_by_id": "6dfbdd5631704091b73cd905a5ae2779",
                    "is_delete": False,
                    "candidate_id": "32fd695b08574876bc4a379a6439fb45",
                    "interview_count": 1,
                    "update_dt": "2020-09-03T11:06:37.000+08:00",
                    "recruitment_channel_id": "add3c4fd09184d2eaedf25924bff28a3",
                    "add_dt": "2020-08-27T19:43:00.000+08:00",
                    "id": "57f20affe6d34d1882e5a1ab23131396",
                    "status": 32,
                    "profession": "XX专业",
                    "residential_address": "广东深圳南山区XX小区",
                    "birthday": None,
                    "education": 5,
                    "latest_company": [
                        "XX公司"
                    ],
                    "sex": 2,
                    "mobile": "18102800000",
                    "salary_max": 8000,
                    "latest_job": "销售经理",
                    "school": "XX大学",
                    "name": "EXCEL导入195",
                    "salary_min": 6000,
                    "work_job_list": [
                        "销售经理"
                    ],
                    "email": "zhangsan@163.com",
                    "work_experience": "2018-06-01"
                },
                {
                    "form_status": 1,
                    "company_id": "ab164df86d10491f90ccbece63cc865e",
                    "job_position_id": "90277287721c4775b011636959520d79",
                    "add_by_id": "5dfc3e1b81644eb5a7ce4a34005c7026",
                    "is_delete": False,
                    "candidate_id": "339bd2bfd07b4a77b655fa47544336f9",
                    "interview_count": 0,
                    "update_dt": "2020-09-17T17:45:36.000+08:00",
                    "recruitment_channel_id": "add3c4fd09184d2eaedf25924bff28a3",
                    "add_dt": "2020-09-17T17:45:36.000+08:00",
                    "id": "22976bd8ec1a4ffe99d2cfd7df3971b7",
                    "status": 30,
                    "profession": "XX专业",
                    "residential_address": "广东深圳南山区XX小区",
                    "birthday": None,
                    "education": 5,
                    "latest_company": [
                        "XX公司"
                    ],
                    "sex": 1,
                    "mobile": "13112345678",
                    "salary_max": 8563,
                    "latest_job": "销售经理",
                    "school": "XX大学",
                    "name": "张三564",
                    "salary_min": 6000,
                    "work_job_list": [
                        "销售经理"
                    ],
                    "email": "zhangsan@xxx.com",
                    "work_experience": None
                },
                {
                    "form_status": 1,
                    "company_id": "ab164df86d10491f90ccbece63cc865e",
                    "job_position_id": "90277287721c4775b011636959520d79",
                    "add_by_id": "5dfc3e1b81644eb5a7ce4a34005c7026",
                    "is_delete": False,
                    "candidate_id": "33466177fee34fb387c29fa7781db426",
                    "interview_count": 0,
                    "update_dt": "2020-09-17T17:45:36.000+08:00",
                    "recruitment_channel_id": "add3c4fd09184d2eaedf25924bff28a3",
                    "add_dt": "2020-09-17T17:45:36.000+08:00",
                    "id": "56de39fe231c4a8baabf4742eff879cc",
                    "status": 30,
                    "profession": "XX专业",
                    "residential_address": "广东深圳南山区XX小区",
                    "birthday": None,
                    "education": 5,
                    "latest_company": [
                        "XX公司"
                    ],
                    "sex": 1,
                    "mobile": "13112345678",
                    "salary_max": 9070,
                    "latest_job": "销售经理",
                    "school": "XX大学",
                    "name": "张三1071",
                    "salary_min": 6000,
                    "work_job_list": [
                        "销售经理"
                    ],
                    "email": "zhangsan@xxx.com",
                    "work_experience": None
                },
                {
                    "form_status": 1,
                    "company_id": "ab164df86d10491f90ccbece63cc865e",
                    "job_position_id": "90277287721c4775b011636959520d79",
                    "add_by_id": "5dfc3e1b81644eb5a7ce4a34005c7026",
                    "is_delete": False,
                    "candidate_id": "33818d9939db449fbe054341e00b843f",
                    "interview_count": 0,
                    "update_dt": "2020-09-17T17:45:36.000+08:00",
                    "recruitment_channel_id": "add3c4fd09184d2eaedf25924bff28a3",
                    "add_dt": "2020-09-17T17:45:36.000+08:00",
                    "id": "50d7502f58744f5f82ce4486d6514c91",
                    "status": 30,
                    "profession": "XX专业",
                    "residential_address": "广东深圳南山区XX小区",
                    "birthday": None,
                    "education": 5,
                    "latest_company": [
                        "XX公司"
                    ],
                    "sex": 1,
                    "mobile": "13112345679",
                    "salary_max": 8532,
                    "latest_job": "销售经理",
                    "school": "XX大学",
                    "name": "张三533",
                    "salary_min": 6000,
                    "work_job_list": [
                        "销售经理"
                    ],
                    "email": "zhangsan@xxx.com",
                    "work_experience": None
                },
                {
                    "form_status": 1,
                    "company_id": "ab164df86d10491f90ccbece63cc865e",
                    "job_position_id": "90277287721c4775b011636959520d79",
                    "add_by_id": "5dfc3e1b81644eb5a7ce4a34005c7026",
                    "is_delete": False,
                    "candidate_id": "335c17c8cc4a4e819e2764e0bb52d1f7",
                    "interview_count": 0,
                    "update_dt": "2020-09-17T17:45:36.000+08:00",
                    "recruitment_channel_id": "add3c4fd09184d2eaedf25924bff28a3",
                    "add_dt": "2020-09-17T17:45:36.000+08:00",
                    "id": "e7da7aa018d940268a9c01783eb150c9",
                    "status": 30,
                    "profession": "XX专业",
                    "residential_address": "广东深圳南山区XX小区",
                    "birthday": None,
                    "education": 5,
                    "latest_company": [
                        "XX公司"
                    ],
                    "sex": 1,
                    "mobile": "13112345679",
                    "salary_max": 8632,
                    "latest_job": "销售经理",
                    "school": "XX大学",
                    "name": "张三633",
                    "salary_min": 6000,
                    "work_job_list": [
                        "销售经理"
                    ],
                    "email": "zhangsan@xxx.com",
                    "work_experience": None
                },
                {
                    "form_status": 1,
                    "company_id": "ab164df86d10491f90ccbece63cc865e",
                    "job_position_id": "90277287721c4775b011636959520d79",
                    "add_by_id": "5dfc3e1b81644eb5a7ce4a34005c7026",
                    "is_delete": False,
                    "candidate_id": "3266e8c83c0e4ea9b91f0f57d7b477fb",
                    "interview_count": 0,
                    "update_dt": "2020-09-17T17:45:36.000+08:00",
                    "recruitment_channel_id": "add3c4fd09184d2eaedf25924bff28a3",
                    "add_dt": "2020-09-17T17:45:36.000+08:00",
                    "id": "f5e8a2ca8f2440429ba885518ed96dc4",
                    "status": 30,
                    "profession": "XX专业",
                    "residential_address": "广东深圳南山区XX小区",
                    "birthday": None,
                    "education": 5,
                    "latest_company": [
                        "XX公司"
                    ],
                    "sex": 1,
                    "mobile": "13112345679",
                    "salary_max": 8189,
                    "latest_job": "销售经理",
                    "school": "XX大学",
                    "name": "张三190",
                    "salary_min": 6000,
                    "work_job_list": [
                        "销售经理"
                    ],
                    "email": "zhangsan@xxx.com",
                    "work_experience": None
                },
                {
                    "form_status": 1,
                    "company_id": "ab164df86d10491f90ccbece63cc865e",
                    "job_position_id": "90277287721c4775b011636959520d79",
                    "add_by_id": "5dfc3e1b81644eb5a7ce4a34005c7026",
                    "is_delete": False,
                    "candidate_id": "33e18db4336f41ef9b3fa3457e19c1fc",
                    "interview_count": 0,
                    "update_dt": "2020-09-17T17:45:36.000+08:00",
                    "recruitment_channel_id": "add3c4fd09184d2eaedf25924bff28a3",
                    "add_dt": "2020-09-17T17:45:36.000+08:00",
                    "id": "e13c9cf552d3465789401a4f8c066ebe",
                    "status": 30,
                    "profession": "XX专业",
                    "residential_address": "广东深圳南山区XX小区",
                    "birthday": None,
                    "education": 5,
                    "latest_company": [
                        "XX公司"
                    ],
                    "sex": 1,
                    "mobile": "13112345679",
                    "salary_max": 8212,
                    "latest_job": "销售经理",
                    "school": "XX大学",
                    "name": "张三213",
                    "salary_min": 6000,
                    "work_job_list": [
                        "销售经理"
                    ],
                    "email": "zhangsan@xxx.com",
                    "work_experience": None,
                    "tag_list": [
                        "014335eab31d46d49678ca688a35c62f",
                        "20162c3c4fd34cf58212178ccf21affe"
                    ]
                }
        ]
        biz = CandidateRecordDataFillBusiness(
            self.company_id,
            [self.user_id],
            search_params=self.search_params,
            data=data
        )
        await biz.fill_data()
        results = biz.result_data
        print(results)

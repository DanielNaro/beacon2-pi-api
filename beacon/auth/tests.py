from aiohttp.test_utils import TestClient, TestServer, loop_context
import unittest
import os
import jwt
from aiohttp import web
from beacon.auth.__main__ import fetch_idp, validate_access_token, authentication, introspection, fetch_user_info
from dotenv import load_dotenv

# for keycloak, create aud in mappers, with custom, aud and beacon for audience
mock_access_token = 'eyJraWQiOiJyc2ExIiwidHlwIjoiYXQrand0IiwiYWxnIjoiUlMyNTYifQ.eyJhdWQiOiI5ZGI5NTBkYi0zMWQ4LTQ5NjYtOWYzNS1lODIyMmQyZmRjZjYiLCJzdWIiOiJhYWUwYWFjMzMzOGFiNDkwNTk3MmZjODRjZjQ5NDAwN2U1OTQxMDlmQGVsaXhpci1ldXJvcGUub3JnIiwiYWNyIjoiaHR0cHM6Ly9yZWZlZHMub3JnL3Byb2ZpbGUvc2ZhIiwic2NvcGUiOiJnYTRnaF9wYXNzcG9ydF92MSBvcGVuaWQgZW1haWwgb2ZmbGluZV9hY2Nlc3MgcHJvZmlsZSIsImF1dGhfdGltZSI6MTcyNzMzNTMzOCwiaXNzIjoiaHR0cHM6Ly9sb2dpbi5lbGl4aXItY3plY2gub3JnL29pZGMvIiwiZXhwIjoxNzI3MzM4OTU2LCJpYXQiOjE3MjczMzUzNTYsImNsaWVudF9pZCI6IjlkYjk1MGRiLTMxZDgtNDk2Ni05ZjM1LWU4MjIyZDJmZGNmNiIsImp0aSI6IjEwNWQ0ZTViLTIwZGMtNDllMi04M2NjLWJmZGUwOWU0ZjNmNSJ9.VA2o3My48nU_lygsKNWTf8O9ATTWsOP-7d8yKGLAlcwV0ckaegI0aQNcIWVBFMr9YV5UBlj964qmMsyRYxYkOH-FmFb6DbMhKYWU0HTFg2mzza_I8bycs7CwV8PnLh_1h0Mb6CBeyFO4swpAXWV6RSieFurOjldQOKPRde7sWkktn9_TCgYdpaf-g5-hfP_-FIJ9_g_UdoBELyIQOPjiYF3RZREMW6vduGN_KZro9QU1OD7YTpyB7AOHPaU4gjGvHfI5hCs9hmLhARxuJgWQZs0vKpSlv9eMhSfbsV42rF4IgyTOSW5BwiPriVDiXhDvjS0K8CIpd7RMya97Rd9Hbw'
mock_access_token_false = 'public'
#dummy test anonymous
#dummy test login
#add test coverage
#audit --> agafar informació molt específica que ens interessa guardar per sempre (de quins individuals ha obtingut resultats positius)

def create_test_app():
    app = web.Application()
    #app.on_startup.append(initialize)
    return app

class TestAuthN(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self._id = 'test'
    def test_auth_fetch_idp(self):
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_fetch_idp():
                idp_issuer, user_info, idp_client_id, idp_client_secret, idp_introspection, idp_jwks_url, algorithm, aud = fetch_idp(self, mock_access_token)
                load_dotenv("beacon/auth/idp_providers/lifescience.env", override=True)
                IDP_ISSUER = os.getenv('ISSUER')
                IDP_CLIENT_ID = os.getenv('CLIENT_ID')
                IDP_CLIENT_SECRET = os.getenv('CLIENT_SECRET')
                IDP_USER_INFO = os.getenv('USER_INFO')
                IDP_INTROSPECTION = os.getenv('INTROSPECTION')
                IDP_JWKS_URL = os.getenv('JWKS_URL')
                assert IDP_ISSUER == idp_issuer
                assert IDP_CLIENT_ID == idp_client_id
                assert IDP_CLIENT_SECRET == idp_client_secret
                assert IDP_USER_INFO == user_info
                assert IDP_INTROSPECTION == idp_introspection
                assert IDP_JWKS_URL == idp_jwks_url
            loop.run_until_complete(test_fetch_idp())
            loop.run_until_complete(client.close())
    def test_auth_validate_access_token(self):
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_validate_access_token():
                load_dotenv("beacon/auth/idp_providers/lifescience.env", override=True)
                IDP_ISSUER = os.getenv('ISSUER')
                IDP_CLIENT_ID = os.getenv('CLIENT_ID')
                IDP_CLIENT_SECRET = os.getenv('CLIENT_SECRET')
                IDP_USER_INFO = os.getenv('USER_INFO')
                IDP_INTROSPECTION = os.getenv('INTROSPECTION')
                IDP_JWKS_URL = os.getenv('JWKS_URL')
                try:
                    header = jwt.get_unverified_header(mock_access_token)
                    algorithm=header["alg"]
                    decoded = jwt.decode(mock_access_token, options={"verify_signature": False})
                    issuer = decoded['iss']
                    aud = decoded['aud']
                except Exception:# pragma: no cover
                    raise web.HTTPUnauthorized()
                access_token_validation = validate_access_token(self, mock_access_token, IDP_ISSUER, IDP_JWKS_URL, algorithm, aud)
                assert access_token_validation == True
            loop.run_until_complete(test_validate_access_token())
            loop.run_until_complete(client.close())
    def test_auth_introspection(self):
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_introspection():
                load_dotenv("beacon/auth/idp_providers/lifescience.env", override=True)
                IDP_ISSUER = os.getenv('ISSUER')
                IDP_CLIENT_ID = os.getenv('CLIENT_ID')
                IDP_CLIENT_SECRET = os.getenv('CLIENT_SECRET')
                IDP_USER_INFO = os.getenv('USER_INFO')
                IDP_INTROSPECTION = os.getenv('INTROSPECTION')
                IDP_JWKS_URL = os.getenv('JWKS_URL')
                list_visa_datasets=[]
                output_introspection = await introspection(self, IDP_INTROSPECTION, IDP_CLIENT_ID, IDP_CLIENT_SECRET, mock_access_token, list_visa_datasets)
                assert output_introspection == True
            loop.run_until_complete(test_introspection())
            loop.run_until_complete(client.close())
    def test_auth_fetch_user_info(self):
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_fetch_user_info():
                load_dotenv("beacon/auth/idp_providers/lifescience.env", override=True)
                IDP_ISSUER = os.getenv('ISSUER')
                IDP_CLIENT_ID = os.getenv('CLIENT_ID')
                IDP_CLIENT_SECRET = os.getenv('CLIENT_SECRET')
                IDP_USER_INFO = os.getenv('USER_INFO')
                IDP_INTROSPECTION = os.getenv('INTROSPECTION')
                IDP_JWKS_URL = os.getenv('JWKS_URL')
                list_visa_datasets=[]
                user, list_visa_datasets = await fetch_user_info(self, mock_access_token, IDP_USER_INFO, IDP_ISSUER, list_visa_datasets)
                assert user.get('preferred_username') == 'costero-e'
            loop.run_until_complete(test_fetch_user_info())
            loop.run_until_complete(client.close())
    def test_auth_authentication(self):
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_authentication():
                user, list_visa_datasets = await authentication(self, mock_access_token)
                assert user.get('preferred_username') == 'costero-e'
            loop.run_until_complete(test_authentication())
            loop.run_until_complete(client.close())
    def test_auth_authentication_false(self):
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_authentication_false():
                user, list_visa_datasets = await authentication(self, mock_access_token_false)
                assert user == 'public'
            loop.run_until_complete(test_authentication_false())
            loop.run_until_complete(client.close())
    def test_auth_check_visa_passports(self):
        with loop_context() as loop:
            app = create_test_app()
            client = TestClient(TestServer(app), loop=loop)
            loop.run_until_complete(client.start_server())
            async def test_check_visa_passports():
                user={}
                user['ga4gh_passport_v1']=['visa']
                visa_datasets = user['ga4gh_passport_v1']
                list_visa_datasets=[]
                if visa_datasets is not None:
                    for visa_dataset in visa_datasets:
                        try:
                            visa = {}
                            load_dotenv("beacon/auth/idp_providers/lifescience.env", override=True)
                            IDP_ISSUER = os.getenv('ISSUER')
                            visa['iss']=IDP_ISSUER
                            visa["ga4gh_visa_v1"]={}
                            visa["ga4gh_visa_v1"]["value"]='visa/dataset'
                            if visa['iss']==IDP_ISSUER:
                                pass
                            else:# pragma: no cover
                                raise web.HTTPUnauthorized('invalid visa token')
                            dataset_url = visa["ga4gh_visa_v1"]["value"]
                            dataset_url_splitted = dataset_url.split('/')
                            visa_dataset = dataset_url_splitted[-1]
                            list_visa_datasets.append(visa_dataset)
                        except Exception:# pragma: no cover
                            visa_dataset = None
                assert list_visa_datasets == ['dataset']
            loop.run_until_complete(test_check_visa_passports())
            loop.run_until_complete(client.close())

if __name__ == '__main__':
    unittest.main()# pragma: no cover
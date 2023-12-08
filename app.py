from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from config import Config
from memo import MemoListResource, MemoResource

from resources.user import UserFollowResource, UserLoginResource, UserLogoutResource, UserRegisterResource, UserUnFollowResource
# 로그아웃 관련된 임포트문
from resources.user import jwt_blocklist

app = Flask(__name__)

# 환경변수 세팅
app.config.from_object(Config)
# JWT 매니저를 초기화
jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload) :
    jti = jwt_payload['jti']
    return jti in jwt_blocklist

api = Api(app)

api.add_resource(UserRegisterResource,'/user/register')
api.add_resource(UserLoginResource, '/user/login')
api.add_resource(UserLogoutResource,'/user/logout')
api.add_resource(MemoListResource,'/memo')

api.add_resource(MemoResource,'/memos/<int:memo_id>')
api.add_resource(UserFollowResource,'/user/follows')
api.add_resource(UserUnFollowResource,'/user/unfollows/<int:followee_id>')


if __name__ =='__main__' :
    app.run()
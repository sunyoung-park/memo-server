from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error

from email_validator import validate_email, EmailNotValidError

from utils import check_password, hash_password

class UserRegisterResource(Resource) :
    
    def post(self) :

        # 1. 클라이언트가 보낸 데이터를 받는다.
        data = request.get_json()
        
        # 2. 이메일 주소 형식이 올바른지 확인한다.
        try :
            validate_email(data['email'])
        except EmailNotValidError as e : 
            print(e)
            return {'error':str(e)}, 400
        
        # 3. 비밀번호 길이가 유효한지 체크한다.
        # 만약, 비번은 4자리 이상 14자리 이하라고 한다면
        # 이런 것을 여기서 체크한다.
        
        if len(data['password']) < 4 or len(data['password']) > 14 :
            return {'error':'비번길이가 올바르지 않습니다.'}, 400
        
        # 4. 비밀번호를 암호화 한다.
        password = hash_password(data['password'])
        
        print(password)

        # 5. DB의 user 테이블에 저장
        try : 
            connection = get_connection()
            query = '''insert into user
                        (nickname, email, password)
                        values
                        (%s,%s,%s);'''
            record = (data['nickname'],
                      data['email'],
                    password) # 암호화된 비밀번호의 변수를 넣어야함 딕셔너리 X
            
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            #### 테이블에 방금 insert한 데이터의
            #### 아이디를 가져오는 방법(집어 넣고 동시에 가져오기)

            user_id = cursor.lastrowid

            cursor.close()
            connection.close()
        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return{'error':str(e)}, 500

        # ★6. user 테이블의 id(PK)로
        #      JWT 토큰을 만들어야 한다.
        
        # user_id 넣어줄테니 암호화해라(양방향 암호화)
        access_token = create_access_token(user_id)

        # 7. 토큰을 클라이언트에게 준다. response
        return {'result':'success','accessToken':access_token}, 200
    
    
class UserLoginResource(Resource) :

    def post(self) : 

        # 1. 클라이언트로부터 데이터를 받아온다.
        data = request.get_json()

        # 2. 유저 테이블에, 이 이메일주소로
        #    데이터를 가져온다.
        try :
            connection = get_connection()
            query = '''select *
                        from user
                        where email = %s;'''
            record = (data['email'],)

            cursor = connection.cursor(dictionary=True) #sql select 할 땐 꼭 dictionary=True
            cursor.execute(query,record)

            result_list = cursor.fetchall() #list 형식으로 리턴

            cursor.close()
            connection.close()



        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error':str(e)}, 500

        # 회원가입을 안한 경우, 리스트에 데이터가 없다.
        if len(result_list) == 0 :
            return{"error":"회원가입을 하세요."}, 400

        # 회원은 맞으니까, 비밀번호가 맞는 지 체크한다.
        # 로그인한 사람이 막 입력한 비밀번호 : data['password']
        # 회원가입할 때 입력했던, 암호화된 비밀번호 : DB에 있다.
        # result_list에 들어 있고,
        # 이 리스트의 첫번 째 데이터에 들어있다.
        # result_list[0]['password']

        check = check_password(data['password'], result_list[0]['password']) 
        #(지금 유저가 입력한 비밀번호, DB에 저장되어 있는 비밀번호)

        # 비번이 맞지 않는 경우
        if check == False :
            return {'error' :'비번이 맞지 않습니다.'}, 406 # not access
        
        # JWT 토큰을 만들어서, 클라이언트에게 응답한다.
        access_token = create_access_token(result_list[0]['id'])
        # access_token = create_access_token(result_list[0]['id'], expires_delta= datetime.timedelta(minutes=2))
        # 토큰 유효기간 만요 시킬 때 datetime.timedelta(파라미터 시분초 등등 변경 가능)
                
        return {'result':'success','accessToken':access_token}, 200
    

jwt_blocklist = set()
class UserLogoutResource(Resource) :
    
    @jwt_required()
    def delete(self) :
        
        jti = get_jwt()['jti']
        print(jti)

        jwt_blocklist.add(jti)

        return {"result" : "success"}, 200
    


class UserFollowResource(Resource) :

    @jwt_required()
    def post(self) :

        data = request.get_json()
        
        user_id = get_jwt_identity()

        print(data)

        try :
            
            connection = get_connection()

            query ='''insert into follows
                        (follower_id,followee_id)
                        values
                        (%s,%s);'''
            
            record = (user_id,
                      data['followee_id'])
            
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return{'result':'fail','error':str(e)}, 500

        return {'result':'success'}, 200
    


    

class UserUnFollowResource(Resource) :

    @jwt_required()
    def delete(self, followee_id) :
        
        user_id = get_jwt_identity()

        try :
            
            connection = get_connection()

            query ='''delete from follows
                    where follower_id = %s and followee_id =%s;;'''
            
            record = (user_id,
                      followee_id)
            
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return{'result':'fail','error':str(e)}, 500

        return {'result':'success'}, 200
    

    
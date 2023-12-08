from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error


class MemoListResource(Resource) :
    
    @jwt_required()
    def post(self):

        data = request.get_json()

        userId = get_jwt_identity()

        print(data)

        try :
            connection = get_connection()

            query = '''insert into memo
                        (userId,title,date,content)
                        values
                        (%s,%s,%s,%s);'''
            record = (userId,
                    data['title'],
                      data['date'],
                      data['content'])
            
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            cursor.close()
            connection.close()



        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return{'result':'fail','error':str(e)}, 500

        return {'result':'success'}, 200
    
    def get(self) :


        try :

            connection = get_connection()
        
            query = '''select *
                        from memo;'''
            
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute(query)

            result_list = cursor.fetchall()

            print(result_list)


            i = 0
            for row in result_list : 
                result_list[i]['date'] = row['date'].isoformat()
                result_list[i]['createdAt'] = row['createdAt'].isoformat()
                result_list[i]['updatedAt'] = row['updatedAt'].isoformat()
                i = i+1

            print(result_list)

            cursor.close()
            connection.close()


        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return{"result":"fail","error":str(e)}, 500
        

        return {"result":"success","items":result_list, "count":len(result_list)}, 200
    

class MemoResource(Resource) :

    
    @jwt_required()
    def delete(self, memoId) :

        userId = get_jwt_identity()

        try : 
            
            connection = get_connection()

            query = '''delete from memo
                        where id = %s and userId = %s;'''
            
            record = (memoId, userId)

            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"result":"fail","error":str(e)}, 500

        return {"result":"success"}, 200
    

    def put(self) :

        data = request.get_json()

        print(data)

        try :
            
            connection = get_connection()

            query = ''''''
        except Error as e :
            pass
        return
    

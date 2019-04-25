from functools import wraps
from pymongo import MongoClient
from bson import ObjectId
from flask import *
from datetime import date
from flask_restful import Resource, Api, reqparse
from bson.json_util import dumps, loads
import json

app = Flask(__name__)
app.secret_key= 'rutgersIsADeadMeme'
SESSION_TYPE = 'redis'
api = Api(app)
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

client = MongoClient('mongodb://admin:admin@cluster0-shard-00-00-avps1.mongodb.net:27017,cluster0-shard-00-01-avps1.mongodb.net:27017,cluster0-shard-00-02-avps1.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true', 27017)

Sext = client['sext-db']

class main_page(Resource):
	def get(self): 
		return {'msg':'hello world', 'error':'None'}

class register(Resource):
    def get(self):
        return {'msg':'None', 'error':'None'}
    def post(self):
    	user = Sext['user']
    	data = request.get_json()
    	if data is None:
    		error = 'email cannot be found in form!'
    		return str(data)
        user.insert_one({"email": data['email']})
      	return str(data)

class login(Resource):
    def get(self):
        return {'msg':'None', 'error':'None'}
    def post(self):
    	error = "None"
    	user = Sext['user']
        data = request.get_json()
        loginUser = user.find_one({"email": data['email']})
        if loginUser == None:
            error = 'Cannot find email given, Please try to registser/login again'
            return {'msg':'None', 'error': error}
        return {'msg':str(loginUser), 'error': error}

class dashboard(Resource):
    def get(self, email):
        user = Sext['user']
        user_data = user.find_one({'email': email})
        if user_data == None:
            error = "No Data"
            return {'msg':'None', 'error':error}
        return str(user_data)

    def post(self, email):
        data = request.get_json()
        user = Sext['user']
        user_data = user.find_one({'email': data})
        if user_data == None:
            error = "Other User does not exist"
            return {'msg':'None', 'error':error}
        new_email = request.get_json()
        user.update({'email': num}, {"$push": {"OId": data}})
        return {'msg':'Added User', 'error': 'None'}

class dashboardChat(Resource):
	def get(self, email, other_email):
		msg = Sext['sext']
		query = {"sender": email, "reciever": other_email}
		data = msg.find(query).sort("time", -1)
		out =[]
		for x in data:
			x["_id"] = str(x["_id"])
			out.append(x)
		return str(out)
		if data == None:
			error = "No Data"
			return {'msg':'None', 'error':error}
		return str(data.get_json())
	def post(self, email, other_email):
		msg = Sext['sext']
		newmsg = {
			"msg": request.get_json(),
			"time": str(date.today()),
            "sender": email,
            "reciever": other_email
            }
		msg.insert_one(newmsg)
		return {'msg':'Added Message', 'error': 'None'}

api.add_resource(main_page,'/')
api.add_resource(login,'/login')
api.add_resource(register,'/register')
api.add_resource(dashboard,'/dashboard/<email>')
api.add_resource(dashboardChat,'/dashboard/<email>/<other_email>')


if __name__ == '__main__':
    app.run(debug=False)

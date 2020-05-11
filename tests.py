#!/usr/bin/env python
import requests

#Integration tests for the RealEstateAPI
#They do not cover all cases, this is a sample of what is possible

URL = 'http://localhost:5000'
headers = {'Content-type': 'application/json'}

#register a first user
register_body = {'surname': 'Morin', 'name':'Louis',"bday" : "11-03-1998"}
r = requests.post(url = URL+'/register', data = register_body, headers = headers)
#we dont send data as json, expecting error
assert(r.status_code == 400)
r = requests.post(url = URL+'/register', json = register_body, headers = headers)
assert(r.status_code == 200)
token1 = (r.json().get("token"))
assert(token1)

##test add estate
estate_body = {
	"token":"anInvalidToken",
	"name": "first house",
	"re_type" : "house",
	"rooms" : [{"name" : "master"}],
	"city" : "Paris",
}
r = requests.post(url = URL+'/add_estate', json = estate_body, headers = headers)
#Wrong authorization
assert(r.status_code == 401)
estate_body["token"] = token1
r = requests.post(url = URL+'/add_estate', json = estate_body, headers = headers)
assert(r.status_code == 200)
estate_id= r.json().get("estate_id")
assert(estate_id)

#register a second user
register_body = {'surname': 'MorDeux', 'name':'Louis',"bday" : "11-03-1998"}
r = requests.post(url = URL+'/register', json = register_body, headers = headers)
assert(r.status_code == 200)
token2 = (r.json().get("token"))
assert(token2)

#we can get all real estates available in Paris
r=	requests.get(url = URL + '/search/Paris',headers = headers)
estates = r.json()
assert(len(estates) == 1)

##user2 add estate
estate_body = {
	"token":token2,
	"name": "user2 house",
	"re_type" : "house",
	"rooms" : [{"name" : "master"}],
	"city" : "paris",
}

r = requests.post(url = URL+'/add_estate', json = estate_body, headers = headers)
assert(r.status_code == 200)
new_estate_id= r.json().get("estate_id")
assert(new_estate_id)

#we now have 2 estates
r=	requests.get(url = URL + '/search/Paris',headers = headers)
estates = r.json()
assert(len(estates) == 2)


#Mordeux try to edit the house of Morin
edit_estate_body = {
	"name": "now a flat",
	"re_type" : "flat",
	"rooms" : []

}
edit_estate_body["token"] = token2
r = requests.put(url = URL+'/update_estate/'+str(estate_id), json = edit_estate_body, headers = headers)
#Wrong authorization
assert(r.status_code == 401)
#User 1 tries
edit_estate_body["token"] = token1
r = requests.put(url = URL+'/update_estate/'+str(estate_id), json = edit_estate_body, headers = headers)			
assert(r.status_code == 200)
estate_id= r.json().get("estate_id")
assert(estate_id)
#we now have 2 estates
r=	requests.get(url = URL + '/search/Paris',headers = headers)
estates = r.json()
estate_modified = estates[0]
assert(estate_modified.get("name") == "now a flat")

edit_estate_body["token"] = token2
r = requests.put(url = URL+'/update_estate/'+str(estate_id), json = edit_estate_body, headers = headers)
#Wrong authorization
assert(r.status_code == 401)

#Lets add a room to the flat
add_room_body = {"token":token1,"name" : "guest room", "id_estate": estate_id}
r = requests.post(url = URL+'/add_room', json = add_room_body, headers = headers)
rep = r.json()
room_id = rep.get("new_room")
assert(room_id)

#anyone can update users
user_body = {"name" : "Claude"}
r = requests.put(url = URL+'/update_user/1', json = user_body, headers = headers)
assert(r.status_code == 200)
#but only of users that exists
r = requests.put(url = URL+'/update_user/3', json = user_body, headers = headers)
assert(r.status_code==400)

#the kids moved back in, let's update the room
#Lets add a room to the flat
update_room_body = {"token":token1,"description" : "cool kids room"}
r = requests.put(url = URL+'/update_room/' + str(room_id), json = update_room_body, headers = headers)
rep = r.json()
room_id = rep.get("room_id")
assert(room_id)

#let's delete the estate of the second user
delete_body = {"token" : token2}
r = requests.delete(url = URL + '/delete_estate/'+str(new_estate_id), json = delete_body, headers = headers)
assert(r.json().get("deleted") == True)

r=	requests.get(url = URL + '/search/Paris',headers = headers)
assert(len(estates) == 2)

print('all tests passed succesfully')



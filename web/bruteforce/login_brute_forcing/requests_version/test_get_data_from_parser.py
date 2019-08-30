from HTMLParser import HTMLParser

# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_results = {}
        self.tag = ""
        self.captcha_block = False
        self.data_captcha_block = []
        self.entityref_captcha_block = ''

    
    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            for name, value in attrs:
                #check whether we enter the captach block to 
                #bruteforce it
                if name == 'class' and value == 'cptch_block':
                    print("Captcha block found!")
                    self.captcha_block = True


    def handle_endtag(self, tag):
        #if we see closing tag p, means we are out of
        #captcha block
        if tag =='p':
            self.captcha_block = False

    def handle_data(self, data):

        #if we are in captcha block we capture the data
        if self.captcha_block:
            #only the index 3 and 4 are useful, the rest is garbage
            self.data_captcha_block.append(data)
            print self.data_captcha_block

    def handle_entityref(self, entity):
        if self.captcha_block:
            print "Encountered some entityref  :", entity
            self.entityref_captcha_block = entity

    def handle_captcha(self,val1, val2, op):
        if op == 'minus':
            return val1 - val2

        if op == 'times':
            return val1 - val2

        else:
            return val1 + val2

fd = open('template_admin_page.html','r')
c = fd.read()
parser = MyHTMLParser()
parser.feed(c)
v1 = int(parser.data_captcha_block[3])
v2 = int(parser.data_captcha_block[4].replace('=',''))
op = parser.entityref_captcha_block
res = parser.handle_captcha(v1, v2, op)
print res

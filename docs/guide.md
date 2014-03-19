# Updating the repunch development and production servers
---------------------------------------------------------

1. Open a terminal and go to the project folder in .../repunch_web

2. Connect to the aws machine:
    - For the development server:
        ssh -i docs/repunchdev.pem ubuntu@ec2-54-242-50-156.compute-1.amazonaws.com
        
    - For the production server:
        ssh -i docs/repunch.pem ubuntu@ec2-23-20-15-30.compute-1.amazonaws.com
        
3. Once connected to the server terminal go to the project folder:
        cd Repunch/repunch_web
        
4. Pull changes.
    - If you are pulling updates that does not contain any changes to any .py files:
        sudo git pull origin master
        
    - Otherwise:
        I. Log out all users. This step is optional - however recommended if you made changes to any Parse class models.
            python manage.py clean_comet_session force
            
        II. Stop the cloud_logger (only for the development server).
            python manager.py cloud_logger stop
            
        III. Stop apache.
            sudo /etc/init.d/apache2 stop
            
        IV. Pull.
            sudo git pull origin master
            
        V. Check the settings file (IMPORTANT). 
            sudo vi repunch/settings.py
        To begin writing to the file using vi, press i. Then make sure that DEBUG = False 
        and PRODUCTION_SERVER = False in development and PRODUCTION_SERVER = True in production.
        Save the changes by pressing escape then entering :w and hit enter. To quit vi, enter :q and hit enter.
        
        VI. Restart apache. In the production server, you will be asked to enter
        a passphrase for the private key for the ssl certificate.The password is repunch7575.
            sudo /etc/init.d/apache2 restart
       
        VII. Start the cloud_logger (only for the development server).
            python manager.py cloud_logger start & disown
        

# Continuing code development
-----------------------------

1. Read up on basic Python 2.7.x (just the basics, nothing fancy)
2. Read up on Django v1.5
3. Read the documentation of ParseObject located in parse/core/models.py 
4. Read up on Python coding style [PEP8](http://legacy.python.org/dev/peps/pep-0008/)
Some parts of the code violate some of the guidlines but for the most part the code is written in PEP8 style.
The most important thing is to use SPACES and NEVER TABS. In your text editor make sure to set "insert spaces instead of tabs".


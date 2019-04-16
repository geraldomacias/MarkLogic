# MarkLogic Data Classifier
[![Build Status](https://travis-ci.org/geraldomacias/MarkLogic.svg?branch=master)](https://travis-ci.org/geraldomacias/MarkLogic)

Do YOU have a bunch of data specifically regarding sports? Well youve come to the right place. Here you will find an implementation of what you'll need.

We are Team Mark, a software development team based out of Cal Poly and we welcome you to our github page. Currently we are developing a Machine Learning Data Classifier specifically applied to sports data. Our machine learner classifies data for the sports of soccer, football, baseball, hockey, and basketball. Currently our machine learner uses linear SVC and naive bayes to classify sports data based on column names and key identifiers. 

Future development involves removal of any found defects and stylization of our current UI and UX. We will also be working on improving the efficiency of our classification strategy by using a more in depth ontology. 

Here is a list of all the necessary licensing for any 3rd party dependancies that we use:
Name              Version  License     
 Docker            18.09.4   Apache Software License                                                             
 Click             7.0       BSD License                                                                                      
 Flask             1.0.2     BSD License                                                                                      
 Flask-Bcrypt      0.7.1     BSD License                                                                                      
 Flask-Cors        3.0.6     MIT License                                                                                      
 Flask-SQLAlchemy  2.3.2     BSD License                                                                                      
 Flask-Testing     0.6.2     BSD License                                                                                      
 Jinja2            2.10.1    BSD License                                                                                      
 MarkupSafe        1.1.1     BSD License                                                                                      
 PyJWT             1.7.1     MIT License                                                                                      
 SQLAlchemy        1.3.2     MIT License                                                                                      
 Werkzeug          0.15.2    BSD License                                                                                      
 atomicwrites      1.3.0     MIT License                                                                                      
 attrs             19.1.0    MIT License                                                                                      
 bcrypt            3.1.6     Apache Software License                                                                          
 boto3             1.9.60    Apache Software License                                                                          
 botocore          1.12.130  Apache Software License                                                                          
 cffi              1.12.2    UNKNOWN                                                                                          
 coverage          4.5.3     Apache Software License                                                                          
 docutils          0.14      Public Domain, Python Software Foundation License, BSD License, GNU General Public License (GPL) 
 gunicorn          19.8.1    MIT License                                                                                      
 itsdangerous      1.1.0     BSD License                                                                                      
 jmespath          0.9.4     MIT License                                                                                      
 more-itertools    7.0.0     MIT License                                                                                      
 pluggy            0.9.0     MIT License                                                                                      
 postgres          2.2.2     CC0 1.0 Universal (CC0 1.0) Public Domain Dedication                                             
 psycopg2          2.7.4     GNU Library or Lesser General Public License (LGPL), Zope Public License                         
 psycopg2-binary   2.8.1     GNU Library or Lesser General Public License (LGPL), Zope Public License                         
 py                1.8.0     MIT License                                                                                      
 pycparser         2.19      BSD License                                                                                      
 pytest            4.1.1     MIT License                                                                                      
 pytest-cov        2.6.1     BSD License                                                                                      
 python-dateutil   2.8.0     BSD License, Apache Software License                                                             
 s3transfer        0.1.13    Apache Software License                                                                          
 six               1.12.0    MIT License                                                                                      
 urllib3           1.24.1    MIT License
 numpy             1.16.2    BSD License
 scipy             1.2.1     BSD License
 scikit-learn      0.20.2    BSD License 
 jupyter           5.7.8     BSD License
 pandas            0.24.2    BSD License

## Installation Steps
To run the code:
1. INSTALL DOCKER (Use desktop install, not homebrew)
2. RUN DOCKER
3. Run the build_and_run.sh script
4. Go to <http://localhost/users/ping>
5. You should see something. If you don't pls let me know cuz that's not good.

Also, check out http://localhost/users and http://localhost/users/<user_id>

Theoretically, this will be the code / microservice for users / login / account stuff. That's why its in the "users" folder. Other services we add (like the machine learning, file upload, all that) will have their own folders, and their own containers. All these containers are joined by the docker-compose-dev.yml (or prod) file.

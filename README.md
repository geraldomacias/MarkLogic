# MarkLogic Data Classifier
[![Build Status](https://travis-ci.org/geraldomacias/MarkLogic.svg?branch=master)](https://travis-ci.org/geraldomacias/MarkLogic)

Do YOU have a bunch of data specifically regarding sports? Well youve come to the right place. Here you will find an implementation of what you'll need.

We are Team Mark, a software development team based out of Cal Poly and we welcome you to our github page. Currently we are developing a Machine Learning Data Classifier specifically applied to sports data. Our machine learner classifies data for the sports of soccer, football, baseball, hockey, and basketball. Currently our machine learner uses linear SVC and naive bayes to classify sports data based on column names and key identifiers. 

Future development involves removal of any found defects and stylization of our current UI and UX. We will also be working on improving the efficiency of our classification strategy by using a more in depth ontology. 

Here is a list of all the necessary licensing for any 3rd party dependancies that we use:



## Installation Steps

I did a few things.
To run the code (which you rly should do pls)
1. INSTALL DOCKER (Easier with desktop install, not homebrew)
2. RUN DOCKER
3. Run the build_and_run.sh script
4. Go to <http://localhost/users/ping>
5. You should see something. If you don't pls let me know cuz that's not good.

Also, check out http://localhost/users and http://localhost/users/<user_id>

Theoretically, this will be the code / microservice for users / login / account stuff. That's why its in the "users" folder. Other services we add (like the machine learning, file upload, all that) will have their own folders, and their own containers. All these containers are joined by the docker-compose-dev.yml (or prod) file.

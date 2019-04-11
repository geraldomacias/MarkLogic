# MarkLogic Data Classifier
[![Build Status](https://travis-ci.org/geraldomacias/MarkLogic.svg?branch=master)](https://travis-ci.org/geraldomacias/MarkLogic)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fgeraldomacias%2FMarkLogic.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fgeraldomacias%2FMarkLogic?ref=badge_shield)

## Installation Steps

I did a few things.
To run the code (which you rly should do pls)
1. INSTALL DOCKER (Easier with desktop install, not homebrew)
2. RUN DOCKER
3. Run the build_and_run.sh script
4. Go to <http://localhost/users/ping>
5. You should see something. If you don't pls let me know cuz that's not good.

Also, check out http://localhost/users and http://localhost/users/<user_id>

Pls look around the code and check it out. I'm not 100% sure what the code is doing either, but together, we can overcome ANY challenge.

Theoretically, this will be the code / microservice for users / login / account stuff. That's why its in the "users" folder. Other services we add (like the machine learning, file upload, all that) will have their own folders, and their own containers. All these containers are joined by the docker-compose-dev.yml (or prod) file.


## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fgeraldomacias%2FMarkLogic.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fgeraldomacias%2FMarkLogic?ref=badge_large)
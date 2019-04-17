# Installation Instructions
## Installing The Backend Using Docker

### 1. Installing Docker and Docker Compose

Depending on your operating system, Docker can be installed in different ways. For full installation instructions, follow [these instructions](https://docs.docker.com/install/).

*Note: If you are using linux, make sure to follow the [Post-installation steps for Linux](https://docs.docker.com/install/linux/linux-postinstall/).*

After Docker is installed, install Docker Compose using [these instructions](https://docs.docker.com/compose/install/).

### 2. Cloning The Repository

Once Docker and Docker Compose are installed, we can now clone [the classifier backend repository](https://github.com/geraldomacias/MarkLogic).

Navigate to wherever you want to clone the repository, and (assuming you have [Git](https://git-scm.com/) installed), enter the following command:

    git clone https://github.com/geraldomacias/MarkLogic.git

Now, there should be a folder called MarkLogic. Navigate into that folder by typing:

    cd MarkLogic

### 3. Spinning Up The Containers

Now that we have the backend repository cloned and our cwd set, let's start up the containers.

I have included a script that will start the containers using Docker Compose, then create the database used for user storage. This script can be executed by typing:

    ./build_and_run.sh

You can also execute the commands manually, as follows:

    docker-compose -f docker-compose-dev.yml build
    docker-compose -f docker-compose-dev.yml up -d
    docker-compose -f docker-compose-dev.yml run users python manage.py recreate-db
    docker-compose -f docker-compose-dev.yml run file_system python manage.py recreate-db
    docker-compose -f docker-compose-dev.yml run machine_learning python manage.py recreate-db

***CAUTION***: The last 3 commands not only create the database, but wipe it as well. DO NOT use these commands in a production environment after it has been set up.

### 4. Installation Complete!

The backend should now be up and running! The following command should show a list of running containers, containing the containers used for the classifier backend.

    docker ps

If these containers are stopped, they can be started again using the `rebuild.sh` script.

Now, the frontend should be able to point to the public IP address of the machine running these docker containers, and communicate correctly. Frontend installation instructions can be found [here](?). ***DOM CAN U FILL IN THIS LINK PLS TY :D***

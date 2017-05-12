=========
Joint Box
=========

TBD

-----------
Development
-----------

First of all ensure you have all prerequisites:

1. Python >=3.5
2. Virtual Environment tool (virtualenv)

Then follow procedure described below to prepare environment for development:

1. Checkout git repository: ``git clone https://github.com/JointBox/jointbox.git``. Open terminal and change dir to the project root.
2. Create virtual environment: ``virtualenv virtualenv``. Activate it: ``source ./virtualenv/bin/activate``
3. Install development requirements: ``pip install -r requirements.txt``
4. Configure hooks: ``ln -s ./development/pre-commit-hook.sh .git/hooks/pre-commit``
5. Install application as a package in dev mode: ``cd src && ./setup.py sdist``
6. Validate your setup:
    * Check if ``jointbox`` and ``jointboxd`` executables are in the context
    * Run ``jointbox -h`` and insure that output doesn't contain exceptions

``````````````````````
Development procedures
``````````````````````

Ensure that all python sources contain license notice:
::
    ./development/copyright-update

In order to run suplementary services under docker you may use predefined docker-compose config:
::
    cd ./development/docker
    docker-compose up -d

Joint Box
=========

TBD

Development
-----------

1. Checkout git repository: ``git clone``. Open terminal and change dir to the project root.
2. Create virtual environment: `virtualenv virtualenv`. Activate it: `source ./virtualenv/bin/activate`
3. Install development requirements: `pip install -r requirements.txt`
4. Configure hooks: `ln -s ./development/pre-commit-hook.sh .git/hooks/pre-commit`
5. Install application as a package in dev mode: `cd src && ./setup.py sdist`
6. Validate your setup:
    * Check if `jointbox` and `jointboxd` executables are in the context
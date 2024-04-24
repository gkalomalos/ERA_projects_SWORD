.. docs documentation master file, created by
   sphinx-quickstart on Wed Apr 24 12:23:02 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to docs's documentation!
================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   costben
   entity
   exposure
   hazard
   impact
   scripts
   setup

Overview
--------
CLIMADERA is an Electron desktop application, featuring a Python-based backend to analyze climate data and calculate risks and a ReactJS frontend to provide a modern and intuitive user GUI.

Dependencies
------------
The application requires internet connection to fetch datasets from online sources. Also, it requires reading data from a .xlsx datasets files, which come bundled withing the application in the data directory. 

Logging
-------
The application logs important actions and errors, facilitating debugging and monitoring. The logs are stored locally in the `app.log` file.

Documentation
-------------
Developer documentation, including a detailed description of API endpoints and usage examples.

Before Opening a Pull Request
------------------------------
Before opening a pull request, please ensure the following steps are completed to maintain code and documentation quality:

1. **Run the Tests**:
   Ensure that all tests pass successfully to maintain application integrity.
   .. code-block:: sh

      python -m unittest backend/tests.py

2. **Comply with Linting Standards**:
   Your code should comply with established linting standards. The CI pipeline will fail if these standards are not met.
   .. code-block:: sh

      pylint backend/ --fail-under=8

3. **Update the Documentation**:
   If your changes affect how users interact with the application or add new features, please update the documentation accordingly. Once updates are made, build the documentation locally to ensure it compiles without errors.
   .. code-block:: sh

      sphinx-build -b html docs/ docs/_build/

   Review the generated HTML files in `docs/_build/` to verify your changes. Include the updated documentation files in your pull request.

4. **Upload Documentation Changes**:
   Along with your code changes, commit any updated documentation files to ensure the documentation remains current and useful for all users.
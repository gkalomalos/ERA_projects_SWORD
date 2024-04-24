Setup and Running
=================

For Developers
--------------

1. **Clone the Repository**:

   .. code-block:: sh

      git clone 
      cd 
      git checkout main

2. **Set Up a Virtual Environment** (optional but recommended):

   .. code-block:: sh

      # Using venv
      python -m venv venv
      source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

      # Or using Conda
      conda env create -f requirements/environment.yml
      conda activate climadera

3. **Install Dependencies** (if not using conda) :

   .. code-block:: sh

      pip install -r requirements/requirements.txt

4. **Create a `.env` File** based on the `.env.template` in the root directory.

5. **Start the Application Locally**:

   .. code-block:: sh

      [instructions]

# RISK WISE

## Overview

The “Enhancing Risk Assessments (ERA) for improved country risk financing strategies” project aims to provide government partners in Egypt and Thailand with a new generation of climate risk assessments for developing their climate change adaptation measures and, subsequently, their climate and disaster risk financing strategies. To this end, the ERA project will apply the Economics of Climate Change Adaptation (ECA) approach and will enhance the underlying risk assessment tool CLIMADA with the following new features:

1. Analyzing impacts of hazards on macroeconomic indicators (e.g., GDP, employment).
2. Analyzing the impact of hazards on non-economic impacts (e.g., access to health and education).
   Additionally, the project aims to enable the dynamic application of CLIMADA by partner institutions through an easy-to-use and accessible graphical user interface (GUI).

RISK WISE is a Graphical User Interface (GUI) for [CLIMADA](https://wcr.ethz.ch/research/climada.html). RISK WISE encompass CLIMADA’s full functionality, including the cost-benefit analyses of adaptation measures and new features developed within the ERA project, in order to enable local project partners to use CLIMADA independently.

## Dependencies and limitations

1. Physical limitations
   RISK WISE is a standalone, portable desktop application designed for ease of use. It is delivered as a self-contained folder containing all the necessary files, including an executable for starting the application. Double-clicking on this executable file will launch the application. No installation or special prerequisites are required. However, to ensure optimal performance, the following minimum system requirements are recommended:
   CPU: 1GHz dual core. Although RISK WISE is not heavily CPU-intensive, tasks like impact calculations, map rendering, and report generation may increase CPU usage.

- RAM: 8GB. This is crucial as the application uses Python’s Pandas library for data handling, performing in-memory analytics. When processing large datasets, such as a 10GB dataset, the application requires at least an equivalent amount of free memory. This is because Python performs many calculations in memory, which can significantly increase the overall memory requirement.
- Operating System: Microsoft Windows 10.
- Internet Connection: Essential for accessing data through CLIMADA’s API.

  These requirements are typical for a general-use laptop/PC.

2. CLIMADA API dependency
   RISK WISE frequently communicates with CLIMADA's API to fetch and validate datasets, among other tasks. API availability is crucial if the API is not accessible, significant functionality issues will arise. RISK WISE uses .hdf5 files for Exposure and Hazard data, obtainable from sources [ETH-Zurich Research Collection](https://www.research-collection.ethz.ch/) and [NASA’s Socioeconomic Data and Applications Center (sedac)](https://sedac.ciesin.columbia.edu/data/collection/gpw-v4/sets/browse). The application's Python backend fetches these files. In their absence, users can provide the necessary parameters, and the application will find, download, and store the datasets.

## Setup and Running the Application

### For Developers

1. **Clone the Repository**:
   ```sh
   git clone git@ath-git.swordgroup.lan:unu/climada-unu.git
   cd CLIMADA-UNU
   git checkout main
   ```
2. **Set Up a Virtual Environment** (optional but recommended):
   _Setting up a local environment is only required to test different parts of the application, for example using Jupyter notebooks to run custom climate scenarios. The application itself does not require a local environment to work, it comes bundled with the frozen climada_env conda environment which includes everything needed for the application to work._

   ```sh
   # Using venv
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

   # Or using Conda
   conda create --name riskwise python=3.11
   conda activate riskwise

   # Or using the prebuilt Conda environment
   conda env create -f requirements/environment.yml
   ```

3. **Install Dependencies for the backend**:

   ```sh
   pip install -r requirements/requirements.txt
   ```

4. **Install Dependencies for the frontend**:
   Before running the app locally, make sure Node.js is installed. Download and install Node.js from [the official Node.js website](https://nodejs.org/). After installing Node.js, navigate to the root directory of the app where the `package.json` file exists using your terminal or command prompt. Then, run the following command to install the dependencies:

   ```sh
   npm install
   ```

5. **Start the ReactJS frontend locally**:
   To start the ReactJS frontend locally, without the connection to the backend, use:

   ```sh
   npm start
   ```

6. **Start the RISK WISE application locally**:
   The application is bundled using [electron-builder](https://www.electron.build/). To start the full application locally, navigate to the root directory of the app and using your terminal or command prompt, run the following command:
   ```sh
   npm run start:electron
   ```

### Build a new executable

To create a new executable for the application, navigate to the root directory of the app and using your terminal or command prompt, run the following command:

```sh
npm run build
```

This will create a new executable at dist/[ version ]

## Logging

The application logs important actions and errors, facilitating debugging and monitoring. The logs are stored locally in the logs/app.log file.

## Documentation

Ensure you generate the updated documentation when pushing relevant code. Navigate to the root directory of the app and using your terminal or command prompt, run the following command:

```sh
sphinx-build -b html docs/ docs/_build
```

Developer documentation, including a detailed description of API endpoints and usage examples, can be found [here](https://ath-git.swordgroup.lan/unu/climada-unu/).

### Install LaTeX (for PDF Generation)

To generate PDFs, you'll need a LaTeX distribution. Follow these instructions based on your operating system:

1. **Windows**: Install [MiKTeX](https://miktex.org/download). During installation, ensure you select the option to install packages on-the-fly, so MiKTeX can automatically download any missing packages.

2. **macOS**: Install [MacTeX](https://tug.org/mactex/). After installation, make sure `pdflatex` is in your PATH by opening a terminal and running:
   ```sh
   which pdflatex
   ```

To generate a PDF version of the documentation, follow these steps:

1. **Build LaTeX Files**: Run the following command to create LaTeX files in the `docs/_build/latex` directory.

   ```sh
   sphinx-build -b latex docs/ docs/_build/latex

   ```

2. **Navigate to LaTeX Directory**:

   ```sh
   cd docs/_build/latex

   ```

3. **Generate PDF with pdflatex**:
   Run the command below, which compiles the tex file to PDF format. If needed, run this command multiple times to ensure cross-references resolve properly.

   ```sh
   pdflatex riskwise.tex
   ```

## Before Opening a Pull Request

Ensure you run the tests and comply with the linting standards before opening a pull request:

- Run tests:

```sh
# Navigate to the backend directory
cd ./backend
# Execute tests
python -m unittest tests/test_api.py

# Navigate to the frontend directory
cd ./src
# Execute tests
npx eslint .
```

- Check linting:

```sh
# Navigate to the backend directory
cd ./backend
# Run pylint
pylint --exit-zero --fail-under=9 .
```

Failure to meet the test coverage and linting standards will result in CI pipeline failures.

## Tag new version

Upon merging a feature branch to the main branch, make sure you tag the new version of the application accordingly.

```sh
git tag -a <version> -m "<tag_title>" -m "tag_comments"

# Example
git tag -a v0.5.5 -m "RISK WISE version 0.5.5" -m "
>>
>> - Refactor run scenario process to increase performance and readability.
>> - Modify information shown on Hazard and Risk maps.
>> - Modify the run era scenario process with proper entity files.
>> - Fix minor issues when extracting information out of hazard .mat and .tif files.
>> "
```

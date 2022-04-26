# Job Recommendation Engine
DS 4300 Final Project: Job Recommendation Engine

Application Demo Video: https://www.youtube.com/watch?v=q8XvdC7n5bs

## Instructions for replicating our project



### 1. Download, install, and configure Neo4j
Instructions to download and install Neo4j are available on the DS 4300 Piazza page.

Please copy the data from the data directory in this repository to your 'import' folder within neo4j. This allows data to be agnostic and accessible through our simple Cypher data import queries. 

Please ensure your neo4j.conf file, found in the conf folder of your neo4j directory, has the following enabled:
- dbms.security.procedures.allowlist=apoc.coll.* , apoc.load* , apoc.convert*
    - Ignore spaces between commas
    - This allows apoc functions to work
- dbms.directories.plugins=plugins
    - Also ensure the apoc=4.4.0.4-all.jar is within your plugins folder
- dbms.directories.import=import
    - This directs Cypher to import data from here
- dbms.security.procedures.whitelist=apoc.*

All other required configurations should already be enabled by default. If issues persist in connecting to Neo4j, please contact us.

### 2. Dataset
Code generating dataset: create_employee_job_data.ipynb. This code may be run to generate the data, which will be populated in the data directory. However, we strongly recommend using the data we have  already made available in the data directory since it is time consuming to generate. Data must then be moved into the import directory of your neo4j folder.

### 3. Building Neo4j model
First connect to neo4j by entering 'neo4j start' in your terminal window, then launch the server. Load the scripts found in the 'Neo4j Script - Importing Data and Creating Models.pdf' file within the neo4j_scripts directory. The employee and job datasets are loaded first (nodes), followed by the join table datasets (edges).

### 4. Optional: Test our Cypher Queries
Run the queries found in the 'Neo4j Script - Job Recommendations Algorithms Queries.pdf' file within the neo4j_scripts directory.

### 5. Running the Command Line /Python Interface Application
1. In your terminal, enter 'python run.py'
2. Enter your neo4j user and password
3. Interact with application
Please review the linked  video at the top of this file for a demo on how this application works and is designed. 

#### Overview of Python files
1. run.py: launches the login and interface
2. job_recommendation_engine_interface.py: landing page for interface application, allows user to choose employee
3. findBestFittingJobs.py: Pertains to Cypher query finding jobs for employees based on matching characteristics
4. findEmployeesJobSearch.py: Pertains to Cypher query finding employees with similar job search history
5. findJobsConnectionHistory.py: Pertains to Cypher query finding jobs based on job history of connections
6. viewHighJobHoldingEmployeeConnections.py: Pertains to Cypher query finding employees connected to those with the most popularly held jobs
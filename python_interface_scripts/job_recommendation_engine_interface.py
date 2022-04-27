from neo4j import GraphDatabase
import pandas as pd
from findBestFittingJobs import findBestFittingJobs
from findEmployeesJobSearch import findEmployeesJobSearch
from findJobsConnectionHistory import findJobsConnectionHistory
from viewHighJobHoldingEmployeeConnections import viewHighJobHoldingEmployeeConnections
from SimilarEmployeesJobRecommendation import SimilarEmployeesJobRecommendation
import os

# Properties of jobs and employees used as keys for Neo4j node objects returned
jobProperties = ["Job ID","Job Title","Location","Degree","Technical Skills","Preferred Technical Skills"]
employeeProperties = ["Employee ID", "Degree", "Location", "Technical Skills"]


# Utility function to create a line separator
def line_separator(mark, count):
    line = ""
    for x in range(count):
        line += mark
    return line


# Message printed when exiting application
exitMsg = line_separator('.', 65) + "\n\nThank you for using the Job Recommendation Engine. \nBest of luck on your search!\n"

# Login validation functionality
def login():
    url = "neo4j://localhost:7687"
    validated = False
    global driver
    # While the user and password has not been input, prompt user to enter credentials
    # to connect to Neo4j database
    while(not validated):
        try:
            user = input("Enter Neo4j user: ")
            password = input("Enter Neo4j password: ")
            # user = "neo4j"
            # password = "neo4jj"
            driver = GraphDatabase.driver(url, auth=(user, password))
            validated = True
        except Exception as e:
            print("Please enter correct user or password\n")

# Function to take in user's input for employee ID and validate 
def inputAndValidateEmployee():
	global employeeID
	employeeIDNotValidated = True

	# Get employee info
	while(employeeIDNotValidated):
		employeeID = input("Please enter your employee ID (0-499) or . to exit: ")
		if(employeeID == "."):
			print(exitMsg)
			os._exit(0)
		if(int(employeeID) in range(0, 500)):
			employeeIDNotValidated = False

	# Return employee node information
	try:
		with driver.session() as session:
			result = session.read_transaction(getEmployeeInfo, employeeID)
			for record in result:
				print("\nWelcome, employee " + record.get("Employee ID"))
				print("Degree: " + record.get("Degree"))
				print("Location: " + record.get("Location"))
				print("Technical Skills: "+ record.get("Technical Skills")+"\n")
	except Exception as e:
		print("Could not retrieve employee information at this time")


# Function to get employee node from Neo4j database
def getEmployeeInfo(tx, employeeID):
	employee = []
	query = '''
		MATCH (Employee {employeeID: $employeeID})
		RETURN Employee as employee
	'''
	result = tx.run(query, employeeID = employeeID)
	for record in result:
		employee.append({"Employee ID": record['employee']['employeeID'], "Location": record['employee']['location'],
				"Degree": record['employee']['degree'], "Technical Skills": record['employee']['technicalSkills']})
	return employee

# Direct user to specified Cypher query 
def main():
	actionValidated = False
	print("\n\n" + line_separator('~', 65) + "\n\nWelcome to the Job Recommendation Engine!\n" +
	      "Our engine utilizes a highly-connected network of jobs and employees to best connect you with.\n ")

	# First get an employee
	inputAndValidateEmployee()

	# Allow user to choose from the following options
	print(line_separator('~', 65) + "\n\nChoose from the following options: \n")
	print("(0) Exit Application\n\n" + 
		"(1) Find jobs that best fit my profile\n" + 
		"(2) Find employees to work with on the job search\n" + 
		"(3) Find jobs based on my connections' job histories\n" +
		"(4) View the employees connected to those at the most popular jobs\n\n" + 
	        "(5) Find jobs that have been applied by Top 10 similar employees based on profiles\n" +
		"(6) Restart\n")

	# Take in a number 0-6 representing exiting an application or a Cypher query
	while(not actionValidated):
		try:
			numAction = input("Please enter a number (0-6): ")
			numAction = int(numAction)
			if(not isinstance(int(numAction), int)):
				print("Please enter a number")
			else:
				if(numAction > 6 or numAction < 0):
					print("Please enter a number 0-6\n")
				elif(numAction == 0):
					print(exitMsg);
					actionValidated = True
					os._exit(0)
				elif(numAction == 1):
					findBestFittingJobs(driver, employeeID)
					actionValidated = True
				elif(numAction == 2):
					findEmployeesJobSearch(driver, employeeID)
					actionValidated = True
				elif(numAction == 3):
					findJobsConnectionHistory(driver, employeeID)
					actionValidated = True
				elif(numAction == 4):
					viewHighJobHoldingEmployeeConnections(driver)
					actionValidated = True
				elif(numAction == 5):
					SimilarEmployeesJobRecommendation(driver, employeeID)
					actionValidated = True
				elif(numAction == 6):
					main()
					actionValidated = True
				else:
					print("Please enter a number 0-6\n")
					actionValidated = True
		except Exception as e:
			print(e)




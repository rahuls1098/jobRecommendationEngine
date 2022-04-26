from neo4j import GraphDatabase
import job_recommendation_engine_interface 
import pandas as pd
import os

# Properties of employees used as keys for Neo4j node objects returned
employeeProperties = ["Employee ID", "Degree", "Location", "Technical Skills"]

 # Utility function to create a line separator
def line_separator(mark, count):
    line = ""
    for x in range(count):
        line += mark
    return line

# Function to retrieve employees
def getEmployeesJobSearch(tx, employeeID,percentage):

    # create a list to record all the recommended employees
	employees = []
    # run neo4j query and get the results(all the recommended employees) from the driver
    # Employee ID and percentage are user-input variables
	result = tx.run('''
			match (e0: Employee {employeeID:$employeeID})-[r0:SEARCHED_FOR]->(:Job)<-[r1:SEARCHED_FOR]-(e1: Employee)
			match
			(e0)-[:SEARCHED_FOR]->(j0:Job),
			(e1)-[:SEARCHED_FOR]->(j1:Job)
			with
			e0,e1,
			count (distinct j0) as j0Count, count (distinct j1) as j1Count
			match (e0)-[:SEARCHED_FOR]->(j:Job)<-[:SEARCHED_FOR]-(e1)
			with
			e0,e1,
			j0Count, j1Count, count (j) as commonJobSearchedCount
			where
			id(e0) < id(e1) and  
			commonJobSearchedCount / $percentage >= j1Count
			return e1 as employees
			order by j0Count, j1Count'''
			, employeeID=employeeID, percentage=percentage)
    
    # each job node returned from the driver is restructured as a dictionary,where the keys are this employee node's properties and values
    # are the corresponding values of employee properties
	for record in result:
		employees.append({"Employee ID": record["employees"]["employeeID"],
		"Location": record["employees"]["location"],"Degree": record["employees"]["degree"],
		"Technical Skills": record["employees"]["technicalSkills"]})
	return employees


# Match employee to closest matching employees based on percentage similarity of job search histories
# Allows user to select how many results (employees) are returned
def findEmployeesJobSearch(driver, employeeID):
	percentageValidated = False
	numJobValidated = False
	query = ""
	print(line_separator("~", 65) + "\n\nLet's connect you to the employees with the most similar job search history, employee " + str(employeeID) + ".\n")
	

	# Validate percentage input
	while(not percentageValidated):
		try:
			percentage = input("(0) Main Menu\n\n" + 
						"Enter desired percentage similarity for job search history (1-100): ")

			percentage = int(percentage)/100
			if(not isinstance(percentage, float)):
				print("Please enter a number\n")
			else:
				if(percentage > 100 or percentage < 0):
					print("Please enter a percentage 1-100\n")
				elif(percentage == 0):
					job_recommendation_engine_interface.main();
					percentageValidated = True
				else:
			
					# Call the function to get employees
					with driver.session() as session:
						result = session.read_transaction(getEmployeesJobSearch, employeeID, percentage)
						print(line_separator("~", 65))

						if(len(result) == 0):
							print("No matching employees found")
						else:
							for record in result:
								print("\nRecommended Colleague: \n")
								for employeeProperty in employeeProperties:
									print(employeeProperty + ": " + str(record.get(employeeProperty)))
					driver.close()
					percentageValidated = True
					print(line_separator("~", 65))
					restart = input("Main Menu [0] or repeat this search [1]: ")
					validated = False
					while(not validated):
						if(int(restart) == 0):
							job_recommendation_engine_interface.main()
							validated = True
						elif(int(restart) == 1):
							findEmployeesJobSearch(driver, employeeID)
							validated = True
				
		except Exception as e:
			print(e)

		
		
			

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
def getHighJobHoldingEmployeeConnections(tx,numEmployees):

    # create a list to record all the recommended employees
	employees = []
    # run neo4j query and get the results(all the recommended employees) from the driver
    # Number of employees returned is based on number specified by user
	result = tx.run('''
				call{match (e:Employee)-[r:WORKED_AT]->(j:Job)
				with e as employee, j as jobs, count(r) as associations
				order by associations desc limit 5
				return collect(employee) as experiencedEmployees}
				 
				match (e0: Employee)-[:CONNECTED_TO]->(e1:Employee)
				where e0 in experiencedEmployees
				return e1 AS employees LIMIT $numEmployees
			'''
			, numEmployees=numEmployees)
    
    # each job node returned from the driver is restructured as a dictionary,where the keys are this employee node's properties and values
    # are the corresponding values of employee properties
	for record in result:
		employees.append({"Employee ID": record["employees"]["employeeID"],
		"Location": record["employees"]["location"],"Degree": record["employees"]["degree"],
		"Technical Skills": record["employees"]["technicalSkills"]})
	return employees


# Match employee to best fitting jobs
# Allows user to select how many results (jobs) are returned
def viewHighJobHoldingEmployeeConnections(driver):
	numEmployeesValidated = False
	query = ""
	print(line_separator("~", 65) + "\n\nHere, you can see which employees are connected to the most popularly held jobs.\n")
	
	# Validate number of employees input
	while(not numEmployeesValidated):
		try:
			numEmployees = input("(0) Main Menu\n\n" + 
						"Enter the number of employees to return (1-499): ")
			numEmployees = int(numEmployees)
			if(not isinstance(numEmployees, int)):
				print("Please enter a number\n")
			else:
				if(numEmployees > 499 or numEmployees < 0):
					print("Please enter a number 1-499\n")
				elif(numEmployees == 0):
					job_recommendation_engine_interface.main();
					numEmployeesValidated = True
				else:
					with driver.session() as session:
						result = session.read_transaction(getHighJobHoldingEmployeeConnections, numEmployees)
						print(line_separator("~", 65))

						if(len(result) == 0):
							print("No matching employees found")
						else:
							for record in result:
								print("\nRecommended Colleague: \n")
								for employeeProperty in employeeProperties:
									print(employeeProperty + ": " + str(record.get(employeeProperty)))
					driver.close()
					numEmployeesValidated = True
					print(line_separator("~", 65))
					restart = input("Main Menu [0] or repeat this search [1]: ")
					validated = False
					while(not validated):
						if(int(restart) == 0):
							job_recommendation_engine_interface.main()
							validated = True
						elif(int(restart) == 1):
							viewHighJobHoldingEmployeeConnections(driver)
							validated = True
				
		except Exception as e:
			print(e)

		
		
			

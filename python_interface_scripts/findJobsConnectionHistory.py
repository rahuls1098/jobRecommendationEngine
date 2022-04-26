from neo4j import GraphDatabase
import job_recommendation_engine_interface 
import pandas as pd
import os

# Properties of jobs used as keys for Neo4j node objects returned
jobProperties = ["Job ID","Job Title","Location","Degree","Technical Skills","Preferred Technical Skills"]

 # Utility function to create a line separator
def line_separator(mark, count):
    line = ""
    for x in range(count):
        line += mark
    return line


# Function to retrieve jobs based  
def getJobsConnectionHistory(tx, employeeID,numJobs):

    # create a list to record all the recommended jobs
    jobs = []
    # run neo4j query and get the results(all the recommended jobs) from the driver
    # User-input employeeID and number of jobs returned
    result = tx.run(
    	"CALL {MATCH (e0: Employee{employeeID:$employeeID})-[r:CONNECTED_TO]->(e1:Employee) " 
                    "WITH toFloat(r.score) AS scores, e1 AS knownEmployees "  
                    "ORDER by scores desc LIMIT 5 "  
                    "RETURN collect(knownEmployees) AS knownEmployees} " 
                    "MATCH (e:Employee)-[r:WORKED_AT]->(j:Job) " 
                    "WHERE e in knownEmployees " 
                    "RETURN j AS jobs LIMIT $numJobs"
    	, employeeID = employeeID, numJobs=numJobs)
    
    # each job node returned from the driver is restructured as a dictionary,where the keys are this job node's properties and values
    # are the corresponding values of job properties
    for record in result:
        jobs.append({"Job ID": record["jobs"]["jobID"], "Job Title": record["jobs"]["jobTitle"],
             "Location": record["jobs"]["location"],"Degree": record["jobs"]["degree"],
             "Technical Skills": record["jobs"]["technicalSkills"],
             "Preferred Technical Skills": record["jobs"]["preferredSkills"]})
    return jobs


# Match employee to best fitting jobs
# Allows user to select how many results (jobs) are returned
def findJobsConnectionHistory(driver, employeeID):
	numJobValidated = False
	query = ""
	print(line_separator("~", 65) + "\n\nLet's connect you, employee " + str(employeeID) + ", to jobs" +
		" based on those previously\nheld by employees (top 5) ranked by their connectedness score to you. \n" +
		"Connectedness score factors in similarities in location and jobs held.\n")

	# Validate number input
	while(not numJobValidated):
		try:
			numJobs = input("(0) Main Menu\n\n" +
				"Enter the number of jobs to return (1-20): ")
			numJobs = int(numJobs)
			if(not isinstance(int(numJobs), int)):
				print("Please enter a number\n")
			else:
				if(numJobs > 20 or numJobs < 0):
					print("Please enter a number 1-20\n")
				
				else:
					# Call upon driver ot get jobs
					with driver.session() as session:
						result = session.read_transaction(getJobsConnectionHistory, employeeID, numJobs)
						print(line_separator("~", 65))
						if(len(result) == 0):
							print("No matching jobs found")
						else:
							for record in result:
								print("\nRecommended Job: \n")
								for jobProperty in jobProperties:
									print(jobProperty + ": " + str(record.get(jobProperty)))
					driver.close()
					numJobValidated = True
					print(line_separator("~", 65))
					restart = input("Main Menu [0] or repeat this search [1]: ")
					validated = False
					while(not validated):
						if(int(restart) == 0):
							job_recommendation_engine_interface.main()
							validated = True
						elif(int(restart) == 1):
							findJobsConnectionHistory(driver, employeeID)
							validated = True					
		except Exception as e:
			print(e)

				
					

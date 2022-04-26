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


# Function to get the jobs that best match the employee's properties
def getBestFittingJobs(tx, employeeID, query,numJobs):

    # create a list to record all the recommended jobs
    jobs = []
    # run neo4j query and get the results(all the recommended jobs) from the driver
    # employee ID and number of jobs retrieved are user-input variables
    result = tx.run("call{Match (e0: Employee {employeeID:$employeeID})\n" + query + "\nORDER BY score DESC LIMIT {}".format(str(numJobs)), employeeID = employeeID)
    
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
def findBestFittingJobs(driver, employeeID):
	jobCriteriaValidated = False
	numJobValidated = False
	query = ""
	print(line_separator("~", 65) + "\n\nLet's find the best jobs for you, employee " + str(employeeID) + ".\n" +
		"Please select how you would like to be matched: \n")

	print("(0) Main Menu\n\n" + 
		"(1) By technical skills (more weight given to required skills)\n" + 
		"(2) By technical skills (no extra weight for required skills)\n" + 
		"(3) By technical skills (weighted) and degree\n" +
		"(4) By technical skills (weighted), degree, and location\n")

	# Get user input to choose which criteria to filter jobs by
	while(not jobCriteriaValidated):
		try:
			numAction = input("Please enter a number (0-4): ")
			numAction = int(numAction)
			if(not isinstance(int(numAction), int)):
				print("Please enter a number")
			else:
				if(numAction > 4 or numAction < 0):
					print("Please enter a number 0-4")
				elif(numAction == 0):
					job_recommendation_engine_interface.main();
					jobCriteriaValidated = True
				# If input is valid, get the appropriate query corresponding to the user's choice
				elif(numAction == 1):
					
					query = '''
						
						Return apoc.convert.fromJsonList(e0.technicalSkills) as skills, e0.location as loc, e0.degree as deg}
						Match (j: Job) 
						With  j as jobs, size(apoc.coll.intersection(skills, apoc.convert.fromJsonList(j.technicalSkills)))*2 + size(apoc.coll.intersection(skills, apoc.convert.fromJsonList(j.preferredSkills))) as score
						Return jobs
						
					'''

					jobCriteriaValidated = True
				elif(numAction == 2):
					query = '''

						Return apoc.convert.fromJsonList(e0.technicalSkills) as skills, e0.location as loc, e0.degree as deg}
						Match (j: Job) 
						With  j as jobs, size(apoc.coll.intersection(skills, apoc.convert.fromJsonList(j.technicalSkills))) as score
						Return jobs
						
					'''

					jobCriteriaValidated = True
				elif(numAction == 3):
					
					query = '''
					
						Return apoc.convert.fromJsonList(e0.technicalSkills) as skills, e0.location as loc, e0.degree as deg}
						Match (j: Job) 
						With  j as jobs, size(apoc.coll.intersection(skills, apoc.convert.fromJsonList(j.technicalSkills)))*2 + size(apoc.coll.intersection(skills, apoc.convert.fromJsonList(j.preferredSkills))) as score
						Where jobs.degree = deg
						Return jobs
					'''
					jobCriteriaValidated = True
				elif(numAction == 4):
					query = '''
				
						Return apoc.convert.fromJsonList(e0.technicalSkills) as skills, e0.location as loc, e0.degree as deg}
						Match (j: Job) 
						With  j as jobs, size(apoc.coll.intersection(skills, apoc.convert.fromJsonList(j.technicalSkills)))*2 + size(apoc.coll.intersection(skills, apoc.convert.fromJsonList(j.preferredSkills))) as score
						Where jobs.location = loc  and jobs.degree = deg
						Return jobs
						
					'''
					jobCriteriaValidated = True

				else:
					print("Please enter a number 0-4\n")
					jobCriteriaValidated = True
		except Exception as e:
			print(e)

		# Validate the number of jobs input by the user
		while(not numJobValidated):
			numJobs = input("Enter the number of jobs to return (1-20): ")
			numJobs = int(numJobs)
			if(not isinstance(numJobs, int)):
				print("Please enter a number\n")
			elif(numJobs > 20 or numJobs < 1):
				print("Please enter a number between 1-20: \n")
			else:
				with driver.session() as session:
					result = session.read_transaction(getBestFittingJobs, employeeID, query, numJobs)
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
						findBestFittingJobs(driver, employeeID)
						validated = True
					

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 02:38:33 2022

@author: liqi
"""

from neo4j import GraphDatabase
import job_recommendation_engine_interface 
import pandas as pd
import os

# Properties of employees used as keys for Neo4j node objects returned
employeeProperties = ["Employee ID", "Degree", "Location", "Technical Skills"]

# Properties of jobs used as keys for Neo4j node objects returned
jobProperties = ["Job ID","Job Title","Location","Degree","Technical Skills","Preferred Technical Skills"]

 # Utility function to create a line separator
def line_separator(mark, count):
    line = ""
    for x in range(count):
        line += mark
    return line


# Function to retrieve jobs applied by Top 10 similar employees based on profiles
def getAppliedJobsOfTop10SimilarEmplyees(tx,employeeID):

    # create a list to record all the recommended jobs
	jobs = []
    # run neo4j query and get the results(all the recommended jobs) from the driver
	result = tx.run('''
				call {
                call{match (e0: Employee {employeeID:$employeeID}),(e0:Employee)-[r:APPLIED_TO]->(j0:Job)
                return apoc.convert.fromJsonList(e0.technicalSkills) as skills, e0.location as loc, e0.degree as deg, e0.employeeID as id, collect(j0) as appliedjobs}
                match (e1: Employee) 
                where e1.employeeID <> id and e1.location = loc and e1.degree = deg
                with  e1, size(apoc.coll.intersection(skills, apoc.convert.fromJsonList(e1.technicalSkills))) as numskills,appliedjobs
                order by numskills DESC limit 10
                return collect(e1) as similarEmployee,appliedjobs
                }
                match (e:Employee)-[r:APPLIED_TO]->(j:Job)
                where e in similarEmployee and not j in appliedjobs
                return j
			'''
			, employeeID = employeeID)
    
    # each job node returned from the driver is restructured as a dictionary,where the keys are this job node's properties and values
    # are the corresponding values of job properties
	for record in result:
		jobs.append({"Job ID": record["jobs"]["jobID"], "Job Title": record["jobs"]["jobTitle"],
             "Location": record["jobs"]["location"],"Degree": record["jobs"]["degree"],
             "Technical Skills": record["jobs"]["technicalSkills"],
             "Preferred Technical Skills": record["jobs"]["preferredSkills"]})
	return jobs


# Match jobs applied by top 10 most similarest employees based on their profiles
# Allows user to input their employee ID number
def SimilarEmployeesJobRecommendation(driver, employeeID):
	employeeIDValidated = False
	print(line_separator("~", 65) + "\n\nLet's show you some jobs applied by the employees with the most similar profiles, employee " + str(employeeID) + ".\n")
	

	# Validate employee ID input
	while(not employeeIDValidated):
		try:
			employeeID = input("(0) Main Menu\n\n" + 
						"Enter one employee ID to get jobs that have been applied by your most similar employees: ")

			if(not isinstance(employeeID, int)):
				print("Please enter a integer\n")
			else:
				if(employeeID < 1 or employeeID > 500):
					print("Please enter an ID 1-500\n")
# 				elif(percentage == 0):
# 					job_recommendation_engine_interface.main();
# 					percentageValidated = True
				else:
			
					# Call the function to get jobs
					with driver.session() as session:
						result = session.read_transaction(getAppliedJobsOfTop10SimilarEmplyees, employeeID)
						print(line_separator("~", 65))

						if(len(result) == 0):
							print("No matching jobs found")
						else:
							for record in result:
								print("\nRecommended Jobs: \n")
								for jobProperty in jobProperties:
									print(jobProperty + ": " + str(record.get(jobProperty)))
					driver.close()
					employeeIDValidated = True
					print(line_separator("~", 65))
					restart = input("Main Menu [0] or repeat this search [1]: ")
					validated = False
					while(not validated):
						if(int(restart) == 0):
							job_recommendation_engine_interface.main()
							validated = True
						elif(int(restart) == 1):
							SimilarEmployeesJobRecommendation(driver, employeeID)
							validated = True
				
		except Exception as e:
			print(e)

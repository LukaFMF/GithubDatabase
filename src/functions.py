def extractDate(timestamp):
	"""
	Extracts the date in form of YYYY-MM-DD from ISO 8601 timestamp
	"""
	return timestamp[:10]

def sanitizeStr(s):
	"""
	Converts special characters in a string to their character representation
	(newline = \n)
	"""
	return repr(s)[1:-1] # repr returns string in quotes, so we need remove them


def getInputYN(question):
	"""
	Asks user a question to which he can answer with y/Y or n/N
	"""
	endChoice = False
	while True:
		try:
			choice = input(f"{question} (Y/N) ")
			if choice == "y" or choice == "Y":
				endChoice = True
				break
			elif choice == "n" or choice == "N":
				break
			else:
				raise Exception()
		except:
			print("Invalid input! Try again...")

	return endChoice

def emptyFile(path):
	"""
	Empties file at path, if file doesnt exist creates empty file
	"""
	open(path,"w").close()

import csv

# define csv file structure
csvDialectName = "githubDB"
csv.register_dialect(csvDialectName,delimiter = ";",
doublequote = False,quoting = csv.QUOTE_NONNUMERIC,
escapechar="\\",strict = True)

def writeCsvData(filename,objData,mode):
	"""
	Writes data to csv file, given by filename
	"""
	with open(f"data/{filename}",mode,newline = "",encoding = "utf8") as file:
		writer = csv.writer(file,dialect = csvDialectName)
		
		# convert objects to tuples
		writer.writerows([el.get() for el in objData])

def readCsvData(filename,classRef):
	"""
	Reads data from csv file and converts it to list of objects
	"""
	with open(f"data/{filename}","r",newline = "",encoding = "utf8") as file:
		reader = csv.reader(file,dialect = csvDialectName)
		
		objData = []
		for row in reader:
			# non quoted data is read as floats, need to convert it to int
			convertedToInt = (int(col) if isinstance(col,float) else col for col in row)

			# empty stings represent None 
			convertedNones = (None if isinstance(col,str) and len(col) == 0 else col 
			for col in convertedToInt)

			# apply tuple elements as constructor arguments
			objData.append(classRef(*convertedNones))  
		return objData


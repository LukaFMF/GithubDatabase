def sanitizeStr(s):
	"""
	Converts special characters in a string to their character representation
	(newline = \n)
	"""
	return repr(s)[1:-1] # repr returns string in quotes, so we need remove them

def extractDate(timestamp):
	"""
	Extracts the date in form of YYYY-MM-DD from ISO 8601 timestamp
	"""
	return timestamp[:10]

def emptyFile(path):
	"""
	Empties file at path, if file doesnt exist creates empty file
	"""
	open(path,"w").close()

import csv

# write dialect
csvDialectWrite = "githubDBwrite"
csv.register_dialect(csvDialectWrite,delimiter = ";",
doublequote = True,quoting = csv.QUOTE_NONNUMERIC,
escapechar = "\\",strict = True)

def writeCsvData(filename,objData,mode):
	"""
	Writes data to csv file, given by filename
	"""
	with open(f"data/{filename}",mode,newline = "",encoding = "utf8") as file:
		writer = csv.writer(file,dialect = csvDialectWrite)
		
		# convert objects to tuples
		writer.writerows([el.get() for el in objData])

# read dialect
csvDialectRead = "githubDBread"
csv.register_dialect(csvDialectRead,delimiter = ";",
doublequote = True,quoting = csv.QUOTE_NONNUMERIC,
strict = True)

def readCsvData(filename,classRef):
	"""
	Reads data from csv file and converts it to list of objects
	"""
	with open(f"data/{filename}","r",newline = "",encoding = "utf8") as file:
		reader = csv.reader(file,dialect = csvDialectRead)
		
		objData = []
		for row in reader:
			# non quoted data is read as floats, need to convert it to int
			convertedToInt = (int(col) if isinstance(col,float) else col for col in row)

			# empty stings represent None 
			convertedNones = (None if isinstance(col,str) and len(col) == 0 else col 
			for col in convertedToInt)

			# replace "\n" with new lines, and other such things 
			replacedN = (col.replace("\\n","\n") if isinstance(col,str) else col 
			for col in convertedNones)

			replacedR = (col.replace("\\r","\r") if isinstance(col,str) else col 
			for col in replacedN)

			replacedT = (col.replace("\\t","\t") if isinstance(col,str) else col 
			for col in replacedR)

			# apply tuple elements as constructor arguments
			objData.append(classRef(*replacedT))  
		return objData


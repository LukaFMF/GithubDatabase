import model

def textInterface():

	while True:
		print("1) fadfda")
		print("2) faaf")
		print("3) Quit")

		try:
			choice = int(input("Izbira: "))
			if choice < 1 or choice > 3:
				raise Exception()


			if choice == 1:
				print("nic")
			elif choice == 2:
				print("4343")
			elif choice == 3:
				print("'dijo")
				break
		except:
			print("Neveljaven vnos, kolega!")


try:
	textInterface()
finally:
	model.conn.close()

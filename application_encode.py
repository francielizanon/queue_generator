from application import Application

#returns a letter that defines an application, we'll use it to have
#a short representation of queues as a sequence of letters
def encode_application(app):
	if app.app == "BTIO":
		if app.nodes == 32:
			return "A"
		elif app.nodes == 64:
			return "B"
		else:
			assert False
	elif app.app == "IOR":
		if app.nodes == 16:
			return "C"
		elif app.nodes == 64:
			return "D"
		else:
			assert False
	elif app.app == "MADBENCH2":
		return "E"
	elif app.app == "S3ASIM":
		return "F"
	elif app.app == "S3D-IO":
		return "G"
	else:
		assert False

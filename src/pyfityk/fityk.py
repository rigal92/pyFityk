import fityk 

def read_map(file, header = "jasko"):
	if header == "jasko":
		f = open(file)
		_ = [next(f) for i in range(13)]
		print(_) 
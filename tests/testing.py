import pyfityk.io as ftk

def main(filename):
	ftk.read_map(filename)



if __name__ == '__main__':
	filename = "data/Raman/map2x2.txt"
	main(filename)
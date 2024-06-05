import pyfityk

def main(filename):
	pyfityk.read_map(filename)



if __name__ == '__main__':
	filename = "../data/map2x2.txt"
	main(filename)
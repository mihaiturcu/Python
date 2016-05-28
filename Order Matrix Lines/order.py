import sys


def bubbleSort(alist):
	"Applies bubbleSort on list and returns it"
	for passnum in range(len(alist)-1,0,-1):
		for i in range(passnum):
			if alist[i]>alist[i+1]:
				temp = alist[i]
				alist[i] = alist[i+1]
				alist[i+1] = temp
	return alist

def read_matrix(filedescriptor):
	"Read matrix, construct list of lists and return constructed object"
	f = open (filedescriptor,'r')
	matrix = [ map(int,line.split(',')) for line in f ]
	return matrix;

def reorder_matrix(matrix):
	"Reorders matrix and returns matrix"
	for line in matrix:
		line = bubbleSort(line)
	return matrix

def nice_print(matrix):
	"This method neatly formats the matrix"
	for line in matrix:
		print line







try:
	matrix = read_matrix(sys.argv[1])
	print matrix;
	print "-----------";
#	print bubbleSort(matrix[0])
	newmatrix = reorder_matrix(matrix)
	nice_print(newmatrix)

except Exception, e:
	print "failed deeply \n-----------\n"
	print e

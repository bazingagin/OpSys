import sys
import queue

class Process:
	def __init__(self,pid,mem,arr_time,run_time):
		self.pid = pid
		self.mem = int(mem)
		self.arr_time = int(arr_time)
		self.run_time = int(run_time)
		self.leave_time = self.arr_time+self.run_time
	def __eq__(self,other):
		return ((self.arr_time,self.leave_time,self.pid,self.mem)==(other.arr_time,other.leave_time,other.pid,other.mem))
	def __ne__(self,other):
		return ((self.arr_time,self.leave_time,self.pid,self.mem)!=(other.arr_time,other.leave_time,other.pid,other.mem))
	def __lt__(self,other):
		return ((self.arr_time,self.leave_time,self.pid)<(other.arr_time,other.leave_time,other.pid))
	def __le__(self,other):
		return ((self.arr_time,self.leave_time,self.pid)<=(other.arr_time,other.leave_time,other.pid))
	def __gt(self,other):
		return ((self.arr_time,self.leave_time,self.pid)>(other.arr_time,other.leave_time,other.pid))
	def __ge__(self,other):
		return ((self.arr_time,self.leave_time,self.pid)>=(other.arr_time,other.leave_time,other.pid))
	def __repr__(self):
		return '%s: %d %d %d'%(self.pid,self.mem,self.arr_time,self.leave_time)


def read_file(fn):
	q = queue.PriorityQueue()
	f = open(fn)
	plist = []
	for line in f:
		line = line.strip()
		if line and not line.startswith('#'):
			ele = line.split()
			rest = ele[2:]
			for r in rest:
				arr = r.split('/')[0]
				run = r.split('/')[1]
				p = Process(ele[0],ele[1],arr,run)
				q.put(p)
	return q

def print_memory(m):
	print('='*32)
	for i in range(8):
		for j in range(32):
			print(m[i*32+j],end='')
		print()
	print('='*32)


# def worst_fit()


# def non_contiguous()

def main(argv):
	if len(argv)!=2:
		sys.exit("ERROR: Invalid arguments\nUSAGE: ./a.oult <input-file>\n")
	#initialize memory
	memory=[]
	for i in range(32*8):
		memory.append('.')
	#read file
	fn = argv[1]
	q = read_file(fn)
	while not q.empty():
		item = q.get()
		print(item)



if __name__=="__main__":
	main(sys.argv)
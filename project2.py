import sys
import queue
from collections import OrderedDict

class Process:
	def __init__(self,pid,mem,arr_time,run_time):
		self.pid = pid
		self.mem = int(mem)
		self.arr_time = int(arr_time)
		self.run_time = int(run_time)
		self.leave_time = self.arr_time+self.run_time
	def __eq__(self,other):
		return ((self.arr_time,self.pid)==(other.arr_time,other.pid))
	#def __ne__(self,other):
	#	return ((self.arr_time,self.leave_time,self.pid,self.mem)!=(other.arr_time,other.leave_time,other.pid,other.mem))
	def __lt__(self,other):
		return ((self.arr_time,self.pid)<(other.arr_time,other.pid))
	def __le__(self,other):
		return ((self.arr_time,self.pid)<=(other.arr_time,other.pid))
	def __gt(self,other):
		return ((self.arr_time,self.pid)>(other.arr_time,other.pid))
	def __ge__(self,other):
		return ((self.arr_time,self.pid)>=(other.arr_time,other.pid))
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
			print(ele[0])
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

def print_event(time,etype,p=None,moved=None,movedlist=None,alg=None):
    if etype == 0:
        print("time %dms: Process %s arrived (requires %d frames)" % (time,p.pid,p.mem))
    elif etype == 1:
        print("time %dms: Placed process %s:" % (time,p.pid))
    elif etype == 2:
        print("time %dms: Cannot place process %s -- skipped!" % (time,p.pid))
    elif etype == 3:
        print("time %dms: Process %s removed:" % (time,p.pid))
    elif etype == 4:
        print("time %dms: Cannot place process %s -- starting defragmentation" % (time,p.pid))
    elif etype == 5:
        print("time %dms: Defragmentation complete (moved %d frames: %s)" % (time,moved,', '.join(str(x) for x in movedlist)))
    elif etype == 6:
        print("time %dms: Simulator started (%s)" % (time,alg))
    elif etype == 7:
        print("time %dms: Simulator ended (%s)" % (time,alg))

def find_loc_worst_fit(p,m):
	idx = 0
	q = queue.PriorityQueue()
	i=0
	while i<len(m):
		if m[i]=='.':
			for j in range(i,len(m)):
				if m[j]!='.':
					q.put([i-j,i])
					i=j
					break;
				if j==len(m)-1:
					q.put([i-j-1,i])
		i+=1
	while not q.empty():
		tmp = q.get()
		if p.mem <= tmp[0]*(-1):
			return tmp[1]
	return -1

def place(idx,p,m):
	for i in range(idx,idx+p.mem):
		m[i] = p.pid
	return m

def unplace(pid,m):
	for i in range(len(m)):
		if m[i]==pid:
			m[i]='.'
	return m

def cal_remain(m):
	count=0
	for a in m:
		if a=='.':
			count+=1
	return count

def find_start(s,m):
	idx_start = -1
	for i in range(s,len(m)):
		if m[i]=='.':
			idx_start = i
			return idx_start
	return idx_start

def find_end(idx_start,m):
	idx_end = -1
	if idx_start!=-1:
		for idx_end in range(idx_start+1,len(m)):
			if m[idx_end]!='.':
				return idx_end
	return idx_end

def defragmentation(m):
	defrag_time = 0
	moved = 0
	movedlist = []
	start = find_start(0,m)
	end = find_end(start,m)
	print("start: %d"%start)
	print("end: %d"%end)
	while end<len(m):
		if end>start and m[end]!='.':
			if m[end] not in movedlist:
				movedlist.append(m[end])
			m[start] = m[end]
			m[end] = '.'
			start = find_start(start+1,m)
			defrag_time +=1
			moved+=1
		end+=1
	return defrag_time,moved,movedlist



def worst_fit(q,m):
	time = 0
	after_time = 0 # time after adding defrag
	print_event(time,6,alg="Contiguous -- Worst-Fit")
	leave_q = queue.PriorityQueue()
	m = list(m) # generate a copy
	while not q.empty() or not leave_q.empty():
		if not leave_q.empty():
			temp = leave_q.get()
			if temp[0]==time:
				m = unplace(temp[1],m)
				print_event(after_time,3,p=Process(temp[1],0,0,0))
				print_memory(m)
				continue
			else:
				leave_q.put(temp)
		
		if not q.empty():
			current = q.get()
			# print("Current: %s"%current)
			# print("Current_Time: %d"%time)
			if current.arr_time==time:
				print_event(after_time,0,p=current)
				idx = find_loc_worst_fit(current,m)
				if idx!=-1: # find a place
					m = place(idx,current,m)
					print_event(after_time,1,p=current)
					print_memory(m)
					leave_q.put([current.leave_time,current.pid])
				else:
					if cal_remain(m) >= current.mem:
						print_event(after_time,4,p=current)
						defrag_time,moved,movedlist = defragmentation(m)
						after_time+=defrag_time
						print_event(after_time,5,moved=moved,movedlist=movedlist)
						print_memory(m)
						idx = find_loc_worst_fit(current,m)
						m = place(idx,current,m)
						print_event(after_time,1,p=current)
						print_memory(m)
						leave_q.put([current.leave_time,current.pid])
					else:
						print_event(after_time,2,p=current)
				if not q.empty():
					p = q.get()
					q.put(p)
					if p.arr_time==time:
						continue
			else:
				q.put(current)
		time+=1
		after_time+=1
	print_event(after_time,7,alg="Contiguous -- Worst-Fit")
	print()

def print_table(md):
    md = OrderedDict(sorted(md.items()))
    print("PAGE TABLE [page,frame]:")
    for pid in md:
        page = 0
        print(pid+': ',end='')
        pages = range(len(md[pid]))
        i = 0
        for p,f in zip(pages,md[pid]):
            i+=1
            print("[%d,%d]"%(p,f),end=' ')
            if i%10==0:
                print()
        print()

def fill_memory(l,p,m):
	for i in l:
		m[i] = p.pid
	return m

def unfill_memory(l,m):
	for i in l:
		m[i] = '.'
	return m

def non_contiguous(q,m1):
	m = list(m1)
	time = 0
	table = {}
	leave_q = queue.PriorityQueue()
	remain_memory = len(m)
	print_event(time,6,alg="Non-contiguous")
	while not q.empty() or not leave_q.empty():
		if not leave_q.empty():
			temp = leave_q.get()
			if temp[0]==time:
				m = unfill_memory(table[temp[1]],m)
				remain_memory+=len(table[temp[1]])
				del table[temp[1]]
				print_event(time,3,p=Process(temp[1],0,0,0))
				print_memory(m)
				print_table(table)
				continue
			else:
				leave_q.put(temp)
		if not q.empty():
			#for i in range(q.qsize()):
			current = q.get()
			if current.arr_time==time:
				print_event(time,0,p=current)
				if remain_memory<current.mem:
					print_event(time,2,p=current)
				else:
					if table=={}:
						table[current.pid] = range(current.mem)
						m = place(0,current,m)
					else:
						table[current.pid] = [emp for emp in range(len(m)) if m[emp]=='.'][:current.mem]
						m = fill_memory(table[current.pid],current,m)
					remain_memory-=current.mem
					print_event(time,1,p=current)
					print_memory(m)
					print_table(table)
					leave_q.put([current.leave_time,current.pid])
				if not q.empty():
					p = q.get()
					q.put(p)
					if p.arr_time==time:
						continue
			else:
				q.put(current)
		time+=1
	print_event(time,7,alg="Non-contiguous")


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
	#worst_fit(q,memory)
	non_contiguous(q,memory)

	# while not q.empty():
	# 	item = q.get()
	# 	print(item)



if __name__=="__main__":
	main(sys.argv)
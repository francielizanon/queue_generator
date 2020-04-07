class OutputFile:
	"""
	Attributes
	----------
	self.arq : file descriptor
		the file that is opened at the constructor and used to 
		output data.
	self.buffer : str
		a buffer to keep things to be written to the file in 
		order to avoid a large number of small writes
	self.buf_size : int
		maximum length of the buffer in number of chars. When
		the buffer is full, it must be written to the file 
		before proceeding.
	"""
	def __init__(self, filename, header="", buf=1*1024*1024):
		"""
		Parameters
		----------
		filename : str
			the name of the file to the created. If it 
			exists, it will be overwritten.
		header : str
			the first line of the file, which is usually a
			header. A "\n" will be added to the end, so no
			need to provide it.
		buf : int
			the maximum buffer size in number of chars.
		"""
		self.arq = open(filename, "w")
		self.buf_size = buf
		self.buffer = ""
		if len(header) > 0:
			self.write(header+"\n")

	def write(self, msg):
		if (len(msg) + len(self.buffer)) > self.buf_size:
			self.arq.write(self.buffer+msg)
			self.buffer = ""
		else:
			self.buffer += msg
		

	def close(self):
		self.arq.write(self.buffer)
		self.arq.close()

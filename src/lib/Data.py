import pickle

class Data:
	"""This class is used to store data on the disk.
	You should use this class to store every sensitive data for your algorithm.
	This works like a dictionnary, you can call .get(ket) and .set(key, value) to
	manage your data.
	"""

	def __init__(self, name):
		self.name = name
		self.file = "./data/{}.pickle".format(self.name)

	def get_data(self):
		"""Returns the data dictionary.
		"""
		try:
			data = pickle.load(open(self.file, "rb"))
		except:
			data = {}
			pickle.dump(data, open(self.file, "wb+"))
		return data

	def get(self, key):
		"""Get the given key from the data on the disk.

		- key: string, the name of the data to return
		"""
		data = self.get_data()
		try:
			return data[key]
		except:
			return None

	def set(self, key, value):
		"""Set the given key to the given value in the dictionnary, and stores it
		to the disk.

		- key: string, the name of the data
		- value: object, the object to save
		"""
		data = self.get_data()
		data[key] = value
		pickle.dump(data, open(self.file, "wb+"))

	def remove(self, key):
		"""Removes the given key in the dictionnary, and save the change on the disk.

		- key: string, the name of the data to delete
		"""
		data = self.get_data()
		data.pop(key)
		pickle.dump(data, open(self.file, "wb+"))

	def reset(self):
		pickle.dump({}, open(self.file, "wb+"))

class Proposition:

	def __init__(self, connection):
		self.connection = connection

	def create_db(self):
		connection = self.connection
		connection.execute('''CREATE TABLE IF NOT EXISTS propositions (
			title TEXT NOT NULL,
			genre TEXT,
			year INTEGER)''')
		connection.commit()
		print("Baza danych została utworzona.")

	def get_input(self):
		title = input("Podaj tytuł filmu: ")
		genre = input("Podaj gatunek filmu: ")
		year = input("Podaj rok produkcji: ")
		if year == "":
			year = None
		if genre == "":
			genre = None

		return title, genre, year

	def save_to_db(self, data_tuple):
		connection = self.connection
		sql_insert = "INSERT INTO propositions VALUES(?, ?, ?)"
		connection.execute(sql_insert, data_tuple)
		connection.commit()

	def delete_from_db(self):
		idnum = input("Podaj numer id: ")
		try:
			idnum = int(idnum)
		except ValueError:
			return print("Błędny numer id.")
		connection = self.connection
		sql_delete = "DELETE FROM propositions WHERE rowid = ?"
		connection.execute(sql_delete, (idnum,))
		connection.commit()
		print("Usunąłeś propozycję numer", idnum)

	def show_propositions(self):
		connection = self.connection
		sql_select = "SELECT rowid, title, genre, year FROM propositions"
		cursor = connection.execute(sql_select)
		if cursor:
			for row in cursor:
				print(row[0], row[1], row[2], row[3])


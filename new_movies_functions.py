import sqlite3
import pyinputplus as pyinput
from datetime import datetime
import re


genres = ["horror", "science-fiction", "wojenny", "sensacyjny", "thriller", "akcji", "komedia", "katastroficzny", "dramat",
		"przygodowy", "fantasy", "psychologiczny", "historyczny", "inny"]
feats_dict = {"Tytuł": "title", "Czas trwania": "length", "Gatunek": "genre", "Data obejrzenia": "watch_date",
			  "Ile razy obejrzany": "times_watched", "Oryginalność": "originality", "Głębia": "depth",
			  "Efekty specjalne": "fx", "Inżynieria społeczna": "social_engineering", "Klimat": "atmosphere",
			  "Rok produkcji": "year", "Gra aktorska": "actors", "Zdjęcia": "pictures", "Ocena ogólna": "overall"}
genres_weights = {"horror": [0.15, 0.15, 0.2, 0.2, 0.1, 0.2],
				  "science-fiction": [0.15, 0.15, 0.2, 0.1, 0.25, 0.15],
				  "wojenny": [0.1, 0.15, 0.15, 0.15, 0.25, 0.2],
				  "sensacyjny": [0.15, 0.15, 0.2, 0.2, 0.1, 0.2],
				  "thriller": [0.2, 0.15, 0.2, 0.15, 0.1, 0.2],
				  "akcji": [0.15, 0.1, 0.2, 0.15, 0.25, 0.15],
				  "komedia": [0.25, 0.1, 0.3, 0.25, 0.0, 0.2],
				  "katastroficzny": [0.1, 0.15, 0.2, 0.15, 0.25, 0.15],
				  "dramat": [0.15, 0.3, 0.2, 0.2, 0.0, 0.15],
				  "przygodowy": [0.2, 0.15, 0.2, 0.2, 0.1, 0.15],
				  "fantasy": [0.2, 0.15, 0.15, 0.15, 0.25, 0.1],
				  "psychologiczny": [0.15, 0.25, 0.15, 0.25, 0.0, 0.2],
				  "historyczny": [0.05, 0.25, 0.3, 0.25, 0.0, 0.15],
				  "inny": [0.2, 0.2, 0.2, 0.2, 0.05, 0.15],}

class Film():
	"""Model filmu i jego cech."""
	
	def __init__(self, idnum, title, genre, length, year, watch_date, originality, depth,
				 social_engineering, actors, pictures, fx, atmosphere, overall, times_watched=0):
		self.idnum = idnum
		self.title = title
		self.genre = genre
		self.length = length
		self.year = year
		self.watch_date = watch_date
		self.times_watched = times_watched
		self.originality = originality
		self.depth = depth
		self.social_engineering = social_engineering
		self.actors = actors
		self.pictures = pictures
		self.fx = fx
		self.atmosphere = atmosphere
		self.overall = overall
		
	def save_movie_to_database(self, db_conn_obj):
		weighted_avg = count_points(self.genre, self.originality, self.depth, self.social_engineering, self.actors,
									self.pictures, self.fx, self.atmosphere, self.overall)
		insert_sql_statement = "INSERT INTO movies (id, title, genre, length, year, watch_date, times_watched, originality,\
		depth, social_engineering, actors, pictures, fx, atmosphere, overall, weighted_avg) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
		movie_feats = (self.idnum, self.title, self.genre, self.length, self.year, self.watch_date,
					   self.times_watched, self.originality, self.depth, self.social_engineering,
					   self.actors, self.pictures, self.fx, self.atmosphere, self.overall, weighted_avg)
		db_conn_obj.execute(insert_sql_statement, movie_feats)
		db_conn_obj.commit()
		print("Film został zapisany w bazie danych.")

		
class DatabaseActions():
	
	def __init__(self, db_conn_obj):
		self.db_conn_obj = db_conn_obj

	def get_db_length(self):
		db_conn_obj = self.db_conn_obj
		sql_select_statement = "SELECT id FROM movies"
		cursor = db_conn_obj.execute(sql_select_statement)
		id_list = []
		for row in cursor:
			id_list.append(row[0])
		sorted_id_list = sorted(id_list)

		last_id = sorted_id_list[len(id_list)-1]
		deleted_ids = [i for i in range(0, sorted_id_list[len(sorted_id_list)-1]) if i not in sorted_id_list]

		return (sorted(deleted_ids), last_id)

	def increment_times_watched(self, idnum):
		"""Zwiększa ilość obejrzeń filmu o 1"""
		db_conn_obj = self.db_conn_obj
		sql_select_statement = "SELECT title, times_watched FROM movies WHERE id = ?"
		cursor = db_conn_obj.execute(sql_select_statement, (idnum,))
		for row in cursor:
			title = row[0]
			times_watched = row[1]
			
		times_watched += 1
		today = datetime.today().strftime("%d-%m-%Y")
		sql_update_statement = "UPDATE movies SET times_watched = ?, watch_date = ? WHERE id = ?"
		db_conn_obj.execute(sql_update_statement, (times_watched, today, idnum))
		db_conn_obj.commit()
		print("Liczba obejrzeń filmu", title, "została zwiększona o 1. Data obejrzenia została zmieniona na datę dzisiejszą.")

	def update_database_record(self, feature, new_value, idnum):
		"""Modyfikuje rekord w bazie danych"""

		feature = verify_new_value(feature, new_value)

		if feature == False:
			print("Podana wartość jest błędna.")
			return
		else:
			feature = feature[0]

		db_conn_obj = self.db_conn_obj
		sql_update_statement = "UPDATE movies SET " + feature + " = ? WHERE id = ?"
		db_conn_obj.execute(sql_update_statement, (new_value, idnum))
		db_conn_obj.commit()
		return print("Baza filmów została zaktualizowana.")

	def recount_points(self, idnum):
		db_conn_obj = self.db_conn_obj
		sql_select_statement  = "SELECT genre, originality, depth, social_engineering, actors, pictures, fx, atmosphere," \
								" overall FROM movies WHERE id = ?"
		cursor = db_conn_obj.execute(sql_select_statement, (idnum,))
		for row in cursor:
			genre = row[0]
			originality = row[1]
			depth = row[2]
			social_engineering = row[3]
			actors = row[4]
			pictures = row[5]
			fx = row[6]
			atmosphere = row[7]
			overall = row[8]

		weighted_avg = count_points(genre, originality, depth, social_engineering, actors, pictures, fx, atmosphere, overall)
		sql_update_statement = "UPDATE movies SET weighted_avg = ? WHERE id = ?"
		db_conn_obj.execute(sql_update_statement, (weighted_avg, idnum))
		db_conn_obj.commit()

	def delete_database_record(self, idnum):
		"""Usuwa rekord z bazy danych"""

		db_conn_obj = self.db_conn_obj
		sql_delete_statement = "DELETE FROM movies WHERE id = ?"
		cursor = db_conn_obj.execute("SELECT title FROM movies WHERE id = ?", (idnum,))
		for row in cursor:
			movie_title = row[0]
		print("Chcesz bezpowrotnie usunąć film " + movie_title + " z bazy filmów.")
		answer = input("Czy jesteś pewien? ")
		if answer != "y":
			print("Film nie został usunięty.")
			return False
		db_conn_obj.execute(sql_delete_statement, (idnum,))
		db_conn_obj.commit()
		return print("Film " + movie_title + " został usunięty z bazy filmów.")

	def get_movies_by_genre(self, genre):
		"""Pobiera z bazy danych i wyświetla filmy danego gatunku"""

		db_conn_obj = self.db_conn_obj
		sql_select_statement = "SELECT title FROM movies WHERE genre = ?"
		cursor = db_conn_obj.execute(sql_select_statement, (genre,))
		for row in cursor:
			print(row[0])

	def get_ranking(self, parameter="all"):

		if parameter != "all":
			try:
				parameter = int(parameter)
			except ValueError:
				return print("Podana wartość jest błędna.")

		db_conn_obj = self.db_conn_obj
		sql_select_statement = "SELECT title, weighted_avg FROM movies"
		cursor = db_conn_obj.execute(sql_select_statement)
		ranking_list = []
		for row in cursor:
			ranking_list.append((row[0], row[1]))

		def second_element(iterable):
			return iterable[1]

		ranking = sorted(ranking_list, key=second_element, reverse=True)

		def print_ranking(parameter):
			if parameter == "all":
				parameter = len(ranking)

			for element in ranking[:parameter]:
				spaces_num = 60 - len(element[0])
				if len(element[0]) <= 55:
					print(element[0] + spaces_num * " " + str(element[1]))
				else:
					print(element[0][:50] + "..." + 7 * " " + str(element[1]))

		print_ranking(parameter)

	def get_db_record(self, idnum):
		db_conn_obj = self.db_conn_obj
		sql_select_statement = "SELECT id, title, genre, length, year, watch_date, times_watched, originality,\
		depth, social_engineering, actors, pictures, fx, atmosphere, overall, weighted_avg FROM movies WHERE id = ?"
		cursor = db_conn_obj.execute(sql_select_statement, (idnum,))
		for row in cursor:
			print("Tytuł:", row[1])
			print("Gatunek:", row[2])
			print("Czas trwania:", row[3])
			print("Rok produkcji:", row[4])
			print("Data obejrzenia:", row[5])
			print("Ile razy obejrzany:", row[6])
			print("Oryginalność:", row[7])
			print("Głębia:", row[8])
			print("Inżynieria społeczna:", row[9])
			print("Gra aktorska:", row[10])
			print("Zdjęcia:", row[11])
			print("Efekty specjalne:", row[12])
			print("Klimat:", row[13])
			print("Ocena ogólna:", row[14])
			print("Średnia ważona:", row[15])


def get_user_input(db_conn_obj, deleted_ids, create_film_instance=True):
	"""Pobiera właściwości filmu od użytkownika. Jeżeli film, lub podobna nazwa filmu jest już w bazie, wyświetla podobne filmy.
	Jeżeli nie ma  parametr create_film_instance jest ustawiony na True, tworzy i zwraca egzemplarz klasy Film.
	Gdy jest ustawiony na False, nie pobiera innych argumentów prócz tytułu, a funkcja pełni role wyszukiwarki."""
	error_msg = "Podana wartość jest nieprawidłowa."
	title = pyinput.inputStr("Podaj tytuł filmu: ")
	conn = sqlite3.connect("movies.db")
	cursor = conn.execute("SELECT id, title FROM movies")

	db_movies_list = []
	for row in cursor:
		db_movies_list.append((row[0], row[1]))
	conn.close()

	if deleted_ids != []:
		idnum = deleted_ids[0]
	else:
		idnum = len(db_movies_list) + 1

	for movie_tuple in db_movies_list:
		if title.lower() == movie_tuple[1].lower():
			if create_film_instance == False:
				print(movie_tuple[0], movie_tuple[1])
			else:
				print(movie_tuple[0], movie_tuple[1])
				print("Film o takiej nazwie znajduje się już w bazie filmów.")
				return False
	
	similar_db_titles = find_repetitions(title, db_movies_list)

	if create_film_instance == False:
		if similar_db_titles != []:
			for db_tuple in similar_db_titles:
				#eliminuje ponowne wyświetlenie tytułu dokładnie pasującego do szukanego
				if title.lower() != db_tuple[1].lower():
					print(db_tuple[0], db_tuple[1])
		else:
			print("Nie znaleziono filmu o takim tytule.")
		return False
	else:
		if similar_db_titles != []:
			print("Znaleziono filmy o podobnych tytułach:")
			for db_tuple in similar_db_titles:
				print(db_tuple[0], db_tuple[1])
			answer = input("Czy chcesz kontynuować zapisywanie nowego filmu? ")
			if answer.lower() != "y":
				print("Dziękuję za skorzystanie z programu.")
				return False
	
	genre = pyinput.inputChoice(choices=(genres), prompt="Podaj gatunek filmu: ")

	length = pyinput.inputStr("Podaj czas trwania filmu w formacie GG:MM: ")
	length_re = re.match("\d\d:\d\d", length)
	if not length_re:
		print(error_msg)
		return False

	year = pyinput.inputNum(prompt="Podaj rok produkcji: ", min=1900, max=datetime.now().year)

	watch_date = pyinput.inputStr("Podaj datę obejrzenia filmu w formacie DD-MM-YYYY: ")
	watchdate_re = re.match("\d\d-\d\d-[12]\d\d\d", watch_date)
	if not watchdate_re:
		print(error_msg)
		return False

	print("Oceń film")
	originality = pyinput.inputNum("Oryginalność: ", min=1, max=10)
	depth = pyinput.inputNum("Głębia: ", min=1, max=10)
	social_engineering = pyinput.inputNum("Inżynieria społeczna: ", min=1, max=10)
	actors = pyinput.inputNum("Gra aktorska: ", min=1, max=10)
	pictures = pyinput.inputNum("Zdjęcia: ", min=0, max=1)
	fx = pyinput.inputNum("Efekty specjalne: ", min=1, max=10)
	atmosphere = pyinput.inputNum("Klimat: ", min=1, max=10)
	overall = pyinput.inputNum("Ocena ogólna: ", min=1, max=10)
	print(idnum)
	new_movie = Film(idnum, title, genre, length, year, watch_date, originality, depth, social_engineering,
					 actors, pictures, fx, atmosphere, overall, times_watched=0)
	return new_movie


def find_repetitions(new_title, db_tuples):
	"""Wyszukuje tytuły filmów, które już znajdują się na liście."""
	
	db_movies_list = []
	for tupl in db_tuples:
		db_movies_list.append(tupl[1])

	repetitions = []
	set_repetitions = []
	if " " in new_title:
		new_title_list = []
		for word in new_title.split():
			new_title_list.append(word.rstrip())

		for movie in db_movies_list:
			stored_title_list = movie.split()
			if len(stored_title_list) > 1 and len(new_title_list) > 1:
				count_to = len(stored_title_list) - 1
				for i in range(0, count_to):
					x = i + 1
					word_list = [stored_title_list[i], stored_title_list[x]]
					temp_word_list = " ".join(word_list)
					search_result = new_title.find(temp_word_list)
					if search_result != -1:
						repetitions.append(movie)

			if new_title_list[-1] == stored_title_list[-1]:
					repetitions.append(movie)

			if new_title.lower() in movie.lower() and len(new_title) > 3:
				repetitions.append(movie)
	else:
		for movie in db_movies_list:
			if new_title.lower() in movie.lower() and len(new_title) > 3:
				repetitions.append(movie)
	
	repetition_tuples = []
	if len(repetitions) != 0:
		set_repetitions = list(set(repetitions))
		for dbtuple in db_tuples:
			if dbtuple[1] in set_repetitions:
				repetition_tuples.append(dbtuple)

	return repetition_tuples


def verify_new_value(feature, new_value):
	"""Weryfikuje nową wartość zapisywaną w bazie danych przez funkcje update_database_record"""
	col_name = ""
	notfound_count = 0

	for key, val in feats_dict.items():
		if feature.lower() == key.lower() or feature.lower() == val.lower():
			col_name = val.lower()
		else:
			notfound_count += 1

	if notfound_count == len(feats_dict):
		return False

	def check_int(value):
		try:
			int_value = int(value)
		except ValueError:
			return False
		else:
			return int_value

	if col_name == "genre":
		if new_value not in genres:
			return False
		else:
			return (col_name, new_value)

	elif col_name in ("originality", "depth", "social_engineering", "actors", "fx", "atmosphere", "overall"):
		new_value = check_int(new_value)
		if new_value != False:
			if not 0 < new_value < 11:
				return False
			else:
				return (col_name, new_value)

	elif col_name == "year":
		new_value = check_int(new_value)
		if new_value != False:
			if not 1900 < new_value < datetime.now().year:
				return False
			else:
				return (col_name, new_value)

	elif col_name == "pictures":
		if type(new_value) is not int or not int(new_value) in (0, 1):
			return False
		else:
			return (col_name, new_value)

	elif col_name == "length":
		length_re = re.match("\d\d:\d\d", new_value)
		if not length_re:
			print("Wpisz czas trwania filmu w formacie GG:MM.")
			return False
		else:
			return (col_name, new_value)

	elif col_name == "watch_date":
		watchdate_re = re.match("\d\d-\d\d-[12]\d\d\d", new_value)
		if not watchdate_re:
			print("Wpisz datę w formacie DD-MM-YYYY.")
			return False
		else:
			return (col_name, new_value)

	elif col_name == "weighted_avg":
		return False

	elif col_name == "id":
		return False

	elif col_name == "times_watched":
		return False

	else:
		return False


def count_points(genre, originality, depth, social_engineering, actors, pictures, fx, atmosphere, overall):
	"""Wylicza ilość punktów przyznanych filmowi na podstawie poszczególnych ocen"""

	#dostosowanie oceny za inżynierię społeczną
	decrease = [(4, -0.5), (3, -0.1), (2, -0.15), (1, -0.2)]
	if social_engineering < 5:
		for i in range(1, 5):
			if i == social_engineering:
				for el in decrease:
					if el[0] == social_engineering:
						decreased_weight = float(genres_weights[genre][2]) + el[1]
						genres_weights[genre][2] = decreased_weight

	local_genres = [originality, depth, social_engineering, actors, fx, atmosphere]
	points = 0.0
	for key, val in genres_weights.items():
		if genre == key:
			points = [float(grade) * weight for grade, weight in zip(local_genres, val)]
			points = sum(points) + float(overall) + float(pictures)
			points = round(points, 2)

	return points

def print_help():
	try:
		with open("movies_help.txt", "r") as fo:
			print(fo.read())
	except IOError:
		print("Brak pliku źródłowego.")











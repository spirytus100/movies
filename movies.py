import sqlite3
import new_movies_functions as movies_functions
import movies_stats
import movies_propositions as propositions


endmsg = "Dziękuję za skorzystanie z programu."
nocommand_msg = "Nie znaleziono polecenia."
keywords = ["all"]


def check_input_parameter(value, deleted_ids, last_id):
	keywords = ["all", "show", "delete", "add", "createdb"]
	try:
		int_value = int(value)
	except ValueError:
		if type(value) is str and value in keywords:
			return value
		else:
			return False
	else:
		if int_value not in deleted_ids and not int_value > last_id:
			return int_value
		else:
			return False

connection = sqlite3.connect("movies.db")

while True:
	user_input = input("\n> ")
	command_len = len(user_input.split())

	#pobranie usuniętych numerów id i ostatniego numeru id
	db_length_instance = movies_functions.DatabaseActions(connection)
	deleted_ids = db_length_instance.get_db_length()[0]
	last_id = db_length_instance.get_db_length()[1]

	if command_len == 1:

		#sprawdza wpis w postaci numeru id filmu i zwraca numer lub false
		only_movie_id = check_input_parameter(user_input, deleted_ids, last_id)

		if user_input == "q":
			print(endmsg)
			break

		elif user_input == "add":
			new_movie = movies_functions.get_user_input(connection, deleted_ids, create_film_instance=True)
			if new_movie != False:
				new_movie.save_movie_to_database(connection)

		elif user_input == "find":
			movies_functions.get_user_input(connection, deleted_ids, create_film_instance=False)

		elif user_input in movies_functions.genres:
			genre = user_input.split()[0]
			find_genre_instance = movies_functions.DatabaseActions(connection)
			find_genre_instance.get_movies_by_genre(genre)

		elif user_input == "recommend":
			recommend_instance = movies_stats.MoviesStats(connection)
			recommend_instance.get_propositions()

		elif only_movie_id != False:
			get_record_instance = movies_functions.DatabaseActions(connection)
			get_record_instance.get_db_record(only_movie_id)

		elif user_input == "help":
			movies_functions.print_help()

		else:
			print(nocommand_msg)

	elif command_len == 2:
		#sprawdzenie, czy argument jest liczbą nie większą niż ilość wierszy bazy danych
		idnum = check_input_parameter(user_input.split()[1], deleted_ids, last_id)
		if idnum == False:
			print("Błędny argument.")
			continue

		if user_input.split()[0] == "increment":
			increment_instance = movies_functions.DatabaseActions(connection)
			increment_instance.increment_times_watched(idnum)

		elif user_input.split()[0] == "update":
			feature = input("Wpisz atrybut, który chcesz zmienić: ")
			if feature not in movies_functions.feats_dict.keys() and feature not in movies_functions.feats_dict.values():
				print("Podana wartość jest błędna.")
				continue
			new_value = input("Wpisz nową wartość: ")
			update_instance = movies_functions.DatabaseActions(connection)
			update_instance.update_database_record(feature, new_value, idnum)
			update_instance.recount_points(idnum)

		elif user_input.split()[0] == "delete":
			delete_instance = movies_functions.DatabaseActions(connection)
			delete_instance.delete_database_record(idnum)

		elif user_input.split()[0] == "ranking":
			ranking_instance = movies_functions.DatabaseActions(connection)
			ranking_instance.get_ranking(parameter=idnum)

		elif user_input.split()[0] == "propositions":
			movies_prop = propositions.Proposition(connection)
			if user_input.split()[1] == "show":
				movies_prop.show_propositions()
			elif user_input.split()[1] == "add":
				data_tuple = movies_prop.get_input()
				movies_prop.save_to_db(data_tuple)
			elif user_input.split()[1] == "delete":
				movies_prop.delete_from_db()
			elif user_input.split()[1] == "createdb":
				movies_prop.create_db()


		else:
			print(nocommand_msg)

connection.close()

		
		
		
import datetime

def get_movies_stats(connection):
    sql_select_statement = "SELECT id, title, genre, length, year, watch_date, times_watched, originality, depth," \
                           " social_engineering, actors, pictures, fx, atmosphere, overall, weighted_avg FROM movies"
    cursor = connection.execute(sql_select_statement)
    stats_list = []
    for row in cursor:
        stats_list.append(list(row))

    return stats_list


class MoviesStats():

    def __init__(self, connection):
        self.connection = connection
        self.stats_list = get_movies_stats(connection)
        self.genres = ["horror", "science-fiction", "wojenny", "sensacyjny", "thriller", "akcji", "komedia", "katastroficzny", "dramat",
		                "przygodowy", "fantasy", "psychologiczny", "historyczny", "inny"]

    def formatted_date(self, watch_date):
        """"Formatuje datę obejrzenia do formatu 'obliczalnego'"""
        formatted_date = datetime.datetime.strptime(watch_date, "%d-%m-%Y")
        return formatted_date

    def formatted_length(self, length):
        """Formatuje string z podanym czasem trwania filmu."""
        split_el = length.split(":")
        hours = int(split_el[0])
        minutes = int(split_el[1])
        hours = hours * 60 * 60
        minutes = minutes * 60
        seconds = hours + minutes
        return seconds

    def assign_points(self, list_sorted_byvalue):
        i = len(list_sorted_byvalue) + 1
        final_list = []
        for el in list_sorted_byvalue:
            i -= 1
            final_list.append((el[0], i))

        return final_list

    def best_genres(self):
        stats_list = self.stats_list
        db_genres_list = []
        db_titles_genres = []
        for row in stats_list:
            db_genres_list.append(row[2])
            db_titles_genres.append((row[1], row[2]))

        best_genres = []
        for genre in self.genres:
            genre_count = db_genres_list.count(genre)
            best_genres.append((genre, genre_count))

        best_genres = sorted(best_genres, reverse=True, key=lambda x: x[1])
        genres_points = []
        i = len(best_genres) + 1
        previous_count = None
        for genre_tuple in best_genres:
            if genre_tuple[1] == previous_count:
                i += 1

            genres_points.append((genre_tuple[0], i))
            previous_count = genre_tuple[1]
            i -= 1

        title_points = []
        for title_tuple in db_titles_genres:
            for genre_tuple in genres_points:
                if title_tuple[1] == genre_tuple[0]:
                    title_points.append((title_tuple[0], genre_tuple[1]))

        return title_points

    def time_since_movie(self):
        stats_list = self.stats_list
        times_list = []
        for row in stats_list:
            times_list.append((row[1], datetime.datetime.today() - self.formatted_date(row[5])))

        times_list = sorted(times_list, reverse=True, key=lambda x: x[1])
        points_list = self.assign_points(times_list)
        return points_list

    def movies_avg_points(self):
        stats_list = self.stats_list
        movies_avg = []
        for row in stats_list:
            movies_avg.append((row[1], row[15]))

        movies_avg = sorted(movies_avg, reverse=True, key=lambda x: x[1])

        points_list = []
        i = len(movies_avg) + 1
        previous_avg = None
        for avgtuple in movies_avg:
            if avgtuple[1] == previous_avg:
                i += 1
                points_list.append((avgtuple[0], i))
            else:
                points_list.append((avgtuple[0], i))
            i -= 1
            previous_avg = avgtuple[1]

        return points_list

    def longer_movie_on_saturday(self, average_points):
        stats_list = self.stats_list
        avg_points_list = []
        if datetime.date.weekday(datetime.datetime.today()) == 5:
            for row in stats_list:
                if int(row[3].split(":")[0]) >= 2:
                    avg_points_list.append((row[1], 0.05 * average_points))
            return avg_points_list
        else:
            return []

    def get_propositions(self):
        best_genres = self.best_genres()
        time_since_movie = self.time_since_movie()
        movies_avg_points = self.movies_avg_points()
        points_tuples = best_genres + time_since_movie + movies_avg_points
        movies_dict = {}
        for point_tuple in points_tuples:
            title = point_tuple[0]
            points = point_tuple[1]
            if title in movies_dict.keys():
                movies_dict[title] += float(points)
            else:
                movies_dict[title] = float(points)

        mean = sum(movies_dict.values()) / len(movies_dict)
        saturday_movies = self.longer_movie_on_saturday(mean)
        for saturday_tuple in saturday_movies:
            title = saturday_tuple[0]
            points = saturday_tuple[1]
            movies_dict[title] += points

        sorted_movies = sorted(movies_dict.items(), reverse=True, key=lambda x: x[1])

        i = 0
        while i < len(sorted_movies):
            print(sorted_movies[i][0])
            i += 1
            if i > 30:
                break














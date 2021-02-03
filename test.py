import unittest
import datetime


def formatted_date(watch_date):
    """"Formatuje datę obejrzenia do formatu 'obliczalnego'"""
    formatted_date = datetime.datetime.strptime(watch_date, "%d-%m-%Y")
    return formatted_date


class MoviesTest(unittest.TestCase):

    def test_check_input_parameters(self):
        keywords = ["all"]
        deleted_ids = [1, 19]
        last_id = 18

        def check_input_parameter(value, deleted_ids, last_id):

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

        #self.assertFalse(check_input_parameter(1, deleted_ids, last_id))
        #self.assertEqual(check_input_parameter(4, deleted_ids, last_id), 4)
        #self.assertFalse(check_input_parameter(11, deleted_ids, last_id))

    def test_time_since_movie(self):
        stats_list = ["01-01-2021", "01-01-2020", "24-12-2020"]
        times_list = []
        for row in stats_list:
            times_list.append(datetime.datetime.today() - formatted_date(row))

        #self.assertEqual(30, times_list[0])
        self.assertEqual(365, times_list[1])
        self.assertEqual(38, times_list[2])


if __name__ == "__main__":
    unittest.main()




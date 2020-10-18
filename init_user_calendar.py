import matse_stundenplan
import sys

user = sys.argv[1]
courses = sys.argv[2].split(',')

matse_stundenplan.combine_courses(user, courses)
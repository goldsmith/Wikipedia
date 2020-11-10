import csv
import os

from numpy.core.defchararray import lower

from .exceptions import BadParameterException

project_folder = "WIKIPEDIA_PROJECT"
file_csv = "{0}{1}".format(os.environ.get(project_folder, None), "\\wikipedia\\list_languages.csv")


def init_list_languages():
  try:
    with open(file_csv, newline='') as file:
      reader = csv.reader(file)
      return list(reader)
  except FileNotFoundError:
    raise BadParameterException("Make sure that the system variable '{0}' is set, "
                                "the value of which must be the path to the current project".format(project_folder))


def find_language(lst, param):
  if lower(param) in lst:
    return True

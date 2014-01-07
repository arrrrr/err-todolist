from errbot import BotPlugin, botcmd
from errbot.utils import get_sender_username
import logging
import time
import datetime
import csv

class Entry:
  def __init__(self, title, creator):
    self.title = title
    self.creator = creator 
    self.description = "No description. :("
    self.timestamp = time.time()
    self.assignees = []

class TodoList(BotPlugin):

  def activate(self):
    """Triggers on plugin activation, loads the old todo list from a file if it exists."""
    # Read the csv file if it exists and initialise the list
    self.l = []
    try:
      with open('todolist.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
          temp_entry = Entry(row[0], row[1])
          temp_entry.description = row[2]
          temp_entry.timestamp = float(row[3])
          temp_entry.assignees = [a for a in row[4::]]
          self.l.append(temp_entry)
    except IOError:
      logging.debug("Failed to load the list from the csv file. Creating a new list.")

    super(TodoList, self).activate()

  def write_csv_file(self):
    """Helper to write the whole list to the csv file"""
    with open("todolist.csv", "w") as csv_file:
      csv_writer = csv.writer(csv_file)
      for item in self.l:
        row = [item.title, item.creator, item.description, item.timestamp] + [a for a in item.assignees]
        csv_writer.writerow([str(s) for s in row])

  @botcmd
  def todo_list(self, mess, args):
    """Lists all entries of the todo list"""
    ret = ""
    if len(self.l) > 0:
        ret += "Listing all entries of the todo list:"
    else:
        ret += "No entries yet. Set some tasks, lazybone!"
    for i, item in enumerate(self.l):
      # Add the item's id in the list and the title to the output
      ret += "\n[" + str(i) + "] " + item.title + ":\n"
      # Add the description to the output
      ret += item.description
      # Add the assignees to the output
      if len(self.l[i].assignees) > 0:
        ret += "\nAssigned to this entry: " + ", ".join(self.l[i].assignees)
      # Add the creator and a timestamp to the output
      ret += "\n(by " + item.creator + ", " + datetime.datetime.fromtimestamp(item.timestamp).strftime('%d.%m.%Y %H:%M:%S') + ")"
    return ret

  @botcmd
  def todo_create(self, mess, args):
    """Creates a new entry on the todo list. Syntax: !todo create <title>."""
    self.l.append(Entry(args, get_sender_username(mess)))
    self.write_csv_file()
    return "Created a new entry with id " + str(len(self.l)-1) + ", use !todo describe " + str(len(self.l)-1) + " to add a detailed description."

  @botcmd(split_args_with=' ')
  def todo_remove(self, mess, args):
    """Removes an entry from the todo list. Syntax !todo remove <ID>. Get the right ID by using !todo list"""
    i = int(args[0])
    if i < len(self.l):
      temp_title = self.l[i].title
      del self.l[i]
      self.write_csv_file()
      return "Successfully removed entry [" + str(i) + "] : " + temp_title + "."
    else:
      return "Couldn't find the todo list entry " + str(i) + ", sorry. Use !todo list to see all entries and their IDs."

  @botcmd(split_args_with=' ')
  def todo_describe(self, mess, args):
    """Changes (and adds) the description of an entry. Syntax: !todo describe <ID> <description>. Get the right ID by using !todo list"""
    i = int(args[0])
    if i < len(self.l):
      self.l[i].description = ' '.join(args[1::])
      self.write_csv_file()
      return "Successfully changed the description of entry [" + str(i) + "] " + self.l[i].title + "."
    else:
      return "Couldn't find the todo list entry " + str(i) + ", sorry. Use !todo list to see all entries and their IDs."

  @botcmd(split_args_with=' ')
  def todo_assign(self, mess, args):
    """Assigns persons to an entry. Syntax: !todo assign <ID> <person_0> [person_1] ... [person_n]. Use !todo list to see all entries and their IDs."""
    i = int(args[0])
    if i < len(self.l):
      self.l[i].assignees += args[1::]
      self.write_csv_file()
      return "Successfully assigned " + ", ".join(args[1::]) + " to [" + str(i) + "] " + self.l[i].title + "."
    else:
      return "Couldn't find the todo list entry " + str(i) + ", sorry. Use !todo list to see all entries and their IDs."

  @botcmd(split_args_with=' ')
  def todo_unassign(self, mess, args):
    """Unassigns persons from an entry. Syntax: !todo unassign <ID> <person_0 [person_1] ... [person_n]. Use !todo list to see all entries and their IDs."""
    i = int(args[0])
    if i < len(self.l):
      self.l[i].assignees = [a for a in self.l[i].assignees if a not in args[1::]]
      self.write_csv_file()
      return "Successfully unassigned " + ", ".join(args[1::]) + " from [" + str(i) + "] " + self.l[i].title + "."
    else:
      return "Couldn't find the todo list entry " + str(i) + ", sorry. Use !todo list to see all entries and their IDs."

  @botcmd(split_args_with=' ')
  def todo_chtitle(self, mess, args):
    """Changes the title of an entry. Syntax: !todo chtitle <ID> <new_tile>."""
    i = int(args[0])
    if i < len(self.l):
      temp_title = self.l[i].title
      self.l[i].title = " ".join(args[1::])
      self.write_csv_file()
      return "Successfully changed the title from " + temp_title + " to " + self.l[i].title + " ."
    else:
      return "Couldn't find the todo list entry " + str(i) + ", sorry. Use !todo list to see all entries and their IDs."

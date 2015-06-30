import datetime


class Chat(object):
    """An object to encapsulate the entire Facebook Message history.

        - Contains a list of Thread objects, which can be accessed using item
          accessing Chat["Thread Name"] style.
        - When initialising, 'myname' should be the name of the user, and 'threads'
          should be a list of Thread objects.
        - Provides useful functions for accessing messages."""

    def __init__(self, myname, threads):
        self.threads = sorted(threads, key=len, reverse=True)
        self._thread_dict = {", ".join(thread.people): thread for thread in self.threads}
        self._total_messages = len(self.all_messages())
        self._myname = myname
        self._all_people = {myname}
        for thread in self.threads:
            self._all_people.update(thread.people)

    def __getitem__(self, key):
        """Allow accessing Thread objects in the list using Chat["Thread Name"].

           This method allows the threads list to be accessed using Chat["Thread Name"]
           or Chat[n] notation."""
        if type(key) is int:
            return self.threads[key]
        elif type(key) is str:
            return self._thread_dict[key]

    def __repr__(self):
        """Set Python's representation of the Chat object."""
        return "<{}'s CHAT LOG: TOTAL_THREADS={} TOTAL_MESSAGES={}>".format(self._myname, len(self.threads), self._total_messages)

    def __len__(self):
        """Return the total number of threads.

           Allows the len() method to be called on a Chat object. This could be
           changed to be the total number of messages, currently stored as
           Chat._total_messages()"""
        return len(self.threads)

    def _date_parse(self, date):
        """Allow dates to be entered as integer tuples (YYYY, MM, DD[, HH, MM]).

           Removes the need to supply datetime objects, but still allows dates
           to be entered as datetime.datetime objects. The Year, Month and
           Day are compulsory, the Hours and Minutes optional. May cause exceptions
           if poorly formatted tuples are used."""
        if type(date) is datetime.datetime:
            return date
        else:
            return datetime.datetime(*date)

    def _recount_messages(self):
        """Update the count of total messages.

           Since Thread objects can be extended dynamically, this may prove
           necessary."""
        self._total_messages = len(self.all_messages())

    def all_messages(self):
        """Return a date ordered list of all messages.

           The list is all messages contained in the Chat object, as a list of
           Message objects."""
        return sorted([message for thread in self.threads for message in thread.messages])

    def all_from(self, name):
        """Return a date ordered list of all messages sent by 'name'.

           The list returned is a list of Message objects. This is distinct from
           Thread.by(name) since all threads are searched by this method. For all
           messages in one thread from 'name', use Thread.by(name) on the correct Thread."""
        return sorted([message for thread in self.threads for message in thread.by(name)])

    def sent_before(self, date):
        """Return a date ordered list of all messages sent before specified date.

           The function returns a list of Message objects. The 'date' can be a
           datetime.datetime object, or a three or five tuple (YYYY, MM, DD[, HH, MM])."""
        return sorted([message for thread in self.threads for message in thread.sent_before(date)])

    def sent_after(self, date):
        """Return a date ordered list of all messages sent after specified date.

           The list returned is a list of Message objects. The 'date' can be a
           datetime.datetime object, or a three or five tuple (YYYY, MM, DD[, HH, MM])."""
        return sorted([message for thread in self.threads for message in thread.sent_after(date)])

    def sent_between(self, start, end=None):
        """Return a date ordered list of all messages sent between specified dates.

            - The list returned is a list of Message objects. The 'start' and 'end'
              can be datetime.datetime objects, or a three or five tuple
              (YYYY, MM, DD[, HH, MM]).
            - Not entering an 'end' date is interpreted as all messages sent on
              the day 'start'. Where a time is specified also, a 24 hour period
              beginning at 'start' is used."""
        return sorted([message for thread in self.threads for message in thread.sent_between(start, end)])

    def search(self, string, ignore_case=False):
        """Return a date ordered list of all messages containing 'string'.

           This function searches in all threads, and returns a list of Message
           objects.
            - The function can be made case-insensitive by setting 'ignore_case'
              to True."""
        return sorted([message for thread in self.threads for message in thread.search(string, ignore_case)])


class Thread(object):
    """An object to encapsulate a Facebook Message thread.

        - Contains a list of participants, a string form of the list and a list
          of messages in the thread as Message objects.
        - When initialising, 'people' should be a list of strings containing the
          names of the participants and 'messages' should be a list of Message
          objects."""

    def __init__(self, people, messages):
        self.people = people
        self.people_str = ", ".join(self.people)
        self.messages = sorted(messages)

    def __getitem__(self, key):
        """Allow accessing Message objects in the messages list using Thread[n].

           Beware out by one errors! The message numbers start counting at 1,
           but the list they are stored in is indexed from 0.
            - This behaviour could be corrected by either subtracting one from
              the key (which causes issues when slicing), or by counting messages
              from 0."""
        return self.messages[key]

    def __repr__(self):
        """Set Python's representation of the Thread object."""
        return '<THREAD: PEOPLE={}, MESSAGE_COUNT={}>'.format(self.people_str, len(self.messages))

    def __len__(self):
        """Return the total number of messages in the thread."""
        return len(self.messages)

    def _add_messages(self, new_messages):
        """Allow adding messages to an already created Thread object.

           This function is useful for merging duplicate threads together."""
        self.messages.extend(new_messages)
        self.messages = sorted(self.messages)

    def _renumber_messages(self):
        """Renumber all messages in the 'messages' list.

           Message objects are are sorted after being added; but if messages are
           added using _add_messages() then the numbering may be incorrect. This
           function fixes that."""
        i = 1
        for message in self.messages:
            message._num = i
            i += 1

    def by(self, name):
        """Return a date ordered list of all messages sent by 'name'.

           Returns a list of Message objects."""
        return [message for message in self.messages if message.sent_by(name)]

    def sent_before(self, date):
        """Return a date ordered list of all messages sent before specified date.

           The function returns a list of Message objects. The 'date' can be a
           datetime.datetime object, or a three or five tuple (YYYY, MM, DD[, HH, MM])."""
        return [message for message in self.messages if message.sent_before(date)]

    def sent_after(self, date):
        """Return a date ordered list of all messages sent after specified date.

           The list returned is a list of Message objects. The 'date' can be a
           datetime.datetime object, or a three or five tuple (YYYY, MM, DD[, HH, MM])."""
        return [message for message in self.messages if message.sent_after(date)]

    def sent_between(self, start, end=None):
        """Return a date ordered list of all messages sent between specified dates.

            - The list returned is a list of Message objects. The 'start' and 'end'
              can be datetime.datetime objects, or a three or five tuple
              (YYYY, MM, DD[, HH, MM]).
            - Not entering an 'end' date is interpreted as all messages sent on
              the day 'start'. Where a time is specified also, a 24 hour period
              beginning at 'start' is used."""
        return [message for message in self.messages if message.sent_between(start, end)]

    def search(self, string, ignore_case=False):
        """Return a date ordered list of messages in Thread containing 'string'.

           This function searches the current thread, and returns a list of Message
           objects.
            - The function can be made case-insensitive by setting 'ignore_case'
              to True."""
        return sorted([message for message in self.messages if message.contains(string, ignore_case)])


class Message(object):
    """An object to encapsulate a Facebook Message.

        - Contains a string of the author's name, the timestamp, number in the thread
          and the body of the message.
        - When initialising, thread_name' should be the containing Thread.people_str,
          'author' should be string containing the message sender's name, 'date_time'
          should be a datetime.datetime object, 'text' should be the content of
          the message and 'num' should be the number of the message in the thread."""

    def __init__(self, thread, author, date_time, text, num):
        self.thread_name = thread
        self.author = author
        self.date_time = date_time
        self.text = text
        self._num = num

    def __repr__(self):
        """Set Python's representation of the Message object."""
        return '<MESSAGE: THREAD={} NUMBER={} TIMESTAMP={} AUTHOR={} MESSAGE="{}">'.\
            format(self.thread_name, self._num, self.date_time, self.author, self.text)

    def __str__(self):
        """Return a string form of a Message in format required for csv output."""
        out = '"' + self.thread_name + '","' + str(self._num) + '","' + self.author + '","' + str(self.date_time) + '","' + self.text + '"\n'
        return out

    def __lt__(self, message):
        """Allow sorting of messages by implementing the less than operator.

           Sorting is by date, unless two messages were sent at the same time,
           in which case message number is used to resolve conflicts. This number
           ordering holds fine for messages in single threads, but offers no real
           objective order outside a thread."""
        if self.date_time == message.date_time:
            if abs(self._num - message._num) > 9000:    # If dates equal, but numbers miles apart
                return False  # MUST be where two 10000 groups join: larger number actually smaller here!
            else:
                return self._num < message._num
        return self.sent_before(message.date_time)

    def __gt__(self, message):
        """Allow sorting of messages by implementing the greater than operator.

           Sorting is by date, unless two messages were sent at the same time,
           in which case message number is used to resolve conflicts. This number
           ordering holds fine for messages in single threads, but offers no real
           objective order outside a thread."""
        if self.date_time == message.date_time:
            if abs(self._num - message._num) > 9000:    # If dates equal, but numbers miles apart
                return True  # MUST be where two 10000 groups join: smaller number actually larger here!
            else:
                return self._num > message._num
        return self.sent_after(message.date_time)

    def __eq__(self, message):
        """Messages are equal if their number, date, author and text are the same."""
        equal = (self._num == message._num) and (self.author == message.author)
        equal = equal and (self.date_time == message.date_time) and (self.text == message.text)
        return equal

    def __len__(self):
        """Return the number of characters in the message body."""
        text = self.text.replace("<|NEWLINE|>", "")  # Undo adding extra characters
        text = text.replace('""', '"')  # And escaping quote marks
        return len(text)

    def _date_parse(self, date):
        """Allow dates to be entered as integer tuples (YYYY, MM, DD[, HH, MM]).

           Removes the need to supply datetime objects, but still allows dates
           to be entered as datetime.datetime objects. The Year, Month and
           Day are compulsory, the Hours and Minutes optional. May cause exceptions
           if poorly formatted tuples are used."""
        if type(date) is datetime.datetime:
            return date
        else:
            return datetime.datetime(*date)

    def sent_by(self, name):
        """Return True if the message was sent by 'name'."""
        return self.author == name

    def sent_before(self, date):
        """Return True if the message was sent before the date specified.

           The 'date' can be a datetime.datetime object, or a three or five tuple
           (YYYY, MM, DD[, HH, MM])."""
        date = self._date_parse(date)
        return self.date_time < date

    def sent_after(self, date):
        """Return True if the message was sent after the date specified.

           The 'date' can be a datetime.datetime object, or a three or five tuple
           (YYYY, MM, DD[, HH, MM])."""
        date = self._date_parse(date)
        return self.date_time > date

    def sent_between(self, start, end=None):
        """Return True if the message was sent between the dates specified.

            - The 'start' and 'end' can be datetime.datetime objects, or
              a three or five tuple (YYYY, MM, DD[, HH, MM]). The start and end times
              are inclusive since this is simplest.
            - Not entering an 'end' date is interpreted as all messages sent on
              the day 'start'. Where a time is specified also, a 24 hour period
              beginning at 'start' is used."""
        start = self._date_parse(start)
        if end is not None:
            end = self._date_parse(end)
        else:
            end = start + datetime.timedelta(1)  # 1 day (24 hours) later than 'start'
        return start <= self.date_time <= end

    def contains(self, search_string, ignore_case=False):
        """Return True if 'search_string' is contained in the message text."""
        if ignore_case:
            return search_string.lower() in self.text.lower()
        else:
            return search_string in self.text

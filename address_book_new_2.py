from collections import UserDict
from datetime import *
import sys, re, pickle
# ---------- Class part ----------

class NameArgumentError(Exception):
    pass


class PhoneArgumentError(Exception):
    pass


class PhoneExistsError(Exception):
    pass


class PhoneDoesNotExistError(Exception):
    pass


class NoNameError(Exception):
    pass


class BirthFormatError(Exception):
    pass


class SearchValueError(Exception):
    pass


class CustomIterator:
    general_counter = 0
    def __init__(self, records_on_page):
        self.records_on_page = records_on_page
        self.b = address_book.copy()
        self.listing = [i for i in self.b]

    def __iter__(self):
        return self
    
    def __next__(self):
        if len(self.b) != 0:
            result = []
            for i in range(self.records_on_page):
                if len(self.b) == 0:
                    break
                a = self.b.pop(self.listing[0])
                del self.listing[0]
                result.append(a)
            return result
        else:
            raise StopIteration


class AddressBook(UserDict):
    def iterator(self, on_page = 2):
        return CustomIterator(on_page)

    def add_record(self, record):
        self.data[record.name.value] = record

    def search(self, name = None, phone = None):
        result_list = []
        if name:
            for k, v in self.data.items():
                if re.search(name, k, flags=re.IGNORECASE):
                    result_list.append(v)
        elif phone:
            for v in self.data.values():
                for i in v.phones:
                    if re.search(phone, i.value):
                        result_list.append(v)
                        break
        return result_list
        # else:
            # return "You did not choose any search parameter"
    
    def delete_record(self, name):
        del self.data[name]


class Field:
    def __init__(self, value):
        self.value = value


class Name(Field):
    pass


class Phone(Field):
    @property
    def var(self):
        return self.value

    @var.setter
    def var(self, new_value):
        if re.fullmatch(r"[0-9]+", new_value):
            self.value = new_value
        else:
            print("Wrong phone format, try again. A phone number can only contain numbers and a '+' at the beginning")


class Birthday(Field):
    @property
    def var(self):
        return self.value

    @var.setter
    def var(self, new_value):
        if re.fullmatch(r"[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{4}", new_value):
            self.value = new_value
        else:
            print("Wrong date format, try again. Please use dd.mm.yyyy format")


class Record():
    def __init__(self, name, phone = None, birthday = None):
        self.name = Name(name)
        self.phones = []
        if phone:
            self.phones.append(Phone(phone))
        self.birthday = Birthday(birthday)

    def add_phone(self, phone):
        self.phones.append(Phone(phone))
    
    def add_birthday(self, birthday):
        self.birthday.var = birthday

    def change_phone(self, old, phone):
        for i in self.phones:
            if i.value == old:
                pos = self.phones.index(i)
                self.phones[pos].var = phone

    def delete_phone(self, phone):
        for i in self.phones:
            if i.value == phone:
                self.phones.remove(i)

    def days_to_birthday(self):
        current_date = datetime.now()
        birth_date = datetime.strptime(self.birthday.value, "%d.%m.%Y")
        if birth_date.month >= current_date.month and birth_date.day >= current_date.day:
            if birth_date.day != current_date.day:
                birth_date = birth_date.replace(year=current_date.year) 
                res = birth_date - current_date
                return f"Days left until the birthday: {res.days}"
            else:
                return f"This day is today!"
        else:
            birth_date = birth_date.replace(year=current_date.year + 1)
            res = birth_date - current_date
            return f"Days left until the birthday: {res.days}"
# ---------- End of class part ----------
# ---------- Func part ----------
def input_error(func):
    def inner(*a,**k):
        try:
            return func(*a,**k)
        except TypeError:
            return "TypeError???What???"
        except AttributeError:
            return "Якщо це повідомлення вилізло, то розробник десь накосячив :)"
        except IndexError:
            return "You entered wrong index, try again"
        except ValueError:
            return "You entered a wrong nuber of arguments, try again"
        except KeyError:
            return "Unknown command. Type 'help' to show a list of commands"
        except NameArgumentError:
            return "Wrong name format, try again. The name can contain only letters of the Latin alphabet"
        except PhoneArgumentError:
            return "Wrong phone format, try again. A phone number can only contain numbers and a '+' at the beginning"
        except PhoneExistsError:
            return "This phone number already exist in adress book"
        except PhoneDoesNotExistError:
            return "Phone number does not exist"
        except NoNameError:
            return "Сontact with that name does not exist"
        except BirthFormatError:
            return "Wrong birthday date format"
        except SearchValueError:
            return "You entered wrong search request"
    return inner


def main():
    print(info())
    with open("address_book.bin", "rb") as file:
        address_book.update(pickle.load(file))

    while True:
        main_input = input("Input command: ")
        body = parser(main_input)
        if type(body) == list:
            func = body[0](body[1], body[2], body[3])
            print(func)
        else:
            print(body)
        # if body[0] == "add" or body[0] == "add_birthday" or body[0] == "change" or body[0] == "remove":
        with open("address_book.bin", "wb") as file:
            pickle.dump(address_book, file)


@input_error
def parser(string):
    string = string.lower()
    string = re.sub(r" +", ' ', string)
    string = re.sub(r"\+", '', re.sub(r"^ +", '', string))
    com, first, second, third, other = "", "", "", "", ""
    flag = True
    for key, value in commands.items():
        if re.search(key, string):
            com = value
            if string != key:
                without_key = re.sub(key, '', string).removeprefix(' ')
                first, second, third, other = re.split(' ', without_key + "    ", maxsplit=3)
            flag = False
            break
    if flag:
        raise KeyError
    return [com, first, second, third, other]

#   -----handler's-----
def hello(*args,**kwargs):
    return "Hi, how can i help you? You can type 'help' to show a list of commands"


@input_error
def add(name, phone_number, *args,**kwargs):
    key = name.capitalize()
    if len(key) == False:
        raise ValueError
    if not re.fullmatch(r"[a-zA-z]+", key):
        raise NameArgumentError
    if phone_number:
        if number_checker(phone_number):
            raise PhoneExistsError
        if key in address_book:
            address_book[key].add_phone(phone_number)
            return f"Phone number {phone_number} successfully added to {key}'s contact"
        else:
            if not re.fullmatch(r"[0-9]+", phone_number):
                raise PhoneArgumentError
            address_book.add_record(Record(key, phone_number))
            return f"Contact {key}, with phone number {phone_number} successfully created"
    else:
        address_book.add_record(Record(key))
        return f"Contact {key} successfully created"


@input_error
def add_birthday(name, birth, *args, **kwargs):
    key = name.capitalize()
    if len(key) == False:
        raise ValueError
    if not re.fullmatch(r"[a-zA-z]+", key):
        raise NameArgumentError
    if key not in address_book:
        raise NoNameError
    if not re.fullmatch(r"[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{4}", birth):
        raise BirthFormatError
    address_book[key].add_birthday(birth)
    return f"{birth} set as birthday for {key} contact"


@input_error
def change(name, old_phone_number, phone_number,*args,**kwargs):
    key = name.capitalize()
    if key not in address_book:
        raise NoNameError
    if len(key) == False or len(phone_number) == False or len(old_phone_number) == False:
        raise ValueError
    if not re.fullmatch(r"[0-9]+", phone_number) or not re.fullmatch(r"[0-9]+", old_phone_number):
        raise PhoneArgumentError
    if number_checker(phone_number):
            raise PhoneExistsError
    if not number_checker(old_phone_number):
            raise PhoneDoesNotExistError
    address_book[key].change_phone(old_phone_number, phone_number)
    return f"{key}'s {old_phone_number} phone number successfully changed on {phone_number}"


@input_error
def remove_record(name, phone_number,*args,**kwargs):
    key = name.capitalize()
    if key not in address_book:
        raise NoNameError
    if not phone_number:
        address_book.delete_record(name=key)
        return f"Contact {key} successfully removed"
    else:
        if len(key) == False or len(phone_number) == False:
            raise ValueError
        if not number_checker(phone_number):
                raise PhoneDoesNotExistError
        address_book[key].delete_phone(phone_number)
        return f"{key}'s {phone_number} phone number successfully removed"


@input_error
def phone(name,*args,**kwargs):
    key = name.capitalize()
    if key not in address_book:
        raise NoNameError
    a = f"{key}'s phone(s) is {', '.join(i.value for i in address_book[key].phones)}." \
        if address_book[key].phones else f"No phone data in {key}'s contact"
    if address_book[key].birthday.value:
        b = address_book[key].days_to_birthday()
    else:
        b = ""
    return f"{a} {b}"

@input_error
def show(*args, **kwargs):
    if bool(address_book):
        page_number = 1
        con = '\n'
        for i in address_book.iterator():
            b = []
            for j in i:
                length = max([len(j.name.value) for j in i])
                a = f"{j.name.value: >{length}}: {', '.join([k.value for k in j.phones]) if j.phones else 'No data'}"
                b.append(a)
            page_output = f"Page {page_number}"
            con += f"{page_output: ^{length * 2 + 2}}" + '\n' + '\n'.join(b) + '\n'*2
            page_number += 1
        return con
    else:
        return "Address book is empty. Use 'add' command, to add a new contact"


def bye(*args, **kwargs):
    sys.exit("Good bye!")


def info(*args,**kwargs):
    s = [
    "\n"
    "Commands should be entered with ONE whitespace between them and/or arguments, without quotes",
    "|{:-^30}|{:-^42}|{:-^99}|".format("Command name", "Syntax", "Descrition"),
    "|{:-^30}|{:-^42}|{:-^99}|".format("help", "help", "Show this page"),
    "|{:-^30}|{:-^42}|{:-^99}|".format("hello", "hello", "Greetings (useless command)"),
    "|{:-^30}|{:-^42}|{:-^99}|".format("add", "add 'name' 'phone'", 
                                      "Create a contact with 'name' and 'phone'. (if contact exists, adds another 'phone')"),
    "|{:-^30}|{:-^42}|{:-^99}|".format("birthday", "birthday 'name' 'date'", "Add birthday to contact ('date' may be in dd.mm.yyyy format)"),
    "|{:-^30}|{:-^42}|{:-^99}|".format("change", "change 'name' 'old_phone' 'new_phone'", #
                                      "Change a phone number 'old_phone' of the selected contact 'name' on 'new_phone'"),
    "|{:-^30}|{:-^42}|{:-^99}|".format("remove", "remove 'name' 'phone'", "Deletes a phone number 'phone' from contact 'name'"),
    "|{:-^30}|{:-^42}|{:-^99}|".format("remove", "remove 'name'", "Deletes a 'name' contact"),
    "|{:-^30}|{:-^42}|{:-^99}|".format("phone", "phone 'name'", 
                                       "Show a phone number of the selected contect 'name' (and days to birthday, if birthday is specified)"),
    "|{:-^30}|{:-^42}|{:-^99}|".format("show all", "show all", "Show contact list"),
    "|{:-^30}|{:-^42}|{:-^99}|".format("search", "search 'phone', search 'name'", "Finds a phone number by name and conversely"),
    "|{:-^30}|{:-^42}|{:-^99}|".format("bye, close, exit, good bye", "any single word from the left list", "Exit this bot"),
    "\n"
    ]
    return "\n".join(s)


@input_error
def search(data, *args,**kwargs): 
    if re.fullmatch(r"[a-zA-z]+", data):
        results = address_book.search(name=data)
    elif re.fullmatch(r"[0-9]+", data):
        results = address_book.search(phone=data)
    else:
        raise SearchValueError
    con = '\n' + f"Search results for '{data}':" + '\n'
    b = []
    for j in results:
        length = max([len(j.name.value) for j in results])
        a = f"{j.name.value: >{length}}: {', '.join([k.value for k in j.phones]) if j.phones else 'No data'}"
        b.append(a)
    con += '\n'.join(b)
    return con
    

def number_checker(num):
    flag = False
    for v in address_book.values():
        for i in v.phones:
            if i.value == num:
                flag = True
                break
    return flag

# ---------- End of func part ----------
commands = {
"hello": hello, 
"add": add, 
"birthday": add_birthday,
"change": change, 
"remove": remove_record,
"phone": phone, 
"show all": show, 
"good bye": bye,
"bye": bye,
"close": bye, 
"exit": bye,
"help": info,
"search" : search
}

address_book = AddressBook()

if __name__ == "__main__":
    main()

menu_option_num = 3


def print_menu():
    print("________ McMahon Lab Reactor Data Pipeline ________")
    print("1) Log new samples")
    print("2) Add to old Samples")
    print("3) Exit")


def get_menu_option():
    raw_input = input("What would you like to do? ")
    try:
        menu_option = int(raw_input)
    except ValueError:
        print("Invalid option")
        menu_option = get_menu_option()

    if menu_option not in range(1, menu_option_num):
        print("Invalid option")
        menu_option = get_menu_option()
    return menu_option

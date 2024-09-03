def message_dont_run(name):
    print(f'This file\n    {name}\nshould not be run directly, please run main.py in the repo')
    input('Press enter to exit')

if __name__ == '__main__':
    message_dont_run(__file__)
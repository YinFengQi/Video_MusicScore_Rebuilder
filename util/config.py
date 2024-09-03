import configparser


def create_config(filename, params):
    config = configparser.ConfigParser()
    for section, settings in params.items():
        config[section] = {key: str(value) for key, value in settings.items()}
    with open(filename, 'w') as configfile:
        config.write(configfile)

if __name__ == '__main__':
    import auxiliary
    auxiliary.message_dont_run(__file__)
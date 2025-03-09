import numpy as np
import matplotlib.pyplot as plt
import telebot

bot = telebot.TeleBot('7930772688:AAF827Z8keqtKrD0hX3rEYVybgSmXg43mRc')
profiles = {}
init_settings = {
    'xmin': 0,
    'ymin': 0,
    'grid': False,
    'data': False,
    'y_val': '',
    'x_val': '',
    'x_values': np.array(None),
    'y_values': np.array(None),
    'path': '',
    'xfreq': 1,
    'yfreq': 1,
    'yticks': 1,
    'xticks': 1
}
id_bd = open('chatid', 'r')
for line in id_bd.readlines():
    buffer = line.split('\n')
    profiles[int(buffer[0])] = init_settings


def get_data(message):
    global profiles
    msg = message.text
    buffer = msg.split('\n')
    profiles[message.chat.id]['y_val'] = buffer[0]
    profiles[message.chat.id]['x_val'] = buffer[2]
    buffer_y = buffer[1].split(' ')
    buffer_x = buffer[3].split(' ')
    for i in range(len(buffer_y)):
        buffer_y[i] = float(buffer_y[i])
    for i in range(len(buffer_x)):
        buffer_x[i] = float(buffer_x[i])
    profiles[message.chat.id]['x_values'] = np.array(buffer_x)
    profiles[message.chat.id]['y_values'] = np.array(buffer_y)
    profiles[message.chat.id]['path'] = 'images/' + str(message.chat.id) + ".png"
    profiles[message.chat.id]['data'] = True
    profiles[message.chat.id]['xmax'] = max(profiles[message.chat.id]['x_values']) + max(
        profiles[message.chat.id]['x_values']) / 10
    profiles[message.chat.id]['ymax'] = max(profiles[message.chat.id]['y_values']) + max(
        profiles[message.chat.id]['y_values']) / 10

    buffer = profiles[message.chat.id]['ymax'] - profiles[message.chat.id]['ymin']
    buffer = str(buffer).split('.')
    if len(buffer[0]) == 1:
        if int(buffer[0]) == 0:
            profiles[message.chat.id]['yfreq'] = 0.1
        else:
            profiles[message.chat.id]['yfreq'] = 0.5
    else:
        profiles[message.chat.id]['yfreq'] = (10 ** (len(buffer[0]) - 2)) + (10 ** (len(buffer[0]) - 2)) * int(
            buffer[0][0])

    buffer = profiles[message.chat.id]['xmax'] - profiles[message.chat.id]['xmin']
    buffer = str(buffer).split('.')
    if len(buffer[0]) == 1:
        if int(buffer[0]) == 0:
            profiles[message.chat.id]['xfreq'] = 0.1
        else:
            profiles[message.chat.id]['xfreq'] = 0.5
    else:
        profiles[message.chat.id]['xfreq'] = (10 ** (len(buffer[0]) - 2)) + (10 ** (len(buffer[0]) - 2)) * int(
            buffer[0][0])


def createplot(message):
    settings = profiles[message.chat.id]
    x_values = settings['x_values']
    y_values = settings['y_values']
    x_val = settings['x_val']
    y_val = settings['y_val']
    path = settings['path']

    xy_values = x_values * y_values
    xsqr_values = x_values ** 2
    ysqr_values = y_values ** 2
    k = (xy_values.mean() - x_values.mean() * y_values.mean()) / (xsqr_values.mean() - x_values.mean() ** 2)
    b = y_values.mean() - k * x_values.mean()

    x0 = settings['xmin']
    y0 = k * x0 + b
    x1 = max(x_values) + max(x_values) / 10
    y1 = k * x1 + b
    fitx = [x0, x1]
    fity = [y0, y1]

    plt.plot(fitx, fity, color='black')
    plt.scatter(x_values, y_values, color='black')
    fsize = 15
    plt.xlabel(x_val, fontsize=fsize)
    plt.ylabel(y_val, fontsize=fsize)

    plt.yticks(np.arange(settings['ymin'], settings['ymax'], settings['yfreq']))
    plt.xticks(np.arange(settings['xmin'], settings['xmax'], settings['xfreq']))

    plt.yticks(np.arange(settings['ymin'], settings['ymax'], settings['yfreq'] / (settings['yticks'] + 1)), minor=True)
    plt.xticks(np.arange(settings['xmin'], settings['xmax'], settings['xfreq'] / (settings['xticks'] + 1)), minor=True)

    plt.ylim(profiles[message.chat.id]['ymin'], profiles[message.chat.id]['ymax'])
    plt.xlim(profiles[message.chat.id]['xmin'], profiles[message.chat.id]['xmax'])

    if settings['grid']:
        plt.grid(which='minor', linewidth='0.5', color='lightgray')
        plt.grid(axis='both')

    plt.savefig(path)
    plt.show()
    return {'k': k, 'b': b}


@bot.message_handler(commands=['start'])
def start_message(message):
    id_bd = open('chatid', 'r+')
    for line in id_bd.readlines():
        if line == str(message.chat.id) + "\n":
            break
    else:
        id_bd.write(str(message.chat.id) + '\n')

    global profiles
    profiles[message.chat.id] = init_settings
    bot.send_message(message.chat.id,
                     text="Отправь данные или воспользуя помощью: /help".format(
                         message.from_user))


@bot.message_handler(commands=['help'])
def help_message(message):
    help_text = ('После отправки данных настройки сбрасывются!\n'
                 'Доступные команды:\n'
                 '/grid - включить/выключить сетку\n'
                 '/plot - создать график\n'
                 '/xfreq T - установить цену деления оси x = T\n'
                 '/yfreq T - установить цену деления оси y = T\n'
                 '/xtick T - установить количество дополнительных делений оси x = T\n'
                 '/ytick T - установить количество дополнительных делений оси y = T\n'
                 'Формат данных:')
    bot.send_message(message.chat.id,
                     text=help_text.format(
                         message.from_user))
    bot.send_message(message.chat.id,
                     text="Название оси y\n0.38 0.54 0.68\nНазвание оси x\n1 2 3".format(
                         message.from_user))


@bot.message_handler(commands=['xtick'])
def set_xtick(message):
    buffer = message.text.split(' ')
    if len(buffer) != 2:
        bot.send_message(message.chat.id, text="Wrong command format")
        return
    profiles[message.chat.id]['xticks'] = int(buffer[1])


@bot.message_handler(commands=['ytick'])
def set_ytick(message):
    buffer = message.text.split(' ')
    if len(buffer) != 2:
        bot.send_message(message.chat.id, text="Wrong command format")
        return
    profiles[message.chat.id]['yticks'] = int(buffer[1])


@bot.message_handler(commands=['xfreq'])
def set_xfreq(message):
    buffer = message.text.split(' ')
    if len(buffer) != 2:
        bot.send_message(message.chat.id, text="Wrong command format")
        return
    profiles[message.chat.id]['xfreq'] = float(buffer[1])


@bot.message_handler(commands=['yfreq'])
def set_yfreq(message):
    buffer = message.text.split(' ')
    if len(buffer) != 2:
        bot.send_message(message.chat.id, text="Wrong command format")
        return
    profiles[message.chat.id]['yfreq'] = float(buffer[1])


@bot.message_handler(commands=['grid'])
def switch_grid(message):
    grid = profiles[message.chat.id]['grid']
    if grid:
        bot.send_message(message.chat.id,
                         text="Сетка выключена".format(
                             message.from_user))
    else:
        bot.send_message(message.chat.id,
                         text="Сетка включена".format(
                             message.from_user))
    profiles[message.chat.id]['grid'] = not profiles[message.chat.id]['grid']


@bot.message_handler(commands=['plot'])
def plot(message):
    if not profiles[message.chat.id]['data']:
        bot.send_message(message.chat.id, text='Нет данных!')
        return
    else:
        send_mnk(message)


@bot.message_handler(content_types=['text'])
def read_message(message):
    # get_data(message)
    try:
        get_data(message)
    except:
        bot.send_message(message.chat.id, "Неизвестная команда/неправильные данные")
        return
    send_mnk(message)


def send_mnk(message):
    result_dict = createplot(message)
    k = str(result_dict['k'])
    b = str(result_dict['b'])

    bot.send_message(message.chat.id, text="y=kx+b, где:\nk = " + k + "\nb = " + b)
    bot.send_document(message.chat.id, open(r'' + profiles[message.chat.id]['path'], 'rb'))


bot.polling(non_stop=True, interval=0)
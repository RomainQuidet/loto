#!/usr/bin/env python3

import urllib.request
import zipfile
import csv
import random
import sys, getopt

def download():
    """ Download main Loto results zip file """
    print('Downloading loto results')
    results_zip = urllib.request.urlopen('https://www.fdj.fr/generated/game/loto/loto2017.zip')
    if results_zip is None:
        print('Error: can\'t download file')
        return None
    if results_zip.getcode() != 200:
        print('Error: can\'t download file')
        return None
    print('OK')
    return results_zip

def extract(zip_file):
    """ Extract Loto main csv file """
    print('Extract loto results')
    with open('loto2017.zip','wb') as output:
      output.write(zip_file.read())
    with zipfile.ZipFile('loto2017.zip') as myzip:
        files_list = myzip.namelist()
        if files_list[0] != 'loto2017.csv':
            print('Error: can\'t find csv file in zip')
            return
        created_file = myzip.extract('loto2017.csv')
        if created_file is None:
            print('Error: can\'t create csv file')
            return
        print('Extracted file: ' + created_file)
        print('OK')
        return created_file
    return None

def simulate_last_draw(csv_file_path):
    """ Simulate a Loto grid against last result """
    print('Simulate Loto bet on last result')
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        last_draw_row = next(reader)
        print_draw_summary(last_draw_row)
        print(' ')
        available_balls_range = range(1, 50)
        my_flash = random.sample(available_balls_range, k=5)
        my_flash.sort()
        my_lucky_number = random.randint(1, 10)
        print('Creating your flash')
        print('=> {}+{}'.format(my_flash, my_lucky_number))
        gain = compute_gain(last_draw_row, my_flash, my_lucky_number)
        print('This makes you {}€'.format(gain))

def compute_gain(row, balls, lucky_number):
    winning_balls = []
    for i in range(1, 6):
        winning_balls.append(int(row['boule_'+str(i)]))
    winning_lucky_number = int(row['numero_chance'])
    common_balls = [value for value in balls if value in winning_balls]
    common_balls_len = len(common_balls)
    rank = 10
    if common_balls_len >= 2:
        rank = 12 - 2 * common_balls_len
    if lucky_number == winning_lucky_number:
        rank = rank - 1
    if rank < 10:
        return float(row['rapport_du_rang' + str(rank)].replace(',', '.'))
    else:
        return 0

def print_draw_summary(row):
    """ Print a summary of a csv row dictionary """
    summary = 'Draw #' + row['annee_numero_de_tirage']
    summary = summary + ' - ' + row['date_de_tirage']
    summary = summary + ' - ' + row['jour_de_tirage']
    print(summary)
    print('Winning combination: ' + row['combinaison_gagnante_en_ordre_croissant'])
    dash = '-' * 36
    for i in range(10):
        if i == 0:
            print(dash)
            print('{:<14s}{:>7s}{:>14s}'.format('Rank','Winners','Gain'))
            print(dash)
        else:
            print('{:<14s}{:>7s}{:>14s}'.format(str(i) + '('+rank_definition(i)+')', row['nombre_de_gagnant_au_rang' + str(i)], row['rapport_du_rang' + str(i)] + '€'))

def compute_balls_statistics(csv_file_path, max_rows=None):
    """ Computes balls statistics over last draws """
    print('Balls statistics')
    balls = range(1,50)
    balls_appearance = {}
    for ball in balls:
        balls_appearance[ball] = 0
    row_counter = 0
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            row_counter += 1
            for i in range(1, 6):
                ball = int(row['boule_'+str(i)])
                balls_appearance[ball] = 1 + balls_appearance[ball]
            if max_rows != None:
                if row_counter > max_rows:
                    break
    dash = '-' * 30
    each_ball_stat = 1/49 + 1/48 + 1/47 + 1/46 + 1/45
    balls_statistics = []
    for i in range(1,50):
        stat = balls_appearance[i] / row_counter
        dist = stat - each_ball_stat
        balls_statistics.append((i, stat, dist))
    sorted_stats = sorted(balls_statistics, key=lambda x:x[2])
    for i in range(49):
        if i == 0:
            print(dash)
            print('{:<7s}{:<12s}{:<12s}'.format('Ball','Stat','Dist'))
            print(dash)
        stats = sorted_stats[i]
        ball = stats[0]
        stat = stats[1]
        dist = stats[2]
        print('{:<7d}{:<12f}{:<12f}'.format(ball, stat, dist))

def rank_definition(rank):
    switcher = {
        1: "5+1",
        2: "5+0",
        3: "4+1",
        4: "4+0",
        5: "3+1",
        6: "3+0",
        7: "2+1",
        8: "2+0",
        9: "1+1 / 0+1"
    }
    return switcher.get(rank, "Invalid rank")

def print_separator(number):
    print('{:-<20}'.format(str(number) + ' '))

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hda:")
    except getopt.GetoptError:
        print ('test.py -h')
        sys.exit(2)
    needs_update_file = True
    show_balls_stats = False
    balls_stats_max_row = 0
    for opt, arg in opts:
        if opt == '-h':
            print('test.py to download Loto file and simulate a flash on last result')
            print('test.py -d to skip Loto file download')
            print('test.py -a 50 to show balls statistics over last 50 draws')
            sys.exit()
        elif opt in ("-d"):
            needs_update_file = False
        elif opt in ("-a"):
            show_balls_stats = True
            balls_stats_max_row = int(arg)
    separator_index = 1
    csv_path = 'loto2017.csv'
    if needs_update_file == True:
        print_separator(separator_index)
        separator_index += 1
        zip_file = download()
        print_separator(separator_index)
        separator_index += 1
        csv_path = extract(zip_file)
    print_separator(separator_index)
    if show_balls_stats == True:
        compute_balls_statistics(csv_path, balls_stats_max_row)
    else:
        simulate_last_draw(csv_path)

if __name__ == "__main__":
   main(sys.argv[1:])

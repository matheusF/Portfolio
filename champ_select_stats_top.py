import pandas as pd
import numpy as np
import re
import time
import itertools

import dataframe_image as dfi
import sys
import pytesseract
from PIL import Image

import winsound
import pyautogui

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def four_points():
    time.sleep(5)
    for i in range(4):
        print(pyautogui.position())
        winsound.Beep(2000, 300)
        time.sleep(2)
        
def wait_select(imagem):
    while True:
        pyautogui.screenshot(imagem)
        image = Image.open(imagem)
        enemy1 = image.crop((509, 80, 930, 114))
        name_enemy1 = pytesseract.image_to_string(enemy1)[0:-1].lower()
        if name_enemy1 == "selecione o seu campeao!":
            break

def enemy_list():
    #button_lol = pyautogui.locateOnScreen('logo_lol.png', grayscale=True, confidence=0.9)
    #pyautogui.click(pyautogui.center(button_lol))
    
    #pyautogui.click(x=555, y=874)
    #time.sleep(0.1)
    
    wait_select("screenshot_champion_select.png")
    
    pyautogui.screenshot("screenshot_champion_select.png")
    
    # "C:\\Users\\matht\\OneDrive\\Área de Trabalho\\imagem-teste2.png"
    image = Image.open("screenshot_champion_select.png")

    enemy1 = image.crop((1120, 182, 1266, 210))
    name_enemy1 = pytesseract.image_to_string(enemy1)[0:-1].lower()

    enemy2 = image.crop((1120, 263, 1266, 290))
    name_enemy2 = pytesseract.image_to_string(enemy2)[0:-1].lower()

    enemy3 = image.crop((1120, 342, 1266, 365))
    name_enemy3 = pytesseract.image_to_string(enemy3)[0:-1].lower()

    enemy4 = image.crop((1120, 423, 1266, 445))
    name_enemy4 = pytesseract.image_to_string(enemy4)[0:-1].lower()

    enemy5 = image.crop((1120, 505, 1266, 526))
    name_enemy5 = pytesseract.image_to_string(enemy5)[0:-1].lower()

    return [name_enemy1, name_enemy2, name_enemy3, name_enemy4, name_enemy5]

def enemy_list_ord(enemys, mp_champs_list):
    for i, enemy in enumerate(enemys):
        enemys[i] = re.sub("[^a-z]", "", enemy)
    enemys_list_ordened = [0,0,0,0,0]
    enemys_position = [0,0,0,0,0]
    cont = 5
    for enemy in enemys:
        if enemy == 'prximoaescolher':
            cont -= 1
    cont1 = 0
    i_continue = []
    j_continue = []
    while cont > 0:
        for i in range(5):
            for j in range(5):
                if i in i_continue or j in j_continue:
                    continue
                elif cont1 >= len(mp_champs_list[j]):
                    if cont1 > 300:
                        cont = 0
                    else:
                        continue
                elif enemys[i] == mp_champs_list[j][cont1]:
                    enemys_list_ordened[j] = enemys[i]
                    enemys_position[j] = cont1
                    #print(i, j, cont1)
                    cont -= 1
                    i_continue.append(i)
                    j_continue.append(j)
        cont1 += 1

    return enemys_list_ordened, enemys

def mp_champs(lane):
    table = []
    for lane_var in ['top', 'jg', 'mid', 'adc', 'sup']:
        if lane == 'top':
            table.append(pd.read_csv('wr_tables_top\\wr'+ lane_var +'.csv', index_col=0).index.tolist())
        if lane == 'jungle':
            table.append(pd.read_csv('wr_tables_jg\\wr'+ lane_var +'.csv', index_col=0).index.tolist())
        if lane == 'support':
            table.append(pd.read_csv('wr_tables_sup\\wr'+ lane_var +'.csv', index_col=0).index.tolist())
    return table

def tablewr(enemy_ordered, lane):
    table = []
    for enemy, enemy_lane in zip(enemy_ordered, ['top', 'jg', 'mid', 'adc', 'sup']):
        if enemy != 0:
            if lane == 'top':
                df_saved = pd.read_csv('wr_tables_top\\wr'+ enemy_lane +'.csv', index_col=0)
                table.append(df_saved[df_saved.index == enemy].values.tolist()[0])
            if lane == 'jungle':
                df_saved = pd.read_csv('wr_tables_jg\\wr'+ enemy_lane +'.csv', index_col=0)
                table.append(df_saved[df_saved.index == enemy].values.tolist()[0])
            if lane == 'support':
                df_saved = pd.read_csv('wr_tables_sup\\wr'+ enemy_lane +'.csv', index_col=0)
                table.append(df_saved[df_saved.index == enemy].values.tolist()[0])
        else:
            table.append([0,0,0])
    return table

def mychampslist(lane):
    if lane == 'top':
        df_saved = pd.read_csv('wr_tables_top\\wrtop.csv', index_col=0)
        return df_saved.columns
    if lane == 'jungle':
        df_saved = pd.read_csv('wr_tables_jg\\wrjg.csv', index_col=0)
        return df_saved.columns
    if lane == 'support':
        df_saved = pd.read_csv('wr_tables_sup\\wrsup.csv', index_col=0)
        return df_saved.columns

def evaluate_list_enemys(enemy_list, mp_champ_table):
    position = [1000,1000,1000,1000,1000]
    for i, enemy in enumerate(enemy_list):
        for j in range(len(mp_champ_table[i])):
            if enemy == mp_champ_table[i][j]:
                position[i] = j
    return max(position)

def atualized_enemy_list(enemy_champs, lane):
    evaluations = []
    pertutations_enemy_list = []
    for perm in itertools.permutations(enemy_champs):
        evaluations.append(evaluate_list_enemys(perm, mp_champs(lane)))
        pertutations_enemy_list.append(perm)
    return pertutations_enemy_list[np.argmin(np.array(evaluations))]

def final_table(lane, tier, patch):
    mychamps = mychampslist(lane)
    mp_champs_table = mp_champs(lane)
    enemy_list_ordered, list_enemy_champs = enemy_list_ord(enemy_list(), mp_champs_table)
    if 'prximoaescolher' not in list_enemy_champs:
        enemy_list_ordered = atualized_enemy_list(list_enemy_champs, lane)
        
    aux = tablewr(enemy_list_ordered, lane)
    df = pd.DataFrame(aux, columns=mychamps, index=enemy_list_ordered)

    meandf = df[df.index != 0].mean().to_frame().T
    meandf = meandf[meandf.index == 0]
    meandf.index = ['mean wr']
    winsound.Beep(2000, 300)
    return pd.concat([df, meandf.round(1)])

N_erro = 0
while True:
    try:
        print(final_table('top', 'all', '30'))
        print("\n")
        if N_erro > 0:
            print("Número de erros: " + str(N_erro))
        time.sleep(60)
        break
    except:
        N_erro += 1
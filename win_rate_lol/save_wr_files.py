import pandas as pd
import numpy as np
import re
import time

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import dataframe_image as dfi
import sys
import pytesseract
from PIL import Image

import winsound
import time
import pyautogui

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

driver = webdriver.Chrome()

driver.get('https://lolalytics.com/lol/tierlist/?lane=top&tier=all')
driver.maximize_window()
#driver.find_elements(By.CSS_SELECTOR, 'button.ncmp__btn')[1].click()
elem = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR,'button.ncmp__btn'))
)
elem[1].click()

def mp_champs(lane, tier, patch):
    driver.get('https://lolalytics.com/lol/tierlist/?lane='+ lane +'&tier='+ tier +'&patch='+patch)
    for i in range(20):
        if driver.find_elements(By.CSS_SELECTOR, 'div.z-20 div div')[i].text == 'Pick':
            driver.find_elements(By.CSS_SELECTOR, 'div.z-20 div div')[i].click()
            break
    time.sleep(2)
    topchamps = []
    #most picked champions
    elem = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR,'.my-auto.justify-center.flex a'))
    )
    for i in elem:
        if i.text != '':
            topchamps.append(re.sub("'|\s|\.", '',i.text.lower()))
    for i, champ in enumerate(topchamps):
        if champ == 'renataglasc':
            topchamps[i] = 'renata'
    return topchamps

def champx1wr(champ1, champ2, lane1, lane2, tier, patch):
    if champ1 == champ2:
        return 0
    else:
        driver.get('https://lolalytics.com/lol/'+ champ1 +'/vs/'+ champ2 +'/build/?lane='+ lane1 +'&vslane='+ lane2 +
                   '&tier='+ tier +'&patch='+patch)
        wr = driver.find_elements(By.CSS_SELECTOR, 'div.w-44 div.mb-1.font-bold')[0].text[:4]
        return round(float(re.sub("%", "", wr)), 1)

def mychampswr(mychamps, champ, lane1, lane2, tier, patch):
    wrs = []
    for c in mychamps:
        wrs.append(champx1wr(c, champ, lane1, lane2, tier, patch))
    return wrs

def tablex1wr(topchamps, mychamps, lane1, lane2, tier, patch):
    topchamps = topchamps
    table = []
    for champ in topchamps:
        try:
            table.append(mychampswr(mychamps, champ, lane1, lane2, tier, patch))
        except:
            print(champ)
    return table

def save_wr_all_lanes(mychamps, lane, tier, patch):
    lanes = ['top', 'jungle', 'middle', 'bottom', 'support']
    num_champ_in_lane = [50, 50, 50, 30, 40]
    if lane == 'top':
        arq_names = ['wr_tables_top\\wrtop.csv', 'wr_tables_top\\wrjg.csv', 'wr_tables_top\\wrmid.csv',
                     'wr_tables_top\\wradc.csv', 'wr_tables_top\\wrsup.csv']
    if lane == 'jungle':
        arq_names = ['wr_tables_jg\\wrtop.csv', 'wr_tables_jg\\wrjg.csv', 'wr_tables_jg\\wrmid.csv',
                     'wr_tables_jg\\wradc.csv', 'wr_tables_jg\\wrsup.csv']
    if lane == 'support':
        arq_names = ['wr_tables_sup\\wrtop.csv', 'wr_tables_sup\\wrjg.csv', 'wr_tables_sup\\wrmid.csv',
                     'wr_tables_sup\\wradc.csv', 'wr_tables_sup\\wrsup.csv']
    for l2, num, arq_name in zip(lanes, num_champ_in_lane, arq_names):
        topchamps = mp_champs(l2, tier, patch)[0:num]
        tablewr = tablex1wr(topchamps, mychamps, lane, l2, tier, patch)
        #print(len(tablewr), len(topchamps))
        pd.DataFrame(tablewr, columns=mychamps, index=topchamps).to_csv(arq_name)
    return 0

#mychamps = ['yorick', 'malphite', 'urgot', 'drmundo'] # top
#mychamps = ['nocturne', 'amumu', 'briar'] # jungle
mychamps = ['sona', 'zyra', 'yuumi'] # support
save_wr_all_lanes(mychamps, 'support', 'all', '30')
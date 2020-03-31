# -*- coding: utf-8 -*

from kivy.config import Config
# ウィンドウサイズの設定
Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '720')
import kivy
kivy.require('1.9.1')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.properties import Clock
from kivy.properties import BooleanProperty
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.utils import get_color_from_hex
from kivy.resources import resource_add_path
from kivy.factory import Factory
from kivy.clock import Clock

import os
import csv
import re
import codecs
import time
import math
import glob
import pygame.mixer
import datetime
from calendar import Calendar
from dateutil.relativedelta import relativedelta

# ファイルのパス(main.pyがあるフォルダの中にあるファイルの絶対パス)
# file_path = os.path.dirname(os.path.abspath(__file__))

# フォントの設定
resource_add_path('fonts')
LabelBase.register(DEFAULT_FONT, 'ipaexg.ttf')


# 各種データ一時保存用
class Holder():
    status = ""
    


class PopupList(BoxLayout):
    schedule = StringProperty("")
    cancel = ObjectProperty(None)
    delete = ObjectProperty(None)
    save = ObjectProperty(None)
    
    @classmethod
    def set_label(self, txt):
        self.schedule = txt


        
class PopupChange(BoxLayout):
    cancel = ObjectProperty(None)
    up_down = ObjectProperty(None)
    year_label = StringProperty("")
    month_label = StringProperty("")
    
    @classmethod
    def changeLabel(self, year, month):
        self.year_label = str(year)
        self.month_label = str(month)

        
        
class PopupSchedule(BoxLayout):
    cancel = ObjectProperty(None)
    schedule_list = StringProperty("")
    
    @classmethod
    def set_schedule(self, txt):
        self.schedule_list = txt
        
    
    
class Any_Calendar(BoxLayout):
    text = StringProperty()
    year = ObjectProperty(int())
    month = ObjectProperty(int())
    day = ObjectProperty(int())
    background = ObjectProperty(None)
    background_through = ObjectProperty(int())
    
    lrc_r = ObjectProperty(int()) # 歌詞の色 r
    lrc_g = ObjectProperty(int()) # 歌詞の色 g
    lrc_b = ObjectProperty(int()) # 歌詞の色 b
    lrc_through = ObjectProperty(int()) # 歌詞の透過度(一応)

        
    # アプリ実行時の初期化の処理
    def __init__(self, **kwargs):
        super(Any_Calendar, self).__init__(**kwargs)
        Clock.schedule_once(self.on_start)
    
    
    def on_start(self, *args):
        # ファイルがなければ作成
        if not os.path.isfile(os.getcwd() + "/schedule.csv"):
            f = open("schedule.csv","w")
            f.close()
        
        # 起動した日を初期値としてセット
        self.year = datetime.date.today().year
        self.month = datetime.date.today().month
        self.day = datetime.date.today().day
        self.ids.month_label.text = str(self.year) + '/' + str(self.month)
        PopupChange.changeLabel(self.year, self.month)
        
        self.change_day(self.year, self.month) # 日付のセット
        self.read_schedule() # その月の予定を書き出す
        # フォーマット指定の仕方：datetime.datetime.today().strftime("%Y/%m")
        
        # 画像の読み込み
        self.setImage()
    
    
    # 画像のセット
    def setImage(self):
        """名前が年月または月の画像があれば読み込み、対応する年月で表示する"""
        self.background_through = 1
        
        pictures = glob.glob('pictures/*')
        target = "image/default.jpg"
        
        for i in range(len(pictures)):
            filename, ext = os.path.splitext(pictures[i])

            if filename == str('pictures/' + str(self.year) + str(self.month)):
                target = pictures[i]
                break
                
            elif filename == str('pictures/' + str(self.month)):
                target = pictures[i]
                break
                
        self.background = target
    
        
        
    
    # カレンダーの各日付のボタンを押した時の処理
    def select(self, row, col):
        if not self.get_btn_txt(row, col) == "":
            schedule = self.get_btn_txt(row, col)
            schedule_split = schedule.split('\n')
            text = ""
            if len(schedule_split) == 1:
                text = text + '[' + str(self.year) + '/' + str(self.month)  + '/' + str(schedule_split[0]) + str(self.get_week_day(col)) + ']' + '\n' + '\nNone'
            else:
                for i in range(len(schedule_split)):
                    if i == 0: text = text + '['  + str(self.year) + '/' + str(self.month)  + '/' + str(schedule_split[0]) + str(self.get_week_day(col)) + ']\n'
                    else: text = text + '\n' + schedule_split[i]
            PopupList.set_label(text)

            content = PopupList(cancel=self.cancel, delete=self.delete, save=self.save)
            self.popup = Popup(title="Schedule", content=content, size_hint=(.8, .7))
            self.popup.open()

            #self.add_btn_txt(row, col, "\naaa")

            #date = datetime.datetime(2019,10,13)
            #print(self.__get_week_number(date), (date.weekday() - 6) % 7)
    
    
    
    # < ボタンを押した時の処理
    def buttonBack(self):
        this_month = datetime.datetime(self.year, self.month, self.day)
        month_ago = this_month - relativedelta(months=1)
        if month_ago.month == 0: month_ago.month = 12
        
        self.year = month_ago.year
        self.month = month_ago.month
        self.day = month_ago.day
        self.ids.month_label.text = str(self.year) + '/' + str(self.month)
        self.change_day(self.year, self.month)
        self.read_schedule()
        self.setImage()
    
    
    
    # > ボタンを押した時の処理
    def buttonNext(self):
        this_month = datetime.datetime(self.year, self.month, self.day)
        month_ago = this_month + relativedelta(months=1)
        if month_ago.month == 13: month_ago.month = 1
            
        self.year = month_ago.year
        self.month = month_ago.month
        self.day = month_ago.day
        self.ids.month_label.text = str(self.year) + '/' + str(self.month)
        self.change_day(self.year, self.month)
        self.read_schedule()
        self.setImage()
    
    
    
    # ポップアップのキャンセルボタン
    def cancel(self):
        self.change_day(self.year, self.month)
        self.read_schedule()
        self.popup.dismiss()
        
    
    # ポップアップのdeleteボタン。指定したスケジュールをファイルから削除する
    # 削除したいスケジュールをフォームに入力した状態でdeleteを押すとそのスケジュールが削除される。
    def delete(self, month, day, txt):
        """csvファイルからデータを読み出す"""
        schedule_list = []
        f = open("schedule.csv","r")
        reader = csv.reader(f)
        schedule_list = [row for row in reader]
        f.close()
        
        """入力されたテキストの行のみ削除して上書き"""
        new_schedule = []
        for schedule in schedule_list:
            if schedule[1] == month and schedule[2] == day and schedule[3] == txt:
                pass
            else:
                new_schedule.append(schedule)
         
        f = open("schedule.csv", "w")
        for i in new_schedule:
            writer = csv.writer(f)
            writer.writerow([int(i[0]), int(i[1]), int(i[2]), i[3]])
        f.close()
    
    
    
    # ポップアップのsaveボタン
    def save(self, year, month, day, txt):
        if str(year) == "" or str(year).isdigit():
            if str(month).isdigit() and str(day).isdigit():
                if (1 <= int(month) <= 12) and (1 <= int(day) <= 31):
                    f = open("schedule.csv","a")
                    writer = csv.writer(f)
                    if str(year) == "": year = 0
                    writer.writerow([year, month, day, txt])
                    f.close()
    
    
    
    # カレンダーの年月を変更するポップアップの表示
    def open_change_updown(self):
        PopupChange.changeLabel(self.year, self.month)
        
        content = PopupChange(up_down=self.up_down, cancel=self.cancel)
        self.popup = Popup(title="Change year/month", content=content, size_hint=(.8, .7))
        self.popup.open()
    
    
    
    # カレンダーの年月を変更する
    def up_down(self, flag):
        if flag == "up_year":
            self.year += 1
        elif flag == "up_month":
            self.month += 1
            if self.month == 13:
                self.month = 1
                self.year += 1
        elif flag == "down_year":
            self.year -= 1
            if self.year == 0:
                self.year = datetime.date.today().year
        elif flag == "down_month":
            self.month -= 1
            if self.month == 0:
                self.month = 12
                self.year -= 1
        else:
            print("error.")
    
        self.ids.month_label.text = str(self.year) + '/' + str(self.month)
        self.change_day(self.year, self.month)
        self.read_schedule()
        self.setImage()
        PopupChange.changeLabel(self.year, self.month)
        
        self.popup.dismiss()
        content = PopupChange(up_down=self.up_down, cancel=self.cancel)
        self.popup = Popup(title="Change year/month", content=content, size_hint=(.8, .7))
        self.popup.open()
        
    
    
    # スケジュールリストを表示
    def open_list(self):
        """csvファイルからデータを読み出す"""
        schedule_list = []
        f = open("schedule.csv","r")
        reader = csv.reader(f)
        schedule_list = [row for row in reader]
        f.close()
        
        """スケジュールリストを日付順にソートする"""
        schedule_list = sorted(schedule_list, key=lambda x: int(x[2]))
        schedule_list = sorted(schedule_list, key=lambda x: int(x[1]))
        
        schedule_text = ""
        for schedule in schedule_list:
            if schedule[0] == "0": schedule[0] = "*"
            text = "  " + str(schedule[0]) + '/' + str(schedule[1]) + '/' + str(schedule[2]) + ': ' + str(schedule[3])
            schedule_text = schedule_text + text + "\n"
            
        PopupSchedule.set_schedule(schedule_text)
        
        content = PopupSchedule(cancel=self.cancel)
        self.popup = Popup(title="Schedule List", content=content, size_hint=(.8, .7))
        self.popup.open()
        
    
    
    # schedule.csvから予定を取得してカレンダーに書き出す
    def read_schedule(self):
        """csvファイルからデータを読み出す"""
        schedule_list = []
        f = open("schedule.csv","r")
        reader = csv.reader(f)
        schedule_list = [row for row in reader]
        f.close()
        
        """読み込んだデータを書き出す"""
        for schedule in schedule_list:
            try:
                if schedule[0] == '0' or schedule[0] == str(self.year):
                    if schedule[1] == str(self.month):
                        date = datetime.datetime(self.year, int(schedule[1]), int(schedule[2]))
                        n_week, week_day = self.__get_week_number(date), (date.weekday() - 6) % 7
                        self.add_btn_txt(n_week, week_day, '\n' + schedule[3])
            except:
                pass
    
    
    
    # 年/月を指定するとその年/月の内容にボタンの日付を更新する
    def change_day(self, year, month):
        """最初に各ラベルを初期化"""
        self.clr_btn_txt()
            
        cl = Calendar(firstweekday=6) # タプル(日付,曜日)が週毎に返される
        month_cl = cl.monthdays2calendar(year, month)
        i = 1 # "1"週目で初期化
        j = 0
        for week in month_cl:
            # weekは[1週目],[2週目],...
            for day in week:
                # dayは週毎の各日の(日付,曜日)
                if day[1] + 1 == 7: j = 0
                else: j = day[1] + 1
                
                if not day[0] == 0: self.set_btn_txt(i, j, str(day[0]))
            i += 1
                
    
    
    # 各ボタンのラベルを初期化
    def clr_btn_txt(self):
        for i in range(1,7):
            for j in range(0,7):
                self.set_btn_txt(i, j, "")
        
        
    
    # 指定したボタンのテキストを取得
    def get_btn_txt(self, row, col):
        txt = ""
        
        if row == 1:
            if col == 0: txt = self.ids.b10.text
            elif col == 1: txt = self.ids.b11.text
            elif col == 2: txt = self.ids.b12.text
            elif col == 3: txt = self.ids.b13.text
            elif col == 4: txt = self.ids.b14.text
            elif col == 5: txt = self.ids.b15.text
            elif col == 6: txt = self.ids.b16.text
            
        elif row == 2:
            if col == 0: txt = self.ids.b20.text
            elif col == 1: txt = self.ids.b21.text
            elif col == 2: txt = self.ids.b22.text
            elif col == 3: txt = self.ids.b23.text
            elif col == 4: txt = self.ids.b24.text
            elif col == 5: txt = self.ids.b25.text
            elif col == 6: txt = self.ids.b26.text
            
        elif row == 3:
            if col == 0: txt = self.ids.b30.text
            elif col == 1: txt = self.ids.b31.text
            elif col == 2: txt = self.ids.b32.text
            elif col == 3: txt = self.ids.b33.text
            elif col == 4: txt = self.ids.b34.text
            elif col == 5: txt = self.ids.b35.text
            elif col == 6: txt = self.ids.b36.text
            
        elif row == 4:
            if col == 0: txt = self.ids.b40.text
            elif col == 1: txt = self.ids.b41.text
            elif col == 2: txt = self.ids.b42.text
            elif col == 3: txt = self.ids.b43.text
            elif col == 4: txt = self.ids.b44.text
            elif col == 5: txt = self.ids.b45.text
            elif col == 6: txt = self.ids.b46.text
            
        elif row == 5:
            if col == 0: txt = self.ids.b50.text
            elif col == 1: txt = self.ids.b51.text
            elif col == 2: txt = self.ids.b52.text
            elif col == 3: txt = self.ids.b53.text
            elif col == 4: txt = self.ids.b54.text
            elif col == 5: txt = self.ids.b55.text
            elif col == 6: txt = self.ids.b56.text
            
        elif row == 6:
            if col == 0: txt = self.ids.b60.text
            elif col == 1: txt = self.ids.b61.text
            elif col == 2: txt = self.ids.b62.text
            elif col == 3: txt = self.ids.b63.text
            elif col == 4: txt = self.ids.b64.text
            elif col == 5: txt = self.ids.b65.text
            elif col == 6: txt = self.ids.b66.text
                
        return txt
    
    
    
    # 指定したボタンにテキストを記述
    def set_btn_txt(self, row, col, txt):
        if row == 1:
            if col == 0: self.ids.b10.text = txt
            elif col == 1: self.ids.b11.text = txt
            elif col == 2: self.ids.b12.text = txt
            elif col == 3: self.ids.b13.text = txt
            elif col == 4: self.ids.b14.text = txt
            elif col == 5: self.ids.b15.text = txt
            elif col == 6: self.ids.b16.text = txt
            
        elif row == 2:
            if col == 0: self.ids.b20.text = txt
            elif col == 1: self.ids.b21.text = txt
            elif col == 2: self.ids.b22.text = txt
            elif col == 3: self.ids.b23.text = txt
            elif col == 4: self.ids.b24.text = txt
            elif col == 5: self.ids.b25.text = txt
            elif col == 6: self.ids.b26.text = txt
            
        elif row == 3:
            if col == 0: self.ids.b30.text = txt
            elif col == 1: self.ids.b31.text = txt
            elif col == 2: self.ids.b32.text = txt
            elif col == 3: self.ids.b33.text = txt
            elif col == 4: self.ids.b34.text = txt
            elif col == 5: self.ids.b35.text = txt
            elif col == 6: self.ids.b36.text = txt
            
        elif row == 4:
            if col == 0: self.ids.b40.text = txt
            elif col == 1: self.ids.b41.text = txt
            elif col == 2: self.ids.b42.text = txt
            elif col == 3: self.ids.b43.text = txt
            elif col == 4: self.ids.b44.text = txt
            elif col == 5: self.ids.b45.text = txt
            elif col == 6: self.ids.b46.text = txt
            
        elif row == 5:
            if col == 0: self.ids.b50.text = txt
            elif col == 1: self.ids.b51.text = txt
            elif col == 2: self.ids.b52.text = txt
            elif col == 3: self.ids.b53.text = txt
            elif col == 4: self.ids.b54.text = txt
            elif col == 5: self.ids.b55.text = txt
            elif col == 6: self.ids.b56.text = txt
            
        elif row == 6:
            if col == 0: self.ids.b60.text = txt
            elif col == 1: self.ids.b61.text = txt
            elif col == 2: self.ids.b62.text = txt
            elif col == 3: self.ids.b63.text = txt
            elif col == 4: self.ids.b64.text = txt
            elif col == 5: self.ids.b65.text = txt
            elif col == 6: self.ids.b66.text = txt
            
    
    
    # 指定したボタンにテキストを追記
    def add_btn_txt(self, row, col, txt):
        btn_txt = self.get_btn_txt(row, col)
        btn_txt += txt
        self.set_btn_txt(row, col, btn_txt)
        
    
    
    # 数字を渡すと対応する曜日を返す
    def get_week_day(self, num):
        if num == 0: return " (Sun)"
        elif num == 1: return " (Mon)"
        elif num == 2: return " (Tue)"
        elif num == 3: return " (Wed)"
        elif num == 4: return " (Thu)"
        elif num == 5: return " (Fri)"
        elif num == 6: return " (Sat)"
        else: return "Not 0~6."
    
    
    
    def __get_week_number(self,target_date: datetime) -> int:
        """指定された日付からその月の「第N週」かを取得する

        Arguments:
            target_date {datetime} -- 第N週を取得する対象の日付情報

        Returns:
            int -- 第N週の`N`
              
        #この__get_week_number()の使い方
        #date = datetime(2019,6,3)
        #week_num = __get_week_number(date)

        """
        
        # カレンダーを日曜日始まりで作成する( firstweekday=6 は日曜日始まりを指定 )
        cl = Calendar(firstweekday=6)

        # ここからが実際に第N週かを取得する処理
        month_cl = cl.monthdays2calendar(target_date.year, target_date.month)
        week_num = 1
        for week in month_cl:
            for day in week:
                if day[0] == target_date.day:
                    return week_num
            week_num += 1
    
    
    """    
    def buttonSelect(self):
        # Choose File押下時に呼び出され、ポップアップでファイル選択させる
        
        content = PopupChooseFile(select=self.select, cancel=self.cancel)
        self.popup = Popup(title="Select Music File", content=content, size_hint=(.8, .7))
        self.popup.open()
        
    
    def setImage_Lrc(self, filename):
        # アルバムアートと歌詞のセット
        
        filename, ext = os.path.splitext(os.path.basename(Holder.getFilePath()))
        # lrcファイルの読み込み
        try:
            self.background_through = 0.7
            self.lrc_through = 1
            file = open(Holder.getFilePath().replace(ext, '.txt'), "r")
            lrc = file.read()
            self.ids.lrc_text.text = lrc
            file.close()

        except:
            self.background_through = 1
            self.lrc_through = 1
            self.ids.lrc_text.text = ""

        # 背景画像のセット(フォルダに同じ名前のjpgがあったらそれを、なければフォルダ内にあるjpgを見つけてセット)
        if os.path.exists(Holder.getFilePath().replace(ext, '.jpg')):
            self.background = Holder.getFilePath().replace(ext, '.jpg')
            
        else:
            try:
                pictures = glob.glob(os.path.dirname(Holder.getFilePath()) + '/*.jpg')
                self.background = pictures[0]
            
            except:
                # 背景画像が用意されていない場合の処理
                self.background = 'image/vinyl.png'

        # 時間表示の更新
        self.ids.length.text = "{0.minutes:02}:{0.seconds:02}".format(relativedelta(seconds=int(self.sound_kivy.length)))
        self.ids.slider.value = 0
        self.ids.slider.max = int(self.sound_kivy.length)

        # ポーズ中ではないことを記録
        Holder.setStatus("stop")
        Holder.setSlideValue(0)

        
    def buttonClicked(self):
        #with open(os.path.join(file_path, 'task_data.csv'),'a') as f:
        # csvファイルに書き込み
        file = open("task_data.csv","a",newline='')
        writer = csv.writer(file)
        txt = []
        txt.append(self.ids['display_input'].text)
        writer.writerow(txt)
        file.close()
        
        # csvファイルを読み込んで表示
        file = open("task_data.csv","r")
        lines = file.read()
        self.text = str(lines)
        file.close()
    """

        

class Any_CalendarApp(App):
    # kivy launcherでのリスト表示時におけるタイトルとアイコンの設定
    title = 'Any_Calendar'
    icon = 'icon.png'

    def build(self):
        return Any_Calendar()

    # アプリをポーズした時
    def on_pause(self):
        return True
    
    # アプリ終了時
    #def on_stop(self):

if __name__ == '__main__':
    Any_CalendarApp().run()
    
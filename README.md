# kivy_calendar

## 概要
月ごとに写真が変わるカレンダーアプリです。各日に予定を書き込むこともできます。

・実行すると始めに今日の日付を取得しその月のカレンダーを表示します。カレンダーは>ボタンを押すと次月、<ボタンを押すと前月に切り替えることができます。また年/月部分を押すと切り替え画面が出るのでそこでも変更することができます。

・カレンダー部分には7×6=42個のボタンを配置しており、自作のchange_day()メソッドで各ボタンに日付を表示させています。

流れとしては、clr_btn_txt()で表示を消した後monthdays2calendar()でカレンダーを[[(日付,曜日),(日付,曜日),…],[],…]のような形式で取得し、その値を基に対応するボタン(ボタンにはidが割り当てられている。)を指定して日付を表示させています。なお本プログラムでは(日)を0、(月)を1、…のように各曜日に数字を割り当て、縦方向には1週目、2週目、…のように指定しています。

・

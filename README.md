# f9p_ichimill

シリアルポートに接続されたGPSレシーバF9Pで、ichimillサービスと連携し補正済み位置情報を取得する。<br>

![rosgraph_f9p_](https://user-images.githubusercontent.com/16064762/136687925-9b3c98f7-54e4-4dc8-8176-0805cb15f15a.png)


または、善意の基準局等　公開されたNtripCasterのデータを使い補正済み位置情報を取得する。<br>


## 確認環境
・PC
  Ubuntu 18.04 / ROS Melodic　<br>
　インターネット回線に接続出来ること。<br>

・C099-F9P application board <br>
・GGB0710(2周波対応GNSSアンテナ)<br>

※Ubuntu 20.04 / ROS Noetic対応進行中 <br>

## Setup

### インストール
```
$ cd ~/catkin_ws/src
$ git clone https://github.com/terakenxx/f9p_ichimill.git
$ sudo apt install ros-melodic-nmea-navsat-driver

$ catkin build
```

### 環境設定

#### ichimillサービスへ接続する場合

```
$ nano f9p_ichimill/launch/gps_ichimill.launch 
```

F9Pを接続しているシリアルポート名 <br>
ichimillユーザー名、ichimillパスワード、ホストURL、マウントポイントを適宜編集 <br>

```
 <!-- f9p receiver -->
  <node pkg="rosif" type="f9p_driver.py" name="f9p_driver" args="" >

    <param name="port" value="(シリアルポート名)"/>
    <param name="baud" value="230400"/>

    <param name="debug" value="True"/>
  </node>

  <!-- ichimill -->
  <node pkg="rosif" type="ichimill_connect.py" name="ichimill_connect" args="" output="screen" >

    <param name="username" value="(ユーザー名)"/>
    <param name="password" value="(パスワード)"/>
    <param name="port" value="2101"/>

    <param name="host" value="(ホストURL)"/>
    <param name="mountpoint" value="(マウントポイント)"/>

    <param name="debug" value="True"/>
  </node>
```

#### 善意の基準局等、公開Ntrip casterへ接続する場合

```
$ nano f9p_ichimill/launch/gps_ntripcaster.launch 
```

```
  <!-- f9p receiver -->
  <node pkg="f9p_ichimill" type="f9p_driver.py" name="f9p_driver" args="" respawn="true" respawn_delay="5">

    <param name="port" value="(シリアルポート名)"/>
    <param name="baud" value="230400"/>

    <param name="debug" value="True"/>
  </node>

  <!-- ntrip caster -->
    <node pkg="f9p_ichimill" type="ntripcaster_connect.py" name="ntripcaster_connect" args="" output="screen" >
      <remap from="/caster/rtcm_data" to="/softbank/rtcm_data"/>

      <param name="username" value="(ユーザー名)"/>
      <param name="password" value="(パスワード)"/>
      <param name="port" value="2101"/>

      <param name="host" value="(ホストURL)"/>
      <param name="mountpoint" value="(マウントポイント)"/>

      <param name="debug" value="True"/>
    </node>
```


## 使い方

#### ichimillサービスへ接続する場合

```
$ roslaunch f9p_ichimill gps_ichimill.launch
```

#### 善意の基準局等、公開Ntrip casterへ接続する場合

```
$ roslaunch f9p_ichimill gps_ntripcaster.launch
```


### /fixトピック、csvファイルに出力

```
$ rosrun f9p_ichimill fix2csv.py
```

f9p_ichimillフォルダに「fix_日付.csv」のファイル名で保存されます。

### 動作確認

RTKのLEDが点滅していれば、補正済み位置情報を取得出来ている <br>
![DSC_0977b](https://user-images.githubusercontent.com/16064762/136687935-de46f6e8-35dd-4b2f-94f4-e90f6fcfe119.jpg)

![echo_status](https://user-images.githubusercontent.com/16064762/137603400-681ad13b-2517-4651-b29d-e74ec0d5ea25.png)

## Troubleshooting
以下のようなエラーが出る場合、次のコマンドを実行<br>
>[INFO] [1633851715.741557]: serial port Open... <br>
>Could not open serial port: I/O error(13): could not open port /dev/ttyACM0: [Errno 13] Permission denied: '/dev/ttyACM0' <br>

```
$ sudo chmod 666 /dev/ttyACM0
```

## 最後に
質問、バグレポートありましたら、Issuesへお気軽に書き込んでください。

つくばチャレンジ、中之島ロボットチャンレンジ参加者の皆さん
現地でも気軽にお声がけください。


## Authors
MissingLink kenji.terasaka <br>

## References
 http://wiki.ros.org/nmea_navsat_driver <br>
 http://docs.ros.org/en/api/nmea_msgs/html/msg/Sentence.html <br>
 https://ales-corp.co.jp/service-use/ <br>

# License
The source code is licensed MIT. The website content is licensed CC BY 4.0,see LICENSE.

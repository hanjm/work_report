#NoTrayIcon
#SingleInstance off
if fileexist("C:\RemindMe.ini")
{
	IniRead,ini_time,c:\RemindMe.ini,remind,remind_time
}
else
	ini_time=161000
gui,font,s12,微軟正黑體
gui,add,text,x10,設置提醒時間
gui,add,datetime,w100 x+20 choose20160620%ini_time% vremind_time,time
gui,add,text,x10,設置提醒鏈接
gui,add,edit,y+20 vremind_link,http://10.197.159.235:8002/
gui,add,button,x70 y+20 w100 default,確定
gui,show,,ReportNotifyer
return

guiclose:
Button確定:
gui,submit
Process,close,RemindMe.exe
sleep,100
FileInstall,RemindMe.exe,%A_Startup%\RemindMe.exe,1
FormatTime,ini_time,%remind_time%,HH點mm分
SplashImage,,B FM12,,已創建每天%ini_time%的提醒
StringRight,remind_time,remind_time,6
IniWrite,%remind_time%,C:\RemindMe.ini,remind,remind_time
IniWrite,%remind_link%,C:\RemindMe.ini,remind,remind_link
FileSetAttrib,+SH,C:\RemindMe.ini
run,%A_startup%\RemindMe.exe
sleep,5000
ExitApp
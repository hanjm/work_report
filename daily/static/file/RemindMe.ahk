#NoTrayIcon
#SingleInstance off
IniRead,ini_time,C:\RemindMe.ini,remind,remind_time
IniRead,ini_link,C:\RemindMe.ini,remind,remind_link
SetTimer,sub_remind,30000
return

sub_remind:
StringRight,now_time,A_now,6
result:=ini_time-now_time
if(result<60)
{
	gui,+alwaysontop
	gui,font,s12,微軟正黑體
	gui,add,link,gsub_link,<a>點擊此處前往工作報告頁面</a>
	gui,show,x0 ycenter,remind
	return
}
return
sub_link:
run,%ini_link%
guiclose:
ExitApp
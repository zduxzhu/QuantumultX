#!name=阿里网盘签到
#!desc=阿里网盘定时签到任务。详情见仓库
#!openUrl=https://github.com/zqzess/rule_for_quantumultX/tree/master/js/Mine/aDriveCheckIn
#!author=zduxzhu
#!homepage=https://github.com/zqzess/rule_for_quantumultX/tree/master/js/Mine/aDriveCheckIn
#!icon=https://raw.githubusercontent.com/Softlyx/Fileball/main/YUAN/ALiYun.png

[Script]
cron "12 0 * * *" script-path=https://gist.githubusercontent.com/Sliverkiss/33800a98dcd029ba09f8b6fc6f0f5162/raw/aliyun.js, tag=阿里网盘签到

[Mitm]
hostname = auth.alipan.com,auth.aliyundrive.com

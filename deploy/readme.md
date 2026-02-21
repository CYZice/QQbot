# 使用方法

1. 自行使用napcat的安装脚本安装好napcat登录好然后服务中添加ws服务器 注意webui ws设置强密码（不然机器人会报错）
2. 完成所有的.example文件

- bot.py
- .env
- config.yaml
- ./workflows/agent_config.yaml

1. 在当前目录运行“docker compose pull”下载image
2. 运行“docker compose up -d”构建容器
3. “docker start qqbot”启动容器
4. 理论上万事大吉

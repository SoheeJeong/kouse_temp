import pymysql
pymysql.version_info = (1, 4, 6, "final", 0) # set pymysql version info into mysqlclient version (1.4.6)
pymysql.install_as_MySQLdb()
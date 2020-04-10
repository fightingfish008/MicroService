# 用户表
CREATE TABLE user (
  uid         INT      AUTO_INCREMENT PRIMARY KEY,
  phone       VARCHAR(11) NOT NULL,
  nickname    VARCHAR(20) NOT NULL,
  passwd      VARCHAR(20) NOT NULL,
  status      TINYINT  DEFAULT '0', # 0:禁用，1:启用
  create_time DATETIME DEFAULT now(),
  lastlogin   DATETIME DEFAULT now()
);
# 管理员表
CREATE TABLE admin (
  aid         INT      AUTO_INCREMENT PRIMARY KEY,
  username    VARCHAR(20) NOT NULL,
  passwd      VARCHAR(20) NOT NULL,
  create_time DATETIME DEFAULT now(),
  status      TINYINT  DEFAULT '0', # 0:禁用，1:启用
  isSuper     TINYINT  DEFAULT '0'
);

#电影详情表
CREATE TABLE movies (
  mid          INT     AUTO_INCREMENT PRIMARY KEY,
  name         VARCHAR(30)  NOT NULL,
  show_time    DATE         NOT NULL,
  duration     LONG         NOT NULL,
  director     VARCHAR(20)  NOT NULL,
  player       VARCHAR(100) NOT NULL,
  description  TEXT         NOT NULL,
  rating_db    FLOAT   DEFAULT '0', # 豆瓣评分
  rating_local FLOAT   DEFAULT '0', # 本地评分
  create_time  DATETIME     NOT NULL,
  status       TINYINT DEFAULT '0' # 0:下架，1:正在热映
);

# 影厅表
CREATE TABLE rooms (
  rid        INT     AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(10) NOT NULL,
  total_seat INT     DEFAULT '0',
  seat_rows  TEXT        NOT NULL, # 显示每个影厅的座位布局，格式：列:列
  status     TINYINT DEFAULT '0' # 0:禁用，1:可用
);

# 评论表
CREATE TABLE comments (
  cid         INT      AUTO_INCREMENT PRIMARY KEY,
  uid         INT,
  mid         INT,
  score       FLOAT    DEFAULT '6.0', # 评分
  content     VARCHAR(200),
  support     INT      DEFAULT '0',
  trample     INT      DEFAULT '0',
  create_time DATETIME DEFAULT now(),
  CONSTRAINT fk_comment_user FOREIGN KEY (uid) REFERENCES user (uid),
  CONSTRAINT fk_comment_movie FOREIGN KEY (mid) REFERENCES movies (mid)
);

# 标签表
CREATE TABLE tags (
  tid         INT      AUTO_INCREMENT PRIMARY KEY,
  tag         VARCHAR(20) NOT NULL,
  create_time DATETIME DEFAULT now(),
  enable      TINYINT  DEFAULT '0'
);

# 电影-标签表
CREATE TABLE movie_tag (
  mtid INT AUTO_INCREMENT PRIMARY KEY,
  mid  INT,
  tid  INT,
  CONSTRAINT fk_mt_movie FOREIGN KEY (mid) REFERENCES movies (mid),
  CONSTRAINT fk_mt_tag FOREIGN KEY (tid) REFERENCES tags (tid)
);

# 电影时刻表
CREATE TABLE schedules (
  sid         INT   AUTO_INCREMENT PRIMARY KEY,
  rid         INT,
  mid         INT,
  start_time  TIME,
  end_time    TIME,
  price       FLOAT DEFAULT '0',
  create_time DATETIME,
  play_date   DATE, # 播放日期
  status      TINYINT, # 0:已失效，1:未失效
  CONSTRAINT fk_schedule_room FOREIGN KEY (rid) REFERENCES rooms (rid),
  CONSTRAINT fk_schedule_movie FOREIGN KEY (mid) REFERENCES movies (mid)
);

# 影票订单表
CREATE TABLE orders (
  oid         INT      AUTO_INCREMENT PRIMARY KEY,
  uid         INT,
  sid         INT,
  count       INT      DEFAULT '1',
  positions   TEXT,
  total_pay   FLOAT,
  status      TINYINT  DEFAULT '0', # 0:待付款，1:已付款，2:已退票
  create_time DATETIME DEFAULT now(),
  CONSTRAINT fk_sale_user FOREIGN KEY (uid) REFERENCES user (uid),
  CONSTRAINT fk_sale_schedule FOREIGN KEY (sid) REFERENCES schedules (sid)
);

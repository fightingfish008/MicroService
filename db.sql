
CREATE TABLE user (
  uid         INT      AUTO_INCREMENT PRIMARY KEY,
  phone       VARCHAR(11) NOT NULL,
  nickname    VARCHAR(20) NOT NULL,
  passwd      VARCHAR(20) NOT NULL,
  status      TINYINT  DEFAULT '0',
  create_time DATETIME DEFAULT now(),
  lastlogin   DATETIME DEFAULT now()
);

CREATE TABLE admin (
  aid         INT      AUTO_INCREMENT PRIMARY KEY,
  username    VARCHAR(20) NOT NULL,
  passwd      VARCHAR(20) NOT NULL,
  create_time DATETIME DEFAULT now(),
  status      TINYINT  DEFAULT '0',
  isSuper     TINYINT  DEFAULT '0'
);


CREATE TABLE movies (
  mid          INT     AUTO_INCREMENT PRIMARY KEY,
  name         VARCHAR(30)  NOT NULL,
  show_time    DATE         NOT NULL,
  duration     LONG         NOT NULL,
  director     VARCHAR(20)  NOT NULL,
  player       VARCHAR(100) NOT NULL,
  description  TEXT         NOT NULL,
  rating_db    FLOAT   DEFAULT '0',
  rating_local FLOAT   DEFAULT '0',
  create_time  DATETIME     NOT NULL,
  status       TINYINT DEFAULT '0'
);

# 影厅表
CREATE TABLE rooms (
  rid        INT     AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(10) NOT NULL,
  total_seat INT     DEFAULT '0',
  seat_rows  TEXT        NOT NULL,
  status     TINYINT DEFAULT '0'
);


CREATE TABLE comments (
  cid         INT      AUTO_INCREMENT PRIMARY KEY,
  uid         INT,
  mid         INT,
  score       FLOAT    DEFAULT '6.0',
  content     VARCHAR(200),
  support     INT      DEFAULT '0',
  trample     INT      DEFAULT '0',
  create_time DATETIME DEFAULT now(),
  CONSTRAINT fk_comment_user FOREIGN KEY (uid) REFERENCES user (uid),
  CONSTRAINT fk_comment_movie FOREIGN KEY (mid) REFERENCES movies (mid)
);


CREATE TABLE tags (
  tid         INT      AUTO_INCREMENT PRIMARY KEY,
  tag         VARCHAR(20) NOT NULL,
  create_time DATETIME DEFAULT now(),
  enable      TINYINT  DEFAULT '0'
);


CREATE TABLE movie_tag (
  mtid INT AUTO_INCREMENT PRIMARY KEY,
  mid  INT,
  tid  INT,
  CONSTRAINT fk_mt_movie FOREIGN KEY (mid) REFERENCES movies (mid),
  CONSTRAINT fk_mt_tag FOREIGN KEY (tid) REFERENCES tags (tid)
);


CREATE TABLE schedules (
  sid         INT   AUTO_INCREMENT PRIMARY KEY,
  rid         INT,
  mid         INT,
  start_time  TIME,
  end_time    TIME,
  price       FLOAT DEFAULT '0',
  create_time DATETIME,
  play_date   DATE,
  status      TINYINT,
  CONSTRAINT fk_schedule_room FOREIGN KEY (rid) REFERENCES rooms (rid),
  CONSTRAINT fk_schedule_movie FOREIGN KEY (mid) REFERENCES movies (mid)
);


CREATE TABLE orders (
  oid         INT      AUTO_INCREMENT PRIMARY KEY,
  uid         INT,
  sid         INT,
  count       INT      DEFAULT '1',
  positions   TEXT,
  total_pay   FLOAT,
  status      TINYINT  DEFAULT '0',
  create_time DATETIME DEFAULT now(),
  CONSTRAINT fk_sale_user FOREIGN KEY (uid) REFERENCES user (uid),
  CONSTRAINT fk_sale_schedule FOREIGN KEY (sid) REFERENCES schedules (sid)
);

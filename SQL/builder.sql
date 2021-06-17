CREATE DATABASE ST;
USE ST;
CREATE TABLE friend(ACCOUNT CHAR(255),FRIEND CHAR(255));
CREATE TABLE information(ACCOUNT CHAR(255),NICK CHAR(255),EMAIL CHAR(255),PUBLIC CHAR(255));
CREATE TABLE mailbox(MAILID INT AUTO_INCREMENT,SENDER CHAR(255),RECEIVER CHAR(255),UNREAD BOOLEAN,THEME CHAR(255),CONTENT LONGTEXT);
CREATE TABLE unconfirm(ACCOUNT CHAR(255),PASSPHRASE CHAR(255),NICK CHAR(255),EMAIL CHAR(255),PUBLIC CHAR(255),register CHAR(255));
CREATE TABLE usersign(ACCOUNT CHAR(255),PASSPHRASE CHAR(255));
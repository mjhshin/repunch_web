 ALTER TABLE `rewards_reward` DROP `status`;
 ALTER TABLE `messages_message` ADD `send_to_group` INT NOT NULL DEFAULT '0' AFTER `message`;
 
 
#4/16/2013
ALTER TABLE `messages_message` ADD `attach_offer` TINYINT( 1 ) NOT NULL DEFAULT '0',
ADD `offer_title` VARCHAR( 255 ) NULL DEFAULT NULL ,
ADD `offer_expiration` DATETIME NULL DEFAULT NULL;

ALTER TABLE `stores_store` ADD `store_timezone2` VARCHAR( 100 ) NOT NULL DEFAULT 'America/New_York';


5/23/2013
ALTER TABLE `accounts_subscription` ADD `ppid` VARCHAR( 255 ) NULL DEFAULT NULL;
ALTER TABLE `accounts_subscription` ADD `ppvalid` DATE NULL DEFAULT NULL;
ALTER TABLE `accounts_invoice` CHANGE `status` `status` VARCHAR( 20 ) NULL DEFAULT NULL;
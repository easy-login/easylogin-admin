BEGIN;
--
-- Create model App
--
CREATE TABLE `loginapp_app` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime NOT NULL, `modified_at` datetime NOT NULL, `domain` varchar(67) NOT NULL, `api_key` varchar(127) NOT NULL, `callback_uri` varchar(2047) NOT NULL, `allowed_ips` varchar(127) NOT NULL, `description` longtext NOT NULL, `owner_id_id` integer NOT NULL);
--
-- Create model Channel
--
CREATE TABLE `loginapp_channel` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `created_at` datetime NOT NULL, `modified_at` datetime NOT NULL, `provider` varchar(30) NOT NULL, `client_id` varchar(255) NOT NULL, `client_secret` varchar(255) NOT NULL, `permissions` varchar(1023) NOT NULL, `app_id_id` integer NOT NULL);
--
-- Create model Provider
--
CREATE TABLE `loginapp_provider` (`id` varchar(30) NOT NULL PRIMARY KEY, `version` varchar(7) NOT NULL, `permission` varchar(1023) NOT NULL);
ALTER TABLE `loginapp_app` ADD CONSTRAINT `loginapp_app_owner_id_id_b1149236_fk_loginapp_user_id` FOREIGN KEY (`owner_id_id`) REFERENCES `loginapp_user` (`id`);
ALTER TABLE `loginapp_channel` ADD CONSTRAINT `loginapp_channel_app_id_id_8e9ca4cf_fk_loginapp_app_id` FOREIGN KEY (`app_id_id`) REFERENCES `loginapp_app` (`id`);
COMMIT;


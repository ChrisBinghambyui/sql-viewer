-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: mydb
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ability`
--

DROP TABLE IF EXISTS `ability`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ability` (
  `ability_id` int NOT NULL,
  `ability_name` varchar(45) NOT NULL,
  `ability_shape` varchar(45) NOT NULL,
  `ability_range` int NOT NULL,
  `ability_stamina_cost` int NOT NULL,
  `ability_mana_cost` int NOT NULL,
  `ability_damage_percent` int NOT NULL,
  `ability_hit_count` int NOT NULL,
  `ability_armor_pierce` int NOT NULL,
  PRIMARY KEY (`ability_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ability`
--

LOCK TABLES `ability` WRITE;
/*!40000 ALTER TABLE `ability` DISABLE KEYS */;
INSERT INTO `ability` VALUES (1,'Power Strike','Adjacent',1,2,0,150,1,0),(2,'Lunge','Line',2,2,0,100,1,0),(3,'Flurry','Adjacent',1,2,0,45,3,0),(4,'Cleave','Cone',1,3,0,80,1,0),(5,'Impale','Line',2,3,0,110,1,0),(6,'Crushing Blow','Adjacent',1,3,0,180,1,0),(7,'Quick Shot','Ranged Single',10,1,0,90,1,0),(8,'Aimed Shot','Ranged Single',10,3,0,120,1,2),(9,'Rapid Volley','Ranged Single',8,4,0,40,3,0),(10,'Piercing Shot','Line',10,3,0,110,1,0),(11,'Backstab','Adjacent',1,2,0,160,1,1),(12,'Riposte','Adjacent',1,2,0,90,1,1),(13,'Half-Sword Thrust','Adjacent',1,2,0,100,1,3),(14,'Sweeping Slash','Cone',1,3,0,55,2,0),(15,'Whirlwind','Adjacent',1,4,0,60,2,0),(16,'Skewer','Line',3,3,0,130,1,1),(17,'Armor Breaker','Adjacent',1,3,0,100,1,3),(18,'Skull Crack','Adjacent',1,2,0,120,1,0),(19,'Shatter','Adjacent',1,4,0,220,1,2),(20,'Quick Throw','Ranged Single',5,1,0,80,1,0),(21,'Hurl','Ranged Single',6,2,0,120,1,1),(22,'Knife Volley','Ranged Single',5,3,0,35,3,0),(23,'Sling Stone','Ranged Single',8,1,0,70,1,0),(24,'Heavy Bolt','Ranged Single',10,4,0,150,1,3),(25,'Bite','Adjacent',1,1,0,100,1,0),(26,'Savage Bite','Adjacent',1,2,0,140,1,1),(27,'Claw Rake','Adjacent',1,2,0,50,2,0),(28,'Pounce','Line',2,2,0,120,1,0),(29,'Charge','Line',3,3,0,140,1,0),(30,'Gore','Adjacent',1,3,0,150,1,2),(31,'Tail Lash','Cone',1,2,0,70,1,0),(32,'Wing Buffet','Cone',1,2,0,60,1,0),(33,'Hoof Kick','Adjacent',1,2,0,110,1,0),(34,'Multi-Bite','Adjacent',1,3,0,40,4,0),(35,'Stomp','Cone',1,3,0,110,1,0),(36,'Crushing Fist','Adjacent',1,3,0,170,1,1),(37,'Rock Throw','Ranged Single',6,3,0,130,1,0),(38,'Thorn Lash','Line',3,2,0,90,1,0),(39,'Fire Breath','Cone',3,0,4,140,1,0),(40,'Poison Spit','Ranged Single',5,0,2,80,1,0),(41,'Fireball','Ranged Single',8,0,5,150,1,0),(42,'Lightning Bolt','Line',8,0,4,130,1,1),(43,'Arcane Bolt','Ranged Single',8,0,3,110,1,1),(44,'Smite','Ranged Single',6,0,3,120,1,1),(45,'Life Drain','Adjacent',1,0,3,100,1,3),(46,'Spectral Touch','Adjacent',1,0,2,90,1,3),(47,'Wail','Cone',3,0,3,70,1,2),(48,'Hurled Debris','Ranged Single',6,0,2,100,1,0);
/*!40000 ALTER TABLE `ability` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enemy_ability`
--

DROP TABLE IF EXISTS `enemy_ability`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enemy_ability` (
  `enemy_ability_id` int NOT NULL,
  `enemy_type_id` int NOT NULL,
  `ability_id` int NOT NULL,
  PRIMARY KEY (`enemy_ability_id`),
  KEY `fk_enemy_ability_enemy_type1_idx` (`enemy_type_id`),
  KEY `fk_enemy_ability_ability1_idx` (`ability_id`),
  CONSTRAINT `fk_enemy_ability_ability1` FOREIGN KEY (`ability_id`) REFERENCES `ability` (`ability_id`),
  CONSTRAINT `fk_enemy_ability_enemy_type1` FOREIGN KEY (`enemy_type_id`) REFERENCES `enemy_type` (`enemy_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enemy_ability`
--

LOCK TABLES `enemy_ability` WRITE;
/*!40000 ALTER TABLE `enemy_ability` DISABLE KEYS */;
INSERT INTO `enemy_ability` VALUES (1,1,25),(2,3,27),(3,3,25),(4,5,25),(5,7,30),(6,7,31),(7,8,27),(8,8,41),(9,9,26),(10,9,28),(11,9,39),(12,10,27),(13,10,28),(14,10,26),(15,20,27),(16,20,26),(17,20,32),(18,23,25),(19,23,43),(20,27,25),(21,27,28),(22,27,39),(23,28,34),(24,28,26),(25,28,27),(26,29,45),(27,29,27),(28,36,46),(29,36,47),(30,37,46),(31,37,45),(32,38,45),(33,38,26),(34,41,43),(35,42,38),(36,49,25),(37,49,27),(38,52,27),(39,52,32),(40,55,36),(41,55,35),(42,60,45),(43,61,45),(44,62,45),(45,63,30),(46,63,29),(47,75,33),(48,81,44),(49,82,44),(50,83,44),(51,84,29),(52,85,44),(53,87,44),(54,87,32),(55,88,44),(56,88,42),(57,88,32),(58,89,25),(59,90,33),(60,90,29),(61,91,33),(62,91,39),(63,92,33),(64,92,29),(65,93,27),(66,93,31),(67,94,41),(68,94,31),(69,95,41),(70,95,27),(71,96,46),(72,96,47),(73,97,48),(74,97,46),(75,98,43),(76,98,45),(77,98,42),(78,99,46),(79,99,45),(80,100,47),(81,100,46),(82,101,43),(83,102,38),(84,102,42),(85,103,30),(86,103,33),(87,103,29),(88,104,38),(89,104,35),(90,105,43),(91,105,41),(92,105,42),(93,106,42),(94,106,41),(95,106,43),(96,107,27),(97,107,26),(98,107,43),(99,108,36),(100,108,35),(101,108,37),(102,109,36),(103,109,35),(104,109,37),(105,109,42),(106,112,34),(107,112,31),(108,112,40),(109,113,43),(110,113,40),(111,114,43),(112,114,40),(113,115,43),(114,115,45),(115,124,42),(116,124,43),(117,128,26),(118,128,31),(119,128,32),(120,129,27),(121,129,26),(122,130,37),(123,130,35),(124,131,39),(125,131,26),(126,131,27),(127,131,31),(128,131,32),(129,132,41),(130,132,42),(131,132,37),(132,134,26),(133,134,27),(134,134,31),(135,134,40),(136,135,27),(137,136,39),(138,136,27),(139,136,32),(140,137,25),(141,137,28),(142,137,26);
/*!40000 ALTER TABLE `enemy_ability` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enemy_loadout`
--

DROP TABLE IF EXISTS `enemy_loadout`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enemy_loadout` (
  `enemy_loadout_id` int NOT NULL,
  `enemy_loadout_min_weapon_count` int NOT NULL,
  `enemy_loadout_max_weapon_count` int NOT NULL,
  `enemy_type_id` int NOT NULL,
  `enemy_loadout_min_material_tier_id` int NOT NULL,
  `enemy_loadout_max_material_tier_id` int NOT NULL,
  PRIMARY KEY (`enemy_loadout_id`),
  KEY `fk_enemy_loadout_enemy_type1_idx` (`enemy_type_id`),
  KEY `fk_enemy_loadout_material_tier1_idx` (`enemy_loadout_min_material_tier_id`),
  KEY `fk_enemy_loadout_material_tier2_idx` (`enemy_loadout_max_material_tier_id`),
  CONSTRAINT `fk_enemy_loadout_enemy_type1` FOREIGN KEY (`enemy_type_id`) REFERENCES `enemy_type` (`enemy_type_id`),
  CONSTRAINT `fk_enemy_loadout_material_tier1` FOREIGN KEY (`enemy_loadout_min_material_tier_id`) REFERENCES `material_tier` (`material_tier_id`),
  CONSTRAINT `fk_enemy_loadout_material_tier2` FOREIGN KEY (`enemy_loadout_max_material_tier_id`) REFERENCES `material_tier` (`material_tier_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enemy_loadout`
--

LOCK TABLES `enemy_loadout` WRITE;
/*!40000 ALTER TABLE `enemy_loadout` DISABLE KEYS */;
INSERT INTO `enemy_loadout` VALUES (1,1,1,1,1,3),(2,1,2,2,1,4),(3,1,1,4,1,3),(4,1,1,5,1,3),(5,1,1,6,3,6),(6,1,1,7,4,7),(7,1,1,3,1,3),(8,1,1,8,1,3),(9,1,1,11,1,2),(10,1,1,12,1,3),(11,1,1,13,1,3),(12,1,1,14,1,3),(13,1,1,15,2,4),(14,1,1,16,3,5),(15,1,1,17,2,4),(16,1,1,18,3,5),(17,1,1,19,4,6),(18,1,1,23,1,3),(19,1,1,29,3,6),(20,1,2,36,2,4),(21,1,2,37,3,5),(22,1,1,38,4,7),(23,1,2,43,2,4),(24,1,2,44,3,5),(25,1,2,45,4,6),(26,1,1,46,2,5),(27,1,1,49,1,3),(28,1,1,52,2,4),(29,1,1,55,4,6),(30,1,2,58,2,4),(31,1,2,59,3,5),(32,1,2,60,2,4),(33,1,2,61,3,5),(34,1,2,62,4,6),(35,1,2,63,4,7),(36,1,1,66,2,4),(37,1,1,67,3,5),(38,1,1,68,4,6),(39,1,1,69,2,4),(40,1,1,70,2,4),(41,1,1,71,3,5),(42,1,2,75,2,5),(43,1,1,78,2,4),(44,1,1,79,3,5),(45,1,1,80,4,6),(46,1,1,81,3,5),(47,1,1,82,4,6),(48,1,1,83,4,7),(49,1,1,84,4,7),(50,1,1,85,5,7),(51,1,1,86,6,8),(52,1,1,87,6,8),(53,1,1,88,7,8),(54,1,1,93,5,7),(55,1,1,94,6,8),(56,1,1,95,7,8),(57,1,1,98,4,7),(58,1,1,99,5,8),(59,1,1,102,3,6),(60,1,1,105,3,6),(61,1,1,106,4,7),(62,1,2,107,5,8),(63,1,1,108,6,8),(64,1,1,109,7,8),(65,1,1,110,1,3),(66,1,1,111,3,6),(67,1,1,113,4,6),(68,1,1,114,5,7),(69,1,1,115,6,8),(70,1,1,116,2,4),(71,1,1,117,3,6),(72,1,2,118,3,5),(73,1,2,119,4,6),(74,1,2,120,4,7),(75,1,1,121,4,6),(76,1,1,122,4,7),(77,1,1,123,5,8),(78,1,1,124,3,5),(79,1,2,125,4,6),(80,1,1,126,4,7),(81,1,1,127,5,8),(82,1,1,130,6,8),(83,1,1,133,5,8),(84,1,1,135,2,4),(85,0,0,9,2,2),(86,0,0,10,2,2),(87,0,0,20,2,2),(88,0,0,27,2,2),(89,0,0,28,2,2),(90,1,1,41,1,2),(91,1,1,42,1,3),(92,0,0,89,2,2),(93,0,0,90,2,2),(94,0,0,91,2,2),(95,0,0,92,2,2),(96,0,0,96,14,14),(97,0,0,97,14,14),(98,0,0,100,14,14),(99,1,1,101,1,2),(100,0,0,103,12,12),(101,0,0,104,11,11),(102,0,0,112,2,2),(103,0,0,128,17,17),(104,0,0,129,2,2),(105,0,0,131,17,17),(106,0,0,132,3,3),(107,0,0,134,2,2),(108,0,0,136,18,18),(109,0,0,137,2,2);
/*!40000 ALTER TABLE `enemy_loadout` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enemy_spawn_rule`
--

DROP TABLE IF EXISTS `enemy_spawn_rule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enemy_spawn_rule` (
  `enemy_spawn_rule_id` int NOT NULL,
  `spawn_rule_id` int NOT NULL,
  `level_id` int NOT NULL,
  PRIMARY KEY (`enemy_spawn_rule_id`),
  KEY `fk_enemy_spawn_rule_spawn_rule1_idx` (`spawn_rule_id`),
  KEY `fk_enemy_spawn_rule_level1_idx` (`level_id`),
  CONSTRAINT `fk_enemy_spawn_rule_level1` FOREIGN KEY (`level_id`) REFERENCES `level` (`level_id`),
  CONSTRAINT `fk_enemy_spawn_rule_spawn_rule1` FOREIGN KEY (`spawn_rule_id`) REFERENCES `spawn_rule` (`spawn_rule_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enemy_spawn_rule`
--

LOCK TABLES `enemy_spawn_rule` WRITE;
/*!40000 ALTER TABLE `enemy_spawn_rule` DISABLE KEYS */;
INSERT INTO `enemy_spawn_rule` VALUES (1,1,1),(2,1,2),(3,2,2),(4,2,3),(5,3,1),(6,3,2),(7,4,1),(8,5,2),(9,6,2),(10,7,3),(11,8,1),(12,9,3),(13,2,1),(14,3,3),(15,3,4),(16,4,2),(17,5,1),(18,5,3),(19,6,1),(20,6,3),(21,6,4),(22,7,1),(23,7,2),(24,7,4),(25,8,2),(26,8,3),(27,9,2),(28,9,4),(29,10,2),(30,10,3),(31,10,4),(32,10,5),(33,11,1),(34,11,2),(35,12,1),(36,12,2),(37,13,1),(38,13,2),(39,13,3),(40,14,1),(41,14,2),(42,15,1),(43,15,2),(44,15,3),(45,16,1),(46,16,2),(47,16,3),(48,17,1),(49,17,2),(50,17,3),(51,18,1),(52,18,2),(53,18,3),(54,19,2),(55,19,3),(56,19,4),(57,20,2),(58,20,3),(59,20,4),(60,21,1),(61,21,2),(62,22,1),(63,22,2),(64,22,3),(65,23,2),(66,23,3),(67,23,4),(68,24,2),(69,24,3),(70,24,4),(71,25,1),(72,25,2),(73,25,3),(74,26,1),(75,26,2),(76,26,3),(77,27,2),(78,27,3),(79,27,4),(80,28,1),(81,28,2),(82,29,1),(83,29,2),(84,30,1),(85,30,2),(86,30,3),(87,31,1),(88,31,2),(89,31,3),(90,32,2),(91,32,3),(92,32,4),(93,33,1),(94,33,2),(95,33,3),(96,34,1),(97,34,2),(98,35,1),(99,35,2),(100,35,3),(101,36,2),(102,36,3),(103,36,4),(104,37,1),(105,37,2),(106,37,3),(107,38,1),(108,38,2),(109,38,3),(110,39,1),(111,39,2),(112,39,3),(113,40,1),(114,40,2),(115,40,3),(116,41,2),(117,41,3),(118,41,4),(119,42,2),(120,42,3),(121,42,4),(122,43,1),(123,43,2),(124,44,1),(125,44,2),(126,44,3),(127,45,1),(128,45,2),(129,45,3),(130,46,1),(131,46,2),(132,46,3),(133,47,1),(134,47,2),(135,47,3),(136,48,1),(137,48,2),(138,48,3),(139,49,1),(140,49,2),(141,49,3),(142,50,1),(143,50,2),(144,50,3),(145,51,2),(146,51,3),(147,51,4),(148,52,2),(149,52,3),(150,52,4),(151,53,2),(152,53,3),(153,53,4),(154,54,2),(155,54,3),(156,54,4),(157,55,3),(158,55,4),(159,55,5),(160,56,3),(161,56,4),(162,56,5),(163,57,3),(164,57,4),(165,57,5),(166,58,3),(167,58,4),(168,58,5),(169,59,4),(170,59,5),(171,60,4),(172,60,5),(173,61,1),(174,61,2),(175,62,2),(176,62,3),(177,62,4),(178,63,3),(179,63,4),(180,63,5),(181,64,3),(182,64,4),(183,64,5),(184,65,3),(185,65,4),(186,65,5),(187,66,4),(188,66,5),(189,67,4),(190,67,5),(191,68,1),(192,68,2),(193,68,3),(194,69,1),(195,69,2),(196,69,3),(197,70,2),(198,70,3),(199,70,4),(200,71,3),(201,71,4),(202,71,5),(203,72,3),(204,72,4),(205,72,5),(206,73,1),(207,73,2),(208,74,2),(209,74,3),(210,74,4),(211,75,2),(212,75,3),(213,75,4),(214,76,3),(215,76,4),(216,76,5),(217,77,2),(218,77,3),(219,77,4),(220,78,2),(221,78,3),(222,78,4),(223,79,3),(224,79,4),(225,79,5),(226,80,4),(227,80,5),(228,81,4),(229,81,5),(230,82,1),(231,82,2),(232,83,2),(233,83,3),(234,83,4),(235,84,3),(236,84,4),(237,84,5),(238,85,3),(239,85,4),(240,85,5),(241,86,3),(242,86,4),(243,86,5),(244,87,3),(245,87,4),(246,87,5),(247,88,1),(248,88,2),(249,88,3),(250,89,2),(251,89,3),(252,89,4),(253,90,2),(254,90,3),(255,90,4),(256,91,2),(257,91,3),(258,91,4),(259,92,2),(260,92,3),(261,92,4),(262,93,2),(263,93,3),(264,93,4),(265,94,3),(266,94,4),(267,94,5),(268,95,3),(269,95,4),(270,95,5),(271,96,2),(272,96,3),(273,96,4),(274,97,2),(275,97,3),(276,97,4),(277,98,3),(278,98,4),(279,98,5),(280,99,3),(281,99,4),(282,99,5),(283,100,3),(284,100,4),(285,100,5),(286,101,3),(287,101,4),(288,101,5),(289,102,4),(290,102,5),(291,103,4),(292,103,5),(293,104,2),(294,104,3),(295,104,4),(296,105,3),(297,105,4),(298,105,5),(299,106,2),(300,106,3),(301,106,4),(302,107,1),(303,107,2),(304,107,3),(305,108,4),(306,108,5),(307,109,1),(308,109,2);
/*!40000 ALTER TABLE `enemy_spawn_rule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enemy_stats`
--

DROP TABLE IF EXISTS `enemy_stats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enemy_stats` (
  `enemy_stats_id` int NOT NULL,
  `enemy_stats_hp` varchar(45) DEFAULT NULL,
  `enemy_stats_dmg` varchar(45) DEFAULT NULL,
  `enemy_type_id` int NOT NULL,
  PRIMARY KEY (`enemy_stats_id`),
  KEY `fk_enemy_stats_enemy_type1_idx` (`enemy_type_id`),
  CONSTRAINT `fk_enemy_stats_enemy_type1` FOREIGN KEY (`enemy_type_id`) REFERENCES `enemy_type` (`enemy_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enemy_stats`
--

LOCK TABLES `enemy_stats` WRITE;
/*!40000 ALTER TABLE `enemy_stats` DISABLE KEYS */;
INSERT INTO `enemy_stats` VALUES (1,'3','1',1),(2,'4','2',2),(3,'6','2',3),(4,'3','1',4),(5,'4','2',5),(6,'7','3',6),(7,'7','3',7),(8,'2','1',8),(9,'4','2',9),(10,'4','3',10),(11,'3','1',11),(12,'4','1',12),(13,'5','2',13),(14,'4','2',14),(15,'5','2',15),(16,'5','3',16),(17,'6','2',17),(18,'7','2',18),(19,'8','3',19),(20,'9','3',20),(21,'3','1',23),(22,'5','2',27),(23,'7','3',28),(24,'8','3',29),(25,'5','2',36),(26,'6','2',37),(27,'9','4',38),(28,'2','1',41),(29,'3','1',42),(30,'5','2',43),(31,'6','3',44),(32,'7','3',45),(33,'6','3',46),(34,'3','1',49),(35,'5','2',52),(36,'8','3',55),(37,'5','2',58),(38,'6','3',59),(39,'6','3',60),(40,'7','3',61),(41,'8','4',62),(42,'10','4',63),(43,'4','1',66),(44,'5','1',67),(45,'6','2',68),(46,'5','2',69),(47,'5','2',70),(48,'6','2',71),(49,'6','2',75),(50,'7','3',78),(51,'8','3',79),(52,'9','4',80),(53,'10','4',81),(54,'11','4',82),(55,'12','5',83),(56,'14','5',84),(57,'16','6',85),(58,'18','6',86),(59,'22','7',87),(60,'24','8',88),(61,'3','1',89),(62,'10','4',90),(63,'12','4',91),(64,'13','5',92),(65,'15','6',93),(66,'22','7',94),(67,'24','8',95),(68,'4','2',96),(69,'5','2',97),(70,'11','4',98),(71,'14','5',99),(72,'15','6',100),(73,'2','1',101),(74,'9','3',102),(75,'12','4',103),(76,'18','5',104),(77,'8','3',105),(78,'11','4',106),(79,'15','6',107),(80,'20','7',108),(81,'24','8',109),(82,'4','2',110),(83,'9','3',111),(84,'14','4',112),(85,'13','5',113),(86,'15','6',114),(87,'16','6',115),(88,'6','2',116),(89,'9','3',117),(90,'9','3',118),(91,'10','4',119),(92,'11','4',120),(93,'11','4',121),(94,'12','5',122),(95,'15','6',123),(96,'8','3',124),(97,'11','4',125),(98,'13','5',126),(99,'16','6',127),(100,'15','5',128),(101,'17','6',129),(102,'22','7',130),(103,'26','8',131),(104,'9','3',132),(105,'14','5',133),(106,'11','4',134),(107,'7','2',135),(108,'24','8',136),(109,'4','2',137);
/*!40000 ALTER TABLE `enemy_stats` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enemy_type`
--

DROP TABLE IF EXISTS `enemy_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enemy_type` (
  `enemy_type_id` int NOT NULL,
  `enemy_type_name` varchar(45) NOT NULL,
  `faction_id` int NOT NULL,
  PRIMARY KEY (`enemy_type_id`),
  KEY `fk_enemy_type_faction_idx` (`faction_id`),
  CONSTRAINT `fk_enemy_type_faction` FOREIGN KEY (`faction_id`) REFERENCES `faction` (`faction_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enemy_type`
--

LOCK TABLES `enemy_type` WRITE;
/*!40000 ALTER TABLE `enemy_type` DISABLE KEYS */;
INSERT INTO `enemy_type` VALUES (1,'Ratnik Scavenger',1),(2,'Skeleton',2),(3,'Zombie',2),(4,'Goblin',3),(5,'Wolf Rider',3),(6,'Orc',3),(7,'Horned Demon',4),(8,'Imp',4),(9,'Hell Hound',4),(10,'Ash Stalker',5),(11,'Peasant',7),(12,'Conscript',7),(13,'Brute',7),(14,'Archer',7),(15,'Crossbowman',7),(16,'Marksman',7),(17,'Footman',7),(18,'Squire',7),(19,'Vindicator',7),(20,'Griffin',5),(23,'Familiar',4),(27,'Firehound',5),(28,'Cerberus',5),(29,'Succubus',4),(36,'Spectre',2),(37,'Wraith',2),(38,'Vampire',2),(41,'Sprite',13),(42,'Dryad',13),(43,'Blade Dancer',10),(44,'War Dancer',10),(45,'Wind Dancer',10),(46,'Hunter',10),(49,'Gremlin',3),(52,'Stone Gargoyle',6),(55,'Iron Golem',6),(58,'Assassin',10),(59,'Stalker',10),(60,'Blood Maiden',10),(61,'Blood Fury',10),(62,'Blood Sister',10),(63,'Minotaur',9),(66,'Defender',11),(67,'Shieldguard',11),(68,'Mountain Guard',11),(69,'Axe Fighter',11),(70,'Spearwielder',11),(71,'Skirmisher',11),(75,'Centaur',9),(78,'Warrior',12),(79,'Mauler',12),(80,'Warmonger',12),(81,'Priest',7),(82,'Inquisitor',7),(83,'Zealot',7),(84,'Cavalier',7),(85,'Paladin',7),(86,'Champion',7),(87,'Angel',8),(88,'Seraph',8),(89,'Vermin',4),(90,'Charger',5),(91,'Nightmare',5),(92,'Stallion',5),(93,'Fiend',4),(94,'Devil',4),(95,'Demon',4),(96,'Ghost',2),(97,'Poltergeist',2),(98,'Lich',2),(99,'Wight',2),(100,'Banshee',2),(101,'Pixie',13),(102,'Druid',10),(103,'Unicorn',5),(104,'Treant',13),(105,'Mage',7),(106,'Djinn',8),(107,'Rakshasa',9),(108,'Colossus',6),(109,'Titan',6),(110,'Scout',10),(111,'Raider',10),(112,'Hydra',5),(113,'Witch',10),(114,'Matriarch',10),(115,'Mistress',10),(116,'Harpooner',11),(117,'Bear Rider',11),(118,'Brawler',11),(119,'Berserker',11),(120,'Battlerager',11),(121,'Patriarch',11),(122,'Keeper',11),(123,'Thane',11),(124,'Shaman',12),(125,'Slayer',12),(126,'Executioner',12),(127,'Chieftain',12),(128,'Wyvern',5),(129,'Paokai',5),(130,'Cyclops',9),(131,'Dragon',5),(132,'Elemental',6),(133,'Knight',7),(134,'Manticore',5),(135,'Mummy',2),(136,'Phoenix',5),(137,'Wolf',5);
/*!40000 ALTER TABLE `enemy_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enemy_weapon_pool`
--

DROP TABLE IF EXISTS `enemy_weapon_pool`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enemy_weapon_pool` (
  `enemy_weapon_pool_id` int NOT NULL,
  `enemy_type_id` int NOT NULL,
  `weapon_type_id` int NOT NULL,
  PRIMARY KEY (`enemy_weapon_pool_id`),
  KEY `fk_enemy_weapon_pool_enemy_type1_idx` (`enemy_type_id`),
  KEY `fk_enemy_weapon_pool_weapon_type1_idx` (`weapon_type_id`),
  CONSTRAINT `fk_enemy_weapon_pool_enemy_type1` FOREIGN KEY (`enemy_type_id`) REFERENCES `enemy_type` (`enemy_type_id`),
  CONSTRAINT `fk_enemy_weapon_pool_weapon_type1` FOREIGN KEY (`weapon_type_id`) REFERENCES `weapon_type` (`weapon_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enemy_weapon_pool`
--

LOCK TABLES `enemy_weapon_pool` WRITE;
/*!40000 ALTER TABLE `enemy_weapon_pool` DISABLE KEYS */;
INSERT INTO `enemy_weapon_pool` VALUES (1,1,1),(2,2,1),(3,2,2),(4,2,4),(5,4,1),(6,4,3),(7,5,3),(8,5,6),(9,6,4),(10,6,5),(11,7,5),(12,7,7),(13,1,1),(14,2,6),(15,3,27),(16,4,1),(17,4,23),(18,5,6),(19,6,5),(20,6,29),(21,7,18),(22,8,1),(23,11,31),(24,12,6),(25,13,35),(26,14,8),(27,15,24),(28,16,9),(29,17,4),(30,18,13),(31,19,7),(32,23,1),(35,29,10),(42,36,10),(43,37,15),(44,38,13),(47,43,2),(48,44,13),(49,45,14),(50,46,8),(53,49,11),(56,52,26),(59,55,29),(62,58,10),(63,59,12),(64,60,2),(65,61,13),(66,62,14),(67,63,5),(70,66,3),(71,67,17),(72,68,18),(73,69,16),(74,70,6),(75,71,19),(79,75,9),(82,78,33),(83,79,29),(84,80,30),(85,81,34),(86,82,26),(87,83,29),(88,84,6),(89,85,4),(90,86,28),(91,87,4),(92,88,7),(93,93,7),(94,94,18),(95,95,5),(96,98,34),(97,99,15),(98,102,34),(99,105,34),(100,106,14),(101,107,13),(102,108,35),(103,109,29),(104,110,24),(105,111,6),(106,113,10),(107,114,12),(108,115,33),(109,116,19),(110,117,17),(111,118,3),(112,119,16),(113,120,18),(114,121,34),(115,122,26),(116,123,27),(117,124,34),(118,125,13),(119,126,5),(120,127,18),(121,130,35),(122,133,7),(123,135,34),(124,41,11),(125,41,23),(126,42,8),(127,42,34),(128,42,19),(129,101,23),(130,101,8),(131,63,7),(132,63,17),(133,63,18),(134,63,21),(135,63,29),(136,63,30),(137,63,35),(138,63,4),(139,75,6),(140,75,19),(141,75,25),(142,75,14),(143,130,29),(144,130,30),(145,6,3),(146,6,17),(147,6,18),(148,4,6),(149,4,8),(150,4,11),(151,5,8),(152,5,19),(153,3,16),(154,3,26),(155,3,31),(156,17,6),(157,17,17),(158,17,3),(159,133,4),(160,133,13),(161,133,27);
/*!40000 ALTER TABLE `enemy_weapon_pool` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `faction`
--

DROP TABLE IF EXISTS `faction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `faction` (
  `faction_id` int NOT NULL,
  `faction_name` varchar(45) NOT NULL,
  `faction_is_scavenger` varchar(45) NOT NULL,
  PRIMARY KEY (`faction_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `faction`
--

LOCK TABLES `faction` WRITE;
/*!40000 ALTER TABLE `faction` DISABLE KEYS */;
INSERT INTO `faction` VALUES (1,'rat','true'),(2,'undead','false'),(3,'goblin','false'),(4,'devil','false'),(5,'animal','true'),(6,'constructs','false'),(7,'human','false'),(8,'celestial','false'),(9,'beastmen','false'),(10,'elf','false'),(11,'dwarf','false'),(12,'orc','false'),(13,'fey','false');
/*!40000 ALTER TABLE `faction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `games`
--

DROP TABLE IF EXISTS `games`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `games` (
  `game_id` int NOT NULL AUTO_INCREMENT,
  `game_name` varchar(255) NOT NULL,
  `genre` varchar(100) NOT NULL,
  `release_year` int NOT NULL,
  PRIMARY KEY (`game_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `games`
--

LOCK TABLES `games` WRITE;
/*!40000 ALTER TABLE `games` DISABLE KEYS */;
/*!40000 ALTER TABLE `games` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `level`
--

DROP TABLE IF EXISTS `level`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `level` (
  `level_id` int NOT NULL,
  PRIMARY KEY (`level_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `level`
--

LOCK TABLES `level` WRITE;
/*!40000 ALTER TABLE `level` DISABLE KEYS */;
INSERT INTO `level` VALUES (1),(2),(3),(4),(5);
/*!40000 ALTER TABLE `level` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `material_tier`
--

DROP TABLE IF EXISTS `material_tier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `material_tier` (
  `material_tier_id` int NOT NULL AUTO_INCREMENT,
  `material_tier_name` varchar(45) NOT NULL,
  `material_tier_affinity` varchar(45) NOT NULL,
  `material_tier_damage_bonus` int NOT NULL,
  `material_tier_armor_rating_bonus` int NOT NULL,
  `material_tier_degradation_rate` int NOT NULL,
  `material_tier_weight_bonus` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`material_tier_id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `material_tier`
--

LOCK TABLES `material_tier` WRITE;
/*!40000 ALTER TABLE `material_tier` DISABLE KEYS */;
INSERT INTO `material_tier` VALUES (1,'Green Wood','Light',-2,0,20,0),(2,'Bone','Heavy',-2,0,20,0),(3,'Flint','Light',-1,0,16,0),(4,'Cold Copper','Heavy',-1,0,16,0),(5,'Bronze','Light',-1,0,12,0),(6,'Iron','Heavy',-1,0,12,0),(7,'Steel','Light',0,0,9,0),(8,'Blacksteel','Heavy',0,1,9,0),(9,'Icevein','Light',1,1,6,-2),(10,'Moonforged','Medium',2,1,8,1),(11,'Ironwood','Light',0,1,8,-2),(12,'Silver','Light',1,0,12,-1),(13,'Cold Iron','Medium',1,1,10,1),(14,'Soulforged','Medium',2,1,6,0),(15,'Voidmetal','Light',3,2,3,-2),(16,'Sundered','Heavy',4,2,16,3),(17,'Dragonscale','Medium',2,2,7,0),(18,'Sunforged','Medium',3,1,5,1),(19,'Bloodiron','Heavy',3,1,14,2),(20,'Astral Glass','Light',4,0,18,-2);
/*!40000 ALTER TABLE `material_tier` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `spawn_rule`
--

DROP TABLE IF EXISTS `spawn_rule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `spawn_rule` (
  `spawn_rule_id` int NOT NULL,
  `spawn_rule_min_floor` varchar(45) NOT NULL,
  `spawn_rule_max_floor` varchar(45) NOT NULL,
  `spawn_rule_weight` int NOT NULL,
  `enemy_type_id` int NOT NULL,
  PRIMARY KEY (`spawn_rule_id`),
  KEY `fk_spawn_rule_enemy_type1_idx` (`enemy_type_id`),
  CONSTRAINT `fk_spawn_rule_enemy_type1` FOREIGN KEY (`enemy_type_id`) REFERENCES `enemy_type` (`enemy_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `spawn_rule`
--

LOCK TABLES `spawn_rule` WRITE;
/*!40000 ALTER TABLE `spawn_rule` DISABLE KEYS */;
INSERT INTO `spawn_rule` VALUES (1,'1','4',50,1),(2,'2','6',30,2),(3,'1','7',35,3),(4,'1','4',45,4),(5,'2','6',30,5),(6,'2','7',30,6),(7,'2','7',30,7),(8,'1','5',40,8),(9,'3','8',22,9),(10,'4','9',15,10),(11,'1','3',50,11),(12,'1','4',45,12),(13,'1','5',38,13),(14,'1','4',40,14),(15,'2','5',34,15),(16,'2','6',28,16),(17,'2','5',34,17),(18,'2','6',28,18),(19,'3','7',24,19),(20,'3','7',22,20),(21,'1','4',45,23),(22,'2','6',32,27),(23,'3','7',24,28),(24,'3','7',22,29),(25,'2','5',34,36),(26,'2','6',28,37),(27,'4','8',20,38),(28,'1','3',48,41),(29,'1','4',42,42),(30,'2','5',34,43),(31,'2','6',28,44),(32,'3','7',22,45),(33,'2','6',30,46),(34,'1','4',46,49),(35,'2','5',34,52),(36,'3','7',24,55),(37,'1','5',36,58),(38,'2','6',28,59),(39,'2','5',32,60),(40,'2','6',26,61),(41,'3','7',22,62),(42,'4','8',18,63),(43,'1','4',42,66),(44,'1','5',36,67),(45,'2','6',30,68),(46,'1','5',36,69),(47,'1','5',36,70),(48,'2','6',30,71),(49,'2','6',32,75),(50,'2','6',30,78),(51,'3','7',24,79),(52,'3','8',20,80),(53,'4','8',18,81),(54,'4','8',16,82),(55,'5','9',14,83),(56,'5','9',13,84),(57,'6','9',11,85),(58,'6','10',9,86),(59,'7','10',7,87),(60,'8','10',5,88),(61,'1','4',44,89),(62,'4','8',18,90),(63,'5','9',15,91),(64,'5','9',13,92),(65,'6','9',11,93),(66,'7','10',7,94),(67,'8','10',5,95),(68,'1','5',36,96),(69,'2','6',30,97),(70,'4','8',17,98),(71,'5','9',13,99),(72,'6','9',11,100),(73,'1','4',46,101),(74,'3','7',22,102),(75,'4','8',16,103),(76,'6','10',10,104),(77,'3','7',24,105),(78,'4','8',17,106),(79,'6','9',11,107),(80,'7','10',7,108),(81,'8','10',5,109),(82,'1','4',40,110),(83,'3','7',22,111),(84,'5','9',13,112),(85,'5','9',14,113),(86,'6','9',11,114),(87,'6','10',9,115),(88,'2','6',30,116),(89,'3','7',22,117),(90,'3','7',22,118),(91,'4','8',18,119),(92,'4','8',16,120),(93,'4','8',17,121),(94,'5','9',14,122),(95,'6','9',11,123),(96,'3','7',24,124),(97,'4','8',17,125),(98,'5','9',13,126),(99,'6','9',11,127),(100,'5','9',12,128),(101,'6','10',9,129),(102,'7','10',7,130),(103,'8','10',5,131),(104,'3','7',22,132),(105,'5','9',13,133),(106,'4','8',16,134),(107,'2','6',28,135),(108,'8','10',5,136),(109,'1','4',42,137);
/*!40000 ALTER TABLE `spawn_rule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `weapon_ability`
--

DROP TABLE IF EXISTS `weapon_ability`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `weapon_ability` (
  `weapon_ability_id` int NOT NULL,
  `weapon_ability_position` int NOT NULL,
  `weapon_type_id` int NOT NULL,
  `ability_id` int NOT NULL,
  PRIMARY KEY (`weapon_ability_id`),
  KEY `fk_weapon_ability_weapon_type1_idx` (`weapon_type_id`),
  KEY `fk_weapon_ability_ability1_idx` (`ability_id`),
  CONSTRAINT `fk_weapon_ability_ability1` FOREIGN KEY (`ability_id`) REFERENCES `ability` (`ability_id`),
  CONSTRAINT `fk_weapon_ability_weapon_type1` FOREIGN KEY (`weapon_type_id`) REFERENCES `weapon_type` (`weapon_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `weapon_ability`
--

LOCK TABLES `weapon_ability` WRITE;
/*!40000 ALTER TABLE `weapon_ability` DISABLE KEYS */;
INSERT INTO `weapon_ability` VALUES (1,1,1,2),(2,2,1,3),(3,3,1,1),(4,1,4,1),(5,2,4,4),(6,3,4,2),(7,1,5,4),(8,2,5,1),(9,3,5,6),(10,1,9,7),(11,2,9,8),(12,3,9,10),(13,1,2,2),(14,2,2,3),(15,3,2,11),(16,1,3,1),(17,2,3,4),(18,3,3,20),(19,1,6,2),(20,2,6,5),(21,3,6,16),(22,1,7,1),(23,2,7,4),(24,3,7,15),(25,1,8,7),(26,2,8,8),(27,3,8,9),(28,1,10,11),(29,2,10,2),(30,3,10,3),(31,1,11,20),(32,2,11,22),(33,3,11,21),(34,1,12,11),(35,2,12,3),(36,3,12,12),(37,1,13,12),(38,2,13,3),(39,3,13,1),(40,1,14,14),(41,2,14,3),(42,3,14,4),(43,1,15,2),(44,2,15,13),(45,3,15,12),(46,1,16,20),(47,2,16,1),(48,3,16,3),(49,1,17,4),(50,2,17,1),(51,3,17,15),(52,1,18,4),(53,2,18,6),(54,3,18,15),(55,1,19,21),(56,2,19,20),(57,3,19,2),(58,1,20,16),(59,2,20,5),(60,3,20,2),(61,1,21,4),(62,2,21,16),(63,3,21,6),(64,1,22,14),(65,2,22,16),(66,3,22,15),(67,1,23,23),(68,2,23,20),(69,3,23,21),(70,1,24,8),(71,2,24,7),(72,3,24,24),(73,1,25,8),(74,2,25,10),(75,3,25,9),(76,1,26,1),(77,2,26,17),(78,3,26,18),(79,1,27,17),(80,2,27,1),(81,3,27,18),(82,1,28,17),(83,2,28,5),(84,3,28,6),(85,1,29,6),(86,2,29,19),(87,3,29,17),(88,1,30,19),(89,2,30,6),(90,3,30,1),(91,1,31,18),(92,2,31,1),(93,3,31,3),(94,1,32,18),(95,2,32,11),(96,3,32,3),(97,1,33,18),(98,2,33,12),(99,3,33,3),(100,1,34,2),(101,2,34,14),(102,3,34,18),(103,1,35,6),(104,2,35,18),(105,3,35,4);
/*!40000 ALTER TABLE `weapon_ability` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `weapon_type`
--

DROP TABLE IF EXISTS `weapon_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `weapon_type` (
  `weapon_type_id` int NOT NULL,
  `name` varchar(45) NOT NULL,
  `weapon_type_category` varchar(45) NOT NULL,
  `weapon_type_skill` varchar(45) NOT NULL,
  `weapon_type_min_damage` int NOT NULL,
  `weapon_type_max_damage` int NOT NULL,
  `weapon_type_is_two_handed` varchar(45) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  PRIMARY KEY (`weapon_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `weapon_type`
--

LOCK TABLES `weapon_type` WRITE;
/*!40000 ALTER TABLE `weapon_type` DISABLE KEYS */;
INSERT INTO `weapon_type` VALUES (1,'Dagger','Light','Short Blade',1,4,'false'),(2,'Shortsword','Light','Short Blade',1,6,'false'),(3,'Hand Axe','Light','Axe',1,4,'false'),(4,'Longsword','Medium','Long Blade',1,6,'true'),(5,'Greataxe','Medium','Axe',1,6,'true'),(6,'Spear','Medium','Spear',1,6,'true'),(7,'Greatsword','Heavy','Long Blade',1,10,'true'),(8,'Short Bow','Ranged','Marksman',1,6,'true'),(9,'Long Bow','Ranged','Marksman',1,6,'true'),(10,'Dirk','Light','Short Blade',1,4,'false'),(11,'Throwing Knife','Light','Short Blade',1,4,'false'),(12,'Keris','Light','Short Blade',1,6,'false'),(13,'Saber','Medium','Long Blade',1,6,'false'),(14,'Scimitar','Medium','Long Blade',1,6,'false'),(15,'Estoc','Medium','Long Blade',1,8,'false'),(16,'Hatchet','Light','Axe',1,4,'false'),(17,'War Axe','Medium','Axe',1,6,'false'),(18,'Battleaxe','Heavy','Axe',1,10,'true'),(19,'Javelin','Light','Spear',1,6,'false'),(20,'Pike','Medium','Spear',1,8,'true'),(21,'Halberd','Heavy','Spear',1,10,'true'),(22,'Glaive','Heavy','Spear',1,10,'true'),(23,'Sling','Ranged','Marksman',1,4,'false'),(24,'Crossbow','Ranged','Marksman',1,8,'true'),(25,'Warbow','Ranged','Marksman',1,8,'true'),(26,'Mallet','Light','Hammer',1,4,'false'),(27,'War Pick','Medium','Hammer',1,6,'false'),(28,'Lucerne','Medium','Hammer',1,8,'true'),(29,'Maul','Heavy','Hammer',1,10,'true'),(30,'Sledge','Heavy','Hammer',1,12,'true'),(31,'Cudgel','Light','Club',1,4,'false'),(32,'Blackjack','Light','Club',1,4,'false'),(33,'Baton','Medium','Club',1,6,'false'),(34,'Quarterstaff','Medium','Club',1,6,'true'),(35,'Greatclub','Heavy','Club',1,10,'true');
/*!40000 ALTER TABLE `weapon_type` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-24 12:25:09

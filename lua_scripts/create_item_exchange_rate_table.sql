-- --------------------------------------------------------
-- Host:                         192.168.0.85
-- Server version:               8.4.6 - MySQL Community Server - GPL
-- Server OS:                    Linux
-- HeidiSQL Version:             12.13.0.7147
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- Dumping structure for table acore_characters.item_exchange_rates
DROP TABLE IF EXISTS `item_exchange_rates`;
CREATE TABLE IF NOT EXISTS `item_exchange_rates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `subject` varchar(64) COLLATE utf8mb4_general_ci NOT NULL,
  `give_item` int NOT NULL,
  `give_qty` int NOT NULL DEFAULT '1',
  `receive_item` int NOT NULL,
  `receive_qty` int NOT NULL DEFAULT '1',
  `enabled` tinyint(1) DEFAULT '1',
  `description` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `subject` (`subject`),
  KEY `subject_2` (`subject`),
  KEY `enabled` (`enabled`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table acore_characters.item_exchange_rates: ~2 rows (approximately)
INSERT INTO `item_exchange_rates` (`id`, `subject`, `give_item`, `give_qty`, `receive_item`, `receive_qty`, `enabled`, `description`) VALUES
	(1, 'TOAC', 10620, 240, 12363, 1, 1, '240 Thorium Ore -> 1 Arcane Crystal'),
	(2, 'BSAC', 12361, 10, 12363, 1, 1, '10 Blue Sapphire -> 1 Arcane Crystal');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;

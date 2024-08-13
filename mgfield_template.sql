-- phpMyAdmin SQL Dump
-- version 5.2.1deb1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Apr 04, 2024 at 08:26 AM
-- Server version: 10.11.6-MariaDB-0+deb12u1
-- PHP Version: 8.2.7

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `mgfield`
--

-- --------------------------------------------------------

--
-- Table structure for table `mgfield`
--

CREATE TABLE `mgfield` (
  `time_utc` datetime(3) NOT NULL,
  `time_local` datetime(3) NOT NULL,
  `x_value` float NOT NULL,
  `y_value` float NOT NULL,
  `z_value` float NOT NULL,
  `out_value` float NOT NULL,
  `measurement_result` float NOT NULL,
  `measurement_duration` float NOT NULL,
  `start_avg` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `netstats`
--

CREATE TABLE `netstats` (
  `time_utc` datetime NOT NULL,
  `time_local` datetime NOT NULL,
  `hostname` text NOT NULL,
  `local_ip` text NOT NULL,
  `packets_sent` text NOT NULL,
  `packets_recv` text NOT NULL,
  `errin` int(11) NOT NULL,
  `errout` int(11) NOT NULL,
  `dropin` int(11) NOT NULL,
  `dropout` int(11) NOT NULL,
  `target1` float NOT NULL,
  `target2` float NOT NULL,
  `target3` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `sysstats`
--

CREATE TABLE `sysstats` (
  `time_utc` datetime NOT NULL,
  `time_local` datetime NOT NULL,
  `cpu_speed` float NOT NULL,
  `cpu_usage` float NOT NULL,
  `cpu_ctx_switches` float NOT NULL,
  `cpu_interrupts` float NOT NULL,
  `cpu_soft_interrupts` float NOT NULL,
  `ram_total` int(11) NOT NULL,
  `ram_free` int(11) NOT NULL,
  `ram_used` int(11) NOT NULL,
  `ram_cached` int(11) NOT NULL,
  `ram_free_wcache_perc` float NOT NULL,
  `ram_free_wocache_perc` float NOT NULL,
  `cpu_thermal` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `temperature`
--

CREATE TABLE `temperature` (
  `time_utc` datetime NOT NULL,
  `time_local` datetime NOT NULL,
  `temperature_value` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

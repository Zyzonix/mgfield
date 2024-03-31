-- phpMyAdmin SQL Dump
-- version 5.2.1deb1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Mar 31, 2024 at 08:19 PM
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
  `time` date NOT NULL,
  `avg_result` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `mgfieldraw`
--

CREATE TABLE `mgfieldraw` (
  `time` date NOT NULL,
  `x_value` int(11) NOT NULL,
  `y_value` int(11) NOT NULL,
  `z_value` int(11) NOT NULL,
  `measurement_result` int(11) NOT NULL,
  `time_delta` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `netstats`
--

CREATE TABLE `netstats` (
  `time` date NOT NULL,
  `hostname` text NOT NULL,
  `local_ip` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `sysstats`
--

CREATE TABLE `sysstats` (
  `time` date NOT NULL,
  `cpu_speed` text NOT NULL,
  `cpu_usage` text NOT NULL,
  `ram_total` text NOT NULL,
  `ram_free` text NOT NULL,
  `ram_used` text NOT NULL,
  `ram_cached` text NOT NULL,
  `ram_free_wcache_perc` text NOT NULL,
  `ram_free_wocache_perc` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `temperature`
--

CREATE TABLE `temperature` (
  `time` date NOT NULL,
  `tempeature_value` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

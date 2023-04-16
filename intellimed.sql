-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 15, 2023 at 08:25 PM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `intellimed`
--

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `sno` int(11) NOT NULL,
  `name` varchar(20) NOT NULL,
  `phoneno` varchar(10) NOT NULL,
  `email` varchar(20) NOT NULL,
  `username` varchar(20) NOT NULL,
  `password` varchar(20) NOT NULL,
  `address` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`sno`, `name`, `phoneno`, `email`, `username`, `password`, `address`) VALUES
(1, 'nipun', '9078645324', 'nipun@gmail.com', 'nipun', '123456', 'hello,thapar'),
(2, 'Suddhasattwa Khan', '1234567893', 'khansuddhasattwa@gma', 'suddha', '123456', '1st floor, A31 Bagha Jatin Sarani, Sector 2A Bidha'),
(3, 'Raj Khan', '1000000000', 'raj@gmail.com', 'Raj', '$2b$10$ONPrQS9Nv3uGg', '1st floor, A31 Bagha Jatin Sarani, Sector 2A Bidha'),
(5, 'harsh', '1234567895', 'harsh@gmail.com', 'Harsh', '$2b$10$y0VJ3t/BgOCVS', 'kdngdkjgntg'),
(6, 'Raju', '123456', 'raju@gmail.com', 'raju', '$2b$10$8p70fjiJ/hNDF', 'djknvdjkjvn'),
(7, 'yupy', '1234567892', 'skha@gmail.com', 'yupy', '$2b$10$VawhcuT7EqvLF', 'rngklt'),
(8, 'harshnipun', '1234567899', 'harshnipun@gmail.com', 'harshnipun', '123456', 'unkjernv'),
(11, 'nipungarg', '1234567645', 'ngarg@gmail.com', 'nipungarg', '123456', 'frrhr');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`sno`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `phoneno` (`phoneno`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `sno` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

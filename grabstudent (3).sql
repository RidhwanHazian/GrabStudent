-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 28, 2025 at 11:30 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `grabstudent`
--

-- --------------------------------------------------------

--
-- Table structure for table `booking`
--

CREATE TABLE `booking` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `name` varchar(100) NOT NULL,
  `pickup` varchar(255) NOT NULL,
  `dropoff` varchar(255) NOT NULL,
  `datetime` datetime NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `driver_id` int(11) DEFAULT NULL,
  `status` enum('Pending','Accepted','On the way','Completed','Cancelled') DEFAULT 'Pending',
  `total_amount` decimal(10,2) DEFAULT 0.00,
  `payment_status` enum('Pending','Paid') DEFAULT 'Pending',
  `payment_method` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `booking`
--

INSERT INTO `booking` (`id`, `user_id`, `name`, `pickup`, `dropoff`, `datetime`, `created_at`, `driver_id`, `status`, `total_amount`, `payment_status`, `payment_method`) VALUES
(1, NULL, 'Ridhwan', 'Jelatang', 'Sungai petai', '2025-08-26 18:27:00', '2025-08-26 10:27:14', 1, 'Completed', 0.00, 'Pending', NULL),
(2, 1, 'Ridhwan', 'Jelatang', 'Sungai petai', '2025-08-26 19:08:00', '2025-08-26 11:08:19', 1, 'Accepted', 0.00, 'Pending', NULL),
(4, 1, 'Ridhwan', 'Jelatang', 'Sungai petai', '2025-08-26 19:14:00', '2025-08-26 11:14:45', 1, 'Completed', 0.00, 'Pending', NULL),
(5, 3, 'Adam', 'jasin', 'MITC', '2025-08-26 19:33:00', '2025-08-26 11:33:12', NULL, 'Pending', 0.00, 'Pending', NULL),
(6, 3, 'Adam', 'Jelatang', 'MITC', '2025-08-27 19:34:00', '2025-08-26 11:34:10', 1, 'Pending', 0.00, 'Pending', NULL),
(7, 1, 'Haris', 'Jelatang', 'Sungai petai', '2025-08-28 10:15:00', '2025-08-27 02:15:49', 1, 'Cancelled', 20.00, 'Paid', 'Online'),
(8, 9, 'olap', 'UiTM Jasin', 'Sungai petai', '2025-08-28 19:08:00', '2025-08-27 11:08:47', 1, 'Accepted', 0.00, 'Pending', NULL),
(9, 2, 'Haris', 'UiTM Jasin', 'Shah Alam', '2025-09-04 19:11:00', '2025-08-27 11:11:18', 1, 'On the way', 0.00, 'Pending', NULL),
(10, 1, 'Ridhwan', 'Jelatang', 'MITC', '2025-08-28 23:59:00', '2025-08-27 15:59:30', 1, 'Completed', 12.00, 'Paid', 'Cash');

-- --------------------------------------------------------

--
-- Table structure for table `drivers`
--

CREATE TABLE `drivers` (
  `driver_id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `drivers`
--

INSERT INTO `drivers` (`driver_id`, `name`, `email`, `password`) VALUES
(1, 'wan', 'mridhwan950@gmail.com', '123'),
(2, 'Someone', 'someone@gmail.com', 's');

-- --------------------------------------------------------

--
-- Table structure for table `feedback`
--

CREATE TABLE `feedback` (
  `id` int(11) NOT NULL,
  `booking_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `rating` int(11) NOT NULL,
  `comment` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `feedback`
--

INSERT INTO `feedback` (`id`, `booking_id`, `user_id`, `rating`, `comment`, `created_at`) VALUES
(4, 10, 1, 3, 'nice', '2025-08-28 04:57:39');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `user_type` enum('customer','driver','admin') NOT NULL DEFAULT 'customer'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `email`, `password`, `name`, `created_at`, `user_type`) VALUES
(1, 'iwghostpride@gmail.com', 'wan', 'Ridhwan', '2025-08-26 11:08:00', 'customer'),
(2, 'harisimran0524@gmail.com', 'h', 'Haris', '2025-08-26 11:15:36', 'customer'),
(3, 'adamirza3107@gmail.com', 'scrypt:32768:8:1$HlLyZdceuj5nL805$e654ca2ce2b4aeeae6ea88b0264399d4416d0d874ab13b4cd31c5e60f7fea4744833e4f56bc94804119fae7547ecd7eceead7b3c5f332029a38d5d43d840733a', 'Adam', '2025-08-26 11:32:52', 'customer'),
(7, 'iwan12@gmail.com', '1234', 'wan', '2025-08-27 02:56:27', 'driver'),
(8, 'admin@example.com', 'admin123', 'Admin', '2025-08-27 04:27:21', 'admin'),
(9, '2023482808@student.uitm.edu.my', '123', 'olap', '2025-08-27 11:04:46', 'customer');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `booking`
--
ALTER TABLE `booking`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `driver_id` (`driver_id`);

--
-- Indexes for table `drivers`
--
ALTER TABLE `drivers`
  ADD PRIMARY KEY (`driver_id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `feedback`
--
ALTER TABLE `feedback`
  ADD PRIMARY KEY (`id`),
  ADD KEY `booking_id` (`booking_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `booking`
--
ALTER TABLE `booking`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `drivers`
--
ALTER TABLE `drivers`
  MODIFY `driver_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `feedback`
--
ALTER TABLE `feedback`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `booking`
--
ALTER TABLE `booking`
  ADD CONSTRAINT `booking_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `booking_ibfk_2` FOREIGN KEY (`driver_id`) REFERENCES `drivers` (`driver_id`);

--
-- Constraints for table `feedback`
--
ALTER TABLE `feedback`
  ADD CONSTRAINT `feedback_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `booking` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `feedback_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

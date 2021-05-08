--
-- 資料庫： `factor_analysis_task`
--

-- --------------------------------------------------------

--
-- 資料表結構 `node`
--

CREATE TABLE `node` (
  `node_id` int(11) PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `name` varchar(50) NOT NULL,
  `cpu_status` double NOT NULL,
  `core_num` double NOT NULL,
  `health` int(1) NOT NULL,
  `health_time` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `task`
--

CREATE TABLE `task` (
  `task_id` int(11) PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `factor_list` longtext NOT NULL,
  `strategy_list` longtext NOT NULL,
  `window_list` longtext NOT NULL,
  `method_list` longtext NOT NULL,
  `group_list` longtext NOT NULL,
  `position_list` longtext NOT NULL,
  `begin_time` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `task_status`
--

CREATE TABLE `task_status` (
  `task_status_id` int(11) PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `task_id` int(11) NOT NULL,
  `factor` varchar(20) NOT NULL,
  `strategy` int(1) NOT NULL,
  `window` int(1) NOT NULL,
  `method` int(1) NOT NULL,
  `group` int(2) NOT NULL,
  `position` int(3) NOT NULL,
  `finish_time` varchar(50) NULL,
  `owner` varchar(50) NOT NULL,
  `status` int(1) NOT NULL DEFAULT 0,
  FOREIGN KEY (task_id) REFERENCES task(task_id) 
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

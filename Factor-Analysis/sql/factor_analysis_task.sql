--
-- 資料庫： `factor_analysis_task`
--

-- --------------------------------------------------------

--
-- 資料表結構 `node`
--

CREATE TABLE `node` (
  `node_id` int(11) PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cpu_status` double NOT NULL,
  `core_num` double NOT NULL,
  `health` int(1) NOT NULL,
  `health_time` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `task`
--

CREATE TABLE `task` (
  `task_id` int(11) PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `factor_list` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `strategy_list` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `group_list` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `position_list` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `n_season` int(1) NOT NULL,
  `begin_time` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `task_status`
--

CREATE TABLE `task_status` (
  `task_status_id` int(11) PRIMARY KEY AUTO_INCREMENT NOT NULL,
  `task_id` int(11) NOT NULL,
  `factor` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `strategy` int(1) NOT NULL,
  `group` int(2) NOT NULL,
  `position` int(3) NOT NULL,
  `n_season` int(1) NOT NULL,
  `finish_time` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `owner` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` int(1) NOT NULL DEFAULT 0,
  FOREIGN KEY (task_id) REFERENCES task(task_id) 
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


INSERT INTO `task` (`task_id`, `factor_list`, `strategy_list`, `group_list`, `position_list`, `n_season`, `begin_time`) 
VALUES
('0', 'EPS|GVI|MOM&PE', '1|2|3', '1|2|3|4|5|6|7|8|9|10', '5|10|15|30|90|150', '2021-02-08 17:50:27.962738'),
('0', 'EPS|CROIC|MOM&PE', '0|2|3', '1|2|3|4|5|6|7|8|9|10', '5|10|15|30|90|150', '2021-02-08 17:50:27.962738');

INSERT INTO `task_status` (`task_status_id`, `task_id`, `factor`, `strategy`, `group`, `position`, `n_season`, `finish_time`, `owner`, `status`) 
VALUES
('0', (SELECT `task_id` from `task` where `begin_time`='2021-02-08 17:50:27.962738'), 'EPS', '1', '1', '5', '0', '2021-02-08 14:14:15.439557', '140.115.87.197-test', '0'),
('0', (SELECT `task_id` from `task` where `begin_time`='2021-02-08 17:50:27.962738'), 'GVI', '1', '1', '15', '0', '2021-02-08 14:14:16.439557', '140.115.87.197-test', '0'),
('0', (SELECT `task_id` from `task` where `begin_time`='2021-02-08 17:50:27.962738'), 'MOM&PE', '2', '1', '30', '0', '2021-02-08 14:14:16.439557', '140.115.87.197-test', '1');

